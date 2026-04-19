import streamlit as st
import pandas as pd
from NorenRestApiPy.NorenApi import NorenApi

# ==============================
# CONFIG
# ==============================
st.set_page_config(page_title="Shoonya AI PRO", layout="wide")
st.title("🚀 Shoonya AI PRO (Official API)")

# ==============================
# LOAD SECRETS
# ==============================
try:
    creds = st.secrets["shoonyasecrets"]
except:
    st.error("❌ secrets.toml not configured properly")
    st.stop()

# ==============================
# API CLASS
# ==============================
class ShoonyaApiPy(NorenApi):
    def __init__(self):
        super().__init__(
            host='https://api.shoonya.com/NorenWClientTP/',
            websocket='wss://api.shoonya.com/NorenWSTP/'
        )

# ==============================
# LOGIN
# ==============================
def login():
    api = ShoonyaApiPy()

    ret = api.login(
        userid=creds["user_id"],
        password=creds["password"],
        twoFA=creds["totp"],
        vendor_code="FA189165",
        api_secret=creds["api_secret"],
        imei="abc1234"
    )

    return api if ret else None

# ==============================
# UI
# ==============================
symbol = st.sidebar.text_input("Symbol", "NIFTY")

if st.sidebar.button("Login & Fetch"):
    api = login()

    if api:
        st.success("✅ Login Successful")

        try:
            data = api.get_option_chain(
                exchange="NSE",
                tradingsymbol=symbol
            )

            df = pd.DataFrame(data)
            st.dataframe(df)

        except Exception as e:
            st.error(f"Error: {e}")

    else:
        st.error("❌ Login Failed")
