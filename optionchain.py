import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import time

st.set_page_config(page_title="Nifty Option Chain", layout="wide")
st.title("📊 NSE Nifty Option Chain Analysis")

# =============================
# FUNCTION
# =============================
@st.cache_data(ttl=60)
def get_option_chain():
    try:
        session = requests.Session()

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://www.nseindia.com/option-chain",
            "Connection": "keep-alive"
        }

        # Step 1: Get cookies
        session.get("https://www.nseindia.com", headers=headers, timeout=10)
        time.sleep(2)

        # Step 2: Fetch API
        url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
        response = session.get(url, headers=headers, timeout=15)

        if response.status_code != 200:
            return None

        data = response.json()

        if "records" not in data or "data" not in data["records"]:
            return None

        rows = []

        for item in data["records"]["data"]:

            strike = item.get("strikePrice", 0)

            call_oi = item.get("CE", {}).get("openInterest", 0)
            put_oi = item.get("PE", {}).get("openInterest", 0)

            rows.append({
                "Strike": strike,
                "Call_OI": call_oi,
                "Put_OI": put_oi
            })

        df = pd.DataFrame(rows)
        return df

    except Exception:
        return None


# =============================
# UI
# =============================
if st.sidebar.button("Fetch Data"):

    with st.spinner("Fetching NSE Data..."):
        df = get_option_chain()

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
        st.error("❌ NSE Data Blocked / Not Available. Try again later.")

else:
    st.info("👉 Click 'Fetch Data' button from sidebar")
