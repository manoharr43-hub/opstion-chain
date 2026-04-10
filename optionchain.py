import streamlit as st
import pandas as pd
import numpy as np

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="Stable Option Chain AI", layout="wide")


# =========================
# DATA GENERATOR (SAFE)
# =========================
def generate_data(symbol):
    base = 22000 if symbol == "NIFTY" else 45000

    df = pd.DataFrame({
        "Strike Price": [base + i * 50 for i in range(20)],
        "CE OI": np.random.randint(500, 2000, 20),
        "PE OI": np.random.randint(500, 2000, 20),
    })

    return df


# =========================
# SESSION STATE INIT
# =========================
if "data_loaded" not in st.session_state:
    st.session_state.data_loaded = False

if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame()


# =========================
# UI
# =========================
st.title("🚀 ULTRA STABLE OPTION CHAIN (NO DISAPPEAR VERSION)")

symbol = st.selectbox("Select Index", ["NIFTY", "BANKNIFTY", "FINNIFTY"])

# =========================
# LOAD BUTTON
# =========================
if st.button("LOAD OPTION CHAIN"):
    st.session_state.data_loaded = True
    st.session_state.df = generate_data(symbol)


# =========================
# DISPLAY DATA (PERSISTENT)
# =========================
if st.session_state.data_loaded:

    df = st.session_state.df.copy()

    # SAFE CALCULATION
    df["OI Diff"] = df["PE OI"] - df["CE OI"]

    df["Trend"] = np.where(df["OI Diff"] > 0, "Bullish", "Bearish")

    st.success("✅ Data Loaded Successfully (Stable Mode)")

    # TABLE
    st.subheader("📊 Option Chain Data")
    st.dataframe(df, use_container_width=True)

    # CHART
    st.subheader("📈 OI Difference Heat")
    st.bar_chart(df["OI Diff"])

    # SUMMARY
    ce_total = df["CE OI"].sum()
    pe_total = df["PE OI"].sum()

    st.subheader("🧠 Market Summary")

    if pe_total > ce_total:
        st.markdown("### 📈 Bullish Market Bias")
    else:
        st.markdown("### 📉 Bearish Market Bias")

# =========================
# INFO
# =========================
st.info("⚠️ Educational Purpose Only - Stable Version Without NSE Blocking")
