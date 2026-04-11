import streamlit as st
import pandas as pd
import requests
from streamlit_autorefresh import st_autorefresh

# =========================
# AUTO REFRESH (1 Min)
# =========================
st_autorefresh(interval=60 * 1000, key="nse_refresh")

st.set_page_config(page_title="REAL NSE AI SCANNER", layout="wide")
st.title("🔥 REAL NSE OPTION CHAIN AI SCANNER")

# =========================
# NSE HEADERS (VERY IMPORTANT)
# =========================
headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br"
}

# =========================
# GET NSE DATA
# =========================
@st.cache_data(ttl=30)
def get_nse_data(symbol):
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
    
    session = requests.Session()
    session.get("https://www.nseindia.com", headers=headers)
    response = session.get(url, headers=headers)
    
    data = response.json()
    return data

# =========================
# SELECT INDEX
# =========================
symbol = st.sidebar.selectbox("Select Index", ["NIFTY", "BANKNIFTY"])

try:
    raw = get_nse_data(symbol)
    records = raw["records"]["data"]
    spot = raw["records"]["underlyingValue"]

    st.metric(f"{symbol} SPOT", spot)

    rows = []
    total_ce_oi = 0
    total_pe_oi = 0

    for item in records:
        strike = item["strikePrice"]
        
        ce = item.get("CE", {})
        pe = item.get("PE", {})
        
        ce_oi = ce.get("openInterest", 0)
        pe_oi = pe.get("openInterest", 0)
        
        ce_ltp = ce.get("lastPrice", 0)
        pe_ltp = pe.get("lastPrice", 0)

        total_ce_oi += ce_oi
        total_pe_oi += pe_oi

        rows.append({
            "Strike": strike,
            "CE_LTP": ce_ltp,
            "CE_OI": ce_oi,
            "PE_LTP": pe_ltp,
            "PE_OI": pe_oi
        })

    df =
