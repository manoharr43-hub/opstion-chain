import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import time

st.set_page_config(page_title="Nifty Option Chain", layout="wide")
st.title("📊 NSE Nifty Option Chain Analysis")

def get_option_chain_data():
    try:
        # NSE Direct URL
        base_url = "https://www.nseindia.com/"
        api_url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
            "Referer": "https://www.nseindia.com/option-chain"
        }

        session = requests.Session()
        
        # Step 1: Modata main page visit chesi Cookies teeskuntunnam
        session.get(base_url, headers=headers, timeout=10)
        time.sleep(2) # 2 seconds gap
        
        # Step 2: Ippudu API call chesthunnam
        response = session.get(api_url, headers=headers, timeout=15)

        if response.status_code == 200:
            data = response.json()
            # Ikkada data undho ledho check chesthunnam
            if 'records' in data and 'data' in data['records']:
                raw_data = data['records']['data']
                rows = []
                for item in raw_data:
                    rows.append({
                        "Strike": item['strikePrice'],
                        "Call_OI": item.get('CE', {}).get('openInterest', 0),
                        "Put_OI": item.get('PE', {}).get('openInterest', 0)
                    })
                return pd.DataFrame(rows)
            else:
                st.error("NSE nundi Response vachindi kaani Data blank ga undi (Blocked).")
                return None
        else:
            st.error(f"NSE Error: Status Code {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error: {e}")
        return None

# --- Main Part ---
if st.sidebar.button('Fetch Latest Data'):
    with st.spinner('NSE nundi data testunnanu, okka nimisham...'):
        df = get_option_chain_data()

    if df is not None and not df.empty:
        # Support & Resistance Calculations
        max_call = df.loc[df['Call_OI'].idxmax()]
        max_put = df.loc[df['Put_OI'].idxmax()]

        c1, c2 = st.columns(2)
        c1.metric("Resistance (Max Call OI)", int(max_call['Strike']))
        c2.metric("Support (Max Put OI)", int(max_put['Strike']))

        # Graph
        st.subheader("Call vs Put Open Interest")
        df_chart = df.sort_values('Strike').tail(30)
        fig = px.bar(df_chart, x='Strike', y=['Call_OI', 'Put_OI'], barmode='group')
        st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(df)
    else:
        st.warning("Ippudu data dorakatledu. Refresh chesi 1 minute agi try cheyandi.")
else:
    st.info("Side panel lo unna 'Fetch Latest Data' button click cheyandi.")
