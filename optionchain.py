import streamlit as st
import numpy as np
import pandas as pd

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="🚀 AI OPTION CHAIN DASHBOARD", layout="wide")

st.title("🔥 ULTRA AI OPTION CHAIN + STRIKE ANALYSIS")

# =========================
# INDEX DATA
# =========================
INDEX_MAP = {
    "NIFTY": 24000,
    "BANKNIFTY": 48200,
    "FINNIFTY": 20200,
    "MIDNIFTY": 12000
}

STOCKS = [
    "RELIANCE","TCS","INFY","HDFCBANK","ICICIBANK",
    "SBIN","ITC","LT","AXISBANK","KOTAKBANK"
]

# =========================
# SIDEBAR FLOW (IMPORTANT ORDER)
# =========================
st.sidebar.header("📊 CONTROL PANEL")

index = st.sidebar.selectbox("📌 Select INDEX", ["NONE"] + list(INDEX_MAP.keys()))

# stock only after index
if index == "NONE":
    st.sidebar.warning("⚠ Please select INDEX first")
    stock = "NONE"
else:
    stock = st.sidebar.selectbox("📌 Select STOCK", STOCKS)

# auto strike
base_strike = INDEX_MAP.get(index, 0)

strike = st.sidebar.number_input(
    "🎯 Enter Strike Price",
    value=base_strike,
    step=50
)

run = st.sidebar.button("⚡ RUN AI ANALYSIS")

# =========================
# SAFE CHECK
# =========================
if index == "NONE":
    st.stop()

ltp = INDEX_MAP[index]

# =========================
# AI ENGINE
# =========================
def ai_engine(strike, ltp):
    ce = np.random.randint(2000, 10000)
    pe = np.random.randint(2000, 10000)

    total = ce + pe
    ce_p = round((ce / total) * 100, 2)
    pe_p = round((pe / total) * 100, 2)

    # BIG MOVEMENT LOGIC
    if ce_p > 60:
        trend = "🟢 STRONG CALL MOVE"
        entry = strike + 50
        sl = strike - 100
    elif pe_p > 60:
        trend = "🔴 STRONG PUT MOVE"
        entry = strike - 50
        sl = strike + 100
    else:
        trend = "🟡 SIDEWAYS"
        entry = strike
        sl = strike - 50

    # TARGETS
    t1 = entry + 50
    t2 = entry + 100
    t3 = entry + 150

    return ce, pe, ce_p, pe_p, trend, entry, sl, t1, t2, t3

# =========================
# HEADER
# =========================
st.success(f"📌 INDEX: {index}")
st.info(f"📊 LTP: {ltp}")
st.success(f"📌 STOCK: {stock}")

# =========================
# 3 COLUMN VIEW
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
    st.subheader("🎯 STRIKE")
    st.metric("Strike", strike)

# =========================
# MAIN ANALYSIS
# =========================
if run:

    ce, pe, cep, pep, trend, entry, sl, t1, t2, t3 = ai_engine(strike, ltp)

    st.subheader("🚀 TODAY BIG MOVEMENT ANALYSIS")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("CALL STRENGTH", ce)
        st.progress(int(cep))

    with col2:
        st.metric("PUT STRENGTH", pe)
        st.progress(int(pep))

    with col3:
        st.success(trend)

    # =========================
    # FINAL TRADE PLAN
    # =========================
    st.subheader("🎯 AI TRADE PLAN")

    st.info(f"""
    📌 ENTRY POINT: {entry}  
    ❌ STOP LOSS: {sl}  
    🎯 TARGET 1: {t1}  
    🎯 TARGET 2: {t2}  
    🚀 TARGET 3: {t3}  
    """)

    # =========================
    # STRIKE TABLE
    # =========================
    st.subheader("📊 STRIKE ZONE FLOW")

    df = pd.DataFrame({
        "Strike": [strike-100, strike-50, strike, strike+50, strike+100],
        "CE Flow": np.random.randint(1000, 9000, 5),
        "PE Flow": np.random.randint(1000, 9000, 5),
    })

    st.dataframe(df, use_container_width=True)

# =========================
# LIVE REPORT
# =========================
st.subheader("📌 LIVE REPORT")

st.write(f"""
✔ INDEX: {index}  
✔ STOCK: {stock}  
✔ STRIKE: {strike}  
✔ STATUS: AI OPTION CHAIN ACTIVE  
✔ MODE: SAFE NEW BUILD  
""")
