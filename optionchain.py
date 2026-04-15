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
st.set_page_config(page_title="🔥 PRO NSE AI SCANNER ULTIMATE", layout="wide")
st_autorefresh(interval=8000, key="refresh")

st.title("🔥 PRO NSE AI SCANNER (LIVE + OPTION CHAIN)")
st.markdown("---")

# =============================
# NSE HEADERS
# =============================
headers = {"User-Agent": "Mozilla/5.0"}

# =============================
# LIVE PRICE FUNCTION
# =============================
def get_live_price(symbol):
    url = f"https://www.nseindia.com/api/quote-equity?symbol={symbol.replace('.NS','')}"
    try:
        session = requests.Session()
        session.get("https://www.nseindia.com", headers=headers)
        data = session.get(url, headers=headers).json()
        return data['priceInfo']['lastPrice']
    except:
        return None

# =============================
# OPTION CHAIN FUNCTIONS
# =============================
def get_option_chain(symbol="NIFTY"):
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
    try:
        session = requests.Session()
        session.get("https://www.nseindia.com", headers=headers)
        return session.get(url, headers=headers).json()
    except:
        return None

def get_pcr_signal(data):
    try:
        ce_oi, pe_oi = 0, 0
        for item in data['records']['data']:
            if 'CE' in item and 'PE' in item:
                ce_oi += item['CE']['openInterest']
                pe_oi += item['PE']['openInterest']
        pcr = pe_oi / (ce_oi + 1e-9)

        if pcr > 1.2:
            return "🔥 BULLISH"
        elif pcr < 0.8:
            return "🔻 BEARISH"
        else:
            return "⚖️ SIDEWAYS"
    except:
        return "N/A"

# =============================
# SECTORS
# =============================
sectors = {
    "Nifty 50": ["RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS"],
    "Banking": ["SBIN.NS","AXISBANK.NS","KOTAKBANK.NS","PNB.NS"],
    "IT": ["WIPRO.NS","HCLTECH.NS","TECHM.NS"],
    "Auto": ["MARUTI.NS","M&M.NS","TATAMOTORS.NS"],
    "Pharma": ["SUNPHARMA.NS","DRREDDY.NS","CIPLA.NS"],
    "Energy": ["ONGC.NS","IOC.NS"],
    "FMCG": ["ITC.NS","NESTLEIND.NS"],
    "Metals": ["TATASTEEL.NS","JSWSTEEL.NS"],
    "Power": ["NTPC.NS","POWERGRID.NS"],
    "Finance": ["BAJFINANCE.NS","BAJAJFINSV.NS"]
}

selected_sector = st.selectbox("📊 Select Sector", list(sectors.keys()))
stocks_to_scan = sectors[selected_sector]

# =============================
# DATA FETCH
# =============================
@st.cache_data(ttl=120)
def get_data(tickers):
    return yf.download(tickers, period="60d", interval="15m", group_by="ticker")

# =============================
# MODEL
# =============================
@st.cache_resource
def train_model(X, y):
    model = RandomForestClassifier(n_estimators=80, max_depth=6, random_state=42)
    model.fit(X, y)
    return model

# =============================
# ANALYSIS ENGINE
# =============================
def analyze(df, stock):
    df = df.copy()

    # EMA
    df['EMA20'] = df['Close'].ewm(span=20).mean()
    df['EMA50'] = df['Close'].ewm(span=50).mean()

    # RSI
    delta = df['Close'].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = -delta.clip(upper=0).rolling(14).mean()
    rs = gain / (loss + 1e-9)
    df['RSI'] = 100 - (100 / (1 + rs))

    # MACD
    df['EMA12'] = df['Close'].ewm(span=12).mean()
    df['EMA26'] = df['Close'].ewm(span=26).mean()
    df['MACD'] = df['EMA12'] - df['EMA26']
    df['Signal'] = df['MACD'].ewm(span=9).mean()

    df.dropna(inplace=True)

    # TARGET
    df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
    df.dropna(inplace=True)

    features = ['EMA20','EMA50','RSI','MACD']
    X = df[features]
    y = df['Target']

    if len(X) < 50:
        return None

    model = train_model(X, y)
    pred = model.predict(X.iloc[[-1]])[0]

    # LIVE PRICE
    live_price = get_live_price(stock)
    price = live_price if live_price else df['Close'].iloc[-1]

    support = df['Low'].tail(40).min()
    resistance = df['High'].tail(40).max()

    # BIG PLAYER
    avg_vol = df['Volume'].rolling(20).mean().iloc[-1]
    vol_ratio = df['Volume'].iloc[-1] / (avg_vol + 1e-9)

    if vol_ratio > 2:
        big = "🔥 BIG BUYER"
    elif vol_ratio < 0.5:
        big = "🔻 BIG SELLER"
    else:
        big = "⚖️ NORMAL"

    # CONFIDENCE
    confidence = 0
    if price > df['EMA20'].iloc[-1] > df['EMA50'].iloc[-1]: confidence += 20
    if 40 < df['RSI'].iloc[-1] < 60: confidence += 15
    if df['MACD'].iloc[-1] > df['Signal'].iloc[-1]: confidence += 20
    if pred == 1: confidence += 20
    if vol_ratio > 1.5: confidence += 15
    if price <= support*1.02 or price >= resistance*0.98: confidence += 10

    if confidence >= 85:
        final = "🔥 HIGH PROBABILITY"
    elif confidence >= 60:
        final = "⚡ WATCH"
    else:
        final = "❌ AVOID"

    signal_text = "🟢 BUY" if pred == 1 else "🔴 SELL"
    entry = round(price,2)
    stoploss = round(support,2) if pred==1 else round(resistance,2)

    opt_sentiment = "CALL STRONG" if pred==1 else "PUT STRONG"

    return final, signal_text, confidence, price, support, resistance, big, entry, stoploss, opt_sentiment

# =============================
# BACKTEST
# =============================
def backtest(df):
    df = df.copy()
    df['EMA20'] = df['Close'].ewm(span=20).mean()
    df['EMA50'] = df['Close'].ewm(span=50).mean()
    df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
    df.dropna(inplace=True)

    correct, total = 0, 0
    for i in range(50, len(df)-1):
        pred = 1 if df['EMA20'].iloc[i] > df['EMA50'].iloc[i] else 0
        if pred == df['Target'].iloc[i]:
            correct += 1
        total += 1
    return round((correct/total)*100,2) if total > 0 else 0

# =============================
# SCANNER EXECUTION
# =============================
data = get_data(stocks_to_scan)
results = []

if data is not None:
    for stock in stocks_to_scan:
        try:
            df = data[stock].dropna()
            out = analyze(df, stock)
            if out is None: continue

            final, signal_text, confidence, price, support, resistance, big, entry, stoploss, opt_sentiment = out
            winrate = backtest(df)

            results.append({
                "Stock": stock,
                "Price": round(price,2),
                "Signal": signal_text,
                "Confidence": confidence,
                "Final": final,
                "Big Player": big,
                "Support": round(support,2),
                "Resistance": round(resistance,2),
                "Entry": entry,
                "Stoploss": stoploss,
                "WinRate%": winrate,
                "Option Sentiment": opt_sentiment
            })

            time.sleep(0.5)

        except:
            continue

    result_df = pd.DataFrame(results).sort_values(by="Confidence", ascending=False)

    st.subheader(f"🔥 {selected_sector} TOP TRADES")
    st.dataframe(result_df, use_container_width=True)

    st.subheader("🔥 HIGH PROBABILITY ONLY")
    st.dataframe(result_df[result_df["Confidence"] >= 85], use_container_width=True)

    # OPTION CHAIN DISPLAY
    st.subheader("📊 OPTION CHAIN SIGNAL")
    opt_data = get_option_chain("NIFTY")
    signal = get_pcr_signal(opt_data)
    st.write("Market Sentiment:", signal)

    # STRONG BUY / SELL
    st.subheader("📊 NSE Strong BUY Stocks")
    st.dataframe(result_df[(result_df["Confidence"] >= 85) & (result_df["Signal"].str.contains("BUY"))])

    st.subheader("📊 NSE Strong SELL Stocks")
    st.dataframe(result_df[(result_df["Confidence"] >= 85) & (result_df["Signal"].str.contains("SELL"))])
