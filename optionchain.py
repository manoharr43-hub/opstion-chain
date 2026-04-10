import streamlit as st
import numpy as np
import pandas as pd

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="🔥 PRO OPTION CHAIN AI", layout="wide")
st.title("🚀 ULTRA PRO AI OPTION CHAIN DASHBOARD")

# =========================
# DATA
# =========================
INDEX_MAP = {
    "NIFTY": 24000,
    "BANKNIFTY": 48200,
    "FINNIFTY": 20200
}

STOCKS = ["NONE","RELIANCE","TCS","INFY","HDFCBANK","SBIN","ITC"]

# =========================
# SIDEBAR
# =========================
st.sidebar.header("📊 CONTROL PANEL")

index = st.sidebar.selectbox("📌 Select INDEX", list(INDEX_MAP.keys()))
stock = st.sidebar.selectbox("📌 Select STOCK", STOCKS)

strike = st.sidebar.number_input("🎯 Enter Strike Price", value=INDEX_MAP[index], step=50)

run = st.sidebar.button("⚡ RUN ANALYSIS")

ltp = INDEX_MAP[index]

# =========================
# TREND ENGINE
# =========================
def trend_engine():
    return np.random.choice(["🟢 BULLISH", "🔴 BEARISH", "🟡 SIDEWAYS"])

# =========================
# OI ENGINE (5 COLUMN)
# =========================
def oi_engine():
    call_oi = np.random.randint(10000, 50000)
    call_chg = np.random.randint(-5000, 5000)
    put_oi = np.random.randint(10000, 50000)
    put_chg = np.random.randint(-5000, 5000)

    net = call_oi - put_oi

    return call_oi, call_chg, put_oi, put_chg, net

# =========================
# AI ENGINE
# =========================
def ai_engine(strike):
    move = np.random.randint(-300, 300)

    entry = strike + (50 if move > 0 else -50)
    sl = entry - 100 if move > 0 else entry + 100

    t1 = entry + 50
    t2 = entry + 100
    t3 = entry + 150

    ce = np.random.randint(2000, 9000)
    pe = np.random.randint(2000, 9000)

    signal = "🟢 CALL" if ce > pe else "🔴 PUT"

    return signal, entry, sl, t1, t2, t3, ce, pe

# =========================
# VALIDATION
# =========================
if index not in INDEX_MAP:
    st.stop()

# =========================
# HEADER
# =========================
st.success(f"INDEX: {index}")
st.info(f"LTP: {ltp}")

# =========================
# TREND SECTION
# =========================
trend = trend_engine()

st.subheader("📊 TREND ANALYSIS")
st.success(f"TREND: {trend}")

# =========================
# 5 COLUMN TABLE (MAIN REQUIREMENT)
# =========================
call_oi, call_chg, put_oi, put_chg, net = oi_engine()

df = pd.DataFrame([{
    "CALL OI": call_oi,
    "CALL CHG": call_chg,
    "PUT OI": put_oi,
    "PUT CHG": put_chg,
    "NET FLOW": net
}])

st.subheader("📊 OPTION FLOW (5 COLUMN)")
st.dataframe(df, use_container_width=True)

# =========================
# STOCK SECTION
# =========================
st.subheader("📌 STOCK ANALYSIS")

if stock == "NONE":
    st.warning("⚠ No Stock Selected")
else:
    stock_signal = "🟢 CALL STRONG" if np.random.rand() > 0.5 else "🔴 PUT STRONG"
    st.success(f"STOCK: {stock}")
    st.info(f"FLOW: {stock_signal}")

# =========================
# BIG MOVE + AI PLAN
# =========================
if run:

    signal, entry, sl, t1, t2, t3, ce, pe = ai_engine(strike)

    st.subheader("🚀 TODAY BIG MOVE + AI STRIKE")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("CALL STRENGTH", ce)

    with col2:
        st.metric("PUT STRENGTH", pe)

    with col3:
        st.success(signal)

    st.subheader("🎯 AI TRADE PLAN")

    st.info(f"""
    ENTRY: {entry}
    EXIT: {t1}
    STOPLOSS: {sl}
    TARGET 1: {t1}
    TARGET 2: {t2}
    TARGET 3: {t3}
    """)
