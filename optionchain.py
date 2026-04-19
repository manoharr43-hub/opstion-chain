import streamlit as st
import requests
import pandas as pd
import time

# =============================
# CONFIG
# =============================
st.set_page_config(page_title="NSE Option Chain PRO", layout="wide")
st.title("📊 NSE Option Chain Live (High Speed)")

# =============================
# SESSION MANAGEMENT (Re-optimized)
# =============================
@st.cache_resource
def get_session():
    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
    }
    session.headers.update(headers)
    try:
        # Initial hit to get cookies
        session.get("https://www.nseindia.com", timeout=10)
    except:
        pass
    return session

# =============================
# DATA FETCHING WITH RETRIES
# =============================
@st.cache_data(ttl=30)  # 30 seconds refresh
def fetch_nse_data(symbol):
    session = get_session()
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
    
    # Retry mechanism (Error వస్తే 3 సార్లు ప్రయత్నిస్తుంది)
    for _ in range(3):
        try:
            response = session.get(url, timeout=15)
            if response.status_code == 200:
                return response.json()
            time.sleep(1) 
        except Exception as e:
            continue
    return None

# =============================
# SIDEBAR CONTROLS
# =============================
st.sidebar.header("Settings")
symbol = st.sidebar.selectbox("Select Index", ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY
