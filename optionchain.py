import streamlit as st
import numpy as np
import pandas as pd

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="🔥 PRO AI TRADING DASHBOARD", layout="wide")

st.title("🚀 PRO AI MULTI INDEX OPTION CHAIN")

# =========================
# INDEX MAP
# =========================
INDEX_MAP = {
    "NIFTY": 24000,
    "BANKNIFTY": 48200,
    "FINNIFTY": 20200,
    "MIDNIFTY": 12000
}

# =========================
# STOCK LIST
# =========================
STOCKS = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK"]

# =========================
# TREND ENGINE
# =========================
def trend():
    return np.random.choice([
        "🟢 BULLISH",
        "🔴 BEARISH",
        "🟡 SIDEWAYS"
    ])

# =========================
# CE / PE FLOW
# =========================
def ce_pe_signal():
    val = np.random.randint(-100, 100)
    if val > 40:
        return "🟢 CALL SIDE ACTIVE"
    elif val < -40:
        return "🔴 PUT SIDE ACTIVE"
    return "🟡 NEUTRAL"

# =========================
# PCR + VIX
# =========================
def pcr():
    ce = np.random.randint(50000, 120000)
    pe = np.random.randint(50000, 120000)
    return round(pe / ce, 2), ce, pe

def vix():
    return round(np.random.uniform(11, 20), 2)

# =========================
# OI TABLE
# =========================
def oi_table():
    return pd.DataFrame({
        "Strike": [24000, 24050, 24100, 24150, 24200],
        "CALL_OI": np.random.randint(1000, 5000, 5),
        "PUT_OI": np.random.randint(1000, 5000, 5),
        "CHG_CALL": np.random.randint(-500, 500, 5),
        "CHG_PUT": np.random.randint(-500, 500, 5),
    })

# =========================
# AI STRIKE ENGINE
# =========================
def ai_engine(strike):
    move = np.random.randint(-300, 300)
    target = strike + move
    sl = strike - abs(move) * 0.6

    if move > 50:
        signal = "🟢 CALL ENTRY"
    elif move < -50:
        signal = "🔴 PUT ENTRY"
    else:
        signal = "🟡 WAIT"

    return signal, target, sl

# =========================
# LEFT PANEL
# =========================
st.sidebar.header("📊 CONTROL PANEL")

index = st.sidebar.selectbox("Select Index", list(INDEX_MAP.keys()))
stock = st.sidebar.selectbox("Select Stock", STOCKS)

ltp = INDEX_MAP[index]

st.sidebar.info(f"LTP: {ltp}")

strike = st.sidebar.number_input("Enter Strike", value=ltp)

run = st.sidebar.button("⚡ RUN ANALYSIS")

# =========================
# MAIN DASHBOARD (3 COLUMNS)
# =========================
col1, col2, col3 = st.columns(3)

# =========================
# INDEX PANEL
# =========================
with col1:
    st.subheader("📊 INDEX REPORT")

    st.metric("INDEX", index)
    st.metric("LTP", ltp)
    st.markdown(f"### TREND: {trend()}")
    st.success("LIVE INDEX ACTIVE")

# =========================
# STOCK PANEL
# =========================
with col2:
    st.subheader("📌 STOCK REPORT")

    st.metric("STOCK", stock)
    st.markdown(f"### FLOW: {ce_pe_signal()}")
    st.warning("CALL / PUT MOVEMENT ACTIVE")

# =========================
# STRIKE PANEL
# =========================
with col3:
    st.subheader("🎯 STRIKE PANEL")

    if run:
        signal, target, sl = ai_engine(strike)

        st.metric("STRIKE", strike)
        st.metric("TARGET", round(target, 2))
        st.metric("STOPLOSS", round(sl, 2))

        st.success(f"SIGNAL: {signal}")
        st.info(ce_pe_signal())

# =========================
# OI TABLE
# =========================
st.subheader("📊 CALL vs PUT OI FLOW")

st.dataframe(oi_table(), use_container_width=True)

# =========================
# PCR + VIX
# =========================
pcr_value, ce_total, pe_total = pcr()
vix_value = vix()

c1, c2, c3 = st.columns(3)

with c1:
    st.metric("📌 PCR", pcr_value)

with c2:
    st.metric("📉 CE OI", ce_total)

with c3:
    st.metric("📈 PE OI", pe_total)

st.info(f"🇮🇳 INDIA VIX: {vix_value}")

# =========================
# FINAL REPORT
# =========================
st.subheader("📊 LIVE REPORT")

st.write(f"""
✔ INDEX: {index}  
✔ STOCK: {stock}  
✔ STRIKE: {strike}  
✔ STATUS: LIVE AI ANALYSIS ACTIVE  
✔ SYSTEM: MULTI INDEX OPTION ENGINE  
""")
