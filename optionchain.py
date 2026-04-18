import streamlit as st
import pandas as pd
import requests
import hashlib
import time
from streamlit_autorefresh import st_autorefresh

# =============================
# CONFIG
# =============================
st.set_page_config(page_title="🔥 NSE AI ULTRA PRO (SHOONYA)", layout="wide")
st_autorefresh(interval=30000, key="refresh")
st.title("🚀 NSE AI ULTRA PRO (LIVE DATA - SHOONYA)")

# =============================
# USER INPUT (SECURE)
# =============================
st.sidebar.header("🔐 Shoonya Login")

userid = st.sidebar.text_input("User ID")
password = st.sidebar.text_input("Password", type="password")
totp = st.sidebar.text_input("TOTP")

vendor_code = "FA"      # change if needed
api_secret = "YOUR_API_SECRET"
imei = "abc1234"

# =============================
# LOGIN FUNCTION
# =============================
def shoonya_login():
    try:
        url = "https://api.shoonya.com/NorenWClientTP/QuickAuth"

        pwd = hashlib.sha256(password.encode()).hexdigest()

        data = {
            "uid": userid,
            "pwd": pwd,
            "factor2": totp,
            "vc": vendor_code,
            "appkey": hashlib.sha256(api_secret.encode()).hexdigest(),
            "imei": imei
        }

        res = requests.post(url, data=data)
        return res.json()

    except Exception as e:
        st.error(f"Login Error: {e}")
        return None

# =============================
# OPTION CHAIN (SHOONYA)
# =============================
def get_option_chain(token):
    url = "https://api.shoonya.com/NorenWClientTP/GetOptionChain"

    data = {
        "uid": userid,
        "token": token,
        "exch": "NFO",
        "tsym": "NIFTY",
        "cnt": "10"
    }

    try:
        res = requests.post(url, data=data)
        return res.json()
    except:
        return []

# =============================
# LOGIN BUTTON
# =============================
if st.sidebar.button("Login"):
    login_data = shoonya_login()

    if login_data and login_data.get("stat") == "Ok":
        st.success("✅ Login Success")

        token = login_data.get("susertoken")

        option_data = get_option_chain(token)

        if not option_data:
            st.error("❌ No Option Data")
            st.stop()

        call_rows, put_rows = [], []

        for row in option_data:
            if "CE" in row:
                ce = row["CE"]
                call_rows.append({
                    "Strike": ce.get("strprc"),
                    "OI": int(ce.get("oi", 0)),
                    "Chg OI": int(ce.get("oi_chg", 0)),
                    "LTP": float(ce.get("lp", 0))
                })

            if "PE" in row:
                pe = row["PE"]
                put_rows.append({
                    "Strike": pe.get("strprc"),
                    "OI": int(pe.get("oi", 0)),
                    "Chg OI": int(pe.get("oi_chg", 0)),
                    "LTP": float(pe.get("lp", 0))
                })

        call_df = pd.DataFrame(call_rows)
        put_df = pd.DataFrame(put_rows)

        # =============================
        # METRICS
        # =============================
        call_oi = call_df["OI"].sum()
        put_oi = put_df["OI"].sum()

        call_chg = call_df["Chg OI"].sum()
        put_chg = put_df["Chg OI"].sum()

        pcr = round(put_oi / call_oi, 2) if call_oi else 1

        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("CALL OI", call_oi)
        col2.metric("CALL OI Chg", call_chg)
        col3.metric("PUT OI", put_oi)
        col4.metric("PUT OI Chg", put_chg)
        col5.metric("PCR", pcr)

        # =============================
        # TOP STRIKES
        # =============================
        st.subheader("🔥 Top CALL")
        st.dataframe(call_df.sort_values("OI", ascending=False).head(5))

        st.subheader("🔥 Top PUT")
        st.dataframe(put_df.sort_values("OI", ascending=False).head(5))

        # =============================
        # SIGNAL LOGIC
        # =============================
        bias = "SIDEWAYS"
        if pcr > 1.2:
            bias = "BULLISH 🚀"
        elif pcr < 0.8:
            bias = "BEARISH 🔻"

        signal = "WAIT"
        if bias == "BULLISH 🚀" and put_chg > call_chg:
            signal = "🔥 CE BUY"
        elif bias == "BEARISH 🔻" and call_chg > put_chg:
            signal = "🔥 PE BUY"

        st.success(f"🤖 AI Signal: {signal}")

    else:
        st.error("❌ Login Failed")
