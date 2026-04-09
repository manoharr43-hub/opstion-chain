import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.express as px

st.set_page_config(page_title="🔥 Option Chain Pro", layout="wide")
st.title("📊 Option Chain Pro Analysis")

# =============================
# STOCK SELECT
# =============================
stocks = ["NIFTY", "BANKNIFTY", "RELIANCE", "INFY"]
symbol = st.sidebar.selectbox("Select Stock", stocks)

# =============================
# DEMO DATA GENERATOR
# =============================
def generate_data():
    strikes = np.arange(22000, 23000, 50)

    data = []
    for strike in strikes:
        call_oi = np.random.randint(10000, 100000)
        put_oi = np.random.randint(10000, 100000)

        call_change = np.random.randint(-5000, 5000)
        put_change = np.random.randint(-5000, 5000)

        data.append({
            "Strike": strike,
            "Call_OI": call_oi,
            "Put_OI": put_oi,
            "Call_Change": call_change,
            "Put_Change": put_change
        })

    return pd.DataFrame(data)

# =============================
# MAIN
# =============================
if st.button("Run Analysis"):

    df = generate_data()

    # =============================
    # TOTAL OI
    # =============================
    total_call = df["Call_OI"].sum()
    total_put = df["Put_OI"].sum()

    total_call_change = df["Call_Change"].sum()
    total_put_change = df["Put_Change"].sum()

    # =============================
    # PCR
    # =============================
    pcr = round(total_put / total_call, 2)

    # =============================
    # SIGNAL
    # =============================
    if total_call_change > total_put_change:
        signal = "🔻 DOWN TREND (CALL WRITING)"
    else:
        signal = "🔺 UP TREND (PUT WRITING)"

    # =============================
    # ACTIVE STRIKE
    # =============================
    active_call = df.loc[df["Call_OI"].idxmax()]
    active_put = df.loc[df["Put_OI"].idxmax()]

    # =============================
    # UI DISPLAY
    # =============================
    c1, c2, c3 = st.columns(3)

    c1.metric("Total Call OI", total_call)
    c2.metric("Total Put OI", total_put)
    c3.metric("PCR", pcr)

    c4, c5 = st.columns(2)
    c4.metric("Call OI Change", total_call_change)
    c5.metric("Put OI Change", total_put_change)

    st.subheader("📢 Market Direction")
    st.success(signal)

    st.subheader("🎯 Active Strikes")
    st.write(f"🔴 Call Side Strong: {int(active_call['Strike'])}")
    st.write(f"🟢 Put Side Strong: {int(active_put['Strike'])}")

    # =============================
    # ENTRY LOGIC
    # =============================
    if pcr > 1 and total_put_change > 0:
        st.success("🟢 BUY SIGNAL (UPSIDE)")
    elif pcr < 1 and total_call_change > 0:
        st.error("🔴 SELL SIGNAL (DOWNSIDE)")
    else:
        st.warning("⚠ NO CLEAR SIGNAL")

    # =============================
    # CHART
    # =============================
    fig = px.bar(
        df,
        x="Strike",
        y=["Call_OI", "Put_OI"],
        barmode="group"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(df)

else:
    st.info("👉 Click Run Analysis")
