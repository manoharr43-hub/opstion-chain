import streamlit as st
import pandas as pd
from NorenRestApiPy.NorenApi import NorenApi

class ShoonyaApiPy(NorenApi):
    def __init__(self):
        NorenApi.__init__(self, host='https://api.shoonya.com/NorenWSTP/', 
                         websocket='wss://api.shoonya.com/NorenWSTP/')

st.set_page_config(page_title="NSE PRO TERMINAL", layout="wide")
st.title("📊 Shoonya Live Option Chain - PRO")

# --- మీ వివరాలు ఇక్కడ ఫిక్స్ చేస్తున్నాను ---
MY_USER_ID = "FA189165"
MY_VENDOR_CODE = "FA189165_U"
MY_API_KEY = "fHYIfEf8A3CHQGONHONKb2XyGjnl7nLDfQbm2AEkylAy2cf9QdAAgeODl9YB6myN"
MY_IMEI = "106.222.234.124"

with st.sidebar:
    st.header("Shoonya Login")
    u_pwd  = st.text_input("Password", type="password")
    u_totp = st.text_input("TOTP (6 Digits)")
    
    st.divider()
    target_idx = st.selectbox("Select Index", ["NIFTY", "BANKNIFTY"])
    login_btn = st.button("🚀 Login & Load Dashboard")

if login_btn:
    try:
        api = ShoonyaApiPy()
        # నేరుగా పైన ఉన్న వివరాలతో లాగిన్ అవుతుంది
        res = api.login(userid=MY_USER_ID, 
                       password=u_pwd, 
                       twoFA=u_totp, 
                       vendor_code=MY_VENDOR_CODE, 
                       api_secret=MY_API_KEY, 
                       imei=MY_IMEI)
        
        if res and res.get('stat') == 'Ok':
            st.success(f"Success! Welcome {res.get('fname')}")
            
            # 1. Fetch Spot Price
            idx_token = '26000' if target_idx == 'NIFTY' else '26009'
            quote = api.get_quotes(exch='NSE', token=idx_token)
            spot = float(quote['lp'])
            st.metric(f"{target_idx} Spot Price", f"₹{spot}")

            # 2. Fetch Option Chain
            st.subheader(f"Option Chain: {target_idx}")
            search_res = api.search_scrip(exch='NFO', searchtext=target_idx)
            if search_res and 'values' in search_res:
                df = pd.DataFrame(search_res['values'])
                st.dataframe(df[['tsym', 'instname', 'expiry', 'token']], use_container_width=True)
        else:
            # ఇక్కడ అసలు కారణం మెసేజ్ లో కనిపిస్తుంది
            st.error(f"లాగిన్ కాలేదు: {res.get('emsg') if res else 'Server Busy'}")
            
    except Exception as e:
        st.error(f"Error: {str(e)}")
