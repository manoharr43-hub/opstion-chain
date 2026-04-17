import streamlit as st
import requests
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

# =============================
# CONFIG
# =============================
st.set_page_config(page_title="🔥 NSE OPTION CHAIN", layout="wide")
st.title("📊 NSE Option Chain + Intraday Dashboard")

# =============================
# FUNCTION: Fetch Option Chain
# =============================
def get_option_chain(symbol="NIFTY"):
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Referer": "https://www.nseindia.com/option-chain"
    }
    session = requests.Session()
    # First request to NSE homepage for cookies
    session.get("https://www.nseindia.com", headers=headers)
    response = session.get(url, headers=headers)
    data = response.json()

    # Safe access: check both records and filtered
    if "records" in data and "data" in data["records"]:
        return data["records"]["data"]
    elif "filtered" in data and "data" in data["filtered"]:
        return data["filtered"]["data"]
    else:
        return []

# =============================
# USER INPUT
# =============================
symbol = st.sidebar.selectbox("Select Index", ["NIFTY", "BANKNIFTY"])

# =============================
# OPTION CHAIN DATA
# =============================
try:
    option_data = get_option_chain(symbol)
    calls, puts = [], []

    for row in option_data:
        ce = row.get("CE")
        pe = row.get("PE")
        if ce:
            calls.append([ce["strikePrice"], ce["openInterest"], ce["changeinOpenInterest"], ce["lastPrice"]])
        if pe:
            puts.append([pe["strikePrice"], pe["openInterest"], pe["changeinOpenInterest"], pe["lastPrice"]])

    call_df = pd.DataFrame(calls, columns=["Strike", "OI", "Chg OI", "LTP"])
    put_df = pd.DataFrame(puts, columns=["Strike", "OI", "Chg OI", "LTP"])

    st.subheader(f"📈 {symbol} CALLS")
    if not call_df.empty:
        st.dataframe(call_df, width="stretch")
    else:
        st.warning("No CALL data available (Market closed or API empty).")

    st.subheader(f"📉 {symbol} PUTS")
    if not put
