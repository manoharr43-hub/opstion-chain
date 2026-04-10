import streamlit as st
import pandas as pd
import numpy as np

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="🔥 NSE Trend Scanner", layout="wide")

# =========================
# DATA (NIFTY / MID NIFTY)
# =========================
def load_data(index):
    if index == "NIFTY":
        return pd.DataFrame({
            "Strike": [22000, 22100, 22200, 22300],
            "CE OI": [1200, 1500, 1100, 900],
            "PE OI": [1000, 1300, 1400, 1600],
        })

    else:  # MID NIFTY
        return pd.DataFrame({
            "Strike": [24000, 24100, 24200, 24300],
            "CE OI": [900, 1100, 1300, 1200],
            "PE OI": [800, 1000, 1500, 1700],
        })

# =========================
# TREND CALCULATION
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
# HEADER
# =========================
st.title("🔥 NSE AI Trend Scanner (NIFTY + MID NIFTY)")

# =========================
# LEFT SIDEBAR
# =========================
st.sidebar.markdown("## 📊 INDEX PANEL")

index = st.sidebar.selectbox(
    "Select Index",
    ["NIFTY", "MID NIFTY"]
)

expiry = st.sidebar.selectbox(
    "📅 Expiry",
    ["Weekly", "Monthly"]
)

# =========================
# LOAD DATA
# =========================
df = load_data(index)

df["AMI"] = (df["CE OI"] + df["PE OI"]) / 2

# =========================
# TREND ANALYSIS
# =========================
trend = get_trend(df)

# =========================
# LEFT SIDE STATUS
# =========================
st.sidebar.markdown("---")
st.sidebar.subheader("📌 Market Status")

st.sidebar.success(f"Index: {index}")
st.sidebar.info(f"Trend: {trend}")
st.sidebar.warning(f"Expiry: {expiry}")

# =========================
# MAIN DASHBOARD
# =========================
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Index", index)

with col2:
    st.metric("Trend", trend)

with col3:
    st.metric("Status", "LIVE")

# =========================
# TABLE
# =========================
st.subheader("📊 Option Chain Data")

st.dataframe(df, use_container_width=True)

# =========================
# AMI CHART
# =========================
st.subheader("📈 AMI Movement")

st.line_chart(df["AMI"])

# =========================
# TREND REPORT (BOTTOM)
# =========================
st.subheader("📌 Trend Report")

if trend == "🟢 BULLISH":
    st.success("Market is STRONG BUYING pressure 📈")
elif trend == "🔴 BEARISH":
    st.error("Market is STRONG SELLING pressure 📉")
else:
    st.warning("Market is SIDEWAYS (no clear trend) ↔️")

# =========================
# FINAL STATUS
# =========================
st.success("✅ NIFTY + MID NIFTY + Trend System Active")
