import streamlit as st
import pandas as pd
import requests

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(layout="wide")
st.title("📊 NSE Option Screener")

# ==========================================
# USER INPUTS
# ==========================================
symbol = st.selectbox("Select Index", ["NIFTY", "BANKNIFTY"])
pcr_threshold = st.slider("PCR Threshold", 0.5, 2.0, 1.0)
volume_filter = st.number_input("Min Volume", value=1000)

# ==========================================
# NSE API CALL
# ==========================================
def fetch_option_chain(symbol):
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
    headers = {"User-Agent": "Mozilla/5.0"}
    session = requests.Session()
    response = session.get(url, headers=headers)
    data = response.json()
    return data["records"]["data"]

option_data = fetch_option_chain(symbol)

# ==========================================
# DATA PROCESSING
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
# FILTERING
# ==========================================
filtered = df[(df["PCR"] >= pcr_threshold) & (df["Volume"] >= volume_filter)]

# ==========================================
# DISPLAY
# ==========================================
st.subheader(f"{symbol} Option Screener Results")
st.dataframe(filtered, use_container_width=True)

# ==========================================
# SENTIMENT
# ==========================================
avg_pcr = df["PCR"].mean()
if avg_pcr > 1:
    st.success(f"Market Sentiment: Bullish (PCR={avg_pcr:.2f})")
else:
    st.error(f"Market Sentiment: Bearish (PCR={avg_pcr:.2f})")
