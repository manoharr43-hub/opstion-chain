# =========================================================
# 🚀 NSE AI PRO MAX V2.9 - FINAL STABLE BUILD
# =========================================================

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from concurrent.futures import ThreadPoolExecutor

# =========================================================
# PAGE CONFIG & AUTO REFRESH
# =========================================================
st.set_page_config(page_title="NSE AI PRO MAX V2.9", layout="wide")
st.fragment(run_every=60)

st.title("🚀 NSE AI PRO MAX V2.9")
st.caption("AI BASED NSE SCANNER + OPTIONS MOMENTUM + CUSTOM CSV SETUP")

# =========================================================
# STOCK LIST (active tickers only)
# =========================================================
nse_stocks = {
    "RELIANCE": "RELIANCE.NS", "HDFCBANK": "HDFCBANK.NS", "INFY": "INFY.NS",
    "ICICIBANK": "ICICIBANK.NS", "TCS": "TCS.NS", "ITC": "ITC.NS",
    "SBIN": "SBIN.NS", "AXISBANK": "AXISBANK.NS", "SUNPHARMA": "SUNPHARMA.NS"
}

# =========================================================
# SIDEBAR SETTINGS
# =========================================================
st.sidebar.header("⚙️ SETTINGS")
selected_stock = st.sidebar.selectbox("SELECT STOCK", list(nse_stocks.keys()))
interval = st.sidebar.selectbox("INTERVAL", ["5m", "15m", "30m", "1h"])
period = st.sidebar.selectbox("PERIOD", ["1d", "5d", "1mo"])
ticker = nse_stocks[selected_stock]

# =========================================================
# HELPER FUNCTIONS
# =========================================================
def calculate_indicators(df):
    if df.empty: return df
    df = df.reset_index()
    df["EMA20"] = df["Close"].ewm(span=20).mean()
    df["EMA50"] = df["Close"].ewm(span=50).mean()
    df["VWAP"] = ((df["Close"] * df["Volume"]).cumsum()) / df["Volume"].cumsum()
    delta = df["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    rs = gain.rolling(14).mean() / loss.rolling(14).mean()
    df["RSI"] = 100 - (100 / (1 + rs))
    df["RSI"] = df["RSI"].fillna(50)
    df["MACD"] = df["Close"].ewm(span=12).mean() - df["Close"].ewm(span=26).mean()
    df["MACD_SIGNAL"] = df["MACD"].ewm(span=9).mean()
    return df

def generate_signal(df):
    latest = df.iloc[-1]
    score = 0
    if latest["EMA20"] > latest["EMA50"]: score += 25
    else: score -= 25
    if latest["Close"] > latest["VWAP"]: score += 25
    else: score -= 25
    if 55 < latest["RSI"] < 70: score += 25
    elif latest["RSI"] > 70: score -= 10
    elif latest["RSI"] < 30: score += 15
    else: score -= 10
    if latest["MACD"] > latest["MACD_SIGNAL"]: score += 25
    else: score -= 25

    if score >= 75: signal = "🚀 STRONG BUY"
    elif score >= 25: signal = "✅ BUY"
    elif score <= -75: signal = "🚨 STRONG SELL"
    elif score <= -25: signal = "🔻 SELL"
    else: signal = "⚠️ SIDEWAYS"
    return signal, score

# =========================================================
# TABS SETUP
# =========================================================
tab1, tab2 = st.tabs(["📈 AI Scanner & Live Setup", "📂 Upload CSV & Extract AI Target"])

# =========================================================
# TAB 1 – LIVE SCANNER
# =========================================================
with tab1:
    try:
        df = yf.download(ticker, interval=interval, period=period, progress=False, auto_adjust=True)
        if df.empty:
            st.error("NO DATA FOUND")
        else:
            df = calculate_indicators(df)
            signal, score = generate_signal(df)
            latest = df.iloc[-1]
            current_price = float(latest["Close"])

            st.subheader("🤖 AI SIGNAL")
            if "BUY" in signal: st.success(f"{signal} (SCORE: {score})")
            elif "SELL" in signal: st.error(f"{signal} (SCORE: {score})")
            else: st.warning(f"{signal} (SCORE: {score})")

            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("PRICE", f"₹ {round(current_price, 2)}")
            col2.metric("RSI", round(float(latest["RSI"]), 2))
            col3.metric("VWAP", round(float(latest["VWAP"]), 2))
            col4.metric("MACD", round(float(latest["MACD"]), 2))
            col5.metric("AI SCORE", f"{score} PTS")

            st.markdown("---")
            st.subheader(f"📈 {selected_stock} LIVE CHART")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df.index, y=df["Close"], mode="lines", name="Close"))
            fig.add_trace(go.Scatter(x=df.index, y=df["EMA20"], mode="lines", name="EMA20"))
            st.plotly_chart(fig, width="stretch")

            st.subheader("🔥 LIVE AI NIFTY 50 SCANNER")
            def scan_stock(item):
                s_name, s_ticker = item
                try:
                    data = yf.download(s_ticker, interval=interval, period=period, progress=False, auto_adjust=True)
                    if data.empty: return None
                    data = calculate_indicators(data)
                    sig, scr = generate_signal(data)
                    return {"STOCK": s_name, "PRICE": round(float(data.iloc[-1]["Close"]), 2),
                            "SIGNAL": sig, "SCORE": scr}
                except: return None

            results = []
            with ThreadPoolExecutor(max_workers=10) as executor:
                scanned = executor.map(scan_stock, nse_stocks.items())
            for item in scanned:
                if item is not None: results.append(item)

            st.dataframe(pd.DataFrame(results).sort_values(by="SCORE", ascending=False),
                         width="stretch", hide_index=True)

    except Exception as e:
        st.error(f"App Error: {str(e)}")

# =========================================================
# TAB 2 – CSV UPLOAD WORKFLOW
# =========================================================
with tab2:
    try:
        st.header("📂 Screener Kit Data Processing")
        st.write("మీరు డౌన్‌లోడ్ చేసిన Screener Excel/CSV ఫైల్ ని ఇక్కడ అప్లోడ్ చేయండి")

        uploaded_file = st.file_uploader("Upload Screener CSV/Excel", type=["csv", "xlsx"])
        if uploaded_file is not None:
            if uploaded_file.name.endswith(".csv"):
                df_csv = pd.read_csv(uploaded_file)
            else:
                df_csv = pd.read_excel(uploaded_file)

            st.success("✅ File Uploaded Successfully")
            st.dataframe(df_csv, width="stretch")

            st.markdown("---")
            st.subheader("🤖 AI Screener Call/Put Setup")

            if {"Strike", "Type", "LTP", "Volume"}.issubset(df_csv.columns):
                calls_df = df_csv[df_csv["Type"].str.upper() == "CE"].copy()
                puts_df = df_csv[df_csv["Type"].str.upper() == "PE"].copy()
                col_call, col_put = st.columns(2)

                with col_call:
                    if not calls_df.empty:
                        c_idx = calls_df["Volume"].idxmax()
                        c_data = calls_df.loc[c_idx]
                        c_ltp = float(c_data["LTP"])
                        st.markdown(f"<h4 style='text-align:center;color:#4CAF50;'>🟢 CALL SIDE: {c_data['Strike']} CE</h4>",
                                    unsafe_allow_html=True)
                        st.info(f"Highest Volume: {int(c_data['Volume'])}")
                        st.metric("ENTRY", f"₹ {round(c_ltp, 2)}")
                        st.metric("STOPLOSS", f"₹ {round(c_ltp * 0.85, 2)}")
                        st.metric("TARGET 1", f"
