
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime as dt, timedelta

st.set_page_config(page_title="Stock Analysis with MACD and EMA", layout="wide")

# ============================================================
# PROJECT: Stock Market Analysis and Prediction Dashboard
# AUTHOR: Preona Dsouza
# COPYRIGHT: © 2026 Preona Dsouza. All Rights Reserved.
#
# Original project implementation and design by the author.
# Unauthorised copying, modification or redistribution
# is prohibited except where permitted by applicable law.
#
# ============================================================

def navigation_bar():
    st.markdown("""
        <style>
        .nav-container {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 55px;
            z-index: 9999999;

            display: flex;
            justify-content: flex-start;
            align-items: center;
            gap: 12px;

            padding: 8px 20px;
            background-color: #e5e7eb;
            border-bottom: 1px solid #d1d5db;
            box-sizing: border-box;
        }

        .nav-container a {
            padding: 6px 13px;
            background-color: #7e087e;
            color: #ffffff !important;
            border: 1px solid #7e087e;
            border-radius: 20px;
            text-decoration: none !important;
            font-size: 11px;
            font-weight: 700;
            white-space: nowrap;
            transition: all 0.3s ease;
        }

        .nav-container a:hover {
            background-color: #d1d5db;
            color: #151226 !important;
            border-color: #d1d5db;
        }

        .nav-container .home-button {
            margin-right: auto;
        }
        </style>

        <div class="nav-container">
            <a class="home-button" href="http://127.0.0.1:8000/navbarpage.html">HOME</a>
            <a href="http://127.0.0.1:8050/" target="_blank">VISUALIZATION</a>
            <a href="http://127.0.0.1:8501/" target="_blank">PREDICTION</a>
            
        </div>
    """, unsafe_allow_html=True)

navigation_bar()
st.title("Stock Analysis with MACD and EMA")

# Stock input
stocksymbol = st.text_input(
    "Enter Stock Symbol",
    value="AAPL",
    placeholder="Example: AAPL, MSFT, RELIANCE.NS"
).strip().upper()

from datetime import datetime, timedelta

start_date = '2021-01-04'

# Latest completed calendar date
display_end_date = datetime.now().date() - timedelta(days=1)

# Yahoo Finance end date is exclusive
download_end_date = display_end_date + timedelta(days=1)

end_date = download_end_date.strftime('%Y-%m-%d')

st.write(f"Time Period: {start_date} to {dt.now().date()}")

st.markdown("""
    <style>
    .preona-watermark {
        position: fixed;
        bottom: 12px;
        right: 18px;
        z-index: 9999999;

        background: rgba(255, 255, 255, 0.94);
        border: 1px solid #7e087e;
        border-radius: 8px;

        padding: 8px 13px;
        text-align: center;

        color: #7e087e;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 1px;

        box-shadow: 0 2px 8px rgba(0,0,0,0.12);
        pointer-events: none;
    }

    .preona-watermark span {
        display: block;
        font-size: 9px;
        font-weight: 500;
        letter-spacing: 0.4px;
        margin-top: 3px;
    }
    </style>

    <div class="preona-watermark">
        By <br> PREONA DSOUZA
       
    </div>
""", unsafe_allow_html=True)


# Download only when the user clicks the button
if st.button("Analyse Stock"):

    if not stocksymbol:
        st.error("Please enter a valid stock symbol.")
        st.stop()

    try:
        with st.spinner(f"Downloading data for {stocksymbol}..."):
            

            data = yf.download(
                stocksymbol,
                start=start_date,
                end=end_date,
                auto_adjust=True,
                progress=False,
                threads=False,
                timeout=20
            )

        if data is None or data.empty:
            st.error(
                f"No historical data returned for {stocksymbol}. "
                "Yahoo Finance may be rate-limiting requests or temporarily unavailable."
            )
            st.stop()

        # Handle yfinance MultiIndex columns
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        if "Close" not in data.columns:
            st.error("Closing price data is unavailable.")
            st.stop()

        close = data["Close"]

        # Ensure Close is a Series
        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0]

        close = close.dropna()

        if len(close) < 50:
            st.error("Not enough historical data to calculate the indicators.")
            st.stop()

        # Calculate EMA
        ema_12 = close.ewm(span=12, adjust=False).mean()
        ema_26 = close.ewm(span=26, adjust=False).mean()

        # Calculate MACD and Signal Line
        macd = ema_12 - ema_26
        signal_line = macd.ewm(span=9, adjust=False).mean()

        # Calculate SMA
        sma = close.rolling(window=20).mean()

        # Create results DataFrame
        results = pd.DataFrame(index=close.index)
        results["Close"] = close
        results["EMA 12"] = ema_12
        results["EMA 26"] = ema_26
        results["MACD"] = macd
        results["Signal Line"] = signal_line
        results["SMA 20"] = sma

        # Detect MACD crossovers
        results["Buy Signal"] = (
            (macd > signal_line) &
            (macd.shift(1) <= signal_line.shift(1))
        )

        results["Sell Signal"] = (
            (macd < signal_line) &
            (macd.shift(1) >= signal_line.shift(1))
        )

        buy_points = results[results["Buy Signal"]]
        sell_points = results[results["Sell Signal"]]

        # Latest values
        latest = results.iloc[-1]

        st.subheader(f"Analysis for {stocksymbol}")

        col1, col2, col3 = st.columns(3)

        col1.metric("Latest Closing Price", f"{latest['Close']:.2f}")
        col2.metric("MACD", f"{latest['MACD']:.4f}")
        col3.metric("Signal Line", f"{latest['Signal Line']:.4f}")

        # Latest trading signal
        if latest["Buy Signal"]:
            st.success("Latest Signal: BUY")
        elif latest["Sell Signal"]:
            st.error("Latest Signal: SELL")
        elif latest["MACD"] > latest["Signal Line"]:
            st.info("Current MACD condition: Bullish")
        else:
            st.info("Current MACD condition: Bearish")

        # Price chart
        st.subheader("Stock Price and Moving Average")

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=results.index,
            y=results["Close"],
            name="Closing Price"
        ))

        fig.add_trace(go.Scatter(
            x=results.index,
            y=results["SMA 20"],
            name="SMA 20"
        ))

        fig.add_trace(go.Scatter(
            x=buy_points.index,
            y=buy_points["Close"],
            mode="markers",
            name="Buy Signal",
            marker=dict(symbol="triangle-up", size=10)
        ))

        fig.add_trace(go.Scatter(
            x=sell_points.index,
            y=sell_points["Close"],
            mode="markers",
            name="Sell Signal",
            marker=dict(symbol="triangle-down", size=10)
        ))

        fig.update_layout(
            title=f"{stocksymbol} - Price and Buy/Sell Signals",
            xaxis_title="Date",
            yaxis_title="Price",
            hovermode="x unified"
        )

        st.plotly_chart(fig, use_container_width=True)

        # MACD chart
        st.subheader("MACD Indicator")

        macd_fig = go.Figure()

        macd_fig.add_trace(go.Scatter(
            x=results.index,
            y=results["MACD"],
            name="MACD"
        ))

        macd_fig.add_trace(go.Scatter(
            x=results.index,
            y=results["Signal Line"],
            name="Signal Line"
        ))

        macd_fig.add_hline(y=0, line_dash="dash")

        macd_fig.update_layout(
            title="MACD and Signal Line",
            xaxis_title="Date",
            yaxis_title="MACD Value"
        )

        st.plotly_chart(macd_fig, use_container_width=True)

        # Latest indicator values
        st.subheader("Latest Indicator Values")

        st.dataframe(
            results.tail(10).sort_index(ascending=False),
            use_container_width=True
        )

    except Exception as e:
        st.error(f"Unable to analyse {stocksymbol}.")
        st.code(str(e))

st.link_button("Advanced analysis and stimualtion", "http://localhost:8503/")