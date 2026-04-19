import streamlit as st
import requests
import hashlib
import json

st.title("🚀 Shoonya Working Login")

userid = st.secrets["USER_ID"]
password = st.secrets["PASSWORD"]
api_secret = st.secrets["API_SECRET"]
totp = st.secrets["TOTP"]

def login():
    url = "https://api.shoonya.com/NorenWClientTP/QuickAuth"

    pwd = hashlib.sha256(password.encode()).hexdigest()
    appkey = hashlib.sha256(api_secret.encode()).hexdigest()

    payload = {
        "uid": userid,
        "pwd": pwd,
        "factor2": totp,
        "vc": "FA",
        "appkey": appkey,
        "imei": "abc1234"
    }

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    res = requests.post(url, data=payload)

    st.write("RAW:", res.text)  # debug

    try:
        data = res.json()
        if data.get("stat") == "Ok":
            st.success("✅ Login Success")
        else:
            st.error(data)
    except:
        st.error("❌ Not JSON Response (API Blocked)")

if st.button("Login"):
    login()
