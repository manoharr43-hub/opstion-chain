import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from streamlit_autorefresh import st_autorefresh

# =============================
# CONFIG
# =============================
st.set_page_config(page_title="🔥 PRO NSE AI DASHBOARD V2", layout="wide")
st_autorefresh(interval=15000, key="refresh")

st.title("🔥 PRO NSE AI DASHBOARD (SAFE VERSION)")
st.markdown("---")

tab1, tab2 = st.tabs(["📊 Dashboard", "🔥 Scanner"])

# =============================
# DATA LOADER (SAFE)
# =============================
@st.cache_data(ttl=60)
def get_data(symbol):
    try:
        df = yf.Ticker(symbol).history(period="3mo", interval="1d")
        if df is None or df.empty:
            return None
        return df
    except:
        return None


@st.cache_data(ttl=60)
def get_multi_data(tickers):
    try:
        data = yf.download(
            tickers,
            period="10d",
            interval="15m",
            group_by="ticker",
            threads=True,
            progress=False
        )
        if data is None or len(data) == 0:
            return None
        return data
    except:
        return None


# =============================
# TREND LOGIC
# =============================
def get_signal(df):
    df = df.copy()
    df['EMA20'] = df['Close'].ewm(span=20).mean()
    df['EMA50'] = df['Close'].ewm(span=50).mean()

    if df['EMA20'].iloc[-1] > df['EMA50'].iloc[-1]:
        return "🟢 BUY"
    else:
        return "🔴 SELL"


def get_strength(df):
    df = df.copy()
    df['EMA20'] = df['Close'].ewm(span=20).mean()
    df['EMA50'] = df['Close'].ewm(span=50).mean()

    rsi = 100 - (100 / (1 + df['Close'].pct_change().rolling(14).mean()))
    df['RSI'] = rsi

    if df['EMA20'].iloc[-1] > df['EMA50'].iloc[-1] and df['RSI'].iloc[-1] > 55:
        return "STRONG BUY"
    elif df['EMA20'].iloc[-1] < df['EMA50'].iloc[-1] and df['RSI'].iloc[-1] < 45:
        return "STRONG SELL"
    else:
        return "NEUTRAL"


# =============================
# 📊 DASHBOARD
# =============================
with tab1:
    st.subheader("📊 Stock Dashboard")

    stock = st.text_input("Enter Stock", "RELIANCE")

    if not stock.endswith(".NS"):
        stock = stock + ".NS"

    df = get_data(stock)

    if df is not None:
        st.line_chart(df['Close'])

        price = df['Close'].iloc[-1]
        st.metric("Price", round(price, 2))

        signal = get_signal(df)
        st.metric("Signal", signal)

    else:
        st.error("Data not available")


# =============================
# 🔥 SCANNER
# =============================
with tab2:
    st.subheader("🔥 NSE SCANNER")

    sectors = {
        "Nifty 50": ["RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS"],
        "Banking": ["SBIN.NS","AXISBANK.NS","KOTAKBANK.NS"],
        "IT": ["WIPRO.NS","HCLTECH.NS","TECHM.NS"],
        "Auto": ["MARUTI.NS","TATAMOTORS.NS","M&M.NS"],
        "FMCG": ["HINDUNILVR.NS","ITC.NS","NESTLEIND.NS"],
        "Pharma": ["SUNPHARMA.NS","DRREDDY.NS","CIPLA.NS"]
    }

    sector = st.selectbox("Select Sector", list(sectors.keys()))
    stocks = sectors[sector]

    data = get_multi_data(stocks)

    results = []

    if data is not None:
        for stock in stocks:
            try:
                if stock not in data.columns.get_level_values(0):
                    continue

                df = data[stock].dropna()

                if len(df) < 20:
                    continue

                signal = get_signal(df)
                strength = get_strength(df)

                results.append({
                    "Stock": stock,
                    "Signal": signal,
                    "Strength": strength,
                    "Price": round(df['Close'].iloc[-1], 2)
                })

            except:
                continue

    res_df = pd.DataFrame(results)

    if res_df
