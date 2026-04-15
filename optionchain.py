import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import requests
import time
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from streamlit_autorefresh import st_autorefresh

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(page_title="🔥 PRO NSE AI SCANNER HEDGE FUND", layout="wide")
st_autorefresh(interval=8000, key="refresh")

st.title("🔥 PRO NSE AI SCANNER (AUTO BOT + AI)")
st.markdown("---")

headers = {"User-Agent": "Mozilla/5.0"}

# =============================
# LIVE PRICE
# =============================
def get_live_price(symbol):
    try:
        s = requests.Session()
        s.get("https://www.nseindia.com", headers=headers)
        url = f"https://www.nseindia.com/api/quote-equity?symbol={symbol.replace('.NS','')}"
        return s.get(url, headers=headers).json()['priceInfo']['lastPrice']
    except:
        return None

# =============================
# MULTI TIMEFRAME DATA
# =============================
def get_multi_tf(stock):
    df15 = yf.download(stock, period="30d", interval="15m")
    df5 = yf.download(stock, period="10d", interval="5m")
    df1h = yf.download(stock, period="60d", interval="1h")
    return df15, df5, df1h

# =============================
# TREND CHECK
# =============================
def trend_check(df):
    df['EMA20'] = df['Close'].ewm(span=20).mean()
    df['EMA50'] = df['Close'].ewm(span=50).mean()
    return "UP" if df['EMA20'].iloc[-1] > df['EMA50'].iloc[-1] else "DOWN"

# =============================
# ATM OPTION
# =============================
def get_atm(price, step=50):
    return int(round(price/step)*step)

# =============================
# AUTO BOT (ENTRY EXIT)
# =============================
def auto_trade(price, signal):
    target = round(price * 1.01,2) if "BUY" in signal else round(price * 0.99,2)
    sl = round(price * 0.99,2) if "BUY" in signal else round(price * 1.01,2)
    return target, sl

# =============================
# MODEL (ENSEMBLE)
# =============================
@st.cache_resource
def train_models(X, y):
    rf = RandomForestClassifier(n_estimators=100)
    gb = GradientBoostingClassifier()
    rf.fit(X,y)
    gb.fit(X,y)
    return rf, gb

# =============================
# ANALYZE
# =============================
def analyze(stock):
    df15, df5, df1h = get_multi_tf(stock)

    df = df15.copy()
    df['EMA20'] = df['Close'].ewm(span=20).mean()
    df['EMA50'] = df['Close'].ewm(span=50).mean()

    df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
    df.dropna(inplace=True)

    X = df[['EMA20','EMA50']]
    y = df['Target']

    if len(X) < 50:
        return None

    rf, gb = train_models(X,y)

    pred1 = rf.predict(X.iloc[[-1]])[0]
    pred2 = gb.predict(X.iloc[[-1]])[0]

    pred = 1 if (pred1 + pred2) >= 1 else 0

    signal = "🟢 BUY" if pred==1 else "🔴 SELL"

    # MULTI TF CONFIRM
    t15 = trend_check(df15)
    t5 = trend_check(df5)
    t1h = trend_check(df1h)

    mtf = f"{t5}/{t15}/{t1h}"

    # LIVE PRICE
    price = get_live_price(stock)
    if not price:
        price = df['Close'].iloc[-1]

    # AUTO BOT
    target, sl = auto_trade(price, signal)

    # ATM
    atm = get_atm(price)
    option = f"{atm} CE" if pred==1 else f"{atm} PE"

    return signal, price, target, sl, option, mtf

# =============================
# SECTORS
# =============================
sectors = {
    "Nifty 50": ["RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS"],
    "Banking": ["SBIN.NS","AXISBANK.NS","KOTAKBANK.NS"]
}

sec = st.selectbox("Select Sector", list(sectors.keys()))

results = []

for stock in sectors[sec]:
    try:
        out = analyze(stock)
        if out is None: continue

        signal, price, target, sl, option, mtf = out

        results.append({
            "Stock": stock,
            "Signal": signal,
            "Price": round(price,2),
            "Target": target,
            "Stoploss": sl,
            "ATM Option": option,
            "Multi TF Trend": mtf
        })

        time.sleep(0.5)
    except:
        continue

df = pd.DataFrame(results)

st.subheader("🔥 AUTO TRADING SIGNALS")
st.dataframe(df, use_container_width=True)
