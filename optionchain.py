import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from streamlit_autorefresh import st_autorefresh
from nsepython import nse_quote_meta, nse_get_top_gainers_losers, nse_get_fno_lot_size
import time
from datetime import datetime, timedelta

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(page_title="🔥 PRO NSE AI SCANNER V7 (NSEPYTHON)", layout="wide")
st_autorefresh(interval=10000, key="refresh") # 10 seconds refresh

st.title("🔥 PRO NSE AI SCANNER (NSEPYTHON EDITION - ULTIMATE)")
st.markdown("---")

# =============================
# SECTORS (NSE Symbols)
# =============================
sectors = {
    "Nifty 50 Gainers/Losers": "gainers_losers", # SPECIAL CASE
    "Banking": ["SBIN","AXISBANK","KOTAKBANK","PNB","HDFCBANK","ICICIBANK"],
    "IT": ["WIPRO","HCLTECH","TECHM","INFY","TCS"],
    "Auto": ["MARUTI","M&M","TATAMOTORS","HEROMOTOCO","BAJAJ-AUTO"],
    "Pharma": ["SUNPHARMA","DRREDDY","CIPLA","APOLLOHOSP","DIVISLAB"],
    "Energy": ["ONGC","IOC","BPCL","GAIL","RELIANCE"],
    "FMCG": ["ITC","NESTLEIND","HINDUNILVR","BRITANNIA"],
    "Metals": ["TATASTEEL","JSWSTEEL","HINDALCO","VEDL"],
    "Power": ["NTPC","POWERGRID","TATAPOWER","ADANIGREEN"],
    "Finance": ["BAJFINANCE","BAJAJFINSV","CHOLAFIN","M&MFIN"]
}

selected_sector = st.selectbox("📊 Select Sector to Scan", list(sectors.keys()))

# =============================
# DATA FETCH (NSEPYTHON BASED)
# =============================
@st.cache_data(ttl=60) # Short TTL for live data
def get_live_data(symbol):
    try:
        meta = nse_quote_meta(symbol)
        if meta and 'data' in meta:
            data = meta['data'][0]
            # NSE data structure construct
            return {
                "Symbol": symbol,
                "LTP": data['lastPrice'],
                "Change%": data['pChange'],
                "Open": data['open'],
                "High": data['dayHigh'],
                "Low": data['dayLow'],
                "PrevClose": data['previousClose'],
                "Volume": data['totalTradedVolume'],
                "Value": data['totalTradedValue'],
                "VWAP": data['basePrice'] # Base price as proxy if VWAP not direct
            }
    except Exception as e:
        return None
    return None

def get_sector_symbols(sector_key):
    if sector_key == "gainers_losers":
        try:
            gainers = nse_get_top_gainers_losers("gainers")
            losers = nse_get_top_gainers_losers("losers")
            symbols = [d['symbol'] for d in gainers['data']] + [d['symbol'] for d in losers['data']]
            return list(set(symbols)) # Unique symbols
        except:
            return []
    else:
        return sectors[sector_key]

stocks_to_scan = get_sector_symbols(selected_sector)

# =============================
# MODEL TRAINING (Constructed from metadata)
# =============================
@st.cache_resource
def train_model(X, y):
    # Mimicking original params
    model = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
    model.fit(X, y)
    return model

# =============================
# ADVANCED ANALYZERS (NEW FEATURES using NSE Data)
# =============================

# 1. Pivot Points S/R (Mimicked Daily Pivots from NSE data)
def get_pivot_points(live_data):
    high = live_data['High']
    low = live_data['Low']
    close = live_data['LTP']
    
    pivot = (high + low + close) / 3
    r1 = (2 * pivot) - low
    s1 = (2 * pivot) - high
    
    return round(s1, 2), round(r1, 2)

# 2. Volume Strength Analyzer (Mimics VSA logic)
def get_volume_strength(live_data):
    # Volume constructed from metadata
    recent_vol = live_data['Volume']
    
    # Heuristic average volume check
    # In live trading, we'd need historical average. 
    # nsepython doesn't easily provide average vol without iteration.
    # Mimicking logic with high threshold on raw vol (simplified)
    if recent_vol >= 5000000: return "🐋 WHALE ENTRY", "Blue", 25
    elif recent_vol >= 2000000: return "👔 INSTITUTIONAL", "Green", 15
    elif recent_vol >= 500000: return "⚖️ NORMAL", "White", 0
    else: return "⚠️ WEAK PARTICIPATION", "Red", -5

# 3. Short Covering Detector (Mimics Price-Vol Spike logic)
def get_short_covering_status(live_data):
    current_price = live_data['LTP']
    prev_close = live_data['PrevClose']
    current_vol = live_data['Volume']
    
    price_change_pct = live_data['Change%']
    
    # Short covering condition: Sudden price spike + Sudden volume spike
    # Heuristic check
    if price_change_pct > 1.5
