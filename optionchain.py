import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.express as px

st.set_page_config(page_title="🔥 Next Level Option AI", layout="wide")
st.title("📊 Next Level Option Chain PRO")

# =============================
# SIDEBAR
# =============================
st.sidebar.title("📊 Market Setup")

indices = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"]
symbol = st.sidebar.selectbox("Select Index", indices)

# Strike input
user_strike = st.sidebar.number_input("🎯 Enter Strike", min_value=0, step=50)

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
if st.button("🚀 Run Scanner"):

    df = fetch_data()

    if df is None or df.empty:
        st.warning("⚠ Demo Data")
        df = demo()

    # =============================
    # ATM STRIKE
    # =============================
    atm = df.iloc[(df["Strike"] - df["Strike"].mean()).abs().argsort()[:1]].iloc[0]["Strike"]

    # =============================
    # SIGNAL LOGIC
    # =============================
    df["Signal"] = "WAIT"
    df["Trade"] = "-"

    for i in range(len(df)):
        if df.loc[i,"Put_Change"] > 3000 and df.loc[i,"Call_Change"] < 0:
            df.loc[i,"Signal"] = "BUY"
            df.loc[i,"Trade"] = "CALL (CE)"

        elif df.loc[i,"Call_Change"] > 3000 and df.loc[i,"Put_Change"] < 0:
            df.loc[i,"Signal"] = "SELL"
            df.loc[i,"Trade"] = "PUT (PE)"

    # =============================
    # BEST STRIKE
    # =============================
    best = df[df["Signal"] != "WAIT"]

    # =============================
    # SUPPORT / RESISTANCE
    # =============================
    resistance = df.loc[df["Call_OI"].idxmax()]["Strike"]
    support = df.loc[df["Put_OI"].idxmax()]["Strike"]

    # =============================
    # UI TOP
    # =============================
    c1,c2,c3 = st.columns(3)
    c1.metric("🎯 ATM", int(atm))
    c2.metric("🔴 Resistance", int(resistance))
    c3.metric("🟢 Support", int(support))

    # =============================
    # STRONG SIGNAL BOX
    # =============================
    st.subheader("🔥 Strong Signals")

    if not best.empty:
        for i in best.index[:5]:
            st.success(f"{df.loc[i,'Trade']} at {int(df.loc[i,'Strike'])}")
    else:
        st.warning("No strong signals")

    # =============================
    # SELECTED STRIKE
    # =============================
    st.subheader("🎯 Selected Strike Trade")

    if user_strike != 0:
        row = df[df["Strike"] == user_strike]

        if not row.empty:
            row = row.iloc[0]

            if row["Signal"] == "BUY":
                st.success("🟢 CALL (CE)")
                st.write("Entry:", user_strike)
                st.write("Target:", user_strike+100)
                st.write("SL:", user_strike-50)

            elif row["Signal"] == "SELL":
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
    st.info("Click Run Scanner")
