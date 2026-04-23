import streamlit as st
import pandas as pd
import pyotp
from NorenRestApiPy import NorenApi

# ==========================================
# API CLASS
# ==========================================
class ShoonyaApiPy(NorenApi):
    def __init__(self):
        super().__init__(
            host='https://api.shoonya.com/NorenWSTP/',
            websocket='wss://api.shoonya.com/NorenWSTP/'
        )

# ==========================================
# LOGIN (ONLY ONCE)
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
# OPTION CHAIN (CUSTOM WRAPPER)
# ==========================================
def fetch_data(api, symbol):
    try:
        idx_map = {"NIFTY": "Nifty 50", "BANKNIFTY": "Nifty Bank"}
        quote = api.get_quotes("NSE", idx_map[symbol])
        spot = float(quote["lp"])

        # Shoonyaలో direct option chain లేదు → మీరు market quotes వాడాలి
        # Example wrapper (pseudo)
        chain = api.get_option_chain("NFO", symbol, spot, 10)

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
        final = pd.merge(
            ce[["Strike", "CE_LTP", "CE_OI"]],
            pe[["Strike", "PE_LTP", "PE_OI"]],
            on="Strike"
        ).sort_values("Strike")
        return spot, final
    except Exception as e:
        st.error(f"Data Error: {e}")
        return None, pd.DataFrame()

# ==========================================
# UI
# ==========================================
st.set_page_config(layout="wide")
st.title("📊 Shoonya Option Chain PRO")

api = login_shoonya()

if api:
    st.success("✅ Connected to Shoonya")
    symbol = st.selectbox("Select Index", ["NIFTY", "BANKNIFTY"])
    spot, df = fetch_data(api, symbol)

    if spot:
        st.subheader(f"{symbol} Spot: ₹{spot}")

    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("No Data")

    # Auto refresh every 10 seconds
    st.experimental_rerun()

else:
    st.error("❌ Login Failed")
