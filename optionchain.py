import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import time

# App Layout Settings
st.set_page_config(page_title="Nifty Option Chain", layout="wide")

st.title("📊 NSE Nifty Option Chain Analysis")
st.write("Live Data analysis for Support and Resistance")

def get_option_chain_data():
    try:
        url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
        
        # New Updated Headers
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.nseindia.com/option-chain"
        }

        session = requests.Session()
        # Modata main page visit chesi cookies collect chesthunnam
        session.get("https://www.nseindia.com", headers=headers, timeout=10)
        time.sleep(1) # Chinna gap isthunnam (Human behavior la)
        
        response = session.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
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
            st.error(f"NSE nundi data ravaledu. Status Code: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error Occurred: {e}")
        return None

# --- Main App Logic ---
if st.sidebar.button('Fetch Latest Data'):
    df = get_option_chain_data()

    if df is not None and not df.empty:
        max_call_oi = df.loc[df['Call_OI'].idxmax()]
        max_put_oi = df.loc[df['Put_OI'].idxmax()]

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Resistance (Highest Call OI)", int(max_call_oi['Strike']))
        with col2:
            st.metric("Support (Highest Put OI)", int(max_put_oi['Strike']))

        st.subheader("Call OI vs Put OI Chart")
        df_chart = df.sort_values('Strike').tail(30) # More strikes for better view
        fig = px.bar(df_chart, x='Strike', y=['Call_OI', 'Put_OI'], 
                     barmode='group', title="Option Interest Comparison")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Detailed Data Table")
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("Data load kaledu. Please try again after some time.")
else:
    st.info("Paina ఉన్న 'Fetch Latest Data' బటన్ క్లిక్ చేయండి.")
