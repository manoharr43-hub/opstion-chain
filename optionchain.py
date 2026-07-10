import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import io
import time
import base64
from concurrent.futures import ThreadPoolExecutor, as_completed
import warnings

warnings.filterwarnings('ignore')

# ==========================================
# 1. PAGE SETUP
# ==========================================
st.set_page_config(page_title="NSE AI PRO V11.10", layout="wide", page_icon="🚀")
st.title("🚀 NSE AI PRO V11.10 - Institutional Ultimate")
st.markdown("**F&O + FVG/BGV Signal Time Enhanced Edition (Corrected)**")
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
# 3. NEW FUNCTIONS FOR SIGNAL TIMES (SAFE INDEXING)
# ==========================================
def calculate_fvg_bgv(df):
    fvg_time, bgv_time = "N/A", "N/A"
    if len(df) > 3:   # కనీసం 4 rows ఉన్నప్పుడు మాత్రమే
        try:
            # Fair Value Gap (FVG)
            if df['Low'].iloc[-1] > df['High'].iloc[-3]:
                fvg_time = df.index[-1].strftime("%d-%b %I:%M %p")
            # Break Value Gap (BGV)
            if df['High'].iloc[-1] < df['Low'].iloc[-3]:
                bgv_time = df.index[-1].strftime("%d-%b %I:%M %p")
        except Exception:
            fvg_time, bgv_time = "Error", "Error"
    return fvg_time, bgv_time

def bullish_bearish_signal_time(df):
    if len(df) < 20: 
        return "N/A"
    try:
        slope, _ = np.polyfit(np.arange(20), df['Close'].tail(20).values, 1)
        sig_time = df.index[-1].strftime("%d-%b %I:%M %p")
        return f"Bullish ⏱️ {sig_time}" if slope > 0 else f"Bearish ⏱️ {sig_time}"
    except Exception:
        return "N/A"

# ==========================================
# 4. PROCESSOR THREAD MODIFIED
# ==========================================
def process_stock_thread(symbol, interval, period, h52w, l52w, nifty_return, daily_close_series):
    try:
        df = yf.download(f"{symbol}.NS", interval=interval, period=period, auto_adjust=True, progress=False)
    except Exception:
        return None
    if df.empty or len(df) < 5: return None

    close = float
