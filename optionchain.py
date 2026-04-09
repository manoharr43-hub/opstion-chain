import streamlit as st
import pandas as pd
import requests
import plotly.express as px

st.set_page_config(page_title="Nifty Option Chain", layout="wide")
st.title("📊 NSE Nifty Option Chain Analysis")

# =============================
# FUNCTION
# =============================
@st.cache_data(ttl=60)
def get_data():
    try:
        url = "https://api.allorigins.win/raw?url=https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
        
        response = requests.get(url, timeout=15)

        if response.status_code != 200:
            return None

        data = response.json()

        if "records" not in data or "data" not in data["records"]:
            return None

        rows = []

        for item in data["records"]["data"]:
            rows.append({
                "Strike": item.get("strikePrice", 0),
                "Call_OI": item.get("CE", {}).get("openInterest", 0),
                "Put_OI": item.get("PE", {}).get("openInterest", 0)
            })

        df = pd.DataFrame(rows)
        return df

    except:
        return None


# =============================
# UI
# =============================
if st.button("Fetch Data"):

    with st.spinner("Fetching data..."):
        df = get_data()

    if df is not None and not df.empty:

        # Support & Resistance
        max_call = df.loc[df["Call_OI"].idxmax()]
        max_put = df.loc[df["Put_OI"].idxmax()]

        col1, col2 = st.columns(2)
        col1.metric("🔴 Resistance (Max Call OI)", int(max_call["Strike"]))
        col2.metric("🟢 Support (Max Put OI)", int(max_put["Strike"]))

        # Chart
        st.subheader("Call vs Put OI")
        df_chart = df.sort_values("Strike").tail(30)

        fig = px.bar(
            df_chart,
            x="Strike",
            y=["Call_OI", "Put_OI"],
            barmode="group"
        )

        st.plotly_chart(fig, use_container_width=True)

        # Table
        st.dataframe(df)

    else:
        st.error("❌ Data not available. Try again later.")

else:
    st.info("👉 Click 'Fetch Data'")
