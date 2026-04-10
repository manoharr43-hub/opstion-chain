import streamlit as st
import pandas as pd
import numpy as np

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="🔥 ATM ZONE BIG MOVE SCANNER", layout="wide")

# =========================
# LTP SIMULATION
# =========================
def get_ltp(index):
    return {
        "NIFTY": 24015,
        "BANKNIFTY": 48250,
        "FINNIFTY": 20250
    }.get(index, 0)

# =========================
# OPTION CHAIN
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
        "CE_OI": np.random.randint(1000, 4000, len(strikes)),
        "PE_OI": np.random.randint(1000, 4000, len(strikes)),
    })

# =========================
# ATM FINDER
# =========================
def get_atm(df, ltp):
    return min(df["Strike"], key=lambda x: abs(x - ltp))

# =========================
# BIG MOVE DETECTOR
# =========================
def big_move_zone(df, atm):
    df["TOTAL_OI"] = df["CE_OI"] + df["PE_OI"]

    # ATM + nearby strikes
    df["DIST"] = abs(df["Strike"] - atm)

    zone = df.sort_values(["DIST", "TOTAL_OI"], ascending=[True, False])

    return zone.head(3)

# =========================
# TREND
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
st.sidebar.title("📊 ATM ZONE PANEL")

index = st.sidebar.selectbox(
    "Select Index",
    ["NIFTY", "BANKNIFTY", "FINNIFTY"]
)

expiry = st.sidebar.radio(
    "Expiry",
    ["Weekly", "Monthly"]
)

# =========================
# DATA
# =========================
ltp = get_ltp(index)
df = option_chain(index)

atm = get_atm(df, ltp)
df["TOTAL_OI"] = df["CE_OI"] + df["PE_OI"]

zone = big_move_zone(df, atm)

trend_value = trend(df)
pcr_value = pcr(df)
vix_value = vix()

# =========================
# HEADER
# =========================
st.title("🔥 ATM ZONE BIG MOVE SCANNER (NEW VERSION)")
st.caption("Detects Big Movement Near ATM Strike | Fully Separate App")

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
c2.metric("ATM Strike", atm)
c3.metric("PCR", pcr_value)
c4.metric("VIX", vix_value)

# =========================
# FULL OPTION CHAIN
# =========================
st.subheader("📊 Option Chain Data")

st.dataframe(df, use_container_width=True)

# =========================
# ATM BIG MOVE ZONE
# =========================
st.subheader("🚀 ATM BIG MOVE ZONE (TOP STRIKES)")

st.dataframe(zone, use_container_width=True)

# =========================
# REPORT
# =========================
st.subheader("📌 Market Report")

st.write(f"""
✔ Index: {index}  
✔ Expiry: {expiry}  
✔ LTP: {ltp}  
✔ ATM: {atm}  
✔ PCR: {pcr_value}  
✔ VIX: {vix_value}  
✔ Trend: {trend_value}  
""")

# =========================
# SIGNAL
# =========================
if pcr_value > 1:
    st.success("🟢 PUT Pressure Strong (Bearish Bias)")
else:
    st.warning("🔴 CALL Pressure Strong (Bullish Bias)")

st.success("✅ ATM ZONE BIG MOVE SCANNER READY (NO OLD CODE IMPACT)")
