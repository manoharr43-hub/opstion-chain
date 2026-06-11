# ==========================================================
# 🚀 HYBRID NSE PRO SCANNER V8 (Live NSE API + Sector Fix)
# ==========================================================

import streamlit as st
import pandas as pd
import numpy as np
import pytz
from datetime import datetime
from nsepython import nsefetch   # ✅ Live NSE API
import yfinance as yf

# ==========================================================
# PAGE CONFIG
# ==========================================================
st.set_page_config(page_title="HYBRID NSE PRO SCANNER V8", layout="wide")
st.title("🚀 HYBRID NSE PRO SCANNER V8")
st.caption("Live NSE API + EMA + RSI + Volume + Breakout Confirmation")

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
# Sector Watchlists
# ==========================================================
sector_stocks = {
    "Banking":["HDFCBANK","ICICIBANK","SBIN","AXISBANK","KOTAKBANK"],
    "IT":["TCS","INFY","WIPRO","HCLTECH","TECHM"],
    "Pharma":["SUNPHARMA","CIPLA","DIVISLAB","DRREDDY"],
    "Energy":["RELIANCE","ONGC","BPCL","NTPC"],
    "Auto":["TATAMOTORS","M&M","EICHERMOT","HEROMOTOCO"],
    "FMCG":["ITC","HINDUNILVR","BRITANNIA","DABUR"]
}

# ==========================================================
# Market Status
# ==========================================================
ist = pytz.timezone("Asia/Kolkata")
now = datetime.now(ist)
market_open = (now.weekday()<5 and now.strftime("%H:%M")>="09:15" and now.strftime("%H:%M")<="15:30")

if market_open:
    st.success(f"🟢 MARKET OPEN | {now.strftime('%d-%b-%Y %I:%M:%S %p')}")
else:
    st.error(f"🔴 MARKET CLOSED | {now.strftime('%d-%b-%Y %I:%M:%S %p')}")

# ==========================================================
# Sidebar Settings
# ==========================================================
st.sidebar.header("⚙️ Scanner Settings")
interval = st.sidebar.selectbox("Interval",["5m","15m","30m","60m","1d"],index=1)
period = st.sidebar.selectbox("Period",["5d","1mo","3mo","6mo"],index=1)
sector = st.sidebar.selectbox("Sector",list(sector_stocks.keys())+["All NSE500"])
rsi_upper = st.sidebar.slider("RSI Upper",50,90,70)
rsi_lower = st.sidebar.slider("RSI Lower",10,50,30)
vol_multiplier = st.sidebar.slider("Volume Spike Multiplier",1.0,5.0,1.5)
breakout_window = st.sidebar.slider("Breakout Window",10,50,20)
show_strong_only = st.sidebar.checkbox("Show Strong Buy Only")

# ==========================================================
# Live NSE Price Fetch
# ==========================================================
def get_live_price(symbol):
    try:
        url = f"https://www.nseindia.com/api/quote-equity?symbol={symbol}"
        data = nsefetch(url)
        return data["priceInfo"]["lastPrice"]
    except:
        return None

# ==========================================================
# RSI Calculation
# ==========================================================
def calculate_rsi(df, period=14):
    delta = df["Close"].diff()
    gain = delta.where(delta>0,0)
    loss = -delta.where(delta<0,0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / (avg_loss + 1e-10)
    return 100 - (100/(1+rs))

# ==========================================================
# Indicators
# ==========================================================
def add_indicators(df):
    if len(df)<60: return pd.DataFrame()
    df = df.copy()
    df["EMA20"] = df["Close"].ewm(span=20,adjust=False).mean()
    df["EMA50"] = df["Close"].ewm(span=50,adjust=False).mean()
    df["RSI"] = calculate_rsi(df)
    df["AVG_VOL"] = df["Volume"].rolling(20).mean()
    return df

# ==========================================================
# Breakout + Volume Confirmation
# ==========================================================
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

# ==========================================================
# Institutional Score Engine
# ==========================================================
def calculate_score(df):
    score=0
    try:
        ema20 = float(df["EMA20"].iloc[-1])
        ema50 = float(df["EMA50"].iloc[-1])
        score += 2 if ema20>ema50 else -2
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

# ==========================================================
# Final Signal
# ==========================================================
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
# RUN SCAN Button
# ==========================================================
st.markdown("---")
scan_btn = st.button("🚀 RUN SCAN", use_container_width=True)

if scan_btn:
    st.info("Scanning started...")
    if sector=="All NSE500":
        selected_stocks=stocks
    else:
        selected_stocks=sector_stocks.get(sector,[])
    results=[]
    for symbol in selected_stocks[:20]:   # demo కోసం 20 మాత్రమే
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
