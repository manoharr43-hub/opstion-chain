import streamlit as st
import pandas as pd
from NorenRestApiPy.NorenApi import NorenApi

# =============================
# CONFIG
# =============================
st.set_page_config(page_title="🔥 NSE AI ULTRA PRO", layout="wide")
st.title("🚀 NSE AI ULTRA PRO (WORKING)")

# =============================
# API CLASS
# =============================
class ShoonyaApi(NorenApi):
    def __init__(self):
        super().__init__(
            host='https://api.shoonya.com/NorenWClientTP/',
            websocket='wss://api.shoonya.com/NorenWSTP/'
        )

api = ShoonyaApi()

# =============================
# LOGIN FUNCTION
# =============================
def login():
    try:
        ret = api.login(
            userid=st.secrets["USER_ID"],
            password=st.secrets["PASSWORD"],
            twoFA=st.secrets["TOTP"],
            vendor_code="FA",
            api_secret=st.secrets["API_SECRET"],
            imei="abc1234"
        )

        if ret and ret.get("stat") == "Ok":
            st.success("✅ Login Success")
            return True
        else:
            st.error(f"❌ Login Failed: {ret}")
            return False

    except Exception as e:
        st.error(f"Error: {e}")
        return False

# =============================
# OPTION CHAIN
# =============================
def get_option_chain():
    try:
        data = api.get_option_chain(
            exchange="NFO",
            tradingsymbol="NIFTY",
            strikeprice="0",
            count="10"
        )
        return data
    except Exception as e:
        st.error(f"Option Chain Error: {e}")
        return None

# =============================
# BUTTON
# =============================
if st.button("🔐 Login & Get Data"):

    if login():

        data = get_option_chain()

        if not data:
            st.stop()

        call_rows, put_rows = [], []

        for row in data.get("values", []):

            if row.get("optt") == "CE":
                call_rows.append({
                    "Strike": row.get("strprc"),
                    "OI": int(row.get("oi", 0)),
                    "LTP": float(row.get("lp", 0))
                })

            elif row.get("optt") == "PE":
                put_rows.append({
                    "Strike": row.get("strprc"),
                    "OI": int(row.get("oi", 0)),
                    "LTP": float(row.get("lp", 0))
                })

        call_df = pd.DataFrame(call_rows)
        put_df = pd.DataFrame(put_rows)

        if call_df.empty or put_df.empty:
            st.warning("⚠️ No data")
            st.stop()

        # =============================
        # METRICS
        # =============================
        call_oi = call_df["OI"].sum()
        put_oi = put_df["OI"].sum()

        pcr = round(put_oi / call_oi, 2)

        col1, col2, col3 = st.columns(3)
        col1.metric("CALL OI", call_oi)
        col2.metric("PUT OI", put_oi)
        col3.metric("PCR", pcr)

        # =============================
        # TABLE
        # =============================
        st.subheader("📊 CALL DATA")
        st.dataframe(call_df)

        st.subheader("📊 PUT DATA")
        st.dataframe(put_df)

        # =============================
        # SIGNAL
        # =============================
        signal = "WAIT"

        if pcr > 1.2:
            signal = "🔥 CE BUY"
        elif pcr < 0.8:
            signal = "🔥 PE BUY"

        st.success(f"🤖 Signal: {signal}")
