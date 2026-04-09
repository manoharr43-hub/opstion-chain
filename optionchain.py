import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.express as px

st.set_page_config(page_title="🔥 Option Chain Ultimate", layout="wide")
st.title("📊 Option Chain Ultimate Scanner")

# =============================
# STOCK SELECT
# =============================
st.sidebar.title("📊 Select Market")

indices = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"]
stocks = [
    "RELIANCE", "INFY", "TCS", "HDFCBANK", "ICICIBANK",
    "SBIN", "LT", "ITC", "WIPRO", "AXISBANK"
]

symbol = st.sidebar.selectbox("Select", indices + stocks)

# =============================
# DEMO DATA
# =============================
def generate_data():
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

    df = generate_data()

    # =============================
    # BIG PLAYER SIGNAL
    # =============================
    df["Signal"] = ""

    for i in range(len(df)):
        call_chg = df.loc[i, "Call_Change"]
        put_chg = df.loc[i, "Put_Change"]

        if put_chg > 3000 and call_chg < 0:
            df.loc[i, "Signal"] = "🟢 BIG BUY"

        elif call_chg > 3000 and put_chg < 0:
            df.loc[i, "Signal"] = "🔴 BIG SELL"

        else:
            df.loc[i, "Signal"] = "-"

    # =============================
    # TOTAL OI
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
    # BREAKOUT LOGIC
    # =============================
    breakout = "NO"

    if total_put_chg > 20000:
        breakout = "🟢 UPSIDE BREAKOUT"

    elif total_call_chg > 20000:
        breakout = "🔴 DOWNSIDE BREAKOUT"

    # =============================
    # FINAL SIGNAL
    # =============================
    final_signal = "WAIT"

    if pcr > 1.2 and total_put_chg > total_call_chg:
        final_signal = "🟢 STRONG BUY"

    elif pcr < 0.8 and total_call_chg > total_put_chg:
        final_signal = "🔴 STRONG SELL"

    # =============================
    # ACTIVE STRIKE
    # =============================
    active_call = df.loc[df["Call_OI"].idxmax()]
    active_put = df.loc[df["Put_OI"].idxmax()]

    # =============================
    # UI
    # =============================
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
    st.subheader("📢 Market Direction")
    st.success(final_signal)

    st.subheader("🔥 Breakout Signal")
    st.info(breakout)

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
