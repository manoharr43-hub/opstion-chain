import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from streamlit_autorefresh import st_autorefresh
import requests

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(page_title="🔥 PRO NSE AI SCANNER V7 MAX", layout="wide")
st_autorefresh(interval=30000, key="refresh")

st.title("🔥 PRO NSE AI SCANNER (ULTIMATE VERSION)")
st.markdown("---")

# =============================
# FAST MODE
# =============================
fast_mode = st.checkbox("⚡ Fast Mode", value=True)

# =============================
# SECTORS
# =============================
sectors = {
    "Nifty 50": ["RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS"],
    "Banking": ["SBIN.NS","AXISBANK.NS","KOTAKBANK.NS"],
    "IT": ["WIPRO.NS","HCLTECH.NS","TECHM.NS"],
    "Auto": ["MARUTI.NS","M&M.NS","TATAMOTORS.NS"]
}

selected_sector = st.selectbox("📊 Select Sector", list(sectors.keys()))
stocks_to_scan = sectors[selected_sector]

# =============================
# TELEGRAM (OPTIONAL)
# =============================
TELEGRAM_TOKEN = ""
CHAT_ID = ""

def send_telegram(msg):
    if TELEGRAM_TOKEN == "" or CHAT_ID == "":
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except:
        pass

# =============================
# DATA FETCH
# =============================
@st.cache_data(ttl=120)
def get_data(tickers):
    return yf.download(tickers, period="30d", interval="15m", group_by="ticker", threads=True)

# =============================
# OPTIMIZER
# =============================
def optimize_data(data):
    try:
        if isinstance(data.columns, pd.MultiIndex):
            for col in data.columns.levels[0]:
                data[col] = data[col].tail(300)
        else:
            data = data.tail(300)
    except:
        pass
    return data

# =============================
# INDICATORS
# =============================
def calculate_indicators(df):
    df = df.copy()

    df['EMA20'] = df['Close'].ewm(span=20).mean()
    df['EMA50'] = df['Close'].ewm(span=50).mean()

    df['EMA12'] = df['Close'].ewm(span=12).mean()
    df['EMA26'] = df['Close'].ewm(span=26).mean()
    df['MACD'] = df['EMA12'] - df['EMA26']
    df['Signal'] = df['MACD'].ewm(span=9).mean()

    delta = df['Close'].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = -delta.clip(upper=0).rolling(14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100/(1+rs))

    return df

# =============================
# BACKTEST
# =============================
def backtest(df):
    correct = 0
    total = 0
    for i in range(50, len(df)-1):
        if df['Close'][i] > df['EMA50'][i]:
            if df['Close'][i+1] > df['Close'][i]:
                correct += 1
            total += 1
    return round((correct/total)*100,2) if total
