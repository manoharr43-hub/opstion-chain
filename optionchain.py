import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf

from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="🔥 LSTM AI OPTION PREDICTOR", layout="wide")

# =========================
# LIVE LTP
# =========================
def get_ltp():
    data = yf.download("^NSEI", period="5d", interval="15m")

    if data.empty:
        return None, None

    close = data["Close"].values
    return data, close

# =========================
# OPTION CHAIN (OLD SAFE)
# =========================
def option_chain(ltp):
    base = round(ltp / 50) * 50
    strikes = [base + i * 50 for i in range(-3, 4)]

    return pd.DataFrame({
        "Strike": strikes,
        "CE_OI": np.random.randint(2000, 8000, len(strikes)),
        "PE_OI": np.random.randint(2000, 8000, len(strikes)),
    })

# =========================
# ATM
# =========================
def get_atm(df, ltp):
    return min(df["Strike"], key=lambda x: abs(x - ltp))

# =========================
# LSTM DATA PREP
# =========================
def prepare_data(data):
    scaler = MinMaxScaler(feature_range=(0,1))
    scaled = scaler.fit_transform(data.reshape(-1,1))

    X, y = [], []

    for i in range(10, len(scaled)):
        X.append(scaled[i-10:i, 0])
        y.append(scaled[i, 0])

    X, y = np.array(X), np.array(y)
    X = X.reshape(X.shape[0], X.shape[1], 1)

    return X, y, scaler

# =========================
# LSTM MODEL
# =========================
def build_lstm():
    model = Sequential()

    model.add(LSTM(units=50, return_sequences=True, input_shape=(10,1)))
    model.add(LSTM(units=50))
    model.add(Dense(1))

    model.compile(optimizer="adam", loss="mean_squared_error")

    return model

# =========================
# LSTM PREDICTION
# =========================
def lstm_predict(close):
    X, y, scaler = prepare_data(close)

    model = build_lstm()
    model.fit(X, y, epochs=3, batch_size=8, verbose=0)

    last_10 = close[-10:]
    last_10_scaled = scaler.transform(last_10.reshape(-1,1))

    X_test = last_10_scaled.reshape(1,10,1)

    pred = model.predict(X_test, verbose=0)
    predicted_price = scaler.inverse_transform(pred)[0][0]

    return predicted_price

# =========================
# SIGNAL ENGINE
# =========================
def signal(live, predicted):
    if predicted > live:
        return "🟢 LSTM SIGNAL: MARKET GOING UP (CALL SIDE)"
    elif predicted < live:
        return "🔴 LSTM SIGNAL: MARKET GOING DOWN (PUT SIDE)"
    else:
        return "🟡 SIDEWAYS"

# =========================
# CE/PE ZONE (OLD SAFE)
# =========================
def ce_pe_zone(df):
    df["CE_PRESSURE"] = df["CE_OI"] / (df["PE_OI"] + 1)
    df["PE_PRESSURE"] = df["PE_OI"] / (df["CE_OI"] + 1)

    return df

# =========================
# UI
# =========================
st.title("🔥 ADVANCED LSTM AI MARKET PREDICTOR")

data, close = get_ltp()

if data is None:
    st.error("Data not loaded")
    st.stop()

live_price = close[-1]

df = option_chain(live_price)
atm = get_atm(df, live_price)

df = ce_pe_zone(df)

# =========================
# LSTM PREDICTION
# =========================
st.subheader("🧠 LSTM AI MODEL TRAINING...")

predicted_price = lstm_predict(close)

final_signal = signal(live_price, predicted_price)

# =========================
# DASHBOARD
# =========================
st.metric("LIVE NIFTY", round(live_price,2))
st.metric("PREDICTED PRICE", round(predicted_price,2))
st.metric("ATM", atm)

st.subheader("📊 OPTION CHAIN")
st.dataframe(df)

# =========================
# AI RESULT
# =========================
st.subheader("🚀 LSTM AI SIGNAL")
st.success(final_signal)

# =========================
# SUMMARY
# =========================
st.write("""
✔ OLD CE/PE SYSTEM SAFE  
✔ NEW LSTM AI MODEL ADDED  
✔ MARKET DIRECTION PREDICTION  
✔ NO REAL MONEY TRADING (SAFE MODE)
""")

st.success("✅ LSTM AI SYSTEM READY (OLD CODE NOT DISTURBED)")
