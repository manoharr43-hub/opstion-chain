# =========================================================
# 🚀 NSE AI PRO MAX V2.8 - FULLY REGENERATED
# =========================================================

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import io
import datetime
import pytz
from concurrent.futures import ThreadPoolExecutor

# =========================================================
# PAGE CONFIG & AUTO REFRESH
# =========================================================
st.set_page_config(page_title="NSE AI PRO MAX V2.8", layout="wide")
st.fragment(run_every=60)

st.title("🚀 NSE AI PRO MAX V2.8")
st.caption("AI BASED NSE SCANNER + OPTIONS MOMENTUM + CUSTOM CSV SETUP")

# =========================================================
# FULL NIFTY 50 STOCK LIST
# =========================================================
nse_stocks = {
    "RELIANCE": "RELIANCE.NS", "HDFCBANK": "HDFCBANK.NS", "INFY": "INFY.NS",
    "ICICIBANK": "ICICIBANK.NS", "TCS": "TCS.NS", "ITC": "ITC.NS",
    "KOTAKBANK": "KOTAKBANK.NS", "LT": "LT.NS", "SBIN": "SBIN.NS",
    "BHARTIARTL": "BHARTIARTL.NS", "ASIANPAINT": "ASIANPAINT.NS",
    "AXISBANK": "AXISBANK.NS", "SUNPHARMA": "SUNPHARMA.NS",
    "TITAN": "TITAN.NS", "ULTRACEMCO": "ULTRACEMCO.NS",
    "WIPRO": "WIPRO.NS", "NESTLEIND": "NESTLEIND.NS"
}

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.header("⚙️ SETTINGS")
selected_stock = st.sidebar.selectbox("SELECT STOCK", list(nse_stocks.keys()))
interval = st.sidebar.selectbox("INTERVAL", ["5m", "15m", "30m", "1h"])
period = st.sidebar.selectbox("PERIOD", ["1d", "5d", "1mo"])
ticker = nse_stocks[selected_stock]

st.sidebar.markdown("---")
st.sidebar.subheader("🔗 QUICK LINKS")
screener_link = "INSERT_YOUR_LINK_HERE"
st.sidebar.markdown(f'''
<a href="{screener_link}" target="_blank" style="text-decoration: none;">
    <div style="background-color: #2E86C1; padding: 10px; border-radius: 5px; text-align: center; color: white; font-weight: bold; margin-bottom: 15px;">
        📊 Open NSE Screener Kit
    </div>
</a>
''', unsafe_allow_html=True)

# =========================================================
# HELPER FUNCTIONS
# =========================================================
def calculate_indicators(df):
    if df.empty: return df
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    df = df.reset_index()
    df['EMA20'] = df['Close'].ewm(span=20).mean()
    df['EMA50'] = df['Close'].ewm(span=50).mean()
    df['VWAP'] = ((df['Close'] * df['Volume']).cumsum()) / df['Volume'].cumsum()
    delta = df['Close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    rs = gain.rolling(14).mean() / loss.rolling(14).mean()
    df['RSI'] = 100 - (100 / (1 + rs))
    df['RSI'] = df['RSI'].fillna(50)
    df['MACD'] = df['Close'].ewm(span=12).mean() - df['Close'].ewm(span=26).mean()
    df['MACD_SIGNAL'] = df['MACD'].ewm(span=9).mean()
    return df

def generate_signal(df):
    latest = df.iloc[-1]
    score = 0
    if latest['EMA20'] > latest['EMA50']: score += 25
    else: score -= 25
    if latest['Close'] > latest['VWAP']: score += 25
    else: score -= 25
    if 55 < latest['RSI'] < 70: score += 25
    elif latest['RSI'] > 70: score -= 10
    elif latest['RSI'] < 30: score += 15
    else: score -= 10
    if latest['MACD'] > latest['MACD_SIGNAL']: score += 25
    else: score -= 25

    if score >= 75: signal = "🚀 STRONG BUY"
    elif score >= 25: signal = "✅ BUY"
    elif score <= -75: signal = "🚨 STRONG SELL"
    elif score <= -25: signal = "🔻 SELL"
    else: signal = "⚠️ SIDEWAYS"
    return signal, score

# =========================================================
# TABS SETUP
# =========================================================
tab1, tab2 = st.tabs(["📈 AI Scanner & Live Setup", "📂 Upload CSV & Extract AI Target"])

# =========================================================
# TAB 1: LIVE SCANNER
# =========================================================
with tab1:
    try:
        df = yf.download(ticker, interval=interval, period=period, progress=False, auto_adjust=True)
        if df.empty:
            st.error("NO DATA FOUND")
        else:
            df = calculate_indicators(df)
            signal, score = generate_signal(df)
            latest = df.iloc[-1]
            current_price = float(latest['Close'])

            st.subheader("🤖 AI SIGNAL")
            if "BUY" in signal: st.success(f"{signal} (SCORE: {score})")
            elif "SELL" in signal: st.error(f"{signal} (SCORE: {score})")
            else: st.warning(f"{signal} (SCORE: {score})")

            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("PRICE", f"₹ {round(current_price, 2)}")
            col2.metric("RSI", round(float(latest['RSI']), 2))
            col3.metric("VWAP", round(float(latest['VWAP']), 2))
            col4.metric("MACD", round(float(latest['MACD']), 2))
            col5.metric("AI SCORE", f"{score} PTS")

            # Chart
            st.markdown("---")
            st.subheader(f"📈 {selected_stock} LIVE CHART")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df['Date'] if 'Date' in df.columns else df.index, y=df['Close'], mode='lines', name='Close'))
            fig.add_trace(go.Scatter(x=df['Date'] if 'Date' in df.columns else df.index, y=df['EMA20'], mode='lines', name='EMA20'))
            st.plotly_chart(fig, use_container_width=True)

            # Scanner
            st.subheader("🔥 LIVE AI NIFTY 50 SCANNER")
            def scan_stock(item):
                s_name, s_ticker = item
                try:
                    data = yf.download(s_ticker, interval=interval, period=period, progress=False, auto_adjust=True)
                    if data.empty: return None
                    data = calculate_indicators(data)
                    sig, scr = generate_signal(data)
                    return {"STOCK": s_name, "PRICE": round(float(data.iloc[-1]['Close']), 2), "SIGNAL
