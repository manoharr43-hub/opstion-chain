import streamlit as st
import pandas as pd
from NorenRestApiPy.NorenApi import NorenApi
import datetime

# --- SHOONYA API CLASS ---
class ShoonyaApiPy(NorenApi):
    def __init__(self):
        NorenApi.__init__(self, host='https://api.shoonya.com/NorenWSTP/', 
                         websocket='wss://api.shoonya.com/NorenWSTP/')

# --- PAGE CONFIG ---
st.set_page_config(page_title="Shoonya Pro Terminal", layout="wide")
st.title("📊 Shoonya Live Option Chain")

# --- SIDEBAR: LOGIN DETAILS ---
with st.sidebar:
    st.header("Shoonya Login")
    u_id   = st.text_input("User ID", value="FA12345") # మీ User ID ఇవ్వండి
    u_pwd  = st.text_input("Password", type="password")
    u_totp = st.text_input("TOTP (From App)")
    u_vc   = st.text_input("Vendor Code", value="FA12345_U")
    u_key  = st.text_input("API Key")
    u_imei = st.text_input("IMEI", value="abc12345")
    
    login_btn = st.button("🚀 Login & Fetch Data")

# --- MAIN LOGIC ---
if login_btn:
    try:
        api = ShoonyaApiPy()
        # Login Attempt
        res = api.login(userid=u_id, password=u_pwd, twoFA=u_totp, 
                       vendor_code=u_vc, api_secret=u_key, imei=u_imei)
        
        if res and res.get('stat') == 'Ok':
            st.success(f"Welcome {res.get('fname')}! Connection Active.")
            
            # Index Selection
            idx = st.selectbox("Select Index", ["NIFTY", "BANKNIFTY"])
            exch = 'NSE' if idx == 'NIFTY' else 'NSE' # Standard NSE
            
            with st.spinner("Fetching Live Option Chain..."):
                # 1. Get Index Quote for ATM price
                quote = api.get_quotes(exch='NSE', token='26000' if idx == 'NIFTY' else '26009')
                lp = float(quote['lp'])
                st.metric(f"{idx} Spot Price", f"₹{lp}")

                # 2. Search Option Chain (Simplified Example)
                # గమనిక: Shoonya లో ఆప్షన్ చైన్ కోసం స్క్రిప్ట్స్ సెర్చ్ చేయాలి
                search_res = api.search_scrip(exch='NFO', searchtext=idx)
                
                if search_res:
                    df = pd.DataFrame(search_res['values'])
                    # Filter for latest expiry
                    st.subheader(f"Live Strikes for {idx}")
                    st.dataframe(df[['tsym', 'instname', 'token']], use_container_width=True)
                else:
                    st.warning("No option strikes found. Check API permissions.")
        else:
            st.error(f"Login Failed: {res.get('emsg') if res else 'Unknown Error'}")
            
    except Exception as e:
        st.error(f"Error: {str(e)}")

else:
    st.info("👈 ఎడమవైపు మీ Shoonya వివరాలు ఎంటర్ చేసి 'Login' నొక్కండి.")

st.divider()
st.caption("Developed for Manohar - Variety Motors | Shoonya API Mode")
