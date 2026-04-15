import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import requests
import time
from sklearn.ensemble import RandomForestClassifier
from streamlit_autorefresh import st_autorefresh

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(page_title="🔥 PRO NSE AI SCANNER AUTO ALERT", layout="wide")
st_autorefresh(interval=5000, key="refresh")

st.title("🔥 PRO NSE AI SCANNER (AUTO ALERT SYSTEM)")
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
# ENTRY LOGIC
# =============================
def get_entry_point(df, signal):
    prev = df.iloc[-2]

    if "BUY" in signal:
        entry = round(prev['High'], 2)
        sl = round(prev['Low'], 2)
        target = round(entry + (entry - sl)*1.5, 2)
    else:
        entry = round(prev['Low'], 2)
        sl = round(prev['High'], 2)
        target = round(entry - (sl - entry)*1.5, 2)

    return entry, sl, target

# =============================
# SCALPING
# =============================
def scalping_signal(df):
    df['EMA9'] = df['Close'].ewm(span=9).mean()
    df['EMA21'] = df['Close'].ewm(span=21).mean()
    last = df.iloc[-1]

    if last['EMA9'] > last['EMA21']:
        return "⚡ BUY"
    else:
        return "⚡ SELL"

# =============================
# OPTION CHAIN
# =============================
def get_option_chain():
    try:
        s = requests.Session()
        s.get("https://www.nseindia.com", headers=headers)
        url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
        data = s.get(url, headers=headers).json()

        ce, pe = 0, 0
        for i in data['records']['data']:
            if 'CE' in i and 'PE' in i:
                ce += i['CE']['openInterest']
                pe += i['PE']['openInterest']

        pcr = pe/(ce+1e-9)

        if pcr > 1.2:
            return "🔥 BULLISH"
        elif pcr < 0.8:
            return "🔻 BEARISH"
        else:
            return "⚖️ SIDEWAYS"
    except:
        return "N/A"

# =============================
# DATA
# =============================
sectors = {
    "Nifty 50": ["RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS"],
    "Banking": ["SBIN.NS","AXISBANK.NS","KOTAKBANK.NS"]
}

selected_sector = st.selectbox("📊 Sector", list(sectors.keys()))
stocks = sectors[selected_sector]

@st.cache_data(ttl=120)
def get_data(tickers):
    return yf.download(tickers, period="30d", interval="15m", group_by="ticker")

# =============================
# MODEL
# =============================
@st.cache_resource
def train(X,y):
    model = RandomForestClassifier(n_estimators=80)
    model.fit(X,y)
    return model

# =============================
# ANALYZE
# =============================
def analyze(df, stock):
    df = df.copy()

    df['EMA20'] = df['Close'].ewm(span=20).mean()
    df['EMA50'] = df['Close'].ewm(span=50).mean()

    df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
    df.dropna(inplace=True)

    X = df[['EMA20','EMA50']]
    y = df['Target']

    if len(X) < 50:
        return None

    model = train(X,y)
    pred = model.predict(X.iloc[[-1]])[0]

    signal = "🟢 BUY" if pred==1 else "🔴 SELL"

    price = get_live_price(stock)
    if not price:
        price = df['Close'].iloc[-1]

    entry, sl, target = get_entry_point(df, signal)

    scalp = scalping_signal(df)

    return signal, price, entry, sl, target, scalp

# =============================
# RUN
# =============================
data = get_data(stocks)
results = []

st.subheader("🔔 LIVE ENTRY ALERTS")

for stock in stocks:
    try:
        df = data[stock].dropna()
        out = analyze(df, stock)
        if out is None: continue

        signal, price, entry, sl, target, scalp = out

        # ALERT LOGIC
        alert = ""
        if "BUY" in signal and price >= entry:
            alert = "🚀 ENTRY BUY HIT"
            st.success(f"{stock} BUY ENTRY HIT at {price}")
            st.balloons()

        elif "SELL" in signal and price <= entry:
            alert = "🔻 ENTRY SELL HIT"
            st.error(f"{stock} SELL ENTRY HIT at {price}")

        results.append({
            "Stock": stock,
            "Signal": signal,
            "Price": round(price,2),
            "Entry": entry,
            "Stoploss": sl,
            "Target": target,
            "Scalping": scalp,
            "Alert": alert
        })

        time.sleep(0.5)

    except:
        continue

df = pd.DataFrame(results)

st.subheader("🔥 AUTO ALERT TRADING TABLE")
st.dataframe(df, use_container_width=True)

# OPTION MARKET
st.subheader("📊 OPTION MARKET")
st.write(get_option_chain())
