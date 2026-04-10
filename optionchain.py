import streamlit as st
import pandas as pd
import numpy as np

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="🔥 BIG PLAYER AI SCANNER", layout="wide")

# =========================
# LTP SIM
# =========================
def get_ltp(index):
    return {
        "NIFTY": 24015,
        "BANKNIFTY": 48250,
        "FINNIFTY": 20250
    }.get(index, 0)

# =========================
# OPTION CHAIN GENERATOR
# =========================
def option_chain(index):
    if index == "NIFTY":
        base, step = 24000, 50
    elif index == "BANKNIFTY":
        base, step = 48200, 100
    else:
        base, step = 20200, 50

    strikes = [base + i * step for i in range(-3, 4)]

    return pd.DataFrame({
        "Strike": strikes,
        "CE_OI": np.random.randint(1000, 5000, len(strikes)),
        "PE_OI": np.random.randint(1000, 5000, len(strikes)),
    })

# =========================
# ATM DETECTION
# =========================
def get_atm(df, ltp):
    return min(df["Strike"], key=lambda x: abs(x - ltp))

# =========================
# BIG PLAYER AI ENGINE
# =========================
def big_player_ai(df):
    df = df.copy()

    # simulate volume (AI observation)
    df["VOLUME"] = np.random.randint(2000, 12000, len(df))

    # OI strength
    df["OI_STRENGTH"] = df["CE_OI"] + df["PE_OI"]

    # CE / PE imbalance
    df["CE_PE_RATIO"] = df["CE_OI"] / (df["PE_OI"] + 1)

    # PE / CE imbalance
    df["PE_CE_RATIO"] = df["PE_OI"] / (df["CE_OI"] + 1)

    # SPIKE SCORE (BIG PLAYER ACTIVITY)
    df["SPIKE_SCORE"] = df["VOLUME"] * df["OI_STRENGTH"]

    # TOP BIG PLAYER ZONE
    top = df.sort_values("SPIKE_SCORE", ascending=False).head(3)

    return top

# =========================
# TREND ENGINE
# =========================
def trend(df):
    ce = df["CE_OI"].sum()
    pe = df["PE_OI"].sum()

    if ce > pe * 1.1:
        return "🟢 BULLISH"
    elif pe > ce * 1.1:
        return "🔴 BEARISH"
    return "🟡 SIDEWAYS"

# =========================
# PCR
# =========================
def pcr(df):
    return round(df["PE_OI"].sum() / df["CE_OI"].sum(), 2)

# =========================
# VIX (SIM)
# =========================
def vix():
    return round(np.random.uniform(11, 18), 2)

# =========================
# SIDEBAR
# =========================
st.sidebar.title("📊 BIG PLAYER AI PANEL")

index = st.sidebar.selectbox(
    "Select Index",
    ["NIFTY", "BANKNIFTY", "FINNIFTY"]
)

expiry = st.sidebar.radio(
    "Select Expiry",
    ["Weekly", "Monthly"]
)

# =========================
# DATA
# =========================
ltp = get_ltp(index)
df = option_chain(index)

atm = get_atm(df, ltp)

df["TOTAL_OI"] = df["CE_OI"] + df["PE_OI"]

big_zone = big_player_ai(df)

trend_value = trend(df)
pcr_value = pcr(df)
vix_value = vix()

# =========================
# HEADER
# =========================
st.title("🔥 NEXT LEVEL BIG PLAYER AI SCANNER")
st.caption("Smart Money Detection | Spike Score Engine | Fully Separate System")

# =========================
# SIDEBAR INFO
# =========================
st.sidebar.markdown("---")
st.sidebar.success(f"Index: {index}")
st.sidebar.info(f"LTP: {ltp}")
st.sidebar.warning(f"ATM: {atm}")
st.sidebar.error(f"PCR: {pcr_value}")
st.sidebar.info(f"VIX: {vix_value}")
st.sidebar.success(f"Trend: {trend_value}")
st.sidebar.info(f"Expiry: {expiry}")

# =========================
# METRICS
# =========================
c1, c2, c3, c4 = st.columns(4)

c1.metric("Index", index)
c2.metric("ATM", atm)
c3.metric("PCR", pcr_value)
c4.metric("VIX", vix_value)

# =========================
# OPTION CHAIN
# =========================
st.subheader("📊 Option Chain Data")

st.dataframe(df, use_container_width=True)

# =========================
# BIG PLAYER ZONE
# =========================
st.subheader("🔥 BIG PLAYER ENTRY ZONE (AI DETECTED)")

st.dataframe(big_zone, use_container_width=True)

# =========================
# REPORT
# =========================
st.subheader("📌 Market Report")

st.write(f"""
✔ Index: {index}  
✔ Expiry: {expiry}  
✔ ATM: {atm}  
✔ PCR: {pcr_value}  
✔ VIX: {vix_value}  
✔ Trend
