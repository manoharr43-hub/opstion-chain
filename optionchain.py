import streamlit as st
import pandas as pd
import requests
import plotly.express as px

st.set_page_config(page_title="Nifty Option Chain", layout="wide")
st.title("📊 NSE Nifty Option Chain Analysis")

def get_data():
    try:
        url = "https://api.allorigins.win/raw?url=https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
        headers = {"User-Agent": "Mozilla/5.0"}

        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            st.error("API error")
            return None

        data = response.json()

        if "records" not in data:
            st.error("No records in data")
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

    except Exception as e:
        st.error(f"Error: {e}")
        return None


# UI
if st.button("Fetch Data"):

    df = get_data()

    if df is not None and not df.empty:

        try:
            max_call = df.loc[df["Call_OI"].idxmax()]
            max_put = df.loc[df["Put_OI"].idxmax()]

            col1, col2 = st.columns(2)
            col1.metric("🔴 Resistance", int(max_call["Strike"]))
            col2.metric("🟢 Support", int(max_put["Strike"]))

            df_chart = df.sort_values("Strike").tail(30)

            fig = px.bar(df_chart, x="Strike", y=["Call_OI", "Put_OI"], barmode="group")
            st.plotly_chart(fig, use_container_width=True)

            st.dataframe(df)

        except Exception as e:
            st.error(f"Display error: {e}")

    else:
        st.warning("No data available")

else:
    st.info("Click Fetch Data")
