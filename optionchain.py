import streamlit as st
import pandas as pd
import numpy as np

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="🔥 NEW NSE PRO SCANNER", layout="wide")

# =========================
# SAFE DATA MODULE (NEW)
# =========================
def get_option_chain(index):
    data = {
        "NIFTY": pd.DataFrame({
            "Strike": [22000, 22100, 22200, 22300, 22400],
            "CE_OI": [1200, 1800, 1100, 900, 1300],
            "PE_OI": [1000, 1300, 1400, 1600, 1700],
        }),

        "BANKNIFTY": pd.DataFrame({
            "Strike": [46000, 46100, 46200, 46300, 46400],
            "CE_OI": [2000, 2800, 2200, 2100, 2500],
            "PE_OI": [1700, 1900, 1600, 2000, 2300],
        }),

        "FINNIFTY": pd.DataFrame({
            "Strike": [20000, 20100, 20200, 20300, 20400],
            "CE_OI": [1500, 1900, 1700, 2100, 1600],
            "PE_OI": [1400, 1600, 1800, 2000, 2200],
        })
    }
    return data.get(index, pd.DataFrame())

# =========================
# TREND ENGINE (NEW)
# =========================
def trend_engine(df):
    ce = df["CE_OI"].sum()
    pe = df["PE_OI"].sum()

    if ce > pe * 1.1:
        return "🟢 BULLISH"
    elif pe > ce * 1.1:
        return "🔴 BEARISH"
    return "🟡 SIDEWAYS"

# =========================
# ATM FINDER
# =========================
def get_atm(df):
    return df.iloc[len(df)//2]["Strike"]

# =========================
# ATM MOVEMENT ZONE
# =========================
def atm_zone(df, atm):
    df["TOTAL_OI"] = df["CE_OI"] + df["PE_OI"]
    return df.iloc[(df["Strike"] - atm).abs().argsort()[:3]]

# =========================
# PCR CALC
# =========================
def pcr(df):
    return round(df["PE_OI"].sum() / df["CE_OI"].sum(), 2)

# =========================
# VIX (SIMULATED SAFE)
# =========================
def vix():
    return round(np.random.uniform(11, 18), 2)

# =========================
# SIDEBAR UI
# =========================
st.sidebar.title("📊 CONTROL PANEL (NEW)")

index = st.sidebar.selectbox(
    "Select Index",
    ["NIFTY", "BANKNIFTY", "FINNIFTY"]
)

expiry = st.sidebar.selectbox(
    "Select Expiry",
    ["Weekly", "Monthly"]
)

# =========================
# LOAD DATA
# =========================
df = get_option_chain(index)

if df.empty:
    st.error("❌ No Data Found")
    st.stop()

# =========================
# CALCULATIONS
# =========================
df["TOTAL_OI"] = df["CE_OI"] + df["PE_OI"]

trend = trend_engine(df)
atm = get_atm(df)
zone = atm_zone(df, atm)
pcr_value = pcr(df)
vix_value = vix()

# =========================
# HEADER
# =========================
st.title("🔥 NEW NSE PRO SCANNER (CLEAN VERSION)")
st.caption("Fully Separated from Old Code | Safe Upgrade Version")

# =========================
# SIDEBAR REPORT
# =========================
st.sidebar.markdown("---")
st.sidebar.success(f"Index: {index}")
st.sidebar.info(f"Expiry: {expiry}")
st.sidebar.warning(f"ATM: {atm}")
st.sidebar.error(f"PCR: {pcr_value}")
st.sidebar.info(f"VIX: {vix_value}")
st.sidebar.success(f"Trend: {trend}")

# =========================
# TOP METRICS
# =========================
c1, c2, c3, c4 = st.columns(4)

c1.metric("Index", index)
c2.metric("Trend", trend)
c3.metric("ATM Strike", atm)
c4.metric("PCR", pcr_value)

# =========================
# TABLE
# =========================
st.subheader("📊 Option Chain Data")

st.dataframe(df, use_container_width=True)

# =========================
# ATM ZONE REPORT
# =========================
st.subheader("🚀 ATM Near Strong Movement Zone")

st.dataframe(zone, use_container_width=True)

# =========================
# REPORT
# =========================
st.subheader("📌 Market Report")

st.write(f"""
✔ Index: {index}  
✔ Expiry: {expiry}  
✔ ATM Strike: {atm}  
✔ PCR Ratio: {pcr_value}  
✔ India VIX: {vix_value}  
✔ Trend: {trend}  
""")

# =========================
# SIGNAL LOGIC
# =========================
if pcr_value > 1:
    st.success("🟢 Bearish Pressure (PUT dominance)")
else:
    st.warning("🔴 Bullish Pressure (CALL dominance)")

st.success("✅ NEW VERSION RUNNING SUCCESSFULLY (OLD CODE SAFE)")
