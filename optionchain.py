import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from streamlit_autorefresh import st_autorefresh

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(page_title="🔥 PRO NSE AI SCANNER ULTIMATE V6", layout="wide")
st_autorefresh(interval=10000, key="refresh")

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
# DATA FETCH (FAST + STABLE)
# =============================
@st.cache_data(ttl=300)
def get_data(tickers):
    return yf.download(
        tickers,
        period="60d",
        interval="15m",
        group_by="ticker",
        threads=True,
        progress=False
    )

# =============================
# MODEL (NO RE-TRAIN ISSUE FIX)
# =============================
@st.cache_resource
def get_model():
    return RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)

# =============================
# PIVOT POINTS
# =============================
def get_pivot_points(df):
    recent = df.tail(10)
    high = recent["High"].max()
    low = recent["Low"].min()
    close = recent["Close"].iloc[-1]

    pivot = (high + low + close) / 3
    r1 = (2 * pivot) - low
    s1 = (2 * pivot) - high

    return round(s1, 2), round(r1, 2)

# =============================
# SHORT COVERING
# =============================
def get_short_covering_status(df):
    if len(df) < 20:
        return "NA", "White", 0

    current_price = df["Close"].iloc[-1]
    price_change_pct = ((current_price - df["Close"].iloc[-2]) / df["Close"].iloc[-2]) * 100

    avg_vol = df["Volume"].rolling(20).mean().iloc[-1]
    vol_ratio = df["Volume"].iloc[-1] / (avg_vol + 1e-9)

    if price_change_pct > 0.8 and vol_ratio >= 1.8 and current_price > df["Close"].rolling(50).mean().iloc[-1]:
        return "⚡ SHORT COVERING", "Cyan", 30
    elif price_change_pct > 0.4 and vol_ratio >= 1.4:
        return "⚖️ VOLUME BREAKOUT", "LightBlue", 10
    else:
        return "⚖️ NORMAL VOL", "White", 0

# =============================
# OPTION STRENGTH (PCR STYLE)
# =============================
def get_option_strength(df):
    recent = df.tail(10)
    bull = recent[recent["Close"] >= recent["Open"]]["Volume"].sum()
    bear = recent[recent["Close"] < recent["Open"]]["Volume"].sum()

    ratio = bull / (bear + 1e-9)

    if ratio > 1.8:
        return "🟢 CALLS STRONG", ratio
    elif ratio < 0.5:
        return "🔴 PUTS STRONG", ratio
    else:
        return "⚖️ NEUTRAL", ratio

# =============================
# BREAKOUT CHECK
# =============================
def get_breakout_status(df, s1, r1):
    price = df["Close"].iloc[-1]
    prev = df["Close"].iloc[-2]

    vol = df["Volume"].iloc[-1]
    avg_vol = df["Volume"].rolling(20).mean().iloc[-1]

    if price > r1 and prev <= r1:
        return "🚀 GENUINE BREAKOUT" if vol > avg_vol * 1.5 else "⚠️ FAKE BREAKOUT"
    elif price < s1 and prev >= s1:
        return "🔻 GENUINE BREAKDOWN" if vol > avg_vol * 1.5 else "⚠️ FAKE BREAKDOWN"
    return "NO BREAKOUT"

# =============================
# CORE ANALYSIS ENGINE
# =============================
def analyze(df):
    df = df.copy()

    if len(df) < 100:
        return None

    # indicators
    df["EMA20"] = df["Close"].ewm(span=20).mean()
    df["EMA50"] = df["Close"].ewm(span=50).mean()
    df["EMA200"] = df["Close"].ewm(span=200).mean()

    delta = df["Close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = -delta.clip(upper=0).rolling(14).mean()
    rs = gain / (loss + 1e-9)
    df["RSI"] = 100 - (100 / (1 + rs))

    df["EMA12"] = df["Close"].ewm(span=12).mean()
    df["EMA26"] = df["Close"].ewm(span=26).mean()
    df["MACD"] = df["EMA12"] - df["EMA26"]
    df["Signal"] = df["MACD"].ewm(span=9).mean()

    df = df.fillna(method="ffill").dropna()

    df = df.iloc[:-1].copy()
    df["Target"] = (df["Close"].shift(-1) > df["Close"]).astype(int)

    features = ["EMA20", "EMA50", "RSI", "MACD"]

    X = df[features].tail(60)
    y = df["Target"].tail(60)

    if len(X) < 30:
        return None

    model = get_model()
    model.fit(X, y)

    pred = model.predict(X.iloc[[-1]])[0]

    price = df["Close"].iloc[-1]

    s1, r1 = get_pivot_points(df)
    covering, _, _ = get_short_covering_status(df)
    opt_sentiment, pcr = get_option_strength(df)
    breakout = get_breakout_status(df, s1, r1)

    confidence = 0
    if price > df["EMA50"].iloc[-1] > df["EMA200"].iloc[-1]:
        confidence += 25
    if pred == 1:
        confidence += 20
    if "CALLS STRONG" in opt_sentiment:
        confidence += 15
    if "SHORT
