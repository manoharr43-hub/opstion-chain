import streamlit as st
import pandas as pd
import numpy as np

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="🔥 ULTRA NSE AI TRADING", layout="wide")

# =========================
# DATA (INDEX BASED)
# =========================
def load_data(index):
    if index == "NIFTY":
        return pd.DataFrame({
            "Strike": [22000, 22100, 22200, 22300, 22400],
            "CE OI": [1200, 1500, 1100, 900, 1300],
            "PE OI": [1000, 1300, 1400, 1600, 1700],
        })
    else:
        return pd.DataFrame({
            "Strike": [46000, 46100, 46200, 46300, 46400],
            "CE OI": [2000, 1800, 2200, 2100, 2500],
            "PE OI": [1700, 1900, 1600, 2000, 2300],
        })

# =========================
# EXPIRY
# =========================
def get_expiries():
    return ["Weekly", "Monthly"]

# =========================
# PCR + VIX
# =========================
def get_pcr(index):
    return 1.15 if index == "NIFTY" else 0.95

def get_vix():
    return 13.8

# =========================
# TREND SYSTEM
# =========================
def get_trend(df):
    ce = df["CE OI"].sum()
    pe = df["PE OI"].sum()

    if ce > pe * 1.1:
        return "🟢 BULLISH"
    elif pe > ce * 1.1:
        return "🔴 BEARISH"
    else:
        return "🟡 SIDEWAYS"

# =========================
# AI SIGNAL ENGINE
# =========================
def smart_signal(ce, pe, pcr, vix):
    ratio = ce / (pe + 1)

    if ratio > 1.2 and pcr > 1 and vix < 15:
        return "🟢 STRONG BUY (BULLISH BREAKOUT)"
    elif ratio < 0.8 and pcr < 1 and vix < 15:
        return "🔴 STRONG SELL (BEARISH BREAKDOWN)"
    elif vix > 18:
        return "⚠️ HIGH VOLATILITY - NO TRADE"
    else:
        return "🟡 SIDEWAYS - WAIT"

# =========================
# HEADER
# =========================
st.title("🔥 ULTRA NSE AI TRADING DASHBOARD")
st.caption("Next Level Smart Money + AI Signal + Trend Engine")

# =========================
# SIDEBAR
# =========================
st.sidebar.markdown("## 📊 CONTROL PANEL")

index = st.sidebar.selectbox("Select Index", ["NIFTY", "MID NIFTY"])
expiry = st.sidebar.selectbox("Select Expiry", get_expiries())

# =========================
# LOAD DATA
# =========================
df = load_data(index)

df["AMI"] = (df["CE OI"] + df["PE OI"]) / 2

# =========================
# CALCULATIONS
# =========================
ce_total = df["CE OI"].sum()
pe_total = df["PE OI"].sum()

pcr = get_pcr(index)
vix = get_vix()

trend = get_trend(df)
signal = smart_signal(ce_total, pe_total, pcr, vix)

# =========================
# HEADER METRICS
# =========================
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Index", index)

with col2:
    st.metric("Trend", trend)

with col3:
    st.metric("Signal", "AI ACTIVE")

# =========================
# SIDE STATUS PANEL
# =========================
st.sidebar.markdown("---")
st.sidebar.success(f"Index: {index}")
st.sidebar.info(f"Trend: {trend}")
st.sidebar.warning(f"Expiry: {expiry}")

# =========================
# MAIN DATA
# =========================
st.subheader("📊 Option Chain Data")

st.dataframe(df, use_container_width=True)

# =========================
# AMI CHART
# =========================
st.subheader("📈 AMI Movement")

st.line_chart(df["AMI"])

# =========================
# MARKET REPORT
# =========================
st.subheader("📊 Market Intelligence Report")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("CE Total", ce_total)

with col2:
    st.metric("PE Total", pe_total)

with col3:
    st.metric("PCR", pcr)

st.metric("India VIX", vix)

# =========================
# AI SIGNAL PANEL
# =========================
st.markdown("---")
st.subheader("🚀 AI Trade Signal Engine")

st.success(signal)

# =========================
# ALERT SYSTEM
# =========================
if "STRONG BUY" in signal:
    st.balloons()

if "STRONG SELL" in signal:
    st.error("⚠️ SELL PRESSURE DETECTED")

# =========================
# FOOTER
# =========================
st.markdown("---")
st.caption("🔥 ULTRA VERSION | AI SIGNAL + PCR + VIX + TREND | NO ERROR SYSTEM")
