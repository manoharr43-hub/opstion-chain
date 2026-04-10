import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.express as px

st.set_page_config(page_title="🔥 Ultra Option AI", layout="wide")
st.title("📊 Ultra Option Chain AI")

# =============================
# SIDEBAR
# =============================
st.sidebar.title("📊 Market Setup")

indices = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"]
symbol = st.sidebar.selectbox("Select Index", indices)

user_strike = st.sidebar.number_input("🎯 Enter Strike", min_value=0, step=50)

# =============================
# FETCH EXPIRY
# =============================
def get_expiries():
    try:
        url = f"https://api.allorigins.win/raw?url=https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
        res = requests.get(url, timeout=10)

        if res.status_code != 200:
            return []

        data = res.json()
        return data["records"]["expiryDates"]

    except:
        return []

expiry_list = get_expiries()

selected_expiry = st.sidebar.selectbox(
    "📅 Select Expiry",
    expiry_list if expiry_list else ["No Data"]
)

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

        rows = []
        for item in data["records"]["data"]:

            if item.get("expiryDate") != selected_expiry:
                continue

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
def demo():
    strikes = np.arange(22000,23000,50)
    data=[]
    for s in strikes:
        data.append({
            "Strike":s,
            "Call_OI":np.random.randint(10000,100000),
            "Put_OI":np.random.randint(10000,100000),
            "Call_Change":np.random.randint(-5000,5000),
            "Put_Change":np.random.randint(-5000,5000)
        })
    return pd.DataFrame(data)

# =============================
# MAIN
# =============================
if st.button("🚀 Run Ultra AI"):

    df = fetch_data()

    if df is None or df.empty:
        st.warning("⚠ Demo Data")
        df = demo()

    # =============================
    # EXPIRY TYPE
    # =============================
    if "No Data" not in selected_expiry:
        day = int(selected_expiry.split("-")[0])
        expiry_type = "🟡 Monthly" if day <= 7 else "🔵 Weekly"
    else:
        expiry_type = "Unknown"

    st.subheader(f"📅 {expiry_type} Expiry")

    # =============================
    # TOTALS
    # =============================
    total_call = df["Call_OI"].sum()
    total_put = df["Put_OI"].sum()
    total_call_chg = df["Call_Change"].sum()
    total_put_chg = df["Put_Change"].sum()
    pcr = round(total_put / total_call, 2)

    # =============================
    # EXPIRY SIGNAL
    # =============================
    if total_put_chg > total_call_chg and pcr > 1:
        expiry_signal = "🟢 BUY SUPPORT"
    elif total_call_chg > total_put_chg and pcr < 1:
        expiry_signal = "🔴 SELL PRESSURE"
    else:
        expiry_signal = "⚠ SIDEWAYS"

    st.subheader("📢 Expiry Signal")
    st.success(expiry_signal)

    # =============================
    # SUPPORT / RESISTANCE
    # =============================
    resistance = df.loc[df["Call_OI"].idxmax()]["Strike"]
    support = df.loc[df["Put_OI"].idxmax()]["Strike"]

    c1,c2 = st.columns(2)
    c1.metric("🔴 Resistance", int(resistance))
    c2.metric("🟢 Support", int(support))

    # =============================
    # TRAP DETECTION
    # =============================
    df["Trap"] = "-"
    for i in range(len(df)):
        if df.loc[i,"Call_Change"] > 4000 and df.loc[i,"Put_Change"] > 4000:
            df.loc[i,"Trap"] = "⚠ TRAP"

    # =============================
    # SCALPING
    # =============================
    df["Scalp"] = "-"
    for i in range(len(df)):
        if df.loc[i,"Put_Change"] > 2000 and df.loc[i,"Call_Change"] < 0:
            df.loc[i,"Scalp"] = "🟢 BUY"
        elif df.loc[i,"Call_Change"] > 2000 and df.loc[i,"Put_Change"] < 0:
            df.loc[i,"Scalp"] = "🔴 SELL"

    # =============================
    # ALERTS
    # =============================
    st.subheader("🚨 Ultra Alerts")

    best_buy = df[df["Scalp"] == "🟢 BUY"]
    best_sell = df[df["Scalp"] == "🔴 SELL"]

    if not best_buy.empty:
        st.success(f"🟢 Best BUY: {int(best_buy.iloc[-1]['Strike'])}")

    if not best_sell.empty:
        st.error(f"🔴 Best SELL: {int(best_sell.iloc[-1]['Strike'])}")

    # =============================
    # STRIKE ENTRY
    # =============================
    st.subheader("🎯 Selected Strike Trade")

    if user_strike != 0:
        row = df[df["Strike"] == user_strike]

        if not row.empty:
            row = row.iloc[0]

            if row["Scalp"] == "🟢 BUY":
                st.success("🟢 CALL (CE)")
                st.write("Entry:", user_strike)
                st.write("Target:", user_strike+100)
                st.write("SL:", user_strike-50)

            elif row["Scalp"] == "🔴 SELL":
                st.error("🔴 PUT (PE)")
                st.write("Entry:", user_strike)
                st.write("Target:", user_strike-100)
                st.write("SL:", user_strike+50)

            else:
                st.warning("No strong move")

    # =============================
    # CHART
    # =============================
    fig = px.bar(df, x="Strike", y=["Call_OI","Put_OI"], barmode="group")
    st.plotly_chart(fig, use_container_width=True)

    # =============================
    # TABLE
    # =============================
    st.dataframe(df)

else:
    st.info("Click Run Ultra AI")
