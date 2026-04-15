import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from streamlit_autorefresh import st_autorefresh
import pandas_ta as ta

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(page_title="🔥 PRO NSE AI SCANNER V4", layout="wide")
st_autorefresh(interval=10000, key="refresh") # 10 seconds refresh

st.title("🔥 PRO NSE AI SCANNER (ULTIMATE EDITION)")
st.markdown("---")

# =============================
# SECTORS
# =============================
sectors = {
    "Nifty 50": ["RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS","BHARTIARTL.NS","SBIN.NS"],
    "Banking": ["SBIN.NS","AXISBANK.NS","KOTAKBANK.NS","PNB.NS","HDFCBANK.NS","ICICIBANK.NS"],
    "IT": ["WIPRO.NS","HCLTECH.NS","TECHM.NS","INFY.NS","TCS.NS"],
    "Auto": ["MARUTI.NS","M&M.NS","TATAMOTORS.NS","HEROMOTOCO.NS"],
    "Pharma": ["SUNPHARMA.NS","DRREDDY.NS","CIPLA.NS","APOLLOHOSP.NS"],
    "Energy": ["ONGC.NS","IOC.NS","BPCL.NS","GAIL.NS"],
    "FMCG": ["ITC.NS","NESTLEIND.NS","HINDUNILVR.NS"],
    "Metals": ["TATASTEEL.NS","JSWSTEEL.NS","HINDALCO.NS"],
    "Power": ["NTPC.NS","POWERGRID.NS","TATAPOWER.NS"],
    "Finance": ["BAJFINANCE.NS","BAJAJFINSV.NS","CHOLAFIN.NS"]
}

selected_sector = st.selectbox("📊 Select Sector to Scan", list(sectors.keys()))
stocks_to_scan = sectors[selected_sector]

# =============================
# DATA FETCH
# =============================
@st.cache_data(ttl=120)
def get_data(tickers):
    # Fetch enough data for 200 EMA and Pivot Points
    return yf.download(tickers, period="60d", interval="15m", group_by="ticker", threads=True)

# =============================
# MODEL TRAINING
# =============================
@st.cache_resource
def train_model(X, y):
    model = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
    model.fit(X, y)
    return model

# =============================
# ADVANCED ANALYZERS (NEW FEATURES)
# =============================

# 1. Pivot Points Support & Resistance
def get_pivot_points(df):
    # Standard Pivot Points using Previous Day's High, Low, Close
    # Since we use 15m data, we need daily data for pivots. 
    # Here, we mimic daily pivots using rolling windows.
    recent = df.tail(10) # Using recent 15m bars to estimate
    high = recent['High'].max()
    low = recent['Low'].min()
    close = recent['Close'].iloc[-1]
    
    pivot = (high + low + close) / 3
    r1 = (2 * pivot) - low
    s1 = (2 * pivot) - high
    
    return round(s1, 2), round(r1, 2)

# 2. Volume Strength Analyzer
def get_volume_strength(df):
    recent_vol = df['Volume'].iloc[-1]
    avg_vol_20 = df['Volume'].rolling(20).mean().iloc[-1]
    vol_ratio = recent_vol / (avg_vol_20 + 1e-9)
    
    if vol_ratio >= 3.0: return "🐋 WHALE", "Blue"
    elif vol_ratio >= 2.0: return "👔 INSTITUTIONAL", "Green"
    elif vol_ratio >= 1.0: return "⚖️ NORMAL", "White"
    else: return "⚠️ WEAK", "Red"

# 3. Call/Put Strength Analyzer (PCR Mimic)
def get_option_strength(df):
    # Volume weighted sentiment for last 10 bars
    recent = df.tail(10)
    vol_bullish = recent[recent['Close'] >= recent['Open']]['Volume'].sum()
    vol_bearish = recent[recent['Close'] < recent['Open']]['Volume'].sum()
    
    pcr_ratio = round(vol_bullish / (vol_bearish + 1e-9), 2)
    
    if pcr_ratio > 1.8: return "🟢 CALLS STRONG", pcr_ratio
    elif pcr_ratio < 0.5: return "🔴 PUTS STRONG", pcr_ratio
    else: return "⚖️ NEUTRAL", pcr_ratio

# 4. Fake Breakout/Breakdown Detector
def get_breakout_status(df, s1, r1):
    price = df['Close'].iloc[-1]
    prev_price = df['Close'].iloc[-2]
    current_vol = df['Volume'].iloc[-1]
    avg_vol_20 = df['Volume'].rolling(20).mean().iloc[-1]
    
    status = "NO BREAKOUT"
    
    # BREAKOUT Logic
    if price > r1 and prev_price <= r1:
        if current_vol > avg_vol_20 * 1.5:
            status = "🚀 GENUINE BREAKOUT"
        else:
            status = "⚠️ FAKE BREAKOUT"
            
    # BREAKDOWN Logic
    elif price < s1 and prev_price >= s1:
        if current_vol > avg_vol_20 * 1.5:
            status = "🔻 GENUINE BREAKDOWN"
        else:
            status = "⚠️ FAKE BREAKDOWN"
            
    return status

# =============================
# CORE ANALYSIS ENGINE
# =============================
def analyze(df):
    df = df.copy()
    
    # Need enough data for 200 EMA
    if len(df) < 100: return None
    
    # Main Indicators
    df['EMA20'] = df['Close'].ewm(span=20).mean()
    df['EMA50'] = df['Close'].ewm(span=50).mean()
    df['EMA200'] = df['Close'].ewm(span=200).mean()
    
    # RSI & MACD
    df.ta.rsi(length=14, append=True)
    df.ta.macd(fast=12, slow=26, signal=9, append=True)
    
    df.dropna(inplace=True)

    # Current Values
    price = df['Close'].iloc[-1]
    ema50 = df['EMA50'].iloc[-1]
    ema200 = df['EMA200'].iloc[-1]
    rsi = df['RSI_14'].iloc[-1]
    macd = df['MACD_12_26_9'].iloc[-1]
    signal = df['MACDs_12_26_9'].iloc[-1]

    # Call new advanced modules
    s1, r1 = get_pivot_points(df)
    vol_status, vol_color = get_volume_strength(df)
    opt_sentiment, pcr_val = get_option_strength(df)
    breakout_status = get_breakout_status(df, s1, r1)

    # AI Prediction
    df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
    features = ['EMA20','EMA50','RSI_14','MACD_12_26_9']
    X = df[features].tail(60) # Train on recent 60 bars
    y = df['Target'].tail(60)
    
    if len(X) < 30: return None
    model = train_model(X, y)
    pred = model.predict(X.iloc[[-1]])[0]

    # Confidence Score (Weighted)
    confidence = 0
    # Trend (25%)
    if price > ema50 > ema200: confidence += 25
    elif price < ema50 < ema200: confidence -= 10 # Penalize against
