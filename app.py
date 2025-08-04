import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import requests
import streamlit_authenticator as stauth

# --- User Authentication ---
names = ["Devi Charan"]
usernames = ["charan"]
passwords = ["1234"]  # Plaintext for demo purposes ONLY

# ❌ Not using hashed passwords in this version
authenticator = stauth.Authenticate(
    names,
    usernames,
    passwords,
    "stock_dashboard",
    "abcdef",
    cookie_expiry_days=1
)

# --- Login Widget ---
name, authentication_status, username = authenticator.login("Login", "main")

# --- Handle Login States ---
if authentication_status == False:
    st.error("❌ Username/password is incorrect")
elif authentication_status == None:
    st.warning("⚠️ Please enter your username and password")
elif authentication_status:

    # --- Authenticated Area ---
    authenticator.logout("Logout", "sidebar")
    st.sidebar.title(f"Welcome, {name} 👋")

    st.title("📈 Real-Time Stock Market Dashboard")

    st.sidebar.header("Stock Input")

    symbol = st.sidebar.text_input("Enter Stock Symbol (e.g., AAPL)", value="AAPL").upper()
    api_key = st.sidebar.text_input("Enter Alpha Vantage API Key", type="password", value="UJP5ZC97Z7TJBWU9")

    if symbol and api_key:
        try:
            # --- Fetch data from Alpha Vantage ---
            url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}&outputsize=compact"
            r = requests.get(url)
            data = r.json()

            if 'Time Series (Daily)' not in data:
                raise ValueError("Invalid API response or API limit reached")

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

            # --- Closing Price Chart ---
            st.subheader(f"📊 Closing Prices for {symbol}")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name="Close Price", line=dict(color='blue')))
            fig.update_layout(title=f"{symbol} Closing Price", xaxis_title="Date", yaxis_title="Price")
            st.plotly_chart(fig, use_container_width=True)

            # --- Simple Moving Average ---
            st.subheader("📈 Simple Moving Average (5-Day)")
            sma = df['Close'].rolling(window=5).mean()
            sma_chart = pd.DataFrame({"Close": df["Close"], "SMA_5": sma})
            st.line_chart(sma_chart)

            # --- Show Table ---
            st.subheader("📋 Last 10 Days of Data")
            st.dataframe(df.tail(10))

        except Exception as e:
            st.error(f"❌ Failed to fetch stock data: {e}")
    else:
        st.info("ℹ️ Please enter a stock symbol and API key.")
