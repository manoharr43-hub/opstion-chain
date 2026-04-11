import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="PRO NSE AI OPTION CHAIN", layout="wide")

# =========================
# DATA GENERATION (STABLE + SIMULATED GREEKS)
# =========================
def generate_data(symbol):
    base = 22000 if symbol == "NIFTY" else 45000

    strikes = [base + i * 50 for i in range(20)]

    df = pd.DataFrame({
        "Strike Price": strikes,
        "CE OI": np.random.randint(500, 2500, 20),
        "PE OI": np.random.randint(500, 2500, 20),
        "Delta": np.random.uniform(0.1, 0.9, 20).round(2),
        "Theta": np.random.uniform(-60, -5, 20).round(2),
        "Gamma": np.random.uniform(0.001, 0.01, 20).round(4),
        "Vega": np.random.uniform(5, 20, 20).round(2)
    })

    return df


# =========================
# LIVE INDEX DATA (OPTIONAL)
# =========================
def get_live_index(symbol):
    try:
        ticker = "^NSEI" if symbol == "NIFTY" else "^NSEBANK"
        data = yf.download(ticker, period="1d", interval="5m")
        return data
    except:
        return pd.DataFrame()


# =========================
# SIGNAL ENGINE
# =========================
def generate_signal(df):
    ce = df["CE OI"].sum()
    pe = df["PE OI"].sum()

    if pe > ce * 1.05:
        return "🟢 STRONG BUY (PUT WRITING ZONE)"
    elif ce > pe * 1.05:
        return "🔴 STRONG SELL (CALL WRITING ZONE)"
    else:
        return "🟡 SIDEWAYS / NO CLEAR TREND"


# =========================
# SESSION STATE
# =========================
if "df" not in st.session_state:
    st.session_state.df =
