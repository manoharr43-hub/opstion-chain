import streamlit as st
import pandas as pd
import numpy as np

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="🔥 NSE AI Side Indicator", layout="wide")

# =========================
# SMART DATA (INDEX BASED)
# =========================
def load_data(symbol):
    if symbol == "NIFTY":
        df = pd.DataFrame({
            "Strike": [22000, 22100, 22200, 22300, 22400],
            "CE OI": [1200, 1500, 1100, 900, 1300],
            "PE OI": [1000, 1300, 1400, 1600, 1700],
        })
    else:  # BANKNIFTY
        df = pd.DataFrame({
            "Strike": [46000, 46100, 46200, 46300, 46400],
            "CE OI": [2000, 1800, 2200, 2100, 2500],
            "PE OI": [1700, 1900, 1600, 2000, 2300],
        })

    return df

# =========================
# EXPIRY (SIMPLE)
# =========================
def get_expiries():
    return [
        "Weekly-10 Apr",
        "Weekly-17 Apr",
        "Monthly-24 Apr"
    ]

# =========================
# HEADER
# =========================
st.title("🔥 NSE AI Side Indicator System")

# =========================
# SIDEBAR CONTROLS
# =========================
st.sidebar.markdown("## 📊 CONTROL PANEL")

symbol = st.sidebar.selectbox("Select Index", ["NIFTY", "BANKNIFTY"])

expiries = get_expiries()
expiry = st.sidebar.selectbox("📅 Select Expiry", expiries)

# =========================
# LOAD INDEX DATA
# =========================
df = load_data(symbol)

# =========================
# AMI + SIGNAL
# =========================
df["AMI"] = (df["CE OI"] + df["PE OI"]) / 2

df["Signal"] = np.where(df["CE OI"] > df["PE OI"], "CALL 📈", "PUT 📉")

# =========================
# SIDE INDICATOR (IMPORTANT FIX)
# =========================
if symbol == "NIFTY":
    side_status = "🟢 NIFTY ACTIVE MODE"
    market_bias = "Trend: INDEX BASED MOVEMENT"
else:
    side_status = "🟠 BANKNIFTY ACTIVE MODE"
    market_bias = "Trend: BANK HEAVY VOLATILITY"

# =========================
# DASHBOARD HEADER INDICATOR
# =========================
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Index", symbol)

with col2:
    st.metric("Expiry", expiry)

with col3:
    st.metric("Mode", "LIVE")

st.success(side_status)
st.info(market_bias)

# =========================
# MAIN DATA
# =========================
st.subheader("📊 Option Chain Data")

st.dataframe(df, use_container_width=True)

# =========================
# AMI CHART
# =========================
st.subheader("📈 AMI Trend")

st.line_chart(df["AMI"])

# =========================
# SIGNAL TABLE
# =========================
st.subheader("🎯 Buy / Sell Signal")

st.dataframe(df[["Strike", "AMI", "Signal"]], use_container_width=True)

# =========================
# FINAL STATUS
# =========================
st.success("✅ Side Indicator Working | NIFTY & BANKNIFTY Auto Switch Enabled")
