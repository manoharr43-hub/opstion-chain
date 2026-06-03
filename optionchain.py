import streamlit as st
import pandas as pd
from nsepython import nse_optionchain_scrapper

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(layout="wide")
st.title("🧠 NSE Option Screener Debug Viewer")

# ==========================================
# USER INPUTS
# ==========================================
symbol = st.selectbox("Select Index", ["NIFTY", "BANKNIFTY"])

# ==========================================
# FETCH RAW DATA
# ==========================================
try:
    data = nse_optionchain_scrapper(symbol)
    st.subheader("🔍 Raw JSON Response from NSE API")
    st.json(data)  # Show full JSON structure
except Exception as e:
    st.error(f"❌ Error fetching data: {e}")
    st.stop()

# ==========================================
# SAFE ACCESS LOGIC
# ==========================================
if "records" in data and "data" in data["records"]:
    option_data = data["records"]["data"]
elif "filtered" in data and "data" in data["filtered"]:
    option_data = data["filtered"]["data"]
else:
    st.warning("⚠️ Unexpected JSON format — check raw data above.")
    st.stop()

# ==========================================
# PROCESS DATA
# ==========================================
rows = []
for item in option_data:
    strike = item["strikePrice"]
    ce_oi = item["CE"]["openInterest"] if "CE" in item else 0
    pe_oi = item["PE"]["openInterest"] if "PE" in item else 0
    ce_vol = item["CE"]["totalTradedVolume"] if "CE" in item else 0
    pe_vol = item["PE"]["totalTradedVolume"] if "PE" in item else 0
    rows.append([strike, ce_oi, pe_oi, ce_vol + pe_vol])

df = pd.DataFrame(rows, columns=["Strike", "CE_OI", "PE_OI", "Volume"])
df["PCR"] = df["PE_OI"] / df["CE_OI"].replace(0, 1)

# ==========================================
# DISPLAY TABLE
# ==========================================
st.subheader(f"{symbol} Option Chain Data")
st.dataframe(df, use_container_width=True)
