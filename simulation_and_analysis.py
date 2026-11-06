import streamlit as st
import yfinance as yf
import pandas as pd
import math
from datetime import date, timedelta



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
# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Stock Analysis Dashboard",
    page_icon="📈",
    layout="wide"
)

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

# ============================================================
# COMPANY LIST
# ============================================================

companies = {
    'Apple Inc.': 'AAPL',
    'Microsoft Corporation': 'MSFT',
    'Reliance Industries Limited': 'RELIANCE.NS',
    'Tata Consultancy Services': 'TCS.NS',
    'HDFC Bank': 'HDFCBANK.NS',
    'Infosys Limited': 'INFY.NS',
    'Hindustan Unilever Limited': 'HINDUNILVR.NS',
    'Bharti Airtel Limited': 'BHARTIARTL.NS',
    'ICICI Bank': 'ICICIBANK.NS',
    'ITC Limited': 'ITC.NS',
    'Axis Bank': 'AXISBANK.NS',
    'State Bank of India': 'SBIN.NS',
    'Bajaj Finance Limited': 'BAJFINANCE.NS',
    'Asian Paints': 'ASIANPAINT.NS',
    'Wipro Limited': 'WIPRO.NS',
    'Mahindra & Mahindra': 'M&M.NS',
    'Maruti Suzuki India Limited': 'MARUTI.NS',
    'Amazon.com Inc.': 'AMZN',
    'Tesla Inc.': 'TSLA',
    'Google': 'GOOGL'
}


# ============================================================
# YAHOO FINANCE HISTORICAL DATA
# ============================================================

@st.cache_data(ttl=900, show_spinner=False)
def get_stock_data(symbol, start_date, end_date):

    data = yf.download(
        symbol,
        start=start_date,
        end=end_date,
        auto_adjust=True,
        progress=False,
        threads=False,
        timeout=30
    )

    if data is None or data.empty:
        raise ValueError(
            f"No historical data returned for {symbol}. "
            "Yahoo Finance may be temporarily unavailable "
            "or rate-limiting requests."
        )

    # Convert MultiIndex columns into ordinary columns.
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    if "Close" not in data.columns:
        raise ValueError(
            f"Closing price data is missing for {symbol}."
        )

    data["Close"] = pd.to_numeric(
        data["Close"], errors="coerce"
    )

    data = data.dropna(subset=["Close"])

    if data.empty:
        raise ValueError(
            f"No valid closing prices found for {symbol}."
        )

    return data


# ============================================================
# CALCULATE STOCK METRICS
# ============================================================

def calculate_metrics(stock_data):

    if stock_data is None or stock_data.empty:
        return None

    if isinstance(stock_data.columns, pd.MultiIndex):
        stock_data = stock_data.copy()
        stock_data.columns = stock_data.columns.get_level_values(0)

    if "Close" not in stock_data.columns:
        return None

    prices = pd.to_numeric(
        stock_data["Close"], errors="coerce"
    ).dropna()

    if len(prices) < 2:
        return None

    if prices.iloc[0] <= 0 or prices.iloc[-1] <= 0:
        return None

    daily_returns = prices.pct_change().dropna()

    if daily_returns.empty:
        return None

    cumulative_return = (
        prices.iloc[-1] / prices.iloc[0]
    ) - 1

    years = (
        prices.index[-1] - prices.index[0]
    ).days / 365.25

    if years <= 0:
        return None

    annualized_return = (
        (prices.iloc[-1] / prices.iloc[0])
        ** (1 / years)
    ) - 1

    avg_daily_return = daily_returns.mean()

    annualized_volatility = (
        daily_returns.std() * math.sqrt(252)
    )

    return {
        "Cumulative Return": cumulative_return,
        "Annualized Return": annualized_return,
        "Avg Daily Return": avg_daily_return,
        "Annualized Volatility": annualized_volatility
    }


# ============================================================
# SHARED DATA FOR THIS STREAMLIT RUN
# ============================================================

stock_data_cache = {}
data_errors = {}


def load_company_data(company, start_date, end_date):

    symbol = companies[company]

    if symbol in stock_data_cache:
        return stock_data_cache[symbol]

    try:

        data = get_stock_data(
            symbol,
            start_date,
            end_date
        )

        stock_data_cache[symbol] = data

        return data

    except Exception as e:

        data_errors[symbol] = str(e)

        return None


# ============================================================
# DATE RANGE
# ============================================================

def get_date_strings(start_date, end_date):

    start_string = start_date.strftime("%Y-%m-%d")

    # Yahoo Finance end date is exclusive.
    end_string = (
        end_date + timedelta(days=1)
    ).strftime("%Y-%m-%d")

    return start_string, end_string


# ============================================================
# 1. STOCK SELECTION
# ============================================================

st.title("Stock Market Analysis Dashboard")

st.header("1. Stock Selection")

selected_companies = st.multiselect(
    "Select companies:",
    list(companies.keys()),
    default=["Apple Inc."]
)

if selected_companies:

    st.write("Selected Companies:")

    for company in selected_companies:
        st.write(f"- {company}")

else:

    st.info("Select at least one company.")


col1, col2 = st.columns(2)

with col1:

    start_date = st.date_input(
        "Start date",
        value=date(2021, 1, 4)
    )

with col2:

    end_date = st.date_input(
        "End date",
        value=date.today()
    )


criteria = st.selectbox(
    "Select ranking criteria:",
    [
        "Cumulative Return",
        "Annualized Return"
    ]
)


if st.button("Analyse Selected Stocks"):

    if not selected_companies:

        st.warning("Please select at least one company.")

    elif start_date >= end_date:

        st.error("End date must be later than start date.")

    else:

        results = []

        start_string, end_string = get_date_strings(
            start_date, end_date
        )

        with st.spinner("Fetching historical stock data..."):

            for company in selected_companies:

                symbol = companies[company]

                stock_data = load_company_data(
                    company,
                    start_string,
                    end_string
                )

                if stock_data is None or stock_data.empty:

                    st.warning(
                        f"No valid historical data available "
                        f"for {company}."
                    )

                    continue

                metrics = calculate_metrics(stock_data)

                if metrics is None:

                    st.warning(
                        f"Unable to calculate metrics for {company}."
                    )

                    continue

                results.append({
                    "Company": company,
                    "Symbol": symbol,
                    "Cumulative Return":
                        metrics["Cumulative Return"],
                    "Annualized Return":
                        metrics["Annualized Return"],
                    "Avg Daily Return":
                        metrics["Avg Daily Return"],
                    "Annualized Volatility":
                        metrics["Annualized Volatility"]
                })

        st.subheader(
            "Top Stocks Based on Selected Criteria"
        )

        if results:

            results_df = pd.DataFrame(results)

            ranked_df = results_df.sort_values(
                by=criteria,
                ascending=False
            ).reset_index(drop=True)

            ranked_df.index += 1

            st.subheader("Stock Performance Ranking")

            st.dataframe(
                ranked_df.style.format({
                    "Cumulative Return": "{:.2%}",
                    "Annualized Return": "{:.2%}",
                    "Avg Daily Return": "{:.4%}",
                    "Annualized Volatility": "{:.2%}"
                }),
                use_container_width=True
            )

            best_stock = ranked_df.iloc[0]

            st.success(
                f"Top-performing stock based on {criteria}: "
                f"{best_stock['Company']}"
            )

        else:

            st.warning(
                "No stock results are available. "
                "Check Yahoo Finance data availability and try again later."
            )

        if data_errors:

            with st.expander("Data Retrieval Details"):

                for symbol, error in data_errors.items():

                    st.error(f"{symbol}: {error}")


# ============================================================
# 2. BEST STOCK TO INVEST IN
# ============================================================

st.divider()

st.header("2. Best Stock to Invest In")

st.caption(
    "Comparison is based on historical cumulative returns "
    "for the companies selected above. Past performance "
    "does not guarantee future returns."
)


if st.button("Find Best Performing Stock"):

    if not selected_companies:

        st.warning(
            "Select companies in Stock Selection first."
        )

    elif start_date >= end_date:

        st.error("Select a valid date range.")

    else:

        results = []

        start_string, end_string = get_date_strings(
            start_date, end_date
        )

        with st.spinner("Comparing selected stocks..."):

            for company in selected_companies:

                symbol = companies[company]

                stock_data = load_company_data(
                    company,
                    start_string,
                    end_string
                )

                if stock_data is None or stock_data.empty:
                    continue

                metrics = calculate_metrics(stock_data)

                if metrics is not None:

                    results.append({
                        "Company": company,
                        "Symbol": symbol,
                        "Cumulative Return":
                            metrics["Cumulative Return"]
                    })

        if results:

            comparison = pd.DataFrame(results)

            comparison = comparison.sort_values(
                "Cumulative Return",
                ascending=False
            ).reset_index(drop=True)

            best = comparison.iloc[0]

            st.write(
                "Based on historical cumulative return, "
                "the top-performing stock is:"
            )

            st.success(best["Company"])

            st.metric(
                "Historical Cumulative Return",
                f"{best['Cumulative Return']:.2%}"
            )

            st.dataframe(
                comparison.style.format({
                    "Cumulative Return": "{:.2%}"
                }),
                use_container_width=True
            )

        else:

            st.warning(
                "Unable to compare stocks because "
                "historical data is unavailable."
            )

        if data_errors:

            with st.expander("Data Retrieval Details"):

                for symbol, error in data_errors.items():
                    st.error(f"{symbol}: {error}")


# ============================================================
# 3. STOCK INVESTMENT CALCULATOR
# ============================================================

st.divider()

st.header("3. Stock Investment Calculator")


def calculate_investment(
    investment_amount,
    stock_price,
    profit_percentage
):

    if stock_price <= 0:

        raise ValueError(
            "Stock price must be greater than zero."
        )

    if investment_amount < stock_price:

        raise ValueError(
            "Investment amount is insufficient to buy one share."
        )

    number_of_shares = math.floor(
        investment_amount / stock_price
    )

    invested_amount = (
        number_of_shares * stock_price
    )

    expected_selling_price = (
        stock_price * (1 + profit_percentage)
    )

    expected_profit = (
        number_of_shares *
        (expected_selling_price - stock_price)
    )

    remaining_cash = (
        investment_amount - invested_amount
    )

    return (
        number_of_shares,
        invested_amount,
        expected_selling_price,
        expected_profit,
        remaining_cash
    )


investment_amount = st.number_input(
    "Investment Amount (in Rupees)",
    min_value=0.0,
    value=10000.0,
    step=500.0
)

stock_price = st.number_input(
    "Share Purchase Price (in Rupees)",
    min_value=0.0,
    value=500.0,
    step=10.0
)

profit = st.number_input(
    "Desired Profit (%)",
    min_value=0.0,
    value=10.0,
    step=1.0
)


if st.button("Calculate"):

    try:

        (
            number_of_shares,
            invested_amount,
            expected_selling_price,
            expected_profit,
            remaining_cash
        ) = calculate_investment(
            investment_amount,
            stock_price,
            profit / 100
        )

        col1, col2 = st.columns(2)

        with col1:

            st.success(
                f"Number of shares: {number_of_shares}"
            )

            st.success(
                f"Amount invested: ₹{invested_amount:.2f}"
            )

            st.success(
                f"Expected profit: ₹{expected_profit:.2f}"
            )

        with col2:

            st.success(
                f"Expected selling price: "
                f"₹{expected_selling_price:.2f}"
            )

            st.success(
                f"Remaining cash: ₹{remaining_cash:.2f}"
            )

    except ValueError as e:

        st.error(str(e))


st.caption(
    "Calculator estimates exclude brokerage, taxes, transaction charges "
    "and other trading costs."
)


# ============================================================
# 4. DAY TRADER SIMULATOR
# ============================================================

st.divider()

st.header("4. Day Trader Simulator")

st.caption(
    "Paper trading only. Uses the latest available daily "
    "closing price, not a real-time market quote."
)


stock_companies = {
    "Apple Inc.": "AAPL",
    "Google": "GOOGL",
    "Microsoft Corporation": "MSFT",
    "Amazon.com Inc.": "AMZN",
    "Meta Platforms Inc.": "META"
}


# ------------------------------------------------------------
# SESSION STATE
# ------------------------------------------------------------

if "position" not in st.session_state:
    st.session_state.position = None

if "completed_trades" not in st.session_state:
    st.session_state.completed_trades = []


# ------------------------------------------------------------
# FETCH LATEST AVAILABLE DAILY CLOSING PRICE
# ------------------------------------------------------------

def get_latest_price(symbol):

    today = date.today()

    trade_start = (
        today - timedelta(days=10)
    ).strftime("%Y-%m-%d")

    trade_end = (
        today + timedelta(days=1)
    ).strftime("%Y-%m-%d")

    trade_data = get_stock_data(
        symbol,
        trade_start,
        trade_end
    )

    prices = trade_data["Close"].dropna()

    if prices.empty:

        raise ValueError(
            f"No valid closing price available for {symbol}."
        )

    return float(prices.iloc[-1])


# ------------------------------------------------------------
# USER INPUT
# ------------------------------------------------------------

stock_company = st.selectbox(
    "Select a stock company:",
    list(stock_companies.keys())
)

quantity = st.number_input(
    "Quantity",
    min_value=1,
    value=1,
    step=1
)

target_price = st.number_input(
    "Target selling price (USD)",
    min_value=0.01,
    value=100.0,
    step=1.0
)


# ------------------------------------------------------------
# ACTIVE POSITION
# ------------------------------------------------------------

if st.session_state.position is not None:

    position = st.session_state.position

    st.info(
        f"Active position: {position['company']} | "
        f"Quantity: {position['quantity']} | "
        f"Buy price: ${position['buy_price']:.2f} | "
        f"Target price: ${position['target_price']:.2f}"
    )

else:

    st.write("No active position.")


# ------------------------------------------------------------
# TRADING BUTTONS
# ------------------------------------------------------------

col1, col2, col3 = st.columns(3)

with col1:

    buy_clicked = st.button(
        "Buy",
        use_container_width=True
    )

with col2:

    check_clicked = st.button(
        "Check Target",
        use_container_width=True
    )

with col3:

    sell_clicked = st.button(
        "Sell",
        use_container_width=True
    )


# ------------------------------------------------------------
# BUY / CHECK TARGET / SELL
# ------------------------------------------------------------

if buy_clicked or check_clicked or sell_clicked:

    try:

        # BUY
        if buy_clicked:

            if st.session_state.position is not None:

                st.warning(
                    "Close your existing position before buying another."
                )

            else:

                trade_symbol = stock_companies[stock_company]

                current_price = get_latest_price(trade_symbol)

                st.write(
                    f"Latest available closing price: "
                    f"${current_price:.2f}"
                )

                if target_price <= current_price:

                    st.warning(
                        "Target selling price must be higher "
                        "than the purchase price."
                    )

                else:

                    st.session_state.position = {
                        "company": stock_company,
                        "symbol": trade_symbol,
                        "quantity": int(quantity),
                        "buy_price": current_price,
                        "target_price": float(target_price)
                    }

                    st.success(
                        f"Bought {quantity} shares of "
                        f"{stock_company} at ${current_price:.2f}."
                    )

        # CHECK TARGET
        elif check_clicked:

            if st.session_state.position is None:

                st.warning(
                    "You have not bought any stock yet."
                )

            else:

                position = st.session_state.position

                current_price = get_latest_price(
                    position["symbol"]
                )

                st.write(
                    f"Latest available closing price: "
                    f"${current_price:.2f}"
                )

                if current_price >= position["target_price"]:

                    st.success(
                        "Target price reached. You can sell your position."
                    )

                else:

                    st.info(
                        f"Target not reached. Current price: "
                        f"${current_price:.2f} | Target: "
                        f"${position['target_price']:.2f}"
                    )

        # SELL
        elif sell_clicked:

            if st.session_state.position is None:

                st.warning(
                    "You have no active position."
                )

            else:

                position = st.session_state.position

                current_price = get_latest_price(
                    position["symbol"]
                )

                profit_loss = (
                    current_price - position["buy_price"]
                ) * position["quantity"]

                st.session_state.completed_trades.append({
                    "Company": position["company"],
                    "Symbol": position["symbol"],
                    "Quantity": position["quantity"],
                    "Buy Price": position["buy_price"],
                    "Sell Price": current_price,
                    "Profit / Loss": profit_loss
                })

                st.session_state.position = None

                if profit_loss >= 0:

                    st.success(
                        f"Trade completed. Profit: ${profit_loss:.2f}"
                    )

                else:

                    st.error(
                        f"Trade completed. Loss: ${abs(profit_loss):.2f}"
                    )

    except Exception as e:

        st.error(
            "Unable to retrieve stock prices. "
            "Yahoo Finance may be rate-limiting requests."
        )

        st.caption(str(e))


# ============================================================
# COMPLETED TRADES
# ============================================================

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


st.subheader("Completed Trades")

if st.session_state.completed_trades:

    trades_df = pd.DataFrame(
        st.session_state.completed_trades
    )

    st.dataframe(
        trades_df.style.format({
            "Buy Price": "${:.2f}",
            "Sell Price": "${:.2f}",
            "Profit / Loss": "${:.2f}"
        }),
        use_container_width=True
    )

    total_profit_loss = trades_df[
        "Profit / Loss"
    ].sum()

    st.metric(
        "Total Profit / Loss",
        f"${total_profit_loss:.2f}"
    )

else:

    st.info("No completed trades.")



st.link_button(" Analysis with MACD and EMA", "http://localhost:8502/")