import streamlit as st
import pandas as pd
import requests
import time

# =============================
# CONFIG
# =============================
st.set_page_config(page_title="NSE Option Chain", layout="wide")
st.title("📊 NSE Option Chain (FREE DATA)")

# =============================
# FETCH NSE DATA
# =============================
@st.cache_data(ttl=30)
def get_data():
    url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    session = requests.Session()
    session.get("https://www.nseindia.com", headers=headers)
    res = session.get(url, headers=headers)

    return res.json()

# =============================
# MAIN
# =============================
try:
    data = get_data()

    records = data["records"]["data"]
    spot = data["records"]["underlyingValue"]

    st.metric("NIFTY Spot", f"₹{spot}")

    rows = []

    for item in records[:20]:

        strike = item.get("strikePrice")

        ce = item.get("CE", {})
        pe = item.get("PE", {})

        rows.append({
            "Strike": strike,
            "CE LTP": ce.get("lastPrice", "-"),
            "PE LTP": pe.get("lastPrice", "-"),
            "CE OI": ce.get("openInterest", "-"),
            "PE OI": pe.get("openInterest", "-")
        })

    df = pd.DataFrame(rows)

    st.dataframe(df, use_container_width=True)

    st.caption("🔄 Auto refresh 10 sec")
    time.sleep(10)
    st.rerun()

except Exception as e:
    st.error(f"Error: {e}")
