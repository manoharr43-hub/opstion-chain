# =============================
# app.py – NSE TOP 500 Scanner
# =============================
import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
import datetime

st.set_page_config(page_title="NSE AI PRO V54.0", layout="wide")

# =============================
# Load NSE Top 500 Stocks
# =============================
@st.cache_data(ttl=86400)
def load_nse500():
    try:
        url = "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"
        df = pd.read_csv(url)
        return df['Symbol'].tolist()
    except:
        return ["RELIANCE","HDFCBANK","INFY"]  # fallback

stocks = load_nse500()

# =============================
# User Inputs
# =============================
st.sidebar.header("Scanner Settings")
selected_stock = st.sidebar.selectbox("Choose Stock", stocks)
interval = st.sidebar.selectbox("Interval", ["5m","15m","30m","1h","1d"])
period = st.sidebar.selectbox("Period", ["5d","1mo","3mo"])

# =============================
# Fetch Data
# =============================
@st.cache_data(ttl=3600)
def get_data(symbol, period, interval):
    return yf.download(symbol+".NS", period=period, interval=interval)

df = get_data(selected_stock, period, interval)

# =============================
# Indicators
# =============================
df['EMA20'] = df['Close'].ewm(span=20).mean()
df['EMA50'] = df['Close'].ewm(span=50).mean()
df['RSI'] = 100 - (100/(1+df['Close'].pct_change().rolling(14).apply(
    lambda x: (x[x>0].mean()/-x[x<0].mean()) if -x[x<0].mean()!=0 else 0)))
df['VWAP'] = (df['Close']*df['Volume']).cumsum()/df['Volume'].cumsum()

# =============================
# Signal Logic
# =============================
df['BUY'] = (df['EMA20'] > df['EMA50']) & (df['Close'] > df['VWAP']) & (df['RSI'] > 55)
df['SELL'] = (df['EMA20'] < df['EMA50']) & (df['Close'] < df['VWAP']) & (df['RSI'] < 45)

# =============================
# Dashboard
# =============================
st.title("📊 NSE AI PRO V54.0 – TOP 500 Scanner")
st.write(f"Selected Stock: **{selected_stock}**")

latest = df.iloc[-1]
st.metric("Trend", "BULLISH" if latest['EMA20']>latest['EMA50'] else "BEARISH")
st.metric("RSI", f"{latest['RSI']:.2f}")
st.metric("VWAP Position", "ABOVE" if latest['Close']>latest['VWAP'] else "BELOW")
st.metric("Signal", "🚀 BUY" if latest['BUY'] else "🔻 SELL" if latest['SELL'] else "WAIT")

st.line_chart(df[['Close','EMA20','EMA50','VWAP']])
