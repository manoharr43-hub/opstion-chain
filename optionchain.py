# =========================================================
# 🚀 NSE OPTION CHAIN AI ANALYZER V2.0
# =========================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import io

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="NSE OPTION CHAIN AI ANALYZER",
    page_icon="🚀",
    layout="wide"
)

# =========================================================
# DARK THEME
# =========================================================

st.markdown("""
<style>

.main {
    background-color: #0E1117;
    color: white;
}

[data-testid="stSidebar"] {
    background-color: #111827;
}

.stMetric {
    background-color: #1F2937;
    border: 1px solid #
