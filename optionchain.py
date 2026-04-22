import streamlit as st
import pandas as pd
import pyotp
from NorenRestApiPy import NorenApi
from streamlit_autorefresh import st_autorefresh

# ==========================================
# 1. API CLASS (Simplified Fix)
# ==========================================
class ShoonyaApiPy(NorenApi):
    def __init__(self):
        # TypeError rakunda ee format lone undali
        super(ShoonyaApiPy, self).__init__(
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
            userid=creds["user_id"], password=creds["password"],
            twoFA=otp, vendor_code=creds["vendor_code"],
            api_secret=creds["api_secret"], imei=creds["imei"]
        )
        if ret and ret.get("stat") == "Ok":
            return api
        return None
    except Exception as e:
        st.error(f"Login error: {e}")
        return None

# ==========================================
# 3. DATA FETCHING
# ==========================================
def get_data(api, symbol):
    try:
        idx_map = {"NIFTY": "Nifty 50", "BANKNIFTY": "Nifty Bank"}
        quote = api.get_quotes("NSE", idx_map[symbol])
        spot = float(quote["lp"])
        chain = api.get_option_chain("NFO", symbol, spot, 10)
        
        if not chain or 'values' not in chain:
            return spot, pd.DataFrame()

        rows = [{"Strike": float(i["stlk"]), "Type": i["optt"], "LTP": float(i.get("lp", 0)), "OI": int(i.get("oi", 0))} for i in chain["values"]]
        df = pd.DataFrame(rows)
        ce = df[df["Type"] == "CE"].rename(columns={"LTP": "CE_LTP", "OI": "CE_OI"})
        pe = df[df["Type"] == "PE"].rename(columns={"LTP": "PE_LTP", "OI": "PE_OI"})
        final = pd.merge(ce[["Strike", "CE_LTP", "CE_OI"]], pe[["Strike", "PE_LTP", "PE_OI"]], on="Strike").sort_values("Strike")
        return spot, final
    except:
        return None, pd.DataFrame()

# ==========================================
# 4. UI
# ==========================================
st.set_page_config(layout="wide")
st.title("📊 Shoonya Option Chain")

# 10 seconds auto refresh
st_autorefresh(interval=10000, key="refresh")

api = login_shoonya()
if api:
    symbol = st.selectbox("Index", ["NIFTY", "BANKNIFTY"])
    spot, df = get_data(api, symbol)
    if spot:
        st.write(f"### {symbol} Spot: {spot}")
        st.dataframe(df, use_container_width=True)
else:
    st.error("Login Failed! Please check your secrets.")
