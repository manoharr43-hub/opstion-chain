# =========================================================
# 🚀 NSE AI PRO MAX V3.0 - NSEPYTHON LIVE DATA + EXCEL EXPORT
# =========================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import io
from concurrent.futures import ThreadPoolExecutor
from nsepython import nsefetch

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(page_title="NSE AI PRO MAX V3.0", layout="wide")
st.fragment(run_every=60)

st.title("🚀 NSE AI PRO MAX V3.0")
st.caption("AI BASED NSE SCANNER + NSEPYTHON LIVE DATA")

# =========================================================
# FULL NIFTY 50 STOCK LIST
# =========================================================
nse_stocks = {
    "APOLLOHOSP": "APOLLOHOSP", "ASIANPAINT": "ASIANPAINT", "AXISBANK": "AXISBANK",
    "BAJAJ-AUTO": "BAJAJ-AUTO", "BAJFINANCE": "BAJFINANCE", "BEL": "BEL",
    "BHARTIARTL": "BHARTIARTL", "BPCL": "BPCL", "BRITANNIA": "BRITANNIA",
    "CIPLA": "CIPLA", "COALINDIA": "COALINDIA", "DIVISLAB": "DIVISLAB",
    "DRREDDY": "DRREDDY", "EICHERMOT": "EICHERMOT", "GRASIM": "GRASIM",
    "HCLTECH": "HCLTECH", "HDFCBANK": "HDFCBANK", "HDFCLIFE": "HDFCLIFE",
    "HEROMOTOCO": "HEROMOTOCO", "HINDALCO": "HINDALCO", "HINDUNILVR": "HINDUNILVR",
    "ICICIBANK": "ICICIBANK", "INDUSINDBK": "INDUSINDBK", "INFY": "INFY",
    "ITC": "ITC", "JSWSTEEL": "JSWSTEEL", "KOTAKBANK": "KOTAKBANK",
    "LT": "LT", "M&M": "M&M", "MARUTI": "MARUTI", "NESTLEIND": "NESTLEIND",
    "NTPC": "NTPC", "ONGC": "ONGC", "POWERGRID": "POWERGRID", "RELIANCE": "RELIANCE",
    "SBILIFE": "SBILIFE", "SBIN": "SBIN", "SUNPHARMA": "SUNPHARMA",
    "TATACONSUM": "TATACONSUM", "TATAMOTORS": "TATAMOTORS", "TATASTEEL": "TATASTEEL",
    "TCS": "TCS", "TECHM": "TECHM", "TITAN": "TITAN", "ULTRACEMCO": "ULTRACEMCO",
    "WIPRO": "WIPRO", "TRENT": "TRENT"
}

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.header("⚙️ SETTINGS")
selected_stock = st.sidebar.selectbox("SELECT STOCK", list(nse_stocks.keys()))

# =========================================================
# HELPER FUNCTION: EXCEL CONVERTER
# =========================================================
def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    return output.getvalue()

# =========================================================
# NSEPYTHON LIVE DATA FETCH
# =========================================================
def get_live_data(symbol):
    try:
        url = f"https://www.nseindia.com/api/quote-equity?symbol={symbol}"
        data = nsefetch(url)
        return data
    except Exception as e:
        return None

# =========================================================
# INDICATOR & SIGNAL GENERATION
# =========================================================
def generate_signal(price, prev_price):
    score = 0
    if price > prev_price: score += 25
    else: score -= 25
    if score >= 25: signal = "✅ BUY"
    elif score <= -25: signal = "🔻 SELL"
    else: signal = "⚠️ SIDEWAYS"
    return signal, score

# =========================================================
# MAIN DISPLAY
# =========================================================
live_data = get_live_data(nse_stocks[selected_stock])
if live_data:
    last_price = live_data['priceInfo']['lastPrice']
    prev_close = live_data['priceInfo']['previousClose']
    signal, score = generate_signal(last_price, prev_close)

    st.subheader("🤖 AI SIGNAL")
    if "BUY" in signal: st.success(f"{signal} (SCORE: {score})")
    elif "SELL" in signal: st.error(f"{signal} (SCORE: {score})")
    else: st.warning(f"{signal} (SCORE: {score})")

    col1, col2 = st.columns(2)
    col1.metric("LIVE PRICE", f"₹ {last_price}")
    col2.metric("PREV CLOSE", f"₹ {prev_close}")
else:
    st.error("⚠️ NSE Live data not available.")

# =========================================================
# LIVE AI SCANNER (NIFTY50)
# =========================================================
st.subheader("🔥 LIVE AI NIFTY 50 SCANNER")

def scan_stock(item):
    s_name, s_symbol = item
    try:
        data = get_live_data(s_symbol)
        if not data: return None
        price = data['priceInfo']['lastPrice']
        prev_close = data['priceInfo']['previousClose']
        sig, scr = generate_signal(price, prev_close)
        return {"STOCK": s_name, "PRICE": price, "SIGNAL": sig, "SCORE": scr}
    except: return None

results = []
with ThreadPoolExecutor(max_workers=15) as executor:
    scanned = executor.map(scan_stock, nse_stocks.items())
for item in scanned:
    if item is not None: results.append(item)

scanner_df = pd.DataFrame(results).sort_values
