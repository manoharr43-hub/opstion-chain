import streamlit as st
import pandas as pd
import numpy as np

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="🔥 NSE MULTI INDEX SCANNER", layout="wide")

# =========================
# INDEX DATA
# =========================
def load_data(index):
    if index == "NIFTY":
        return pd.DataFrame({
            "Strike": [22000, 22100, 22200, 22300, 22400],
            "CE OI": [1200, 1800, 1100, 900, 1300],
            "PE OI": [1000, 1300, 1400, 1600, 1700],
        })

    elif index == "BANKNIFTY":
        return pd.DataFrame({
            "Strike": [46000, 46100, 46200, 46300, 46400],
            "CE OI": [2000, 2800, 2200, 2100, 2500],
            "PE OI": [1700, 1900, 1600, 2000, 2300],
        })

    elif index == "MIDCPNIFTY":
        return pd.DataFrame({
            "Strike": [12000, 12100, 12200, 12300, 12400],
            "CE OI": [900, 1100, 1500, 1200, 1400],
            "PE OI": [800, 1000, 1200, 1600, 1800],
        })

    else:
        return pd.DataFrame()

# =========================
# MOVEMENT CALCULATION
# =========================
def get_movement(df):
    df["Total OI"] = df["CE OI"] + df["PE OI"]
    return df

def strongest_strike(df):
    max_row = df.loc[df["Total OI"].idxmax()]
    return max_row["Strike"], max_row["Total OI"]

def index_strength(df):
    return df["Total OI"].sum()

# =========================
# HEADER
# =========================
st.title("🔥 ULTRA NSE MULTI INDEX MOVEMENT SCANNER")

# =========================
# LEFT SIDE PANEL
# =========================
st.sidebar.markdown("## 📊 INDEX SELECTION")

indices = ["NIFTY", "BANKNIFTY", "MIDCPNIFTY"]

selected_index = st.sidebar.selectbox("Select Index", indices)

# =========================
# LOAD DATA
# =========================
df = load_data(selected_index)

if df.empty:
    st.error("No data available")
    st.stop()

df = get_movement(df)

# =========================
# STRONG MOVEMENT LOGIC
# =========================
strong_strike, strong_value = strongest_strike(df)
total_strength = index_strength(df)

# =========================
# SIDE PANEL REPORT
# =========================
st.sidebar.markdown("---")
st.sidebar.subheader("📌 Market Strength")

st.sidebar.success(f"Index: {selected_index}")
st.sidebar.info(f"Total Strength: {total_strength}")
st.sidebar.warning(f"Strong Strike: {strong_strike}")

# =========================
# MAIN DASHBOARD
# =========================
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Index", selected_index)

with col2:
    st.metric("Strong Strike", strong_strike)

with col3:
    st.metric("Strength", total_strength)

# =========================
# TABLE
# =========================
st.subheader("📊 Option Chain Movement Data")

st.dataframe(df, use_container_width=True)

# =========================
# STRIKE MOVEMENT ANALYSIS
# =========================
st.subheader("🚀 Highest Strike Movement")

st.success(f"🔥 Strongest Strike: {strong_strike} | Value: {strong_value}")

# =========================
# MULTI INDEX COMPARISON (BONUS)
# =========================
st.subheader("📊 Index Comparison")

compare_data = pd.DataFrame({
    "Index": ["NIFTY", "BANKNIFTY", "MIDCPNIFTY"],
    "Strength": [
        index_strength(load_data("NIFTY")),
        index_strength(load_data("BANKNIFTY")),
        index_strength(load_data("MIDCPNIFTY")),
    ]
})

st.bar_chart(compare_data.set_index("Index"))

# =========================
# FINAL STATUS
# =========================
st.success("🔥 MULTI INDEX + STRIKE MOVEMENT SYSTEM ACTIVE")
