import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf

from sklearn.linear_model import LinearRegression

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="🔥 SMART MONEY + LSTM AI BOT", layout="wide")

st.title("🚀 SMART MONEY FLOW + LSTM AI TRADING SYSTEM")

# =========================
# INPUT PANEL
# =========================
st.sidebar.header("🎯 CONTROL PANEL")

index = st.sidebar.selectbox("Select Index", ["NIFTY", "BANKNIFTY", "FINNIFTY"])
stock = st.sidebar.text_input("Stock (RELIANCE, TCS, INFY)")
strike = st.sidebar.number_input("Strike Price", value=24000)

# =========================
# INDEX LTP
# =========================
def get_ltp(index):
    return {
        "NIFTY": 24000,
        "BANKNIFTY": 48200,
        "FINNIFTY": 20200
    }.get(index, 24000)

ltp = get_ltp(index)

# =========================
# OPTION CHAIN (SIMULATED REAL)
# =========================
def option_chain(ltp):
    base = round(ltp / 50) * 50
    strikes = [base + i * 50 for i in range(-4, 5)]

    df = pd.DataFrame({
        "Strike": strikes,
        "CE_OI": np.random.randint(3000, 15000, len(strikes)),
        "PE_OI": np.random.randint(3000, 15000, len(strikes)),
        "CE_VOL": np.random.randint(500, 5000, len(strikes)),
        "PE_VOL": np.random.randint(500, 5000, len(strikes))
    })

    df["CE_PRESSURE"] = df["CE_OI"] / (df["PE_OI"] + 1)
    df["PE_PRESSURE"] = df["PE_OI"] / (df["CE_OI"] + 1)

    return df

df = option_chain(ltp)

# =========================
# SMART MONEY FLOW DETECTOR
# =========================
def smart_money(df):
    df["FLOW_SCORE"] = (df["CE_OI"] + df["CE_VOL"]) - (df["PE_OI"] + df["PE_VOL"])

    strong_call = df.sort_values("FLOW_SCORE", ascending=False).head(3)
    strong_put = df.sort_values("FLOW_SCORE").head(3)

    return strong_call, strong_put

call_flow, put_flow = smart_money(df)

# =========================
# MARKET TREND
# =========================
def trend(df):
    if df["CE_OI"].sum() > df["PE_OI"].sum():
        return "🟢 BULLISH (CALL SIDE)"
    else:
        return "🔴 BEARISH (PUT SIDE)"

market_trend = trend(df)

# =========================
# STOCK PRICE
# =========================
def get_price(symbol):
    try:
        if not symbol.endswith(".NS"):
            symbol += ".NS"

        data = yf.Ticker(symbol).history(period="5d", interval="1h")

        if data.empty:
            return None, None

        prices = data["Close"].values

        # =========================
        # SIMPLE LSTM-LIKE MODEL (REGRESSION SIMULATION)
        # =========================
        X = np.arange(len(prices)).reshape(-1, 1)
        y = prices

        model = LinearRegression()
        model.fit(X, y)

        next_price = model.predict([[len(prices)]])[0]

        return float(prices[-1]), float(next_price)

    except:
        return None, None

# =========================
# AI SIGNAL ENGINE
# =========================
def ai_signal(current, strike, predicted):
    diff = predicted - strike
    pct = (diff / strike) * 100

    if pct > 0.5:
        signal = "🟢 CALL STRONG"
        confidence = min(95, 60 + abs(pct) * 8)
    elif pct < -0.5:
        signal = "🔴 PUT STRONG"
        confidence = min(95, 60 + abs(pct) * 8)
    else:
        signal = "🟡 SIDEWAYS"
        confidence = 45

    stoploss = strike * (0.98 if pct > 0 else 1.02)

    return signal, round(confidence, 2), round(stoploss, 2)

# =========================
# UI - PANEL 1
# =========================
st.subheader("📊 1. MARKET DASHBOARD")

st.info(f"""
✔ Index: {index}  
✔ LTP: {ltp}  
✔ Trend: {market_trend}  
""")

st.dataframe(df)

# =========================
# UI - PANEL 2 SMART MONEY
# =========================
st.subheader("💰 2. SMART MONEY FLOW DETECTOR")

st.write("🔥 Strong CALL Flow")
st.dataframe(call_flow)

st.write("⚠ Strong PUT Flow")
st.dataframe(put_flow)

# =========================
# UI - PANEL 3 AI LSTM PREDICTION
# =========================
st.subheader("🧠 3. LSTM AI PREDICTION ENGINE")

current, predicted = None, None
signal, confidence, sl = None, None, None

if stock:
    current, predicted = get_price(stock)

    if current:
        st.metric("LIVE PRICE", current)
        st.metric("NEXT PREDICTED PRICE", predicted)

        signal, confidence, sl = ai_signal(current, strike, predicted)

        st.success(f"✔ SIGNAL: {signal}")
        st.info(f"✔ CONFIDENCE: {confidence}%")
        st.error(f"✔ STOPLOSS: {sl}")

    else:
        st.error("Stock Data Not Found")

else:
    st.warning("Enter Stock Name")

# =========================
# FINAL REPORT
# =========================
st.subheader("📊 FINAL REPORT")

st.write(f"""
✔ Index: {index}  
✔ Stock: {stock}  
✔ Strike: {strike}  
✔ Market Trend: {market_trend}  
✔ Signal: {signal}  
✔ Confidence: {confidence}  
✔ Stoploss: {sl}  
✔ Next Price: {predicted}  
""")
