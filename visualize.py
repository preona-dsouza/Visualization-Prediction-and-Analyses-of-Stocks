
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import yfinance as yf

from datetime import date, timedelta
from cachetools import TTLCache, cached


app = dash.Dash(__name__)

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Stock Dashboard</title>
        {%favicon%}
        {%css%}

        <style>
            .nav-button {
                background-color: #7e087e;
                color: #ffffff;
                border: 1px solid #7e087e;
                border-radius: 20px;
                padding: 8px 16px;
                font-size: 11px;
                font-weight: 700;
                cursor: pointer;
                transition: all 0.3s ease;
            }

            .nav-button:hover {
                background-color: #d1d5db;
                color: #151226;
                border-color: #d1d5db;
            }
        </style>
    </head>

    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Keep downloaded data for 15 minutes.
stock_cache = TTLCache(maxsize=20, ttl=900)


@cached(stock_cache)
def get_stock_data(symbol):
    end_date = date.today() + timedelta(days=1)

    data = yf.download(
        symbol,
        start="2025-08-01",
        end=end_date.strftime("%Y-%m-%d"),
        auto_adjust=True,
        progress=False,
        threads=False,
        timeout=15
    )

    if data.empty:
        return pd.DataFrame()

    # Handle yfinance MultiIndex columns.
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    return data


app.layout = html.Div([
      # Navigation bar
 html.Div([
    html.A(
        html.Button("HOME", className="nav-button"),
        href="http://127.0.0.1:8000/navbarpage.html"
    ),

    html.A(
        html.Button("STOCK PREDICTION", className="nav-button"),
        href="http://127.0.0.1:8501/",
        
    ),

  
    html.A(
        html.Button("STOCK ANALYSIS", className="nav-button"),
        href="http://127.0.0.1:8502/",
        
    ),

], style={
    "display": "flex",
    "justifyContent": "center",
    "alignItems": "center",
    "gap": "15px",
    "padding": "18px",
    "backgroundColor": "#e5e7eb",
    "borderRadius": "10px",
    "marginBottom": "25px",
    "flexWrap": "wrap"
}),
    html.H1("Stock Visualizing Dashboard"),

   
    html.P("Select a stock symbol:"),

    dcc.Dropdown(
        id="input",
        options=[
            {"label": "Tata Consultancy Services", "value": "TCS.NS"},
            {"label": "Tesla Inc.", "value": "TSLA"},
            {"label": "Adani Power Limited", "value": "ADANIPOWER.NS"},
            {"label": "Tata Motors Limited", "value": "TATAMOTORS.NS"},
            {"label": "Bharti Airtel Limited", "value": "BHARTIARTL.NS"},
            {"label": "State Bank of India", "value": "SBIN.NS"},
            {"label": "Maruti Suzuki India Limited", "value": "MARUTI.NS"},
            {"label": "Bharat Petroleum Corporation Limited", "value": "BPCL.NS"},
            {"label": "Infosys Limited", "value": "INFY.NS"}
        ],
        value=None,
        placeholder="Choose a stock",
        clearable=True
    ),

    dcc.Loading(
        children=html.Div([
            dcc.Graph(id="stock_graph"),
            html.Div(id="stock_table"),
            dcc.Graph(id="output-graph"),
            dcc.Graph(id="stock_graph_live")
        ])
    )
])


@app.callback(
    Output("stock_graph", "figure"),
    Output("stock_table", "children"),
    Output("output-graph", "figure"),
    Output("stock_graph_live", "figure"),
    Input("input", "value")
)
def update_graph_and_table(stock_symbol):

    empty_fig = go.Figure()

    if not stock_symbol:
        return empty_fig, [], empty_fig, empty_fig

    try:
        # Reuse cached data rather than downloading it repeatedly.
        stock_data = get_stock_data(stock_symbol).copy()

        if stock_data.empty:
            message = html.P(
                "No historical data available. Yahoo Finance may be "
                "temporarily unavailable or rate-limiting requests."
            )
            return empty_fig, message, empty_fig, empty_fig

        close = stock_data["Close"]
        open_price = stock_data["Open"]
        high = stock_data["High"]
        low = stock_data["Low"]

        # Candlestick chart
        stock_graph = go.Figure(
            data=[
                go.Candlestick(
                    x=stock_data.index,
                    open=open_price,
                    high=high,
                    low=low,
                    close=close,
                    name="Stock Price"
                )
            ]
        )

        stock_graph.update_layout(
            title=f"{stock_symbol} Stock Price",
            xaxis_title="Date",
            yaxis_title="Price",
            template="plotly_white"
        )

        # Display the latest 10 trading sessions.
        table_data = stock_data.tail(10).reset_index()
        date_column = table_data.columns[0]

        stock_table = html.Table(
            style={
                "border": "1px solid black",
                "borderCollapse": "collapse",
                "margin": "auto",
                "width": "90%"
            },
            children=[
                html.Thead(
                    html.Tr([
                        html.Th(col, style={"padding": "8px"})
                        for col in [
                            "Date", "Open", "High", "Low", "Close"
                        ]
                    ])
                ),
                html.Tbody([
                    html.Tr([
                        html.Td(
                            row[date_column].strftime("%Y-%m-%d"),
                            style={"padding": "8px"}
                        ),
                        *[
                            html.Td(
                                round(float(row[col]), 2),
                                style={"padding": "8px"}
                            )
                            for col in ["Open", "High", "Low", "Close"]
                        ]
                    ])
                    for _, row in table_data.iterrows()
                ])
            ]
        )

        # Technical indicators
        stock_data["Moving Average"] = close.rolling(20).mean()
        stock_data["Cumulative Average"] = close.expanding().mean()
        stock_data["EWMA30"] = close.ewm(span=30).mean()

        window = 20
        weights = np.arange(1, window + 1)

        stock_data["Weighted MA"] = close.rolling(window).apply(
            lambda prices: np.dot(prices, weights) / weights.sum(),
            raw=True
        )

        # Polynomial fit (requires at least four observations).
        x_values = np.arange(len(stock_data))

        if len(stock_data) >= 4:
            poly_fit = np.polyfit(x_values, close.to_numpy(), 3)
            polynomial_values = np.polyval(poly_fit, x_values)
        else:
            polynomial_values = np.full(len(stock_data), np.nan)

        # Moving average chart
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=stock_data.index,
            y=close,
            name="Close Price"
        ))

        fig.add_trace(go.Scatter(
            x=stock_data.index,
            y=stock_data["Moving Average"],
            name="Moving Average (20)"
        ))

        fig.add_trace(go.Scatter(
            x=stock_data.index,
            y=stock_data["Cumulative Average"],
            name="Cumulative Average"
        ))

        fig.add_trace(go.Scatter(
            x=stock_data.index,
            y=stock_data["EWMA30"],
            name="Exponential Moving Average (30)"
        ))

        fig.add_trace(go.Scatter(
            x=stock_data.index,
            y=stock_data["Weighted MA"],
            name="Weighted Moving Average"
        ))

        fig.add_trace(go.Scatter(
            x=stock_data.index,
            y=polynomial_values,
            name="Polynomial Fit"
        ))

        fig.update_layout(
            title=f"{stock_symbol} Stock Price with Moving Averages",
            xaxis_title="Date",
            yaxis_title="Price",
            template="plotly_white"
        )

        # Historical closing-price chart.
        # This is not a real-time live chart.
        fig_live = go.Figure()

        fig_live.add_trace(go.Scatter(
            x=stock_data.index,
            y=close,
            name="Close Price"
        ))

        fig_live.update_layout(
            title=f"{stock_symbol} Historical Closing Price",
            xaxis_title="Date",
            yaxis_title="Price",
            template="plotly_white"
        )

        return stock_graph, stock_table, fig, fig_live
    
    except Exception as e:
        error_message = html.P(f"Unable to retrieve stock data: {e}")
        return empty_fig, error_message, empty_fig, empty_fig


if __name__ == "__main__":
    app.run_server(
        debug=False,
        use_reloader=False,
        port=8050
    )
