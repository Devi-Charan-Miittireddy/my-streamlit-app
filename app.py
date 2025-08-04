import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import requests

st.set_page_config(page_title="Stock Dashboard", layout="wide")
st.title("📈 Simple Real-Time Stock Market Dashboard")

# --- User input ---
st.sidebar.header("Enter Stock Info")
symbol = st.sidebar.text_input("Stock Symbol (e.g., AAPL)", value="AAPL").upper()
api_key = st.sidebar.text_input("Alpha Vantage API Key", type="password", value="UJP5ZC97Z7TJBWU9")

# --- Fetch and process data ---
if symbol and api_key:
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}&outputsize=compact"
    response = requests.get(url)
    data = response.json()

    try:
        df = pd.DataFrame(data['Time Series (Daily)']).T
        df = df.rename(columns={
            '1. open': 'Open',
            '2. high': 'High',
            '3. low': 'Low',
            '4. close': 'Close',
            '5. volume': 'Volume'
        })
        df.index = pd.to_datetime(df.index)
        df = df.astype(float)
        df = df.sort_index()

        # --- Price Chart ---
        st.subheader(f"📊 Closing Price of {symbol}")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name="Close", line=dict(color='blue')))
        fig.update_layout(xaxis_title="Date", yaxis_title="Price", template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

        # --- Moving Average Chart ---
        st.subheader("📈 5-Day Simple Moving Average")
        df['SMA_5'] = df['Close'].rolling(window=5).mean()
        st.line_chart(df[['Close', 'SMA_5']])

        # --- Recent Data Table ---
        st.subheader("📋 Latest Stock Data")
        st.dataframe(df.tail(10))

    except Exception as e:
        st.error("Error fetching stock data. Please check the symbol or API key.")
else:
    st.info("Please enter a stock symbol and API key in the sidebar.")
