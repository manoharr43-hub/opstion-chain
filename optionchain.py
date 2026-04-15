import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from streamlit_autorefresh import st_autorefresh

# =============================
# CONFIG
# =============================
st.set_page_config(page_title="🔥 MANOHAR NSE AI PRO", layout="wide")
st_autorefresh(interval=15000, key="refresh")

st.title("🚀 MANOHAR NSE AI PRO TERMINAL")
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "🔥 Scanner", "📂 Backtest"])

# =============================
# DATA FUNCTIONS
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
# STRATEGY ENGINE
# =============================
def signal_engine(df):
    df = df.copy()
    df['EMA20'] = df['Close'].ewm(span=20).mean()
    df['EMA50'] = df['Close'].ewm(span=50).mean()

    if df['EMA20'].iloc[-1] > df['EMA50'].iloc[-1]:
        return "🟢 BUY"
    else:
        return "🔴 SELL"


def strength_engine(df):
    df = df.copy()
    df['EMA20'] = df['Close'].ewm(span=20).mean()
    df['EMA50'] = df['Close'].ewm(span=50).mean()

    rsi = 100 - (100 / (
