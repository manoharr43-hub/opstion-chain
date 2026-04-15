import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from streamlit_autorefresh import st_autorefresh

# =============================
# CONFIG
# =============================
st.set_page_config(page_title="🔥 NSE AI PRO TERMINAL", layout="wide")
st_autorefresh(interval=15000, key="refresh")

st.title("🚀 MANOHAR NSE AI PRO TERMINAL")
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "🔥 Scanner", "📂 Backtest"])

# =============================
# DATA
# =============================
@st.cache_data(ttl=60)
def get_data(symbol):
    try:
        df = yf.Ticker(symbol).history(period="3mo", interval="1d")
        return df if df is not None and not df.empty else None
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
        return data if data is not None and len(data) > 0 else None
    except:
        return None


# =============================
# INDICATORS (FIXED SAFE RSI)
# =============================
def add_indicators(df):
    df = df.copy()

    df["EMA20"] = df["Close"].ewm(span=20).mean()
    df["EMA50"] = df["Close"].ewm(span=50).mean()

    delta = df["Close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = -delta.clip(upper=0).rolling(14).mean()

    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))

    return df


def signal(df):
    df = add_indicators(df)

    if df["EMA20"].iloc[-1] > df["EMA50"].iloc[-1]:
        return "🟢 BUY"
    else:
        return "🔴 SELL"


def strength(df):
    df = add_indicators(df)

    if df["EMA20"].iloc[-1] > df["EMA50"].iloc[-1] and df["RSI"].iloc[-1] > 55:
        return "STRONG BUY"
    elif df["EMA20"].iloc[-1] < df["EMA50"].iloc[-1] and df["RSI"].iloc[-1] < 45:
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
        df = add_indicators(df)

        st.line_chart(df["Close"])
        st.metric("Price", round(df["Close"].iloc[-1], 2))
        st.metric("Signal", signal(df))
    else:
        st.error("No Data Found")


# =============================
# 🔥 SCANNER
# =============================
with tab2:
    st.subheader("🔥 NSE SECTOR SCANNER")

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

                df = add_indicators(df)

                results.append({
                    "Stock": stock,
                    "Price": round(df["Close"].iloc[-1], 2),
                    "Signal": signal(df),
                    "Strength": strength(df)
                })

            except:
                continue

    res_df = pd.DataFrame(results)

    if not res_df.empty:
        st.dataframe(res_df, use_container_width=True)

        st.markdown("### 🟢 STRONG BUY")
        st.dataframe(res_df[res_df["Strength"] == "STRONG BUY"])

        st.markdown("### 🔴 STRONG SELL")
        st.dataframe(res
