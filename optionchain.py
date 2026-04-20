import streamlit as st
import pandas as pd
import requests
import time

st.set_page_config(page_title="Option Chain PRO", layout="wide")
st.title("📊 NSE Option Chain (Working Version)")

# =============================
# FETCH DATA (UNBLOCKED SOURCE)
# =============================
@st.cache_data(ttl=20)
def get_data(symbol):

    if symbol == "NIFTY":
        url = "https://cdn.jsdelivr.net/gh/zerodha/nse-option-chain-data@latest/nifty.json"
    else:
        url = "https://cdn.jsdelivr.net/gh/zerodha/nse-option-chain-data@latest/banknifty.json"

    try:
        res = requests.get(url, timeout=5)
        return res.json()
    except:
        return None


# =============================
# UI
# =============================
symbol = st.selectbox("Select Index", ["NIFTY", "BANKNIFTY"])

data = get_data(symbol)

if not data:
    st.error("❌ Data fetch failed")
    st.stop()

spot = data.get("underlyingValue", 0)
st.metric(f"{symbol} Spot", f"₹{spot}")

rows = []

# =============================
# BUILD TABLE
# =============================
for item in data.get("data", [])[:25]:

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
