import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="🔥 CE vs PE + AI TRADING BOT", layout="wide")

# =========================
# INDEX LTP
# =========================
def get_ltp(index):
    return {
        "NIFTY": 24015,
        "BANKNIFTY": 48250,
        "FINNIFTY": 20250
    }.get(index, 24000)

# =========================
# OPTION CHAIN
# =========================
def option_chain(ltp):
    ltp = float(ltp)
    base = round(ltp / 50) * 50
    strikes = [base + i * 50 for i in range(-3, 4)]

    return pd.DataFrame({
        "Strike": strikes,
        "CE_OI": np.random.randint(2000, 9000, len(strikes)),
        "PE_OI": np.random.randint(2000, 9000, len(strikes)),
    })

# =========================
# CE PE ZONES
# =========================
def ce_pe_zone(df):
    df["CE_PRESSURE"] = df["CE_OI"] / (df["PE_OI"] + 1)
    df["PE_PRESSURE"] = df["PE_OI"] / (df["CE_OI"] + 1)

    return (
        df.sort_values("CE_PRESSURE", ascending=False).head(3),
        df.sort_values("PE_PRESSURE", ascending=False).head(3)
    )

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
# STOCK PRICE
# =========================
def get_price(symbol):
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
# AI TRADING ENGINE
# =========================
def ai_engine(price, strike):
    diff = price - strike
    perc = (diff / strike) * 100

    # ENTRY
    if abs(perc) < 0.5:
        entry = "🟡 NO TRADE (WAIT)"
    elif perc > 0.5:
        entry = "🟢 CALL ENTRY"
    else:
        entry = "🔴 PUT ENTRY"

    # EXIT
    if abs(perc) > 2:
        exit_signal = "⚠ EXIT (TARGET HIT)"
    else:
        exit_signal = "🟡 HOLD"

    # STOPLOSS
    stoploss = round(strike * (0.98 if perc > 0 else 1.02), 2)

    return entry, exit_signal, stoploss

# =========================
# UI
# =========================
st.title("🔥 CE vs PE + AI TRADING BOT (SAFE VERSION)")

# SIDEBAR
index = st.sidebar.selectbox("Index", ["NIFTY", "BANKNIFTY", "FINNIFTY"])
stock = st.sidebar.text_input("Stock Search (RELIANCE, TCS, INFY)")
strike = st.sidebar.number_input("Strike Price", value=24000)

# DATA
ltp = get_ltp(index)
df = option_chain(ltp)

ce_zone, pe_zone = ce_pe_zone(df)
trend_value = trend(df)

# =========================
# OPTION CHAIN
# =========================
st.subheader("📊 Option Chain")
st.dataframe(df)

# =========================
# CE PE ZONES
# =========================
st.subheader("🚀 CE ZONE")
st.dataframe(ce_zone)

st.subheader("📉 PE ZONE")
st.dataframe(pe_zone)

# =========================
# STOCK ANALYSIS
# =========================
st.subheader("📌 STOCK ANALYSIS")

price = None
entry = exit_signal = stoploss = None

if stock:
    with st.spinner("Loading Stock..."):
        price = get_price(stock)

    if price:
        entry, exit_signal, stoploss = ai_engine(price, strike)

        st.metric("Live Price", price)
        st.success(entry)
        st.warning(exit_signal)
        st.error(f"STOPLOSS: {stoploss}")
    else:
        st.error("Stock Data Not Found")

# =========================
# REPORT
# =========================
st.subheader("📊 FINAL REPORT")

st.write(f"""
✔ Index: {index}  
✔ LTP: {ltp}  
✔ Trend: {trend_value}  
✔ Stock: {stock}  
✔ Strike: {strike}  
✔ Entry: {entry}  
✔ Exit: {exit_signal}  
✔ Stoploss: {stoploss}  
""")

# =========================
# FINAL SIGNAL
# =========================
if df["CE_PRESSURE"].mean() > df["PE_PRESSURE"].mean():
    st.success("🟢 CALL SIDE STRONG MARKET")
else:
    st.warning("🔴 PUT SIDE STRONG MARKET")
