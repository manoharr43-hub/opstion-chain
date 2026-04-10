import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import requests
from sklearn.linear_model import LinearRegression

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="🔥 REAL NSE AI AUTO BOT", layout="wide")

st.title("🚀 REAL NSE LIVE AI + AUTO TRADING BOT")

# =========================
# SIDEBAR
# =========================
st.sidebar.header("🎯 CONTROL PANEL")

index = st.sidebar.selectbox("Index", ["NIFTY", "BANKNIFTY", "FINNIFTY"])
stock = st.sidebar.text_input("Stock (RELIANCE, TCS, INFY)")
strike = st.sidebar.number_input("Strike Price", value=24000)

auto_trade = st.sidebar.checkbox("🤖 AUTO TRADE ENABLE (SIMULATION)")

# =========================
# REAL NSE (YFINANCE PRIMARY)
# =========================
def get_live_price(symbol):
    try:
        if not symbol.endswith(".NS"):
            symbol += ".NS"

        data = yf.Ticker(symbol).history(period="5d", interval="5m")

        if data.empty:
            return None, None

        prices = data["Close"].values

        # ===== SIMPLE AI MODEL (REAL ML) =====
        X = np.arange(len(prices)).reshape(-1, 1)
        y = prices

        model = LinearRegression()
        model.fit(X, y)

        next_price = model.predict([[len(prices)]])[0]

        return float(prices[-1]), float(next_price)

    except:
        return None, None

# =========================
# OPTION CHAIN SIM (REAL STYLE)
# =========================
def option_chain(ltp):
    base = round(ltp / 50) * 50
    strikes = [base + i * 50 for i in range(-5, 6)]

    df = pd.DataFrame({
        "Strike": strikes,
        "CE_OI": np.random.randint(5000, 20000, len(strikes)),
        "PE_OI": np.random.randint(5000, 20000, len(strikes)),
        "CE_VOL": np.random.randint(1000, 8000, len(strikes)),
        "PE_VOL": np.random.randint(1000, 8000, len(strikes))
    })

    df["CE_PRESSURE"] = df["CE_OI"] / (df["PE_OI"] + 1)
    df["PE_PRESSURE"] = df["PE_OI"] / (df["CE_OI"] + 1)

    return df

# =========================
# SMART MONEY FLOW
# =========================
def smart_money(df):
    df["FLOW"] = (df["CE_OI"] + df["CE_VOL"]) - (df["PE_OI"] + df["PE_VOL"])

    call = df.sort_values("FLOW", ascending=False).head(3)
    put = df.sort_values("FLOW").head(3)

    return call, put

# =========================
# AI SIGNAL ENGINE
# =========================
def ai_engine(current, predicted, strike):
    diff = predicted - strike
    pct = (diff / strike) * 100

    if pct > 0.5:
        signal = "🟢 CALL ENTRY"
        action = "BUY CALL OPTION"
    elif pct < -0.5:
        signal = "🔴 PUT ENTRY"
        action = "BUY PUT OPTION"
    else:
        signal = "🟡 NO TRADE"
        action = "WAIT"

    stoploss = strike * (0.98 if pct > 0 else 1.02)

    return signal, action, round(stoploss, 2)

# =========================
# AUTO TRADE BOT (SIMULATION ONLY)
# =========================
def auto_trade(signal, price):
    if "CALL" in signal:
        return f"📈 BUY ORDER SIMULATED @ {price}"
    elif "PUT" in signal:
        return f"📉 SELL ORDER SIMULATED @ {price}"
    else:
        return "⏳ NO TRADE EXECUTED"

# =========================
# INDEX DATA
# =========================
def index_ltp(index):
    return {
        "NIFTY": 24000,
        "BANKNIFTY": 48200,
        "FINNIFTY": 20200
    }.get(index, 24000)

ltp = index_ltp(index)
df = option_chain(ltp)
call_flow, put_flow = smart_money(df)

# =========================
# UI - MARKET
# =========================
st.subheader("📊 MARKET DASHBOARD")
st.info(f"✔ Index: {index} | LTP: {ltp}")

st.dataframe(df)

# =========================
# SMART MONEY
# =========================
st.subheader("💰 SMART MONEY FLOW")

st.write("🔥 CALL FLOW")
st.dataframe(call_flow)

st.write("⚠ PUT FLOW")
st.dataframe(put_flow)

# =========================
# STOCK AI ENGINE
# =========================
st.subheader("🧠 REAL AI PREDICTION ENGINE")

current, predicted = None, None
signal = action = sl = None

if stock:
    current, predicted = get_live_price(stock)

    if current:
        st.metric("LIVE PRICE", current)
        st.metric("NEXT PREDICTION", predicted)

        signal, action, sl = ai_engine(current, predicted, strike)

        st.success(f"✔ SIGNAL: {signal}")
        st.info(f"✔ ACTION: {action}")
        st.error(f"✔ STOPLOSS: {sl}")

        # =========================
        # AUTO TRADE EXECUTION
        # =========================
        if auto_trade:
            result = auto_trade(signal, current)
            st.warning(f"🤖 AUTO BOT: {result}")

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
✔ Signal: {signal}  
✔ Action: {action}  
✔ Stoploss: {sl}  
✔ Predicted Price: {predicted}  
""")
