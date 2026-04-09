import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.express as px
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

st.set_page_config(page_title="🔥 REAL AI Option Chain", layout="wide")
st.title("📊 REAL AI Option Chain Scanner")

# =============================
# SIDEBAR
# =============================
st.sidebar.title("📊 Market Setup")

indices = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"]
index_symbol = st.sidebar.selectbox("Select Index", indices)

expiry_type = st.sidebar.selectbox("Select Expiry", ["Weekly", "Monthly"])

stocks = ["RELIANCE","INFY","TCS","HDFCBANK","ICICIBANK","SBIN","ITC"]
search_stock = st.sidebar.selectbox("🔍 Stock", [""] + stocks)

# Quick buttons
st.sidebar.markdown("### ⭐ Quick Select")
c1, c2 = st.sidebar.columns(2)
if c1.button("RELIANCE"): search_stock="RELIANCE"
if c2.button("INFY"): search_stock="INFY"

# Strike input
st.sidebar.markdown("### 🎯 Strike Entry")
user_strike = st.sidebar.number_input("Enter Strike", min_value=0, step=50)

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
if st.button("🚀 Run REAL AI Scanner"):

    df = fetch_data()

    if df is None or df.empty:
        st.warning("⚠ Using Demo Data")
        df = demo()

    # =============================
    # BASIC CALC
    # =============================
    total_call = df["Call_OI"].sum()
    total_put = df["Put_OI"].sum()

    total_call_chg = df["Call_Change"].sum()
    total_put_chg = df["Put_Change"].sum()

    pcr = round(total_put / total_call, 2)

    # =============================
    # REAL AI MODEL
    # =============================
    X = df[["Call_OI","Put_OI","Call_Change","Put_Change"]]
    y = ((df["Put_Change"] > df["Call_Change"]) & (df["Put_OI"] > df["Call_OI"])).astype(int)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    model = RandomForestClassifier(n_estimators=100)
    model.fit(X_train, y_train)

    df["AI_Pred"] = model.predict(X)
    proba = model.predict_proba(X)

    df["AI_Confidence"] = np.round(proba.max(axis=1)*100,2)
    df["AI_Signal"] = df["AI_Pred"].map({1:"🟢 BUY",0:"🔴 SELL"})

    # Filter strong signals
    df["Final_AI"] = "WAIT"
    for i in range(len(df)):
        if df.loc[i,"AI_Confidence"] > 70:
            df.loc[i,"Final_AI"] = df.loc[i,"AI_Signal"]

    # =============================
    # BEST AI TRADE
    # =============================
    best_trade = df[df["AI_Confidence"] > 75]

    # =============================
    # STRIKE ENTRY SYSTEM
    # =============================
    show_trade=False

    if user_strike != 0:
        row = df[df["Strike"] == user_strike]

        if not row.empty:
            row = row.iloc[0]

            if row["Final_AI"] == "🟢 BUY":
                trade="🟢 BUY CALL"
                entry=user_strike
                target=user_strike+100
                sl=user_strike-50
                show_trade=True

            elif row["Final_AI"] == "🔴 SELL":
                trade="🔴 BUY PUT"
                entry=user_strike
                target=user_strike-100
                sl=user_strike+50
                show_trade=True

    # =============================
    # ACTIVE STRIKE
    # =============================
    active_call = df.loc[df["Call_OI"].idxmax()]
    active_put = df.loc[df["Put_OI"].idxmax()]

    # =============================
    # UI
    # =============================
    st.subheader(f"📌 {symbol}")

    c1,c2,c3 = st.columns(3)
    c1.metric("Call OI", total_call)
    c2.metric("Put OI", total_put)
    c3.metric("PCR", pcr)

    # Final simple signal
    if pcr > 1.2:
        st.success("🟢 Market Bullish")
    elif pcr < 0.8:
        st.error("🔴 Market Bearish")
    else:
        st.warning("⚠ Sideways")

    # =============================
    # AI TABLE
    # =============================
    st.subheader("🤖 AI Signals")
    st.dataframe(df[["Strike","AI_Signal","AI_Confidence","Final_AI"]])

    # =============================
    # BEST TRADE
    # =============================
    st.subheader("🚀 Best AI Trade")

    if not best_trade.empty:
        best = best_trade.iloc[-1]

        if best["AI_Signal"] == "🟢 BUY":
            st.success(f"BUY CALL near {int(best['Strike'])} (Conf: {best['AI_Confidence']}%)")
        else:
            st.error(f"BUY PUT near {int(best['Strike'])} (Conf: {best['AI_Confidence']}%)")
    else:
        st.warning("No strong AI trade")

    # =============================
    # STRIKE ENTRY DISPLAY
    # =============================
    st.subheader("🎯 Manual Strike Trade")

    if show_trade:
        a,b,c,d = st.columns(4)
        a.metric("Type", trade)
        b.metric("Entry", entry)
        c.metric("Target", target)
        d.metric("SL", sl)
    else:
        st.info("No strong signal for selected strike")

    # =============================
    # LEVELS
    # =============================
    st.subheader("🎯 Key Levels")
    st.write("Resistance:", int(active_call["Strike"]))
    st.write("Support:", int(active_put["Strike"]))

    # =============================
    # CHART
    # =============================
    fig = px.bar(df, x="Strike", y=["Call_OI","Put_OI"], barmode="group")
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(df)

else:
    st.info("👉 Click Run REAL AI Scanner")
