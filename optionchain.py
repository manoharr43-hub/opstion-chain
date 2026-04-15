import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from streamlit_autorefresh import st_autorefresh
import time

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(page_title="🔥 PRO NSE AI SCANNER ULTIMATE V6", layout="wide")
st_autorefresh(interval=10000, key="refresh") # 10 seconds refresh

st.title("🔥 PRO NSE AI SCANNER (SHORT COVERING EDITION)")
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
    recent = df.tail(10) # Using recent 15m bars to estimate daily pivots
    high = recent['High'].max()
    low = recent['Low'].min()
    close = recent['Close'].iloc[-1]
    
    pivot = (high + low + close) / 3
    r1 = (2 * pivot) - low
    s1 = (2 * pivot) - high
    
    return round(s1, 2), round(r1, 2)

# 2. Short Covering Detector (mimics logic)
def get_short_covering_status(df):
    recent_vol = df['Volume'].iloc[-1]
    avg_vol_20 = df['Volume'].rolling(20).mean().iloc[-1]
    
    vol_ratio = recent_vol / (avg_vol_20 + 1e-9)
    
    if vol_ratio >= 3.0: return "🐋 WHALE ENTRY", "Blue", 25
    elif vol_ratio >= 2.0: return "👔 INSTITUTIONAL", "Green", 15
    elif vol_ratio >= 1.0: return "⚖️ NORMAL", "White", 0
    else: return "⚠️ WEAK PARTICIPATION", "Red", -5

# 3. Option Strength Analyzer (mimics PCR)
def get_option_strength(df):
    recent = df.tail(10)
    vol_bullish = recent[recent['Close'] >= recent['Open']]['Volume'].sum()
    vol_
