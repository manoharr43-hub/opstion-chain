import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="🔥 ULTRA AI OPTION COMMAND CENTER", layout="wide")

# =========================
# HEADER
# =========================
st.title("🚀 ULTRA AI TRADING COMMAND CENTER")

# =========================
# SIDEBAR INPUTS
# =========================
st.sidebar.header("🎯 CONTROL PANEL")

index = st.sidebar.selectbox("Select Index", ["NIFTY", "BANKNIFTY", "FINNIFTY"])
stock = st.sidebar.text_input("Enter Stock (RELIANCE, TCS, INFY)")
strike = st.sidebar.number_input("Strike Price", value=24000)

# =========================
# INDEX LTP (MOCK SAFE)
# =========================
def get_ltp(index):
    data = {
        "NIFTY": 24000,
        "BANKNIFTY": 48200,
        "FINNIFTY": 20200
    }
    return data.get(index, 24000)

ltp = get_ltp(index)

# =========================
# OPTION CHAIN ENGINE
# =========================
def option_chain(ltp):
    base = round(ltp / 50) * 50
    strikes = [base + i * 50 for i in range(-4, 5)]

    df = pd.DataFrame({
        "Strike": strikes,
        "CE_OI": np.random.randint(2000, 12000, len(strikes)),
        "PE_OI": np.random.randint(2000, 12000, len(strikes))
    })

    df["CE_PRESSURE"] = df["CE_OI"] / (df["PE_OI"] + 1)
    df["PE_PRESSURE"] = df["PE_OI"] / (df["CE_OI"] + 1)

    return df

df = option_chain(ltp)

# =========================
# MARKET TREND
# =========================
def market_trend(df):
    ce = df["CE_OI"].sum()
    pe = df["PE_OI"].sum()

    if ce > pe * 1.1:
        return "🟢 BULLISH (CALL ZONE)"
    elif pe > ce * 1.1:
        return "🔴 BEARISH (PUT ZONE)"
    return "🟡 SIDEWAYS"

trend = market_trend(df)

# =========================
# STOCK PRICE FETCH
# =========================
def get_stock_price(symbol):
    try:
        if not symbol.endswith(".NS"):
            symbol += ".NS"

        data = yf.Ticker(symbol).history(period="1d", interval="1m")

        if data.empty:
            return None

        return float(data["Close"].iloc[-1])

    except:
        return None

# =========================
# AI SIGNAL ENGINE
# =========================
def ai_engine(price, strike):
    diff = price - strike
    pct = (diff / strike) * 100

    if pct > 0.5:
        entry = "🟢 CALL ENTRY"
        confidence = min(90, 50 + abs(pct)*10)
    elif pct < -0.5:
        entry = "🔴 PUT ENTRY"
        confidence = min(90, 50 + abs(pct)*10)
    else:
        entry = "🟡 WAIT"
        confidence = 40

    exit_signal = "⚠ EXIT" if abs(pct) > 2 else "🟡 HOLD"

    stoploss = strike * (0.98 if pct > 0 else 1.02)

    return entry, exit_signal, round(stoploss, 2), round(confidence, 2)

# =========================
# UI - PANELS
# =========================

# =========================
# PANEL 1 - MARKET DASHBOARD
# =========================
st.subheader("📊 1. MARKET DASHBOARD")

st.info(f"""
✔ INDEX: {index}  
✔ LTP: {ltp}  
✔ TREND: {trend}  
""")

st.dataframe(df)

# =========================
# PANEL 2 - STOCK TRACKER
# =========================
st.subheader("📌 2. STOCK TRACKER")

price = None
entry = exit_signal = sl = confidence = None

if stock:
    price = get_stock_price(stock)

    if price:
        st.metric("LIVE PRICE", price)
        st.success(f"✔ Tracking: {stock}")
    else:
        st.error("Stock Not Found")
else:
    st.warning("Enter Stock Name")

# =========================
# PANEL 3 - STRIKE AI REPORT
# =========================
st.subheader("🎯 3. STRIKE AI REPORT")

if stock and price:
    entry, exit_signal, sl, confidence = ai_engine(price, strike)

    st.success(f"✔ STRIKE: {strike}")
    st.success(f"✔ ENTRY: {entry}")
    st.info(f"✔ CONFIDENCE: {confidence}%")
    st.warning(f"✔ EXIT: {exit_signal}")
    st.error(f"✔ STOPLOSS: {sl}")

# =========================
# FINAL REPORT (BOTTOM)
# =========================
st.subheader("📊 FINAL REPORT")

st.write(f"""
✔ Index: {index}  
✔ Stock: {stock}  
✔ Strike: {strike}  
✔ Market Trend: {trend}  
✔ Entry Signal: {entry}  
✔ Confidence: {confidence}  
✔ Exit: {exit_signal}  
✔ Stoploss: {sl}  
""")
