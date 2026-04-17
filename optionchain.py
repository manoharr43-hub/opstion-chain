import streamlit as st
import requests
import pandas as pd
from datetime import datetime

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
    if "records" in data and "data" in data["records"]:
        return data["records"]["data"]
    else:
        return []

# =============================
# USER INPUT
# =============================
symbol = st.sidebar.selectbox("Select Index", ["NIFTY", "BANKNIFTY"])

# =============================
# FETCH DATA
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

    # =============================
    # DISPLAY TABLES
    # =============================
    st.subheader(f"📈 {symbol} CALLS")
    st.dataframe(call_df.style.applymap(lambda v: "background-color:lightgreen" if isinstance(v, (int,float)) and v>0 else ""))

    st.subheader(f"📉 {symbol} PUTS")
    st.dataframe(put_df.style.applymap(lambda v: "background-color:salmon" if isinstance(v, (int,float)) and v<0 else ""))

    # =============================
    # PCR CALCULATION
    # =============================
    total_calls = call_df["OI"].sum()
    total_puts = put_df["OI"].sum()
    pcr = round(total_puts / total_calls, 2) if total_calls != 0 else 0
    st.metric(label=f"{symbol} PCR (Put/Call Ratio)", value=pcr)

    # =============================
    # INTRADAY SIGNALS (Mock Example)
    # =============================
    st.subheader(f"⏱️ Intraday Signals - {symbol} (15 mins)")
    intraday_data = [
        ["12:45", 90987130, 1.76, "BUY"],
        ["12:30", 88337015, 1.76, "BUY"],
        ["12:15", 89207755, 1.79, "BUY"],
        ["12:00", 97324760, 1.99, "BUY"],
        ["11:45", 73244080, 1.63, "BUY"],
    ]
    intraday_df = pd.DataFrame(intraday_data, columns=["Time", "Diff", "PCR", "Signal"])
    st.dataframe(intraday_df.style.applymap(
        lambda v: "background-color:lightgreen" if v=="BUY" else "background-color:salmon",
        subset=["Signal"]
    ))

except Exception as e:
    st.error(f"Error fetching data: {e}")
