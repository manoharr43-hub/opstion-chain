# ============================================
# 🚀 NSE OPTION CHAIN AI PRO MAX
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
    page_title="NSE AI OPTION PRO",
    layout="wide"
)

# ============================================
# TITLE
# ============================================

st.title("🚀 NSE AI OPTION PRO MAX")
st.markdown("### LIVE AI Trading Dashboard")

# ============================================
# SIDEBAR
# ============================================

st.sidebar.header("⚙️ SETTINGS")

symbol = st.sidebar.selectbox(
    "Select Symbol",
    [
        "RELIANCE.NS",
        "TCS.NS",
        "INFY.NS",
        "HDFCBANK.NS",
        "ICICIBANK.NS",
        "^NSEI",
        "^BANKNIFTY"
    ]
)

interval = st.sidebar.selectbox(
    "Interval",
    ["5m", "15m", "30m", "1h"]
)

period = st.sidebar.selectbox(
    "Period",
    ["1d", "5d", "1mo"]
)

# ============================================
# DATA DOWNLOAD
# ============================================

@st.cache_data(ttl=60)
def load_data(symbol, period, interval):

    df = yf.download(
        tickers=symbol,
        period=period,
        interval=interval,
        auto_adjust=True,
        progress=False
    )

    if df.empty:
        return pd.DataFrame()

    # ============================================
    # FIX MULTI INDEX COLUMNS
    # ============================================

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df.copy()

    # ============================================
    # FORCE SERIES
    # ============================================

    close = df["Close"].squeeze()
    high = df["High"].squeeze()
    low = df["Low"].squeeze()
    volume = df["Volume"].squeeze()

    # ============================================
    # EMA
    # ============================================

    df["EMA20"] = close.ewm(span=20).mean()
    df["EMA50"] = close.ewm(span=50).mean()

    # ============================================
    # VWAP
    # ============================================

    df["VWAP"] = (
        (close * volume).cumsum()
        / volume.cumsum()
    )

    # ============================================
    # RSI
    # ============================================

    delta = close.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss

    df["RSI"] = 100 - (100 / (1 + rs))

    df["RSI"] = df["RSI"].fillna(50)

    # ============================================
    # ATR
    # ============================================

    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())

    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    df["ATR"] = tr.rolling(14).mean()

    # ============================================
    # BUY SIGNAL
    # ============================================

    df["BUY"] = (
        (df["EMA20"] > df["EMA50"]) &
        (close > df["VWAP"]) &
        (df["RSI"] > 55)
    )

    # ============================================
    # SELL SIGNAL
    # ============================================

    df["SELL"] = (
        (df["EMA20"] < df["EMA50"]) &
        (close < df["VWAP"]) &
        (df["RSI"] < 45)
    )

    return df

# ============================================
# LOAD DATA
# ============================================

df = load_data(symbol, period, interval)

# ============================================
# EMPTY CHECK
# ============================================

if df.empty:
    st.error("❌ No Data Found")
    st.stop()

# ============================================
# LATEST VALUES
# ============================================

latest = df.iloc[-1]

ltp = round(float(latest["Close"]), 2)
rsi = round(float(latest["RSI"]), 2)
vwap = round(float(latest["VWAP"]), 2)
ema20 = round(float(latest["EMA20"]), 2)
ema50 = round(float(latest["EMA50"]), 2)
atr = round(float(latest["ATR"]), 2)

# ============================================
# SIGNAL
# ============================================

signal = "SIDEWAYS"

if latest["BUY"]:
    signal = "BUY"

if latest["SELL"]:
    signal = "SELL"

# ============================================
# METRICS
# ============================================

col1, col2, col3, col4, col5, col6 = st.columns(6)

col1.metric("LTP", ltp)
col2.metric("RSI", rsi)
col3.metric("VWAP", vwap)
col4.metric("EMA20", ema20)
col5.metric("EMA50", ema50)
col6.metric("ATR", atr)

# ============================================
# SIGNAL DISPLAY
# ============================================

st.subheader("📡 AI SIGNAL")

if signal == "BUY":
    st.success("🚀 BUY SIGNAL DETECTED")

elif signal == "SELL":
    st.error("🔻 SELL SIGNAL DETECTED")

else:
    st.warning("⚠️ SIDEWAYS MARKET")

# ============================================
# CHART
# ============================================

fig = go.Figure()

# PRICE
fig.add_trace(
    go.Scatter(
        x=df.index,
        y=df["Close"],
        mode="lines",
        name="Close"
    )
)

# EMA20
fig.add_trace(
    go.Scatter(
        x=df.index,
        y=df["EMA20"],
        mode="lines",
        name="EMA20"
    )
)

# EMA50
fig.add_trace(
    go.Scatter(
        x=df.index,
        y=df["EMA50"],
        mode="lines",
        name="EMA50"
    )
)

# VWAP
fig.add_trace(
    go.Scatter(
        x=df.index,
        y=df["VWAP"],
        mode="lines",
        name="VWAP"
    )
)

fig.update_layout(
    title=f"{symbol} LIVE CHART",
    height=600,
    xaxis_title="Time",
    yaxis_title="Price"
)

st.plotly_chart(fig, use_container_width=True)

# ============================================
# LAST SIGNALS
# ============================================

st.subheader("📋 LAST 10 SIGNALS")

signals_df = df[
    (df["BUY"] == True) |
    (df["SELL"] == True)
].copy()

signals_df["Signal"] = np.where(
    signals_df["BUY"],
    "BUY",
    "SELL"
)

show_df = signals_df[
    ["Close", "RSI", "VWAP", "Signal"]
].tail(10)

st.dataframe(show_df, use_container_width=True)

# ============================================
# MARKET STATUS
# ============================================

st.subheader("📈 MARKET STATUS")

if rsi > 70:
    st.error("🔥 OVERBOUGHT MARKET")

elif rsi < 30:
    st.success("💎 OVERSOLD MARKET")

else:
    st.info("⚖️ NORMAL MARKET")

# ============================================
# FOOTER
# ============================================

st.markdown("---")

st.caption(
    f"Updated: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"
)
