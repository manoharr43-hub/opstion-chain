import streamlit as st
from optionchain import option_chain_dashboard

st.set_page_config(
    page_title="NSE OPTIONCHAIN PRO",
    layout="wide"
)

st.title("🚀 NSE OPTIONCHAIN PRO")

option_chain_dashboard()
