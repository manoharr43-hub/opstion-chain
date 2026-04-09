import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.express as px

st.set_page_config(page_title="🔥 Option Chain PRO Scanner", layout="wide")
st.title("📊 Option Chain PRO Scanner")

# =============================
# SIDEBAR
# =============================
st.sidebar.title("📊 Smart Market Setup")

# Index select
indices = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"]
index_symbol = st.sidebar.selectbox("Select Index", indices)

# Expiry select
expiry_type = st.sidebar.selectbox("Select Expiry", ["Weekly", "Monthly"])

# Stock search
stocks = [
    "RELIANCE", "INFY", "TCS", "HDFCBANK", "ICICIBANK",
    "SBIN", "LT", "ITC", "WIPRO", "AXISBANK",
    "KOTAKBANK", "HCLTECH", "BAJFINANCE", "MARUTI"
]

search_stock = st.sidebar.selectbox("🔍 Search / Select Stock", [""] + stocks)

# Quick buttons
st.sidebar.markdown("### ⭐ Quick Stocks")
col1, col2 = st.sidebar.columns(2)

if col1.button("RELIANCE"):
    search_stock = "RELIANCE"
if col2.button("INFY"):
    search_stock = "INFY"
if col1.button("HDFC"):
    search_stock = "HDFCBANK"
if col2.button("ICICI"):
    search_stock = "ICICIBANK"

# Final symbol
if search_stock != "":
    symbol = search_stock
    market_type = "Stock"
else:
    symbol = index_symbol
    market_type = "Index"

# =============================
# FETCH DATA
# =============================
def fetch_data():
    try:
        if market_type == "Index":
            url = f"https://api.allorigins.win/raw?url=https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
        else:
            url = f"https://api.allorigins.win/raw?url=https://www.nseindia.com/api/option-chain-equities?symbol={symbol}"

        res = requests.get(url, timeout=10)

        if res.status_code != 200:
            return None

        data = res.json()

        if "records" not in data or "data" not in data["records"]:
            return None

        rows = []
        for item in data["records"]["data"]:
            rows.append({
                "Strike": item.get("strikePrice", 0),
                "Call_OI": item.get("CE", {}).get("openInterest", 0),
                "Put_OI": item.get("PE", {}).get("openInterest", 0),
                "Call_Change": item.get("CE", {}).get("changeinOpenInterest", 0),
                "Put_Change": item.get("PE", {}).get("changeinOpenInterest", 0)
            })

        return pd.DataFrame(rows)

    except:
        return None

# =============================
# DEMO DATA
# =============================
def demo_data():
    strikes = np.arange(22000, 23000, 50)
    data = []

    for strike in strikes:
        data.append({
            "Strike": strike,
            "Call_OI": np.random.randint(10000, 100000),
            "Put_OI": np.random.randint(10000, 100000),
            "Call_Change": np.random.randint(-5000, 5000),
            "Put_Change": np.random.randint(-5000, 5000)
        })

    return pd.DataFrame(data)

# =============================
# MAIN
# =============================
if st.button("🚀 Run Scanner"):

    df = fetch_data()

    # fallback
    if df is None or df.empty:
        st.warning("⚠ Live data not available → Showing Demo Data")
        df = demo_data()

    # =============================
    # BIG PLAYER SIGNAL
    # =============================
    df["Signal"] = "-"

    for i in range(len(df)):
        call_chg = df.loc[i, "Call_Change"]
        put_chg = df.loc[i, "Put_Change"]

        if put_chg > 3000 and call_chg < 0:
            df.loc[i, "Signal"] = "🟢 BIG BUY"
        elif call_chg > 3000 and put_chg < 0:
            df.loc[i, "Signal"] = "🔴 BIG SELL"

    # =============================
    # TOTALS
    # =============================
    total_call = df["Call_OI"].sum()
    total_put = df["Put_OI"].sum()

    total_call_chg = df["Call_Change"].sum()
    total_put_chg = df["Put_Change"].sum()

    # =============================
    # PCR
    # =============================
    pcr = round(total_put / total_call, 2)

    # =============================
    # FINAL SIGNAL
    # =============================
    if pcr > 1.2 and total_put_chg > total_call_chg:
        final_signal = "🟢 STRONG BUY"
    elif pcr < 0.8 and total_call_chg > total_put_chg:
        final_signal = "🔴 STRONG SELL"
    else:
        final_signal = "⚠ WAIT"

    # =============================
    # ACTIVE STRIKE
    # =============================
    active_call = df.loc[df["Call_OI"].idxmax()]
    active_put = df.loc[df["Put_OI"].idxmax()]

    # =============================
    # UI
    # =============================
    st.subheader(f"📌 Selected: {symbol}")

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Call OI", total_call)
    c2.metric("Total Put OI", total_put)
    c3.metric("PCR", pcr)

    c4, c5 = st.columns(2)
    c4.metric("Call OI Change", total_call_chg)
    c5.metric("Put OI Change", total_put_chg)

    # =============================
    # DISPLAY
    # =============================
    st.subheader("📢 Final Signal")
    st.success(final_signal)

    # =============================
    # ENTRY SUGGESTION
    # =============================
    st.subheader("🎯 Smart Entry Suggestion")

    entry = "NO TRADE"

    if pcr > 1.2 and total_put_chg > total_call_chg:
        entry = f"🟢 BUY CALL near {int(active_put['Strike'])}"
    elif pcr < 0.8 and total_call_chg > total_put_chg:
        entry = f"🔴 BUY PUT near {int(active_call['Strike'])}"

    st.success(entry)

    # =============================
    # ACTIVE STRIKE
    # =============================
    st.subheader("🎯 Active Strikes")
    st.write(f"🔴 Resistance: {int(active_call['Strike'])}")
    st.write(f"🟢 Support: {int(active_put['Strike'])}")

    # =============================
    # CHART
    # =============================
    fig = px.bar(df, x="Strike", y=["Call_OI", "Put_OI"], barmode="group")
    st.plotly_chart(fig, use_container_width=True)

    # =============================
    # TABLE
    # =============================
    st.dataframe(df)

else:
    st.info("👉 Click Run Scanner")
