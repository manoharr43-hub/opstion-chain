import streamlit as st
import pandas as pd
import numpy as np

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="🔥 CE vs PE BIG MOVE ZONE", layout="wide")

# =========================
# LTP
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
        "CE_OI": np.random.randint(1000, 4500, len(strikes)),
        "PE_OI": np.random.randint(1000, 4500, len(strikes)),
    })

# =========================
# ATM FINDER
# =========================
def get_atm(df, ltp):
    return min(df["Strike"], key=lambda x: abs(x - ltp))

# =========================
# CE vs PE PRESSURE ZONE
# =========================
def ce_pe_zone(df, atm):
    df["TOTAL_OI"] = df["CE_OI"] + df["PE_OI"]
    df["DIST"] = abs(df["Strike"] - atm)

    # CE dominance
    df["CE_PRESSURE"] = df["CE_OI"] / (df["PE_OI"] + 1)

    # PE dominance
    df["PE_PRESSURE"] = df["PE_OI"] / (df["CE_OI"] + 1)

    ce_zone = df.sort_values(["CE_PRESSURE", "DIST"], ascending=[False, True]).head(3)
    pe_zone = df.sort_values(["PE_PRESSURE", "DIST"], ascending=[False, True]).head(3)

    return ce_zone, pe_zone

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
# VIX
# =========================
def vix():
    return round(np.random.uniform(11, 18), 2)

# =========================
# SIDEBAR
# =========================
st.sidebar.title("📊 CE vs PE ZONE PANEL")

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

ce_zone, pe_zone = ce_pe_zone(df, atm)

trend_value = trend(df)
pcr_value = pcr(df)
vix_value = vix()

# =========================
# HEADER
# =========================
st.title("🔥 CE vs PE BIG MOVE ZONE SCANNER")
st.caption("Separate Call & Put Pressure Detection (ATM Based)")

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
# FULL TABLE
# =========================
st.subheader("📊 Option Chain")

st.dataframe(df, use_container_width=True)

# =========================
# CE BIG MOVE ZONE
# =========================
st.subheader("🚀 CE (CALL) BIG MOVE ZONE")

st.dataframe(ce_zone, use_container_width=True)

# =========================
# PE BIG MOVE ZONE
# =========================
st.subheader("📉 PE (PUT) BIG MOVE ZONE")

st.dataframe(pe_zone, use_container_width=True)

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
✔ Trend: {trend_value}  
""")

# =========================
# SIGNAL
# =========================
if ce_zone["CE_PRESSURE"].mean() > pe_zone["PE_PRESSURE"].mean():
    st.success("🟢 CALL SIDE STRONG (CE DOMINANCE)")
else:
    st.warning("🔴 PUT SIDE STRONG (PE DOMINANCE)")

st.success("✅ CE vs PE BIG MOVE ZONE READY (OLD CODE SAFE)")
