import streamlit as st
import sys
import os

# =========================
# LOAD LOCAL API
# =========================
sys.path.append(os.path.join(os.getcwd(), "NorenRestApiPy"))

from NorenApi import NorenApi

# =========================
# API CLASS
# =========================
class ShoonyaApiPy(NorenApi):
    def __init__(self):
        NorenApi.__init__(
            self,
            host='https://api.shoonya.com/NorenWSTP/',
            websocket='wss://api.shoonya.com/NorenWS/'
        )

# =========================
# UI
# =========================
st.set_page_config(layout="wide")
st.title("🚀 Shoonya API Test (Local Library)")

# =========================
# TEST API LOAD
# =========================
try:
    api = ShoonyaApiPy()
    st.success("✅ NorenApi Loaded Successfully")

except Exception as e:
    st.error(f"❌ Error: {e}")
