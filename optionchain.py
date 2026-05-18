# ============================================
# 🚀 NSE AI SIGNAL SAFE VERSION
# ============================================

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ============================================
# PAGE CONFIG
# ============================================

st.set_page_config(page_title="AI SIGNAL", layout="wide")

st.title("♟️ AI SIGNAL")

# ============================================
# STOCKS
# ============================================

stocks = {
    "RELIANCE": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "INFY": "INFY.NS",
    "HDFCBANK": "HDFCBANK.NS",
    "ICICIBANK": "ICICIBANK.NS"
}

# ============================================
# SIDEBAR
# ============================================

stock_name = st.sidebar.selectbox(
    "Select Stock",
    list(stocks.keys())
)

ticker = stocks[stock_name]

interval = st.sidebar.selectbox(
    "Interval",
    ["5m", "15m", "30m"]
)

period = st.sidebar.selectbox(
    "Period",
    ["1d", "5d"]
)

# ============================================
# DOWNLOAD DATA
# ============================================

try:

    df = yf.download(
        ticker,
        interval=interval,
        period=period,
        progress=False,
        auto_adjust=True
    )

    # ============================================
    # EMPTY DATA FIX
    # ============================================

    if df.empty:
        st.error("NO DATA FOUND")
        st.stop()

    # ============================================
    # FIX MULTI INDEX
    # ============================================

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # ============================================
    # RESET INDEX
    # ============================================

    df = df.reset_index()

    # ============================================
    # EMA
    # ============================================

    df['EMA20'] = df['Close'].ewm(span=20).mean()

    df['EMA50'] = df['Close'].ewm(span=50).mean()

    # ============================================
    # VWAP
    # ============================================

    df['VWAP'] = (
        (df['Close'] * df['Volume']).cumsum()
        / df['Volume'].cumsum()
    )

    # ============================================
    # RSI
    # ============================================

    delta = df['Close'].diff()

    gain = delta.clip(lower=0)

    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()

    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss

    df['RSI'] = 100 - (100 / (1 + rs))

    df['RSI'] = df['RSI'].fillna(50)

    # ============================================
    # SIGNALS
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

    # ============================================
    # LATEST ROW
    # ============================================

    latest = df.iloc[-1]

    # ============================================
    # SIGNAL SHOW
    # ============================================

    if latest['BUY']:
        st.success("🚀 BUY SIGNAL")

    elif latest['SELL']:
        st.error("🔻 SELL SIGNAL")

    else:
        st.warning("⚠️ SIDEWAYS MARKET")

    # ============================================
    # LIVE PRICE
    # ============================================

    st.metric(
        "LIVE PRICE",
        f"₹ {round(latest['Close'], 2)}"
    )

    # ============================================
    # CHART
    # ============================================

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['Close'],
        name='Close'
    ))

    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['EMA20'],
        name='EMA20'
    ))

    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['EMA50'],
        name='EMA50'
    ))

    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['VWAP'],
        name='VWAP'
    ))

    fig.update_layout(
        title=f"{stock_name} LIVE CHART",
        height=600
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # ============================================
    # TABLE
    # ============================================

    st.dataframe(
        df.tail(20),
        use_container_width=True
    )

except Exception as e:

    st.error("APP ERROR")

    st.code(str(e))
