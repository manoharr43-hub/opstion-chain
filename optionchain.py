import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import time

st.set_page_config(page_title="Nifty Option Chain", layout="wide")
st.title("📊 NSE Nifty Option Chain Analysis")

@st.cache_data(ttl=60)
def get_option_chain_data():
    try:
        url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"

        session = requests.Session()

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br"
        }

        # Step 1: Get cookies
        session.get("https://www.nseindia.com", headers=headers)
        time.sleep(1)

        # Step 2: API call
        response = session.get(url, headers=headers)

        if response.status_code != 200:
            st.error(f"NSE Blocked: {response.status_code}")
            return None

        data = response.json()

        if "records" not in data:
            st.error("No records found")
            return None

        rows = []
        for item in data["records"]["data"]:

            strike = item.get("strikePrice", 0)

            call_oi = 0
            put_oi = 0

            if "CE" in item:
                call_oi = item["CE"].get("openInterest", 0)

            if "PE" in item:
                put_oi = item["PE"].get("openInterest", 0)

            rows.append({
                "Strike": strike,
                "Call_OI": call_oi,
                "Put_OI": put_oi
            })

        df = pd.DataFrame(rows)
        return df

    except Exception as e:
        st.error(f"Error: {e}")
        return None


# UI
if st.sidebar.button('Fetch Latest Data'):
    with st.spinner('Fetching data...'):
        df = get_option_chain_data()

    if df is not None and not df.empty:

        max_call = df.loc[df['Call_OI'].idxmax()]
        max_put = df.loc[df['Put_OI'].idxmax()]

        c1, c2 = st.columns(2)
        c1.metric("Resistance (Max Call OI)", int(max_call['Strike']))
        c2.metric("Support (Max Put OI)", int(max_put['Strike']))

        st.subheader("Call vs Put OI")

        df_chart = df.sort_values('Strike').tail(30)

        fig = px.bar(
            df_chart,
            x='Strike',
            y=['Call_OI', 'Put_OI'],
            barmode='group'
        )

        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df)

    else:
        st.warning("No data. Try again after 1 minute.")

else:
    st.info("Click 'Fetch Latest Data'")
