import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.express as px

st.set_page_config(page_title="Nifty Option Chain", layout="wide")
st.title("📊 Nifty Option Chain Analysis")

# =============================
# REAL DATA FETCH
# =============================
def fetch_real_data():
    try:
        url = "https://api.allorigins.win/raw?url=https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
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
                "Put_OI": item.get("PE", {}).get("openInterest", 0)
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
            "Put_OI": np.random.randint(10000, 100000)
        })

    return pd.DataFrame(data)


# =============================
# MAIN LOGIC
# =============================
if st.button("Fetch Data"):

    with st.spinner("Loading data..."):
        df = fetch_real_data()

    # 👉 fallback to demo
    if df is None or df.empty:
        st.warning("⚠ Live data not available, showing demo data")
        df = generate_demo()

    # Support & Resistance
    max_call = df.loc[df["Call_OI"].idxmax()]
    max_put = df.loc[df["Put_OI"].idxmax()]

    col1, col2 = st.columns(2)
    col1.metric("🔴 Resistance", int(max_call["Strike"]))
    col2.metric("🟢 Support", int(max_put["Strike"]))

    # Chart
    st.subheader("Call vs Put OI")

    fig = px.bar(
        df,
        x="Strike",
        y=["Call_OI", "Put_OI"],
        barmode="group"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(df)

else:
    st.info("👉 Click Fetch Data")
