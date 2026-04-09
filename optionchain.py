import streamlit as st
import pandas as pd
import requests
import plotly.express as px

st.set_page_config(page_title="Nifty Option Chain", layout="wide")
st.title("📊 NSE Nifty Option Chain Analysis")

# =============================
# MULTI API FETCH
# =============================
def fetch_data(url):
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            return res.json()
    except:
        return None

def get_data():
    urls = [
        "https://api.allorigins.win/raw?url=https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY",
        "https://api.codetabs.com/v1/proxy?quest=https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
    ]

    for url in urls:
        data = fetch_data(url)
        if data and "records" in data:
            try:
                rows = []
                for item in data["records"]["data"]:
                    rows.append({
                        "Strike": item.get("strikePrice", 0),
                        "Call_OI": item.get("CE", {}).get("openInterest", 0),
                        "Put_OI": item.get("PE", {}).get("openInterest", 0)
                    })
                return pd.DataFrame(rows)
            except:
                continue

    return None


# =============================
# UI
# =============================
if st.button("Fetch Data"):

    with st.spinner("Fetching data..."):
        df = get_data()

    if df is not None and not df.empty:

        max_call = df.loc[df["Call_OI"].idxmax()]
        max_put = df.loc[df["Put_OI"].idxmax()]

        col1, col2 = st.columns(2)
        col1.metric("🔴 Resistance", int(max_call["Strike"]))
        col2.metric("🟢 Support", int(max_put["Strike"]))

        df_chart = df.sort_values("Strike").tail(30)

        fig = px.bar(df_chart, x="Strike", y=["Call_OI", "Put_OI"], barmode="group")
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(df)

    else:
        st.error("❌ All APIs failed. Try after some time.")

else:
    st.info("👉 Click Fetch Data")
