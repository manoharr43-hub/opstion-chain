import streamlit as st
import pandas as pd
import requests
import time

st.set_page_config(page_title="NSE Option Chain", layout="wide")
st.title("📊 NSE Option Chain LIVE")

# =============================
# FETCH DATA
# =============================
@st.cache_data(ttl=30)
def get_data(symbol="NIFTY"):

    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Referer": "https://www.nseindia.com/option-chain"
    }

    session = requests.Session()

    # IMPORTANT: first hit homepage to get cookies
    session.get("https://www.nseindia.com", headers=headers)

    res = session.get(url, headers=headers)

    try:
        data = res.json()
        return data
    except:
        return None


# =============================
# UI
# =============================
symbol = st.selectbox("Select Index", ["NIFTY", "BANKNIFTY"])

data = get_data(symbol)

if not data or "records" not in data:
    st.error("❌ NSE data fetch failed. Try again.")
    st.stop()

records = data["records"]["data"]
spot = data["records"]["underlyingValue"]

st.metric(f"{symbol} Spot", f"₹{spot}")

rows = []

# =============================
# BUILD TABLE
# =============================
for item in records[:25]:

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

# =============================
# AUTO REFRESH
# =============================
st.caption("🔄 Auto refresh every 10 sec")
time.sleep(10)
st.rerun()
