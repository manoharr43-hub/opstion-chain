import streamlit as st
import requests
import time
import pandas as pd

st.set_page_config(layout="wide")
st.title("📊 NSE Option Screener with Retry")

def fetch_option_chain(symbol, retries=3, delay=5):
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.nseindia.com/"
    }
    session = requests.Session()

    for i in range(retries):
        try:
            response = session.get(url, headers=headers, timeout=10)
            if response.headers.get("Content-Type") == "application/json":
                data = response.json()
                return data["records"]["data"]
            else:
                st.warning(f"⚠️ Attempt {i+1}: NSE returned non-JSON response")
        except Exception as e:
            st.warning(f"⚠️ Attempt {i+1} failed: {e}")
        time.sleep(delay)

    st.error("❌ All retries failed. NSE API blocked or returned invalid data.")
    return []

# ==========================================
# USER INPUTS
# ==========================================
symbol = st.selectbox("Select Index", ["NIFTY", "BANKNIFTY"])
pcr_threshold = st.slider("PCR Threshold", 0.5, 2.0, 1.0)
volume_filter = st.number_input("Min Volume", value=1000)

# ==========================================
# FETCH DATA
# ==========================================
option_data = fetch_option_chain(symbol)

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

filtered = df[(df["PCR"] >= pcr_threshold) & (df["Volume"] >= volume_filter)]

st.subheader(f"{symbol} Option Screener Results")
st.dataframe(filtered, use_container_width=True)

avg_pcr = df["PCR"].mean()
if avg_pcr > 1:
    st.success(f"Market Sentiment: Bullish (PCR={avg_pcr:.2f})")
else:
    st.error(f"Market Sentiment: Bearish (PCR={avg_pcr:.2f})")
