import streamlit as st
import pandas as pd
import requests
import time

st.set_page_config(page_title="NSE Option Chain", layout="wide")
st.title("📊 NSE Option Chain LIVE")

# =============================
# FETCH NSE DATA (RETRY LOGIC)
# =============================
@st.cache_data(ttl=20)
def get_data(symbol):

    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.nseindia.com/option-chain",
        "Connection": "keep-alive"
    }

    session = requests.Session()

    try:
        # Step 1: Get cookies
        session.get("https://www.nseindia.com", headers=headers, timeout=5)

        # Step 2: Fetch data
        response = session.get(url, headers=headers, timeout=5)

        if response.status_code == 200:
            return response.json()
        else:
            return None

    except:
        return None


# =============================
# UI
# =============================
symbol = st.selectbox("Select Index", ["NIFTY", "BANKNIFTY"])

data = get_data(symbol)

# =============================
# FAIL SAFE (IMPORTANT)
# =============================
if not data or "records" not in data:
    st.warning("⚠️ NSE blocked request. Retrying...")

    time.sleep(2)
    data = get_data(symbol)

if not data or "records" not in data:
    st.error("❌ NSE data blocked (Cloud issue). Try refresh.")
    st.stop()

# =============================
# DATA PROCESS
# =============================
records = data["records"]["data"]
spot = data["records"]["underlyingValue"]

st.metric(f"{symbol} Spot", f"₹{spot}")

rows = []

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
