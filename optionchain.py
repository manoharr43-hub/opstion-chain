# ==========================================================
# 🚀 HYBRID NSE PRO SCANNER V7 (RUN SCAN Visible + STRONG SELL)
# ==========================================================

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import pytz
from io import BytesIO
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# ==========================================================
# PAGE CONFIG
# ==========================================================
st.set_page_config(page_title="HYBRID NSE PRO SCANNER V7", layout="wide")
st.title("🚀 HYBRID NSE PRO SCANNER V7")
st.caption("EMA + RSI + Volume + Breakout Confirmation + Institutional Scoring")

# ==========================================================
# NSE500 Loader
# ==========================================================
@st.cache_data(ttl=86400)
def load_nse500():
    try:
        url = "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"
        df = pd.read_csv(url)
        return sorted(df["Symbol"].dropna().unique().tolist())
    except:
        return ["RELIANCE","TCS","INFY","HDFCBANK","ICICIBANK","SBIN","ITC","LT"]

stocks = load_nse500()

# ==========================================================
# Sidebar Settings
# ==========================================================
st.sidebar.header("⚙️ Scanner Settings")
interval = st.sidebar.selectbox("Interval",["5m","15m","30m","60m","1d"],index=1)
period = st.sidebar.selectbox("Period",["5d","1mo","3mo","6mo"],index=1)
rsi_upper = st.sidebar.slider("RSI Upper",50,90,70)
rsi_lower = st.sidebar.slider("RSI Lower",10,50,30)
vol_multiplier = st.sidebar.slider("Volume Spike Multiplier",1.0,5.0,1.5)
breakout_window = st.sidebar.slider("Breakout Window",10,50,20)
show_strong_only = st.sidebar.checkbox("Show Strong Buy Only")

# ==========================================================
# Indicators + Signals
# ==========================================================
def calculate_rsi(df, period=14):
    delta = df["Close"].diff()
    gain = delta.where(delta>0,0)
    loss = -delta.where(delta<0,0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / (avg_loss + 1e-10)
    return 100 - (100/(1+rs))

def add_indicators(df):
    if len(df)<60: return pd.DataFrame()
    df = df.copy()
    df["EMA20"] = df["Close"].ewm(span=20,adjust=False).mean()
    df["EMA50"] = df["Close"].ewm(span=50,adjust=False).mean()
    df["RSI"] = calculate_rsi(df)
    df["AVG_VOL"] = df["Volume"].rolling(20).mean()
    return df

def breakout_with_volume(df):
    try:
        if df.empty or len(df)<breakout_window: return "WAIT"
        latest_close = float(df["Close"].iloc[-1])
        current_vol = float(df["Volume"].iloc[-1])
        avg_vol = float(df["AVG_VOL"].iloc[-1])
        breakout_high = df["High"].rolling(breakout_window).max().shift(1).iloc[-1]
        breakout_low = df["Low"].rolling(breakout_window).min().shift(1).iloc[-1]
        if pd.isna(breakout_high) or pd.isna(breakout_low): return "WAIT"
        if latest_close>breakout_high and current_vol>avg_vol*vol_multiplier: return "BULLISH CONFIRMED"
        elif latest_close<breakout_low and current_vol>avg_vol*vol_multiplier: return "BEARISH CONFIRMED"
        elif latest_close>breakout_high: return "BULLISH (Weak)"
        elif latest_close<breakout_low: return "BEARISH (Weak)"
        return "NO"
    except:
        return "WAIT"

def ema_signal(df):
    try:
        ema20 = float(df["EMA20"].iloc[-1])
        ema50 = float(df["EMA50"].iloc[-1])
        return "BUY" if ema20>ema50 else "SELL"
    except:
        return "WAIT"

def calculate_score(df):
    score=0
    try:
        if ema_signal(df)=="BUY": score+=2
        else: score-=2
        rsi=float(df["RSI"].iloc[-1])
        if rsi>rsi_upper: score+=1
        elif rsi<rsi_lower: score-=1
        bo=breakout_with_volume(df)
        if "BULLISH CONFIRMED" in bo: score+=2
        elif "BEARISH CONFIRMED" in bo: score-=2
        elif "Weak" in bo: score+=1
        return score
    except:
        return 0

def final_signal(score):
    if score>=5: return "STRONG BUY"
    if score>=3: return "BUY"
    if score==2: return "WATCH"
    if score==1: return "WAIT"
    if score==0: return "NEUTRAL"
    if score==-1: return "WEAK SELL"
    if score<=-2 and score>-4: return "SELL"
    if score<=-4: return "STRONG SELL"
    return "NEUTRAL"

# ==========================================================
# RUN SCAN BUTTON (Always Visible)
# ==========================================================
st.markdown("---")
scan_btn = st.button("🚀 RUN SCAN", use_container_width=True)

if scan_btn:
    st.info("Scanning started...")
    results=[]
    for symbol in stocks[:20]:   # demo కోసం 20 stocks మాత్రమే
        df=yf.download(f"{symbol}.NS",interval=interval,period=period,auto_adjust=True,progress=False,threads=False)
        if df.empty: continue
        df=add_indicators(df)
        if df.empty: continue
        score=calculate_score(df)
        signal=final_signal(score)
        latest=df.iloc[-1]
        results.append({
            "Stock":symbol,
            "Price":round(float(latest["Close"]),2),
            "EMA":ema_signal(df),
            "RSI":round(float(latest["RSI"]),2),
            "Breakout":breakout_with_volume(df),
            "Score":score,
            "Signal":signal
        })
    result_df=pd.DataFrame(results)
    if show_strong_only:
        result_df=result_df[result_df["Signal"]=="STRONG BUY"]
    st.dataframe(result_df.style.applymap(
        lambda x: "color: green" if x=="STRONG BUY" else ("color: red" if x=="STRONG SELL" else ""),
        subset=["Signal"]
    ),use_container_width=True)
