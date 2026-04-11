import streamlit as st
import pandas as pd
import requests
import time

# =========================
# PAGE SETUP
# =========================
st.set_page_config(page_title="HYBRID NSE AI SCANNER", layout="wide")
st.title("🔥 MANOHAR HYBRID NSE OPTION SCANNER")

# =========================
# NSE PRIMARY FETCH
# =========================
def get_nse_data(symbol):
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"

    session = requests.Session()

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.nseindia.com/"
    }

    try:
        session.get("https://www.nseindia.com", headers=headers, timeout=5)
        response = session.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            return response.json()
        else:
            return None
    except:
        return None

# =========================
# NSEPYTHON BACKUP
# =========================
def get_backup_data(symbol):
    try:
        from nsepython import nse_optionchain_scrapper
        return nse_optionchain_scrapper(symbol)
    except:
        return None

# =========================
# HYBRID FETCH
# =========================
def fetch_data(symbol):
    for i in range(3):
        data = get_nse_data(symbol)
        if data:
            return data
        time.sleep(2)

    st.warning("⚠️ Switching to Backup Data...")
    return get_backup_data(symbol)

# =========================
# SELECT INDEX
# =========================
symbol = st.sidebar.selectbox("Select Index", ["NIFTY", "BANKNIFTY"])

raw = fetch_data(symbol)

if raw is None:
    st.error("❌ Data Load Failed Completely")
    st.stop()

# =========================
