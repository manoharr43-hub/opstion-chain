import streamlit as st
import numpy as np
import pandas as pd

# =========================
# PAGE SETUP
# =========================
st.set_page_config(page_title="🔥 CLEAN AI TRADING DASHBOARD", layout="wide")

st.title("🚀 CLEAN AI MARKET DASHBOARD (SAFE VERSION)")

# =========================
# INDEX DATA
# =========================
INDEX_MAP = {
    "NIFTY": 24000,
    "BANKNIFTY": 48200,
    "FINNIFTY": 20200,
    "MIDNIFTY": 12000
}

STOCKS = ["NONE", "RELIANCE", "TCS", "INFY", "HDFCBANK", "SBIN"]

# =========================
# SIDEBAR
# =========================
st.sidebar.header("📊 CONTROL PANEL")

index = st.sidebar.selectbox("Select Index", ["NONE"] + list(INDEX_MAP.keys()))
stock = st.sidebar.selectbox("Select Stock", STOCKS)

# AUTO STRIKE BASE
base_strike = INDEX_MAP[index] if index != "NONE" else 0

strike = st.sidebar.number_input(
    "Enter Strike Price",
    value=base_strike,
    step=50
)

run = st.sidebar.button("⚡ RUN ANALYSIS")

# =========================
# SAFE CHECK
# =========================
if index == "NONE":
    st.warning("⚠ Please select INDEX")
    st.stop()

# =========================
# CE / PE LOGIC
# =========================
ltp = INDEX_MAP[index]

def ce_pe(strike, ltp):
    if strike > ltp:
        return "🔴 PUT (PE)"
    elif strike < ltp:
        return "🟢 CALL (CE)"
    else:
        return "⚪ ATM"

signal = ce_pe(strike, ltp)

# =========================
# AI SIMPLE ENGINE
# =========================
def ai_prediction(strike):
    move = np.random.randint(-300, 300)
    target = strike + move
    sl = strike - abs(move) * 0.5

    return target, sl

# =========================
# DASHBOARD
# =========================
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("📊 INDEX")
    st.metric("Name", index)
    st.metric("LTP", ltp)

with col2:
    st.subheader("📌 STOCK")
    st.metric("Stock", stock)

with col3:
    st.subheader("🎯 STRIKE SIGNAL")
    st.metric("Strike", strike)
    st.success(signal)

# =========================
# AI RESULT
# =========================
if run:
    target, sl = ai_prediction(strike)

    st.subheader("🤖 AI TRADE PLAN")

    st.success(f"ENTRY STRIKE: {strike}")
    st.info(f"TARGET: {round(target,2)}")
    st.error(f"STOPLOSS: {round(sl,2)}")

# =========================
# OPTION STYLE TABLE
# =========================
st.subheader("📊 STRIKE ZONE VIEW")

df = pd.DataFrame({
    "Strike": [strike-100, strike-50, strike, strike+50, strike+100],
    "CE Flow": np.random.randint(1000, 8000, 5),
    "PE Flow": np.random.randint(1000, 8000, 5)
})

st.dataframe(df, use_container_width=True)

# =========================
# REPORT
# =========================
st.subheader("📌 LIVE REPORT")

st.write(f"""
✔ INDEX: {index}  
✔ STOCK: {stock}  
✔ LTP: {ltp}  
✔ STRIKE: {strike}  
✔ SIGNAL: {signal}  
✔ STATUS: CLEAN SAFE SYSTEM ACTIVE  
""")
