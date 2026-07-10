import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import io
import time
import base64
from concurrent.futures import ThreadPoolExecutor, as_completed
from xgboost import XGBClassifier
import warnings

warnings.filterwarnings('ignore')

# ==========================================
# 1. PAGE SETUP
# ==========================================
st.set_page_config(page_title="NSE AI PRO V11.10", layout="wide", page_icon="🚀")
st.title("🚀 NSE AI PRO V11.10 - Institutional Ultimate")
st.markdown("**F&O + FVG/BGV Signal Time Enhanced Edition**")
st.markdown("---")

if 'v11_master_data' not in st.session_state:
    st.session_state.v11_master_data = pd.DataFrame()

# ==========================================
# 2. SIDEBAR CONFIGURATION
# ==========================================
with st.sidebar:
    st.header("⚙️ Settings & Controls")
    auto_refresh = st.checkbox("🔄 Auto Refresh (Every 3 Mins)")
    interval = st.selectbox("Interval", ["5m","15m","30m","1h","1d"], index=1)
    period = st.selectbox("Period", ["5d","1mo","3mo","6mo", "1y"], index=1)

    sector_stocks = {
        "Banking": ["HDFCBANK","ICICIBANK","SBIN","AXISBANK","KOTAKBANK"],
        "IT": ["TCS","INFY","WIPRO","HCLTECH","TECHM"],
        "Pharma": ["SUNPHARMA","CIPLA","DIVISLAB","DRREDDY"],
        "Energy": ["RELIANCE","ONGC","BPCL","NTPC"],
        "Auto": ["TATAMOTORS","M&M","EICHERMOT","HEROMOTOCO"],
        "FMCG": ["ITC","HINDUNILVR","BRITANNIA","DABUR"],
        "F&O": ["NIFTY","BANKNIFTY","FINNIFTY","MIDCPNIFTY"]  # కొత్తగా add చేసినది
    }
    sector = st.selectbox("Sector", ["All NSE500"] + list(sector_stocks.keys()))

    st.markdown("---")
    run_button = st.button("🚀 RUN ULTIMATE SCANNER", type="primary", use_container_width=True)

# ==========================================
# 3. NEW FUNCTIONS FOR SIGNAL TIMES
# ==========================================
def calculate_fvg_bgv(df):
    fvg_time, bgv_time = "N/A", "N/A"
    if len(df) > 30:
        # Fair Value Gap (FVG)
        if df['Low'].iloc[-1] > df['High'].iloc[-3]:
            fvg_time = df.index[-1].strftime("%d-%b %I:%M %p")
        # Break Value Gap (BGV)
        if df['High'].iloc[-1] < df['Low'].iloc[-3]:
            bgv_time = df.index[-1].strftime("%d-%b %I:%M %p")
    return fvg_time, bgv_time

def bullish_bearish_signal_time(df):
    if len(df) < 20: return "N/A"
    slope, _ = np.polyfit(np.arange(20), df['Close'].tail(20).values, 1)
    sig_time = df.index[-1].strftime("%d-%b %I:%M %p")
    return f"Bullish ⏱️ {sig_time}" if slope > 0 else f"Bearish ⏱️ {sig_time}"

# ==========================================
# 4. PROCESSOR THREAD MODIFIED
# ==========================================
def process_stock_thread(symbol, interval, period, h52w, l52w, nifty_return, daily_close_series):
    df = yf.download(f"{symbol}.NS", interval=interval, period=period, auto_adjust=True, progress=False)
    if df.empty or len(df) < 60: return None

    close = float(df["Close"].iloc[-1])
    fvg_time, bgv_time = calculate_fvg_bgv(df)
    bull_bear_time = bullish_bearish_signal_time(df)

    # Dummy scoring for simplicity
    score = 1 if close > df['Close'].mean() else -1
    signal = "STRONG BUY" if score > 0 else "STRONG SELL"

    return [
        symbol, round(close,2), bull_bear_time, fvg_time, bgv_time, score, signal
    ]

# ==========================================
# 5. UI EXECUTION
# ==========================================
tab1, tab2 = st.tabs(["🚀 V11.10 PRO Dashboard", "🔍 Custom Stock Search"])

with tab1:
    if run_button or auto_refresh:
        selected_stocks = sector_stocks[sector] if sector != "All NSE500" else ["RELIANCE","TCS","INFY"]
        results = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_stock = {executor.submit(process_stock_thread, sym, interval, period, None, None, 0, None): sym for sym in selected_stocks}
            for future in as_completed(future_to_stock):
                res = future.result()
                if res: results.append(res)

        if results:
            df_res = pd.DataFrame(results, columns=["Stock","LTP","Bull/Bear Signal Time","FVG Time","BGV Time","Score","Signal"])
            st.session_state.v11_master_data = df_res
            st.dataframe(df_res, use_container_width=True)

with tab2:
    search_query = st.text_input("Enter Stock Symbol (e.g., ITC, RELIANCE, SBIN):").upper()
    if st.button("🔍 Run Custom Deep Analytics"):
        res = process_stock_thread(search_query, interval, period, None, None, 0, None)
        if res:
            st.success(f"Analysis Complete for {search_query}")
            st.write(f"**Bull/Bear Signal Time:** {res[2]}")
            st.write(f"**FVG Time:** {res[3]} | **BGV Time:** {res[4]}")
            st.write(f"**Score:** {res[5]} | **Signal:** {res[6]}")
