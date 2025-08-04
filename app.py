import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import requests
import streamlit_authenticator as stauth

# --- USER AUTHENTICATION ---
names = ["Devi Charan"]
usernames = ["charan"]
passwords = ["1234"]

# 🔐 Generate hashed passwords
hashed_passwords = stauth.Hasher(passwords).generate()

# 🔐 Setup authentication
authenticator = stauth.Authenticate(
    names,
    usernames,
    hashed_passwords,
    "stock_dashboard",
    "abcdef",
    cookie_expiry_days=1
)

# --- LOGIN UI ---
name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status == False:
    st.error("❌ Username/password is incorrect")
elif authentication_status == None:
    st.warning("⚠️ Please enter your username and password")
elif authentication_status:
    # --- LOGGED IN VIEW ---
    authenticator.logout("Logout", "sidebar")
    st.sidebar.title(f"Welcome, {name} 👋")

    st.title("📈 Real-Time Stock Market Dashboard")

    st.sidebar.header("Stock Input")
    symbol = st.sidebar.text_input("Enter Stock Symbol (e.g., AAPL)", value="AAPL").upper()
    api_key = st.sidebar.text_input("Enter Alpha Vantage API Key", type="password", value="UJP5ZC97Z7TJBWU9")

    if symbol and api_key:
        # --- Fetch stock data ---
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

            # --- Chart: Closing Prices ---
            st.subheader(f"📊 Closing Prices for {symbol}")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name="Close Price", line=dict(color='blue')))
            fig.update_layout(title=f"{symbol} Closing Price", xaxis_title="Date", yaxis_title="Price")
            st.plotly_chart(fig, use_container_width=True)

            # --- Chart: Simple Moving Average (5-day) ---
            st.subheader("📈 5-Day Simple Moving Average (SMA)")
            sma = df['Close'].rolling(window=5).mean()
            st.line_chart(sma)

            # --- Show latest data ---
            st.subheader("📋 Latest Data")
            st.dataframe(df.tail(10))

        except Exception as e:
            st.error("❌ Failed to fetch stock data. Check the stock symbol or API key.")
    else:
        st.info("ℹ️ Please enter both the stock symbol and your API key.")
