import streamlit as st
import pandas as pd
import pyotp
from NorenRestApiPy import NorenApi
from streamlit_autorefresh import st_autorefresh

# ==========================================
# 1. API CLASS SETUP
# ==========================================
class ShoonyaApiPy(NorenApi):
    def __init__(self):
        NorenApi.__init__(self, 
            host='https://api.shoonya.com/NorenWS/', 
            websocket='wss://api.shoonya.com/NorenWSToken/'
        )

# ==========================================
# 2. LOGIN FUNCTION
# ==========================================
@st.cache_resource
def login_shoonya():
    try:
        creds = st.secrets["shoonya"]
        otp = pyotp.TOTP(creds["totp_key"]).now()

        api = ShoonyaApiPy()
        ret = api.login(
            userid=creds["user_id"],
            password=creds["password"],
            twoFA=otp,
            vendor_code=creds["vendor_code"],
            api_secret=creds["api_secret"],
            imei=creds["imei"]
        )

        if ret and ret.get("stat") == "Ok":
            return api
        else:
            st.error(f"Login Failed: {ret.get('emsg')}")
            return None
    except Exception as e:
        st.error(f"Login Error: {e}")
        return None

# ==========================================
# 3. DATA FETCHING FUNCTION
# ==========================================
def fetch_data(api, symbol):
    try:
        idx_name = "Nifty 50" if symbol == "NIFTY" else "Nifty Bank"
        quote = api.get_quotes("NSE", idx_name)
        
        if not quote or 'lp' not in quote:
            return None, pd.DataFrame()
            
        spot = float(quote["lp"])
        chain = api.get_option_chain("NFO", symbol, spot, 10)
        
        if not chain or 'values' not in chain:
            return spot, pd.DataFrame()

        rows = []
        for item in chain["values"]:
            rows.append({
                "Strike": float(item["stlk"]),
                "Type": item["optt"],
                "LTP": float(item.get("lp", 0)),
                "OI": int(item.get("oi", 0)),
            })

        df = pd.DataFrame(rows)
        ce = df[df["Type"] == "CE"].rename(columns={"LTP": "CE_LTP", "OI": "CE_OI"})
        pe = df[df["Type"] == "PE"].rename(columns={"LTP": "PE_LTP", "OI": "PE_OI"})
        
        final_df = pd.merge(
            ce[["Strike", "CE_LTP", "CE_OI"]],
            pe[["Strike", "PE_LTP", "PE_OI"]],
            on="Strike"
        ).sort_values("Strike")
        
        return spot, final_df
    except Exception as e:
        st.error(f"Fetch Error: {e}")
        return None, pd.DataFrame()

# ==========================================
# 4. MAIN UI
# ==========================================
st.set_page_config(layout="wide")
st.title("📊 Shoonya Live Option Chain")

# Auto-refresh every 10 seconds
st_autorefresh(interval=10000, key="auto_refresh")

api = login_shoonya()

if api:
    st.sidebar.success("Connected")
    symbol = st.selectbox("Select Index", ["NIFTY", "BANKNIFTY"])
    spot, df = fetch_data(api, symbol)

    if spot:
        st.subheader(f"{symbol} Spot: ₹{spot}")

    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("No Data Available")
else:
    st.error("Login Failed")
