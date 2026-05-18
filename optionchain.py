# ============================================
# 🚀 NSE AI OPTION CHAIN PRO MAX
# ============================================

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# ============================================
# PAGE CONFIG
# ============================================

st.set_page_config(
    page_title="NSE AI SIGNAL",
    layout="wide"
)

st.title("♟️ AI SIGNAL")

# ============================================
# STOCK LIST
# ============================================

stocks = {
    "RELIANCE": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "INFY": "INFY.NS",
    "HDFCBANK": "HDFCBANK.NS",
    "ICICIBANK": "ICICIBANK.NS",
    "SBIN": "SBIN.NS",
    "LT": "LT.NS",
    "ITC": "ITC.NS",
    "BHARTIARTL": "BHARTIARTL.NS"
}

# ============================================
# SIDEBAR
# ============================================

st.sidebar.header("⚙️ SETTINGS")

stock_name = st.sidebar.selectbox(
    "Select Stock",
    list(stocks.keys())
)

interval = st.sidebar.selectbox(
    "Select Interval",
    ["5m", "15m", "30m", "1h"]
)

period = st.sidebar.selectbox(
    "Select Period",
    ["1d", "5d", "1mo"]
)

ticker = stocks[stock_name]

# ============================================
# DATA DOWNLOAD
# ============================================

try:

    df = yf.download(
        ticker,
        interval=interval,
        period=period,
        auto_adjust=True,
        progress=False
    )

    # ============================================
    # FIX MULTIINDEX ISSUE
    # ============================================

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df.reset_index()

    # ============================================
    # REQUIRED COLUMNS CHECK
    # ============================================

    needed = ['Open', 'High', 'Low', 'Close', 'Volume']

    for col in needed:
        if col not in df.columns:
            st.error(f"Missing Column: {col}")
            st.stop()

    # ============================================
    # INDICATORS
    # ============================================

    # EMA
    df['EMA20'] = df['Close'].ewm(span=20).mean()
    df['EMA50'] = df['Close'].ewm(span=50).mean()

    # RSI
    delta = df['Close'].diff()

    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)

    gain = pd.Series(gain)
    loss = pd.Series(loss)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss

    df['RSI'] = 100 - (100 / (1 + rs))

    # FIX FILLNA ERROR
    df['RSI'] = df['RSI'].fillna(50)

    # ============================================
    # VWAP FIX
    # ============================================

    close = df['Close'].astype(float)
    volume = df['Volume'].astype(float)

    df['VWAP'] = (
        (close * volume).cumsum()
        / volume.cumsum()
    )

    # ============================================
    # BUY / SELL SIGNALS
    # ============================================

    df['BUY'] = (
        (df['EMA20'] > df['EMA50']) &
        (df['Close'] > df['VWAP']) &
        (df['RSI'] > 55)
    )

    df['SELL'] = (
        (df['EMA20'] < df['EMA50']) &
        (df['Close'] < df['VWAP']) &
        (df['RSI'] < 45)
    )

    latest = df.iloc[-1]

    # ============================================
    # SIGNAL DISPLAY
    # ============================================

    if latest['BUY']:
        st.success("🚀 BUY SIGNAL DETECTED")

    elif latest['SELL']:
        st.error("🔻 SELL SIGNAL DETECTED")

    else:
        st.warning("⚠️ NO CLEAR SIGNAL")

    # ============================================
    # LIVE PRICE
    # ============================================

    st.metric(
        label=f"{stock_name} LIVE PRICE",
        value=f"₹ {round(latest['Close'], 2)}"
    )

    # ============================================
    # CHART
    # ============================================

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['Close'],
        mode='lines',
        name='Close'
    ))

    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['EMA20'],
        mode='lines',
        name='EMA20'
    ))

    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['EMA50'],
        mode='lines',
        name='EMA50'
    ))

    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['VWAP'],
        mode='lines',
        name='VWAP'
    ))

    fig.update_layout(
        title=f"{stock_name} LIVE CHART",
        height=600,
        xaxis_title="Time",
        yaxis_title="Price"
    )

    st.plotly_chart(fig, use_container_width=True)

    # ============================================
    # DATA TABLE
    # ============================================

    st.subheader("📊 LIVE DATA")

    st.dataframe(
        df.tail(20),
        use_container_width=True
    )

    # ============================================
    # RSI METER
    # ============================================

    st.subheader("📈 RSI STATUS")

    rsi = round(latest['RSI'], 2)

    if rsi > 70:
        st.error(f"RSI : {rsi} → OVERBOUGHT")

    elif rsi < 30:
        st.success(f"RSI : {rsi} → OVERSOLD")

    else:
        st.info(f"RSI : {rsi} → NORMAL")

except Exception as e:

    st.error("APP ERROR")
    st.code(str(e))
