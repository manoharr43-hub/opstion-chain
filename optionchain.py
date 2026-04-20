import streamlit as st
import pandas as pd
import requests
import time

st.set_page_config(page_title="Option Chain PRO", layout="wide")
st.title("📊 Option Chain (Stable Version)")

# =============================
# MULTI SOURCE FETCH
# =============================
def fetch_data(symbol):

    urls = [
        # Source 1
        f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}",

        # Source 2 (backup)
        f"https://query1.finance.yahoo.com/v7/finance/options/{'^NSEI' if symbol=='NIFTY' else '^NSEBANK'}"
    ]

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    for url in urls:
        try:
            session = requests.Session()
            session.get("https://www.google.com", headers=headers)

            res = session.get(url, headers=headers, timeout=5)

            if res.status_code == 200:
                return res.json()
        except:
            continue

    return None


# =============================
# UI
# =============================
symbol = st.selectbox("Select Index", ["NIFTY", "BANKNIFTY"])

data = fetch_data(symbol)

if not data:
    st.error("❌ All data sources failed (Cloud restriction)")
    st.stop()

rows = []

# =============================
# TRY NSE FORMAT
# =============================
try:
    records = data["records"]["data"]
    spot = data["records"]["underlyingValue"]

    for item in records[:20]:
        rows.append({
            "Strike": item.get("strikePrice"),
            "CE LTP": item.get("CE", {}).get("lastPrice", "-"),
            "PE LTP": item.get("PE", {}).get("lastPrice", "-"),
        })

except:
    # =============================
    # TRY YAHOO FORMAT
    # =============================
    try:
        result = data["optionChain"]["result"][0]
        spot = result["quote"]["regularMarketPrice"]

        calls = result["options"][0]["calls"]
        puts = result["options"][0]["puts"]

        for i in range(min(len(calls), 20)):
            rows.append({
                "Strike": calls[i]["strike"],
                "CE LTP": calls[i]["lastPrice"],
                "PE LTP": puts[i]["lastPrice"]
            })

    except:
        st.error("❌ Data parse failed")
        st.stop()

# =============================
# DISPLAY
# =============================
st.metric(f"{symbol} Spot", f"₹{spot}")

df = pd.DataFrame(rows)
st.dataframe(df, use_container_width=True)

# =============================
# AUTO REFRESH
# =============================
st.caption("🔄 Auto refresh every 15 sec")
time.sleep(15)
st.rerun()
