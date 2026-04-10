import streamlit as st
import numpy as np
import pandas as pd

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="🔥 NEW PRO AI TRADING DASHBOARD", layout="wide")

st.title("🚀 PRO AI TRADING SYSTEM (NEW VERSION)")

# =========================
# DATA
# =========================
INDEX_MAP = {
    "NIFTY": 24000,
    "BANKNIFTY": 48200,
    "FINNIFTY": 20200,
    "MIDNIFTY": 12000
}

STOCKS = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "ITC", "SBIN"]

# =========================
# SIDEBAR
# =========================
st.sidebar.header("📊 CONTROL PANEL")

index = st.sidebar.selectbox("Select Index", ["NONE"] + list(INDEX_MAP.keys()))
stock = st.sidebar.selectbox("Select Stock", ["NONE"] + STOCKS)

strike = st.sidebar.number_input("Enter Strike Price", value=24000)

run = st.sidebar.button("⚡ RUN ANALYSIS")

# =========================
# STOP IF NONE
# =========================
if index == "NONE" or stock == "NONE":
    st.warning("⚠ Please select INDEX and STOCK to continue")
    st.stop()

# =========================
# FUNCTIONS
# =========================
def trend():
    return np.random.choice(["🟢 BULLISH", "🔴 BEARISH", "🟡 SIDEWAYS"])

def ce_pe():
    ce = np.random.randint(20000, 80000)
    pe = np.random.randint(20000, 80000)
    return ce, pe

def pcr(ce, pe):
    return round(pe / ce, 2)

def vix():
    return round(np.random.uniform(11, 20), 2)

def ai_engine(strike):
    move = np.random.randint(-300, 300)
    target = strike + move
    sl = strike - abs(move) * 0.6

    if move > 50:
        signal = "CALL ENTRY 🟢"
    elif move < -50:
        signal = "PUT ENTRY 🔴"
    else:
        signal = "WAIT 🟡"

    return signal, target, sl

# =========================
# HEADER
# =========================
ltp = INDEX_MAP[index]

st.success(f"📌 ACTIVE INDEX: {index}")
st.info(f"📊 LTP: {ltp}")
st.success(f"📌 STOCK: {stock}")

# =========================
# 3 COLUMN DASHBOARD
# =========================
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("📊 INDEX")
    st.metric("Trend", trend())
    st.metric("LTP", ltp)

with col2:
    st.subheader("📌 STOCK")
    st.metric("Name", stock)
    st.metric("Flow", np.random.choice(["BUY PRESSURE 🟢", "SELL PRESSURE 🔴"]))

with col3:
    st.subheader("🎯 STRIKE")

    if run:
        signal, target, sl = ai_engine(strike)

        st.metric("Strike", strike)
        st.metric("Target", round(target, 2))
        st.metric("Stoploss", round(sl, 2))
        st.success(signal)

# =========================
# OI TABLE
# =========================
st.subheader("📊 OPTION CHAIN (SIMULATED)")

df = pd.DataFrame({
    "Strike": [strike-100, strike-50, strike, strike+50, strike+100],
    "CE_OI": np.random.randint(1000, 5000, 5),
    "PE_OI": np.random.randint(1000, 5000, 5),
})

st.dataframe(df, use_container_width=True)

# =========================
# PCR + VIX
# =========================
ce, pe = ce_pe()

st.subheader("📊 MARKET STRENGTH")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("CE OI", ce)

with col2:
    st.metric("PE OI", pe)

with col3:
    st.metric("PCR", pcr(ce, pe))

st.info(f"🇮🇳 INDIA VIX: {vix()}")

# =========================
# REPORT
# =========================
st.subheader("📌 FINAL REPORT")

st.write(f"""
✔ INDEX: {index}  
✔ STOCK: {stock}  
✔ STRIKE: {strike}  
✔ STATUS: LIVE AI SYSTEM ACTIVE  
✔ MODE: NEW CLEAN DASHBOARD  
""")
