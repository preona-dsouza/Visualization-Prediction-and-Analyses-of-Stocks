import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import tensorflow as tf
import yfinance as yf
import xgboost as xgb

from datetime import datetime as dt, timedelta
from keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
from plotly import graph_objects as go
from prophet import Prophet
from prophet.plot import plot_plotly
from newsapi import NewsApiClient
from bs4 import BeautifulSoup
import requests
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
            <a href="http://127.0.0.1:8050/" >VISUALIZATION</a>
            <a href="http://127.0.0.1:8502/" >STOCK ANALYSIS</a>
        </div>
    """, unsafe_allow_html=True)

navigation_bar()


# ============================================================
# PERMANENT AUTHOR WATERMARK
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


@st.cache_data(ttl=900, show_spinner=False)
def download_stock_data(ticker, start, end):
    data = yf.download(
        ticker,
        start=start,
        end=end,
        auto_adjust=False,
        progress=False,
        threads=False
    )

    if data is None or data.empty:
        raise ValueError(
            "Yahoo Finance returned no data. "
            "Possible rate limit or temporary service failure."
        )

    return data
from datetime import datetime, timedelta
from newsapi import NewsApiClient
import tensorflow as tf
import tensorflow as tf

print(tf.__version__)
#load Model 
model = load_model('stocPrice.keras')
st.header(' Stock Prediction Dashboard ')
def get_stock_news(ticker, num_articles=5):
    try:
        news_api_key = st.secrets["NEWS_API_KEY"]

        newsapi = NewsApiClient(api_key=news_api_key)
        top_headlines = newsapi.get_everything(q=ticker, language='en', sort_by='publishedAt')
        articles = top_headlines['articles'][:num_articles]
        return articles
    except:
        return None

start = '2025-01-01'
today = dt.now()

ticker = st.text_input(
    "Enter Stock Ticker Symbol (e.g., AAPL, GOOG):"
).strip().upper()

# Stop execution if no ticker is entered
if not ticker:
    st.info("Enter a stock ticker symbol to view stock data.")
    st.stop()

# Display current news related to the stock
st.sidebar.title("Stock News Dashboard")

articles = get_stock_news(ticker, num_articles=8)

if articles:
    for article in articles:
        st.sidebar.write(f"- [{article['title']}]({article['url']})")
else:
    st.sidebar.write("Failed to retrieve current news. Please try again later.")

# Download stock data
# Download stock data
try:
    with st.spinner(f"Downloading data for {ticker}..."):
        data = download_stock_data(ticker, start, today)

    # Handle newer yfinance MultiIndex columns
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    data = data.reset_index()

    st.write(data)

except Exception as e:
    st.error(f"Unable to retrieve stock data: {e}")
    st.stop()

st.subheader('Stock Line Chart')
st.write("Downloaded columns:", data.columns.tolist())
st.write("Data preview:", data.head())       
# Keep only the closing price
if 'Close' not in data.columns:
    st.error("Closing price column is missing from the downloaded data.")
    st.stop()

data = data[['Close']].copy()

st.subheader('Stock Line Chart')
st.line_chart(data)

train_data = data[:-100]
test_data = data[-200:]

scaler = MinMaxScaler(feature_range=(0,1))
train_data_scale = scaler.fit_transform(train_data)
test_data_scale = scaler.transform(test_data)
base_days = 100
x = []
y = []
for i in range(base_days, test_data_scale.shape[0]):
    x.append(test_data_scale[i-base_days:i])
    y.append(test_data_scale[i,0])

x, y = np.array(x), np.array(y)
x = np.reshape(x, (x.shape[0],x.shape[1],1))

st.subheader('Predicted vs Original Prices ')
pred = model.predict(x)
pred = scaler.inverse_transform(pred)
preds = pred.reshape(-1,1)
ys = scaler.inverse_transform(y.reshape(-1,1))
preds = pd.DataFrame(preds, columns=['Predicted Price'])
ys = pd.DataFrame(ys, columns=['Original Price'])
chart_data = pd.concat((preds, ys), axis=1)
st.write(chart_data)
st.subheader('Predicted vs Original Prices Chart ')
st.line_chart(chart_data)


window = 50  
ma_50_days = data.Close.rolling(window).mean()
fif1=plt.figure(figsize=(10, 8))
plt.title('Stock Price with 50-day SMA')
plt.plot(data.Close, 'g', label='Closing Price')
plt.plot(ma_50_days, 'r', label='50-Day SMA')

plt.show()
st.pyplot(fif1)
# Predict future values for the next 2 days
predicted_predictions = model.predict(x)

# Inverse normalization to get actual predicted values
predicted_prices = scaler.inverse_transform(predicted_predictions.reshape(-1, 1))
num_predictions=2
# Extract the last 2 predicted prices for future forecast
future_predictions = predicted_prices[-2:]
future_predictions=predicted_prices.flatten()[:num_predictions]





# Streamlit app layout and visualization
st.title("LSTM Stock Future Prediction")

# Display predicted prices with actual close price for comparison
plt.figure(figsize=(10, 6))
plt.plot(data['Close'].index[:-2], data['Close'].values[:-2], label="Actual Close Price")
plt.plot(data['Close'].index[-2:], future_predictions, label="Predicted Close Price")
plt.xlabel("Date")
plt.ylabel("Close Price")
plt.title("LSTM Predicted vs. Actual Close Prices")
plt.legend()
st.pyplot(plt)




import numpy as np
import pandas as pd
import yfinance as yf
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt


# Display predicted values for the next 2 days
st.write("Predicted Close Prices for the Next 2 Days:")

for i in range(num_predictions):
        st.write(f"Day {i+1}: {future_predictions[i].flatten()}")





import streamlit as st
from bs4 import BeautifulSoup
import requests
from datetime import datetime
import streamlit as st







import streamlit as st

# List of popular financial news websites or RSS feeds
news_sources = [
    "https://www.reuters.com/markets/us/",
    "https://www.bloomberg.com/quote/SPX:IND",  # S&P 500 news on Bloomberg
    "https://finance.yahoo.com/",
    "https://www.cnbc.com/market/",
    "https://www.wsj.com/market-data",
]

st.sidebar.write(news_sources)



