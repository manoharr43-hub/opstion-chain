import streamlit as st
import pandas as pd
import numpy as np
import requests
import yfinance as yf
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="🔥 NSE AI TRADING V2", layout="wide")
st_autorefresh(interval=20000, key="refresh")

st.title("🔥 NSE AI Trading System V2 (LIVE + AI + BOT)")

# =========================
# LIVE PRICE
# =========================
def get_price(symbol="^NSEI"):
    data = yf.download(symbol, period="5d", interval="5m")
    return data

# =========================
# OPTION CHAIN (NSE)
# =========================
def get_option_chain(symbol="NIFTY"):
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "accept": "application/json"
    }
    session = requests.Session()
    session.get("https://www.nseindia.com", headers=headers)
    response = session.get(url, headers=headers)
    return response.json()

def parse_option_chain(data):
    records = data['records']['data']
    calls = []
    puts = []

    for item in records:
        if "CE" in item:
            calls.append(item["CE"])
        if "PE" in item:
            puts.append(item["PE"])

    return pd.DataFrame(calls), pd.DataFrame(puts)

# =========================
# SMART MONEY FLOW (SIMULATED)
# =========================
def smart_money_flow():
    fii = np.random.randint(-500, 1500)
    dii = np.random.randint(-300, 1200)
    return fii, dii

# =========================
# SCALPING SIGNAL ENGINE
# =========================
def scalping_signal(df):
    df["ema5"] = df["Close"].ewm(span=5).mean()
    df["ema20"] = df["Close"].ewm(span=20).mean()

    if df["ema5"].iloc[-1] > df["ema20"].iloc[-1]:
        return "🟢 BUY SIGNAL"
    else:
        return "🔴 SELL SIGNAL"

# =========================
# LSTM PREDICTION (SIMPLE)
# =========================
def lstm_predict(df):
    data = df["Close"].values.reshape(-1, 1)

    scaler = MinMaxScaler()
    data_scaled = scaler.fit_transform(data)

    X, y = [], []
    for i in range(10, len(data_scaled)):
        X.append(data_scaled[i-10:i, 0])
        y.append(data_scaled[i, 0])

    X, y = np.array(X), np.array(y)
    X = X.reshape((X.shape[0], X.shape[1], 1))

    model = Sequential()
    model.add(LSTM(50, return_sequences=True, input_shape=(X.shape[1], 1)))
    model.add(LSTM(50))
    model.add(Dense(1))

    model.compile(optimizer="adam", loss="mse")
    model.fit(X, y, epochs=3, batch_size=16, verbose=0)

    pred = model.predict(X[-1].reshape(1, 10, 1))
    return scaler.inverse_transform(pred)[0][0]

# =========================
# AUTO TRADING BOT (SIMULATION)
# =========================
def auto_bot(signal):
    if "BUY" in signal:
        return "✅ AUTO BUY EXECUTED (SIMULATED)"
    else:
        return "❌ AUTO SELL EXECUTED (SIMULATED)"

# =========================
# UI
# =========================
symbol = st.selectbox("Select Index", ["^NSEI", "^NSEBANK"])

data = get_price(symbol)

st.subheader("📊 LIVE PRICE CHART")
st.line_chart(data["Close"])

# =========================
# OPTION CHAIN
# =========================
st.subheader("🟢 OPTION CHAIN")
try:
    oc = get_option_chain("NIFTY")
    calls, puts = parse_option_chain(oc)

    st.write("CALLS")
    st.dataframe(calls.head(10))

    st.write("PUTS")
    st.dataframe(puts.head(10))

except:
    st.warning("Option Chain load error (NSE blocking sometimes)")

# =========================
# SMART MONEY FLOW
# =========================
st.subheader("🟢 SMART MONEY FLOW (FII/DII)")
fii, dii = smart_money_flow()

st.metric("FII Flow", fii)
st.metric("DII Flow", dii)

# =========================
# SCALPING SIGNAL
# =========================
st.subheader("📊 SCALPING SIGNAL")
signal = scalping_signal(data)
st.success(signal)

# =========================
# LSTM PREDICTION
# =========================
st.subheader("⚡ LSTM PRICE PREDICTION")
try:
    pred = lstm_predict(data)
    st.info(f"Next Predicted Price: {pred}")
except:
    st.warning("LSTM training error (low data)")

# =========================
# AUTO BOT
# =========================
st.subheader("🔵 AUTO BUY/SELL BOT")
bot_result = auto_bot(signal)
st.write(bot_result)
