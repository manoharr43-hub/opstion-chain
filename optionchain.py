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
st.sidebar.title("📊 Select Market")

indices = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"]

stocks = [
    "RELIANCE", "INFY", "TCS", "HDFCBANK", "ICICIBANK",
    "SBIN", "LT", "ITC", "WIPRO", "AXISBANK",
    "KOTAKBANK", "HCLTECH", "BAJFINANCE", "MARUTI",
    "ADANIENT", "TATASTEEL", "POWERGRID"
]

symbol = st.sidebar.selectbox("Choose Index / Stock", indices + stocks)

# =============================
# REAL DATA FETCH
# =============================
def fetch_real_data():
    try:
        url = f"https://api.allorigins.win/raw?url=https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
        res = requests.get(url, timeout=10)

        if res.status_code != 200:
            return None

        data = res.json()

        if "records" not in data:
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
# DEMO DATA (FALLBACK)
# =============================
def generate_demo():
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
if st.button("🚀 Run Analysis"):

    with st.spinner("Fetching data..."):
        df = fetch_real_data()

    # fallback
    if df is None or df.empty:
        st.warning("⚠ Live data not available → Showing Demo Data")
        df = generate_demo()

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
    # SIGNAL LOGIC
    # =============================
    if total_call_change > total_put_change:
        direction = "🔻 DOWN TREND"
    else:
        direction = "🔺 UP TREND"

    # =============================
    # ACTIVE STRIKE
    # =============================
    active_call = df.loc[df["Call_OI"].idxmax()]
    active_put = df.loc[df["Put_OI"].idxmax()]

    # =============================
    # UI METRICS
    # =============================
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Call OI", total_call)
    c2.metric("Total Put OI", total_put)
    c3.metric("PCR", pcr)

    c4, c5 = st.columns(2)
    c4.metric("Call OI Change", total_call_change)
    c5.metric("Put OI Change", total_put_change)

    # =============================
    # SIGNAL DISPLAY
    # =============================
    st.subheader("📢 Market Direction")
    st.success(direction)

    # =============================
    # ENTRY SIGNAL
    # =============================
    st.subheader("🚀 Entry Signal")

    if pcr > 1 and total_put_change > 0:
        st.success("🟢 BUY (Market Up)")
    elif pcr < 1 and total_call_change > 0:
        st.error("🔴 SELL (Market Down)")
    else:
        st.warning("⚠ No Clear Signal")

    # =============================
    # ACTIVE STRIKE
    # =============================
    st.subheader("🎯 Active Strikes")
    st.write(f"🔴 Call Strong Strike: {int(active_call['Strike'])}")
    st.write(f"🟢 Put Strong Strike: {int(active_put['Strike'])}")

    # =============================
    # CHART
    # =============================
    st.subheader("📊 OI Chart")

    fig = px.bar(
        df,
        x="Strike",
        y=["Call_OI", "Put_OI"],
        barmode="group"
    )

    st.plotly_chart(fig, use_container_width=True)

    # =============================
    # DATA TABLE
    # =============================
    st.dataframe(df)

else:
    st.info("👉 Click 'Run Analysis'")
