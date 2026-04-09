import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.express as px

st.set_page_config(page_title="Option Chain Smart Scanner", layout="wide")
st.title("📊 Option Chain Smart Scanner")

# =============================
# SIDEBAR
# =============================
st.sidebar.title("📊 Market Settings")

indices = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"]
symbol = st.sidebar.selectbox("Select Index", indices)

expiry_type = st.sidebar.selectbox("Select Expiry", ["Weekly", "Monthly"])

# =============================
# FETCH DATA
# =============================
def fetch_data():
    try:
        url = f"https://api.allorigins.win/raw?url=https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
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

    if df is None or df.empty:
        st.warning("⚠ Live data not available → Showing Demo Data")
        df = demo_data()

    # =============================
    # SIGNAL COLUMN
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
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Call OI", total_call)
    c2.metric("Total Put OI", total_put)
    c3.metric("PCR", pcr)

    c4, c5 = st.columns(2)
    c4.metric("Call OI Change", total_call_chg)
    c5.metric("Put OI Change", total_put_chg)

    st.subheader("📢 Final Signal")
    st.success(final_signal)

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
