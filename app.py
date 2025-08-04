import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import requests

# --- Page config ---
st.set_page_config(page_title="Stock Dashboard", layout="wide")
st.title("📈 Real-Time Stock Market Dashboard")

# --- Sidebar Inputs ---
st.sidebar.header("Select Stock(s)")
popular_stocks = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "Tesla": "TSLA",
    "Google": "GOOGL",
    "Amazon": "AMZN",
    "Meta": "META",
    "Netflix": "NFLX"
}

selected_stock = st.sidebar.selectbox("Choose a stock", list(popular_stocks.keys()))
compare_others = st.sidebar.multiselect("Compare with others", [k for k in popular_stocks if k != selected_stock])
api_key = st.sidebar.text_input("Alpha Vantage API Key", type="password", value="UJP5ZC97Z7TJBWU9")

# --- Function to fetch stock data ---
def fetch_stock_data(symbol, api_key):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}&outputsize=compact"
    r = requests.get(url)
    data = r.json()
    if 'Time Series (Daily)' not in data:
        return None
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
    return df

# --- Main Chart ---
if api_key:
    main_symbol = popular_stocks[selected_stock]
    main_df = fetch_stock_data(main_symbol, api_key)

    if main_df is not None:
        st.subheader(f"📊 Closing Price of {main_symbol}")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=main_df.index, y=main_df['Close'], name=main_symbol, line=dict(width=2)))

        # --- Comparison Stocks ---
        for company in compare_others:
            symbol = popular_stocks[company]
            df = fetch_stock_data(symbol, api_key)
            if df is not None:
                fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name=symbol, line=dict(dash='dash')))

        fig.update_layout(title="Stock Closing Price Comparison", xaxis_title="Date", yaxis_title="Price", template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

        # --- Moving Average ---
        st.subheader(f"📈 5-Day SMA for {main_symbol}")
        main_df['SMA_5'] = main_df['Close'].rolling(window=5).mean()
        st.line_chart(main_df[['Close', 'SMA_5']])

        # --- Latest Table ---
        st.subheader("📋 Recent Data")
        st.dataframe(main_df.tail(10))
    else:
        st.error("⚠️ Failed to fetch data. Check your API key or try again later.")
else:
    st.info("🔑 Please enter your Alpha Vantage API key.")
