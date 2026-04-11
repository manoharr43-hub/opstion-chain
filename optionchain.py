import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

# ==========================================
# AUTO REFRESH (5 Minutes)
# ==========================================
st_autorefresh(interval=5 * 60 * 1000, key="smart_refresh")

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(page_title="SMART AI OPTION SCANNER", layout="wide")

st.title("🚀 MANOHAR SMART AI MARKET SCANNER")

# ==========================================
# REAL INDEX DATA (IMPROVED FETCHING)
# ==========================================
@st.cache_data(ttl=60) # 1 minute cache to prevent rapid API blocks
def get_live_index():
    symbols = {
        "NIFTY": "^NSEI",
        "BANKNIFTY": "^NSEBANK",
        "FINNIFTY": "^CNXFINANCE",
        "MIDCAPNIFTY": "^NSEMDCP50"
    }
    
    result = {}
    
    for name, symbol in symbols.items():
        try:
            # period="5d" usage to ensure data availability even on holidays
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="5d", interval="5m")
            
            if not data.empty and len(data) >= 2:
                last = data.iloc[-1]
                prev = data.iloc[-2]
                
                price = round(last["Close"], 2)
                change = round(price - prev["Close"], 2)
                # If volume is 0, setting a default for calculation
                volume = int(last["Volume"]) if last["Volume"] > 0 else 500000 
                
                result[name] = {"price": price, "chg": change, "vol": volume}
            else:
                # Fallback values if no data
                result[name] = {"price": 1.0, "chg": 0.0, "vol": 100000}
        except:
            result[name] = {"price": 1.0, "chg": 0.0, "vol": 100000}
    
    return result

idx_data = get_live_index()

# ==========================================
# DISPLAY INDEX METRICS
# ==========================================
c1, c2, c3, c4 = st.columns(4)

c1.metric("NIFTY", idx_data["NIFTY"]["price"], idx_data["NIFTY"]["chg"])
c2.metric("BANKNIFTY", idx_data["BANKNIFTY"]["price"], idx_data["BANKNIFTY"]["chg"])
c3.metric("FINNIFTY", idx_data["FINNIFTY"]["price"], idx_data["FINNIFTY"]["chg"])
c4.metric("MIDCAPNIFTY", idx_data["MIDCAPNIFTY"]["price"], idx_data["MIDCAPNIFTY"]["chg"])

st.divider()

# ==========================================
# SELECT INDEX
# ==========================================
selected_idx = st.sidebar.selectbox(
    "SELECT INDEX",
    ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCAPNIFTY"]
)

# Use current price or a placeholder
spot_price = idx_data[selected_idx]["price"]
base_volume = idx_data[selected_idx]["vol"]

# ==========================================
# SMART OPTION DATA GENERATOR (SAME LOGIC)
# ==========================================
def generate_smart_data(spot, volume):
    # If price is 1 (placeholder), don't show complex data
    if spot <= 10:
        return pd.DataFrame(), 1.0

    gap = 100 if spot > 30000 else 50
    stri
