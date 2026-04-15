import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# =============================
# CONFIG
# =============================
st.set_page_config(page_title="🔥 MANOHAR NSE AI PRO", layout="wide")
st_autorefresh(interval=60000, key="refresh")

st.title("🚀 MANOHAR NSE AI PRO TERMINAL")
st.markdown("---")

# =============================
# SAFE ANALYSIS LOGIC
# =============================
def analyze_data(df):
    if df is None or df.empty or len(df) < 50:
        return None

    df = df.copy()

    df["EMA20"] = df["Close"].ewm(span=20).mean()
    df["EMA50"] = df["Close"].ewm(span=50).mean()
    df["VOL_AVG"] = df["Volume"].rolling(window=20).mean()

    curr_price = df["Close"].iloc[-1]
    curr_e20 = df["EMA20"].iloc[-1]
    curr_e50 = df["EMA50"].iloc[-1]
    curr_vol = df["Volume"].iloc[-1]
    curr_avg_vol = df["VOL_AVG"].iloc[-1]

    # Safety check NaN
    if np.isnan(curr_avg_vol):
        return None

    cp_strength = "🔵 CALL STRONG" if curr_e20 > curr_e50 else "🔴 PUT STRONG"
    big_player = "🔥 ACTIVE" if curr_vol > (curr_avg_vol * 1.5) else "💤 NORMAL"

    observation = "WAIT"
    entry = sl = target = 0

    recent_high = df["High"].iloc[-10:].max()
    recent_low = df["Low"].iloc[-10:].min()
    risk = max((recent_high - recent_low), curr_price * 0.01)

    if curr_e20 > curr_e50 and curr_vol > curr_avg_vol:
        observation = "🚀 STRONG BUY"
        entry = curr_price
        sl = curr_price - (risk * 0.5)
        target = curr_price + risk

    elif curr_e20 < curr_e50 and curr_vol > curr_avg_vol:
        observation = "💀 STRONG SELL"
        entry = curr_price
        sl = curr_price + (risk * 0.5)
        target = curr_price - risk

    return (
        cp_strength,
        observation,
        big_player,
        round(entry, 2),
        round(sl, 2),
        round(target, 2),
    )

# =============================
# SECTORS
# =============================
all_sectors = {
    "Nifty 50": ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "SBIN"],
    "Banking": ["SBIN", "AXISBANK", "KOTAKBANK", "HDFCBANK", "ICICIBANK"],
    "Auto": ["TATAMOTORS", "MARUTI", "M&M", "HEROMOTOCO"],
    "Metal": ["TATASTEEL", "HINDALCO", "JSWSTEEL"],
    "IT Sector": ["TCS", "INFY", "WIPRO", "HCLTECH"],
    "Pharma": ["SUNPHARMA", "CIPLA", "DRREDDY"]
}

# =============================
# SIDEBAR
# =============================
st.sidebar.title("📂 Backtest Panel")
bt_date = st.sidebar.date_input("Select Date", datetime.now() - timedelta(days=1))
bt_stock_input = st.sidebar.text_input("Stock (optional)").upper()

# =============================
# LIVE SCANNER
# =============================
selected_sector = st.selectbox("📂 Select Sector", list(all_sectors.keys()))
stocks = all_sectors[selected_sector]

if st.button("🔍 START LIVE SCANNER", use_container_width=True):

    results = []

    with st.spinner("AI Scanning Market..."):
        for s in stocks:
            try:
                df = yf.download(s + ".NS", period="2d", interval="15m", progress=False)

                res = analyze_data(df)

                if res:
                    results.append({
                        "Stock": s,
                        "Price": float(df["Close"].iloc[-1]),
                        "Signal": res[1],
                        "Strength": res[0],
                        "Entry": res[3],
                        "SL": res[4],
                        "Target": res[5],
                        "Big Players": res[2],
                        "Time": df.index[-1].strftime("%H:%M")
                    })

            except Exception:
                continue

    if results:
        st.dataframe(pd.DataFrame(results), use_container_width=True)
    else:
        st.error("No Data Found")

# =============================
# BACKTEST
# =============================
st.markdown("---")
st.subheader(f"📅 Backtest Report - {bt_date}")

if st.sidebar.button("📊 Run Backtest"):

    bt_results = []
    target_list = [bt_stock_input] if bt_stock_input else stocks

    with st.spinner("Running Backtest..."):
        for s in target_list:
            try:
                df = yf.download(
                    s + ".NS",
                    start=str(bt_date),
                    end=str(bt_date + timedelta(days=1)),
                    interval="15m",
                    progress=False
                )

                if df.empty:
                    continue

                for i in range(50, len(df)):
                    sub = df.iloc[:i+1]
                    res = analyze_data(sub)

                    if res and res[1] != "WAIT":
                        bt_results.append({
                            "Time": sub.index[-1].strftime("%H:%M"),
                            "Stock": s,
                            "Signal": res[1],
                            "Entry": res[3],
                            "SL": res[4],
                            "Target": res[5]
                        })

            except Exception:
                continue

    if bt_results:
        st.dataframe(pd.DataFrame(bt_results), use_container_width=True)
    else:
        st.warning("No Strong Signals Found")
