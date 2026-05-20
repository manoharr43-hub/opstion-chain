# =========================================================
# 🚀 NSE AI PRO MAX V3.0 - INSTITUTIONAL EDITION
# =========================================================

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from concurrent.futures import ThreadPoolExecutor
from streamlit_autorefresh import st_autorefresh
import ta

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="NSE AI PRO MAX V3.0",
    layout="wide",
    page_icon="🚀"
)

st_autorefresh(interval=60000, key="refresh")

# =========================================================
# DARK CSS
# =========================================================
st.markdown("""
<style>
.main {
    background-color: #0E1117;
    color: white;
}
.stMetric {
    background: #1E1E1E;
    padding: 10px;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# TITLE
# =========================================================
st.title("🚀 NSE AI PRO MAX V3.0")
st.caption("INSTITUTIONAL EDITION")

# =========================================================
# NSE STOCKS
# =========================================================
nse_stocks = {
    "RELIANCE": "RELIANCE.NS",
    "HDFCBANK": "HDFCBANK.NS",
    "INFY": "INFY.NS",
    "ICICIBANK": "ICICIBANK.NS",
    "TCS": "TCS.NS",
    "SBIN": "SBIN.NS",
    "ITC": "ITC.NS",
    "LT": "LT.NS",
    "AXISBANK": "AXISBANK.NS",
    "SUNPHARMA": "SUNPHARMA.NS"
}

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.header("⚙️ SETTINGS")

selected_stock = st.sidebar.selectbox(
    "SELECT STOCK",
    list(nse_stocks.keys())
)

interval = st.sidebar.selectbox(
    "INTERVAL",
    ["5m", "15m", "30m", "1h"]
)

period = st.sidebar.selectbox(
    "PERIOD",
    ["1d", "5d", "1mo"]
)

ticker = nse_stocks[selected_stock]

# =========================================================
# INDICATORS
# =========================================================
def calculate_indicators(df):

    df["EMA20"] = ta.trend.ema_indicator(df["Close"], window=20)
    df["EMA50"] = ta.trend.ema_indicator(df["Close"], window=50)

    df["RSI"] = ta.momentum.rsi(df["Close"], window=14)

    macd = ta.trend.MACD(df["Close"])
    df["MACD"] = macd.macd()
    df["MACD_SIGNAL"] = macd.macd_signal()

    bb = ta.volatility.BollingerBands(df["Close"])
    df["BB_HIGH"] = bb.bollinger_hband()
    df["BB_LOW"] = bb.bollinger_lband()

    atr = ta.volatility.AverageTrueRange(
        df["High"],
        df["Low"],
        df["Close"]
    )

    df["ATR"] = atr.average_true_range()

    df["VWAP"] = (
        (df["Close"] * df["Volume"]).cumsum()
    ) / df["Volume"].cumsum()

    return df

# =========================================================
# AI SIGNAL ENGINE
# =========================================================
def generate_ai_signal(df):

    latest = df.iloc[-1]

    score = 0

    # EMA TREND
    if latest["EMA20"] > latest["EMA50"]:
        score += 25
    else:
        score -= 25

    # VWAP
    if latest["Close"] > latest["VWAP"]:
        score += 20
    else:
        score -= 20

    # RSI
    if 55 < latest["RSI"] < 70:
        score += 20

    elif latest["RSI"] > 75:
        score -= 10

    # MACD
    if latest["MACD"] > latest["MACD_SIGNAL"]:
        score += 25
    else:
        score -= 25

    # VOLUME
    recent_volume = df["Volume"].tail(5).mean()

    if latest["Volume"] > recent_volume:
        score += 10

    # FINAL SIGNAL
    if score >= 70:
        signal = "🚀 STRONG BUY"

    elif score >= 30:
        signal = "✅ BUY"

    elif score <= -70:
        signal = "🚨 STRONG SELL"

    elif score <= -30:
        signal = "🔻 SELL"

    else:
        signal = "⚠️ SIDEWAYS"

    return signal, score

# =========================================================
# MAIN DATA
# =========================================================
try:

    df = yf.download(
        ticker,
        interval=interval,
        period=period,
        progress=False,
        auto_adjust=True
    )

    if df.empty:
        st.error("NO DATA FOUND")

    else:

        df = calculate_indicators(df)

        signal, score = generate_ai_signal(df)

        latest = df.iloc[-1]

        current_price = float(latest["Close"])

        # =================================================
        # AI SIGNAL
        # =================================================
        st.subheader("🤖 AI SIGNAL")

        if "BUY" in signal:
            st.success(f"{signal} | SCORE: {score}")

        elif "SELL" in signal:
            st.error(f"{signal} | SCORE: {score}")

        else:
            st.warning(f"{signal} | SCORE: {score}")

        # =================================================
        # METRICS
        # =================================================
        c1, c2, c3, c4, c5 = st.columns(5)

        c1.metric("PRICE", f"₹ {round(current_price,2)}")
        c2.metric("RSI", round(float(latest["RSI"]),2))
        c3.metric("VWAP", round(float(latest["VWAP"]),2))
        c4.metric("MACD", round(float(latest["MACD"]),2))
        c5.metric("AI SCORE", score)

        # =================================================
        # ATR TARGETS
        # =================================================
        atr = float(latest["ATR"])

        entry = current_price
        sl = entry - atr
        target1 = entry + atr
        target2 = entry + (atr * 2)
        target3 = entry + (atr * 3)

        st.markdown("---")
        st.subheader("🎯 AI TARGET ENGINE")

        a1, a2, a3, a4, a5 = st.columns(5)

        a1.metric("ENTRY", round(entry,2))
        a2.metric("SL", round(sl,2))
        a3.metric("TARGET 1", round(target1,2))
        a4.metric("TARGET 2", round(target2,2))
        a5.metric("TARGET 3", round(target3,2))

        # =================================================
        # CHART
        # =================================================
        st.markdown("---")
        st.subheader(f"📈 {selected_stock} LIVE CHART")

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["Close"],
                mode="lines",
                name="Close"
            )
        )

        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["EMA20"],
                mode="lines",
                name="EMA20"
            )
        )

        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["EMA50"],
                mode="lines",
                name="EMA50"
            )
        )

        fig.update_layout(
            template="plotly_dark",
            height=600
        )

        st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"ERROR : {str(e)}")
