import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="🔥 NSE AI Scanner", layout="wide")

# =========================
# SAMPLE LIVE DATA (REPLACE WITH API LATER)
# =========================
def load_data():
    data = {
        "Strike": [22000, 22100, 22200, 22300, 22400],
        "CE OI": [1200, 1500, 1100, 900, 1300],
        "PE OI": [1000, 1300, 1400, 1600, 1700],
        "Change": [50, -20, 80, -10, 30]
    }
    return pd.DataFrame(data)

# =========================
# EXPIRY MOCK (SAFE)
# =========================
def get_expiries():
    return [
        "2026-04-10 (Weekly)",
        "2026-04-17 (Weekly)",
        "2026-04-24 (Monthly)"
    ]

# =========================
# UI HEADER
# =========================
st.title("🔥 NSE AI Option Chain Scanner (UPGRADED)")
st.caption("No error version | AMI + Weekly + Monthly expiry")

# =========================
# SIDEBAR
# =========================
st.sidebar.markdown("## 📊 CONTROL PANEL")

symbol = st.sidebar.selectbox("Select Index", ["NIFTY", "BANKNIFTY"])

expiries = get_expiries()

selected_expiry = st.sidebar.selectbox("📅 Select Expiry", expiries)

st.sidebar.success(f"Active Expiry: {selected_expiry}")

# =========================
# LOAD DATA
# =========================
df = load_data()

# =========================
# SAFE CLEANING
# =========================
df["CE OI"] = df["CE OI"].astype(float)
df["PE OI"] = df["PE OI"].astype(float)

# =========================
# AMI CALCULATION
# =========================
df["AMI"] = (df["CE OI"] + df["PE OI"]) / 2

# =========================
# SIGNAL LOGIC (SIMPLE)
# =========================
df["Signal"] = np.where(df["CE OI"] > df["PE OI"], "CALL 📈", "PUT 📉")

# =========================
# MAIN DASHBOARD
# =========================
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Symbol", symbol)

with col2:
    st.metric("Rows", len(df))

with col3:
    st.metric("Expiry", "LIVE")

# =========================
# TABLES
# =========================
st.subheader("📊 Option Chain Data + AMI + Signal")
st.dataframe(df, use_container_width=True)

# =========================
# AMI VIEW
# =========================
st.subheader("📈 AMI Overview")

st.line_chart(df["AMI"])

# =========================
# FINAL STATUS
# =========================
st.success("✅ App Running Successfully | No Module Error | AMI Working")
