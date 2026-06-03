import streamlit as st
import pandas as pd
from nsetools import Nse

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(layout="wide")
st.title("📊 NSE Option Screener (nsetools version)")

# ==========================================
# USER INPUTS
# ==========================================
symbol = st.selectbox("Select Index", ["NIFTY", "BANKNIFTY"])
pcr_threshold = st.slider("PCR Threshold", 0.5, 2.0, 1.0)
volume_filter = st.number_input("Min Volume", value=1000)

# ==========================================
# FETCH DATA USING NSETTOOLS
# ==========================================
nse = Nse()
try:
    quote = nse.get_quote(symbol)
    st.subheader("🔍 Raw Quote Data from NSE")
    st.json(quote)
except Exception as e:
    st.error(f"❌ Error fetching data: {e}")
    st.stop()

# ==========================================
# SAMPLE OPTION DATA (SIMULATION)
# ==========================================
# nsetools doesn't provide full option chain, so we simulate basic structure
data = {
    "Strike": [22000, 22100, 22200, 22300],
    "CE_OI": [12000, 15000, 18000, 20000],
    "PE_OI": [8000, 20000, 25000, 30000],
    "Volume": [500, 1200, 3000, 4500]
}
df = pd.DataFrame(data)
df["PCR"] = df["PE_OI"] / df["CE_OI"]

# ==========================================
# FILTERING
# ==========================================
filtered = df[(df["PCR"] >= pcr_threshold) & (df["Volume"] >= volume_filter)]

# ==========================================
# DISPLAY RESULTS
# ==========================================
st.subheader(f"{symbol} Option Screener Results")
st.dataframe(filtered, use_container_width=True)

avg_pcr = df["PCR"].mean()
if avg_pcr > 1:
    st.success(f"Market Sentiment: Bullish (PCR={avg_pcr:.2f})")
else:
    st.error(f"Market Sentiment: Bearish (PCR={avg_pcr:.2f})")
