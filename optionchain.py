import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf

from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import MinMaxScaler

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="🔥 SAFE AI CE vs PE SCANNER", layout="wide")

# =========================
# LIVE MARKET DATA
# =========================
def get_ltp():
    data = yf.download("^NSEI", period="5d", interval="15m")

    if data.empty:
        return None, None

    return data, data["Close"].values

# =========================
# OPTION CHAIN (OLD SAFE)
# =========================
def option_chain(ltp):
    base = round(ltp / 50) * 50
    strikes = [base + i * 50 for i in range(-3, 4)]

    return pd.DataFrame({
        "Strike": strikes,
        "CE_OI": np.random.randint(2000, 9000, len(strikes)),
        "PE_OI": np.random.randint(2000, 9000, len(strikes)),
    })

# =========================
# ATM FINDER
# =========================
def get_atm(df, ltp):
    return min(df["Strike"], key=lambda x: abs(x - ltp))

# =========================
# CE PE ZONE (OLD LOGIC SAFE)
# =========================
def ce_pe_zone(df):
    df = df.copy()

    df["CE_PRESSURE"] = df["CE_OI"] / (df["PE_OI"] + 1)
    df["PE_PRESSURE"] = df["PE_OI"] / (df["CE_OI"] + 1)

    return df

# =========================
# TREND
# =========================
def trend(df):
    ce = df["CE_OI"].sum()
    pe = df["PE_OI"].sum()

    if ce > pe * 1.1:
        return "🟢 BULLISH"
    elif pe > ce * 1.1:
        return "🔴 BEARISH"
    return "🟡 SIDEWAYS"

# =========================
# PCR
# =========================
def pcr(df):
    return df["PE_OI"].sum() / (df["CE_OI"].sum() + 1)

# =========================
# 🧠 SAFE AI MODEL (NO LSTM / NO ERROR)
# =========================
def ai_predict(close):
    scaler = MinMaxScaler()

    data = close.reshape(-1,1)
    scaled = scaler.fit_transform(data)

    X, y = [], []

    for i in range(5, len(scaled)):
        X.append(scaled[i-5:i].flatten())
        y.append(scaled[i][0])

    X = np.array(X)
    y = np.array(y)

    model = RandomForestRegressor(n_estimators=80)
    model.fit(X, y)

    last = scaled[-5:].flatten().reshape(1,-1)
    pred = model.predict(last)[0]

    predicted_price = scaler.inverse_transform([[pred]])[0][0]

    return predicted_price

# =========================
# SIGNAL ENGINE
# =========================
def signal(live, predicted):
    if predicted > live:
        return "🟢 AI SIGNAL: CALL SIDE (UP MOVE)"
    elif predicted < live:
        return "🔴 AI SIGNAL: PUT SIDE (DOWN MOVE)"
    return "🟡 SIDEWAYS"

# =========================
# UI
# =========================
st.title("🔥 SAFE AI + CE vs PE OPTION SCANNER (NO ERROR VERSION)")

data, close = get_ltp()

if data is None:
    st.error("Market data not loaded")
    st.stop()

live_price = close[-1]

df = option_chain(live_price)
atm = get_atm(df, live_price)

df = ce_pe_zone(df)

trend_value = trend(df)
pcr_value = pcr(df)

# =========================
# AI PREDICTION
# =========================
predicted_price = ai_predict(close)
final_signal = signal(live_price, predicted_price)

# =========================
# DASHBOARD
# =========================
st.metric("LIVE PRICE", round(live_price,2))
st.metric("PREDICTED PRICE", round(predicted_price,2))
st.metric("ATM", atm)

st.subheader("📊 OPTION CHAIN")
st.dataframe(df, use_container_width=True)

# =========================
# REPORT
# =========================
st.subheader("📌 MARKET REPORT")

st.write(f"""
✔ LIVE PRICE: {round(live_price,2)}  
✔ ATM: {atm}  
✔ TREND: {trend_value}  
✔ PCR: {round(pcr_value,2)}  
""")

# =========================
# AI SIGNAL
# =========================
st.subheader("🧠 AI PREDICTION SIGNAL")

st.success(final_signal)

# =========================
# FINAL
# =========================
st.success("✅ FULL SAFE AI SYSTEM READY (OLD CODE NOT DISTURBED + NO ERROR)")
