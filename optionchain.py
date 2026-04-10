import streamlit as st
import pandas as pd
import numpy as np
import requests
import time

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="🔥 NSE AI OPTION + STOCK SCANNER", layout="wide")

# =========================
# SESSION (NSE SAFE)
# =========================
headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "application/json,text/plain,*/*",
    "Referer": "https://www.nseindia.com"
}

session = requests.Session()
session.headers.update(headers)

# =========================
# INDEX LIST
# =========================
INDEX_LIST = [
    "NIFTY",
    "BANKNIFTY",
    "FINNIFTY",
    "MIDCPNIFTY",
    "NIFTYNXT50"
]

# =========================
# STOCK SYMBOL FIX
# =========================
def normalize_stock(symbol):
    symbol = symbol.upper().strip()

    common = {
        "RELIANCE": "RELIANCE.NS",
        "INFY": "INFY.NS",
        "TCS": "TCS.NS",
        "HDFCBANK": "HDFCBANK.NS",
        "ICICIBANK": "ICICIBANK.NS"
    }

    return common.get(symbol, symbol if symbol.endswith(".NS") else symbol + ".NS")

# =========================
# STOCK ANALYSIS
# =========================
def stock_analysis(symbol):
    try:
        symbol = normalize_stock(symbol)

        url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbol}"
        res = requests.get(url, timeout=5)

        if res.text.strip() == "":
            return None, None, "⚠ EMPTY RESPONSE"

        data = res.json()
        result = data.get("quoteResponse", {}).get("result", [])

        if not result:
            return None, None, "⚠ STOCK NOT FOUND"

        result = result[0]

        price = result.get("regularMarketPrice", 0)
        change = result.get("regularMarketChangePercent", 0)

        if change > 1:
            signal = "🟢 CALL SIDE STRONG"
        elif change < -1:
            signal = "🔴 PUT SIDE STRONG"
        else:
            signal = "🟡 SIDEWAYS"

        return price, change, signal

    except Exception as e:
        return None, None, f"⚠ ERROR: {str(e)}"

# =========================
# NSE OPTION CHAIN
# =========================
def fetch_option_chain(symbol):
    try:
        url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"

        session.get("https://www.nseindia.com", timeout=5)
        time.sleep(1)

        res = session.get(url, timeout=10)

        if res.text.strip() == "":
            return None

        data = res.json()
        records = data["records"]["data"]

        rows = []
        for i in records:
            strike = i.get("strikePrice")

            ce = i.get("CE", {})
            pe = i.get("PE", {})

            rows.append([
                strike,
                ce.get("openInterest", 0),
                pe.get("openInterest", 0),
                ce.get("totalTradedVolume", 0),
                pe.get("totalTradedVolume", 0),
            ])

        return pd.DataFrame(rows, columns=["Strike", "CE_OI", "PE_OI", "CE_VOL", "PE_VOL"])

    except:
        return None

# =========================
# SIDEBAR
# =========================
st.sidebar.title("📊 CONTROL PANEL")

index = st.sidebar.selectbox("Select Index", INDEX_LIST)

stock = st.sidebar.text_input("🔎 Search ANY Stock", "RELIANCE")

expiry = st.sidebar.radio("Expiry", ["Weekly", "Monthly"])

# =========================
# DATA LOAD
# =========================
df = fetch_option_chain(index)

if df is None or df.empty:
    st.warning("⚠ NSE BLOCKED → fallback mode")

    df = pd.DataFrame({
        "Strike": np.arange(24000, 24150, 50),
        "CE_OI": np.random.randint(2000, 8000, 3),
        "PE_OI": np.random.randint(2000, 8000, 3),
        "CE_VOL": np.random.randint(100, 500, 3),
        "PE_VOL": np.random.randint(100, 500, 3),
    })

# =========================
# STOCK DATA
# =========================
price, change, stock_signal = stock_analysis(stock)

# =========================
# ATM
# =========================
ltp = df["Strike"].mean()
atm = min(df["Strike"], key=lambda x: abs(x - ltp))

# =========================
# PRESSURE ENGINE
# =========================
df["CE_PRESSURE"] = df["CE_OI"] / (df["PE_OI"] + 1)
df["PE_PRESSURE"] = df["PE_OI"] / (df["CE_OI"] + 1)

ce_total = df["CE_OI"].sum()
pe_total = df["PE_OI"].sum()

# =========================
# TREND
# =========================
if ce_total > pe_total * 1.1:
    trend = "🟢 BULLISH"
elif pe_total > ce_total * 1.1:
    trend = "🔴 BEARISH"
else:
    trend = "🟡 SIDEWAYS"

# =========================
# UI HEADER
# =========================
st.title("🔥 NSE AI OPTION CHAIN + STOCK SCANNER")

# =========================
# LEFT METRICS
# =========================
c1, c2, c3 = st.columns(3)

c1.metric("INDEX", index)
c2.metric("ATM", atm)
c3.metric("TREND", trend)

# =========================
# STOCK PANEL
# =========================
st.subheader("📌 STOCK ANALYSIS")

if price is None:
    st.error(stock_signal)
else:
    st.metric("Stock Price", price)
    st.metric("Change %", change)
    st.success(stock_signal)

# =========================
# OPTION CHAIN
# =========================
st.subheader("📊 OPTION CHAIN")
st.dataframe(df, use_container_width=True)

# =========================
# ZONES
# =========================
st.subheader("🚀 CE STRONG ZONE")
st.dataframe(df.sort_values("CE_PRESSURE", ascending=False).head(5))

st.subheader("📉 PE STRONG ZONE")
st.dataframe(df.sort_values("PE_PRESSURE", ascending=False).head(5))

# =========================
# FINAL SIGNAL
# =========================
st.subheader("🧠 FINAL AI SIGNAL")

if "CALL" in stock_signal and ce_total > pe_total:
    st.success("🟢 STRONG CALL CONFIRMED")
elif "PUT" in stock_signal and pe_total > ce_total:
    st.error("🔴 STRONG PUT CONFIRMED")
else:
    st.warning("🟡 MIXED MARKET")

st.success("✅ SYSTEM READY (OLD CODE SAFE + FULL UPGRADE)")
