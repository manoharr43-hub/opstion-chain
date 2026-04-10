import streamlit as st
import pandas as pd
import numpy as np

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="🔥 NEW NSE PRO SCANNER V2", layout="wide")

# =========================
# LIVE SIM PRICES
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

    strikes = [base + i * step for i in range(-2, 3)]

    return pd.DataFrame({
        "Strike": strikes,
        "CE_OI": np.random.randint(1000, 3500, 5),
        "PE_OI": np.random.randint(1000, 3500, 5),
    })

# =========================
# ATM CALC
# =========================
def find_atm(df, ltp):
    return min(df["Strike"], key=lambda x: abs(x - ltp))

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
st.sidebar.title("📊 NEW CONTROL PANEL")

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

atm = find_atm(df, ltp)
df["TOTAL_OI"] = df["CE_OI"] + df["PE_OI"]

trend_value = trend(df)
pcr_value = pcr(df)
vix_value = vix()

# =========================
# HEADER
# =========================
st.title("🔥 NEW NSE PRO SCANNER V2 (SEPARATE APP)")
st.caption("No Old Code Impact | Clean New Version")

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
c2.metric("LTP", ltp)
c3.metric("ATM", atm)
c4.metric("PCR", pcr_value)

# =========================
# TABLE
# =========================
st.subheader("📊 Option Chain Data")

st.dataframe(df, use_container_width=True)

# =========================
# ATM ZONE
# =========================
st.subheader("🚀 ATM Zone")

atm_df = df[df["Strike"] == atm]
st.dataframe(atm_df, use_container_width=True)

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
    st.success("🟢 PUT Dominance (Bearish Bias)")
else:
    st.warning("🔴 CALL Dominance (Bullish Bias)")

st.success("✅ NEW SEPARATE VERSION RUNNING SUCCESSFULLY")
