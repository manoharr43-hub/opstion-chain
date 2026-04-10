import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf

# =========================
# PAGE SETUP
# =========================
st.set_page_config(page_title="🔥 NSE AI OPTION BOT", layout="wide")

# =========================
# HEADER
# =========================
st.title("🚀 NSE AI OPTION CHAIN + CE/PE SYSTEM")

# =========================
# SIDEBAR INPUTS
# =========================
st.sidebar.header("🎯 CONTROL PANEL")

sector = st.sidebar.selectbox(
    "Select Index",
    ["NIFTY", "BANKNIFTY", "FINNIFTY"]
)

stock = st.sidebar.text_input("Stock Name (RELIANCE, TCS, INFY)")
strike = st.sidebar.number_input("Strike Price", value=24000)

# =========================
# INDEX LTP (SAFE MOCK)
# =========================
def get_index_ltp(index):
    data = {
        "NIFTY": 24010,
        "BANKNIFTY": 48200,
        "FINNIFTY": 20200
    }
    return data.get(index, 24000)

ltp = get_index_ltp(sector)

# =========================
# OPTION CHAIN MOCK
# =========================
def option_chain(ltp):
    base = round(ltp / 50) * 50
    strikes = [base + i * 50 for i in range(-3, 4)]

    df = pd.DataFrame({
        "Strike": strikes,
        "CE_OI": np.random.randint(1000, 9000, len(strikes)),
        "PE_OI": np.random.randint(1000, 9000, len(strikes))
    })

    return df

df = option_chain(ltp)

# =========================
# CE / PE STRENGTH
# =========================
def ce_pe_strength(df):
    df["CE_PRESSURE"] = df["CE_OI"] / (df["PE_OI"] + 1)
    df["PE_PRESSURE"] = df["PE_OI"] / (df["CE_OI"] + 1)

    return df

df = ce_pe_strength(df)

# =========================
# TREND
# =========================
def trend(df):
    if df["CE_OI"].sum() > df["PE_OI"].sum():
        return "🟢 BULLISH (CALL SIDE)"
    else:
        return "🔴 BEARISH (PUT SIDE)"

market_trend = trend(df)

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
# CE / PE SIGNAL ENGINE
# =========================
def signal_engine(price, strike):
    diff = price - strike
    pct = (diff / strike) * 100

    if pct > 0.5:
        signal = "🟢 CALL ENTRY"
    elif pct < -0.5:
        signal = "🔴 PUT ENTRY"
    else:
        signal = "🟡 WAIT"

    exit_signal = "⚠ EXIT" if abs(pct) > 2 else "🟡 HOLD"

    stoploss = strike * (0.98 if pct > 0 else 1.02)

    return signal, exit_signal, round(stoploss, 2)

# =========================
# UI - 3 REPORT PANELS
# =========================

# =========================
# PANEL 1 - SECTOR REPORT
# =========================
st.subheader("📊 1. SECTOR REPORT")

st.info(f"""
✔ Selected Index: {sector}  
✔ LTP: {ltp}  
✔ Market Trend: {market_trend}  
""")

st.dataframe(df)

# =========================
# PANEL 2 - STOCK REPORT
# =========================
st.subheader("📌 2. STOCK REPORT")

price = None
signal = exit_signal = sl = None

if stock:
    price = get_stock_price(stock)

    if price:
        st.success(f"✔ Stock: {stock}")
        st.metric("LIVE PRICE", price)
    else:
        st.error("Stock Data Not Found")

else:
    st.warning("Enter Stock Name")

# =========================
# PANEL 3 - STRIKE REPORT (CE / PE)
# =========================
st.subheader("🎯 3. STRIKE REPORT (CE / PE AI)")

if stock and price:
    signal, exit_signal, sl = signal_engine(price, strike)

    st.success(f"✔ Strike Price: {strike}")
    st.success(f"✔ Entry Signal: {signal}")
    st.warning(f"✔ Exit Signal: {exit_signal}")
    st.error(f"✔ Stoploss: {sl}")

# =========================
# FINAL SUMMARY
# =========================
st.subheader("📊 FINAL SUMMARY REPORT")

st.write(f"""
✔ Index: {sector}  
✔ Stock: {stock}  
✔ Strike: {strike}  
✔ Market Trend: {market_trend}  
✔ Entry: {signal}  
✔ Exit: {exit_signal}  
✔ Stoploss: {sl}  
""")
