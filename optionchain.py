import streamlit as st
import pandas as pd
import numpy as np

# =========================
# PAGE SETUP
# =========================
st.set_page_config(page_title="🔥 NSE BIG PLAYER AI v2", layout="wide")

# =========================
# INDEX LTP
# =========================
def get_ltp(index):
    ltp_map = {
        "NIFTY": 24015,
        "BANKNIFTY": 48250,
        "FINNIFTY": 20250
    }
    return ltp_map.get(index, 24000)

# =========================
# OPTION CHAIN (SIM DATA)
# =========================
def option_chain(index):
    if index == "NIFTY":
        base, step = 24000, 50
    elif index == "BANKNIFTY":
        base, step = 48200, 100
    else:
        base, step = 20200, 50

    strikes = [base + i * step for i in range(-5, 6)]

    df = pd.DataFrame({
        "Strike": strikes,
        "CE_OI": np.random.randint(1000, 7000, len(strikes)),
        "PE_OI": np.random.randint(1000, 7000, len(strikes)),
    })

    return df

# =========================
# ADD VOLUME
# =========================
def add_volume(df):
    df = df.copy()
    df["VOLUME"] = np.random.randint(2000, 20000, len(df))
    return df

# =========================
# ATM DETECTION
# =========================
def find_atm(df, ltp):
    return min(df["Strike"], key=lambda x: abs(x - ltp))

# =========================
# TREND ENGINE
# =========================
def trend_engine(df):
    ce = df["CE_OI"].sum()
    pe = df["PE_OI"].sum()

    if ce > pe * 1.1:
        return "🟢 BULLISH"
    elif pe > ce * 1.1:
        return "🔴 BEARISH"
    else:
        return "🟡 SIDEWAYS"

# =========================
# PCR CALC
# =========================
def pcr(df):
    return round(df["PE_OI"].sum() / df["CE_OI"].sum(), 2)

# =========================
# PRESSURE ENGINE
# =========================
def pressure_engine(df):
    ce = df["CE_OI"].sum()
    pe = df["PE_OI"].sum()

    if ce > pe:
        return "📈 CE PRESSURE (CALL BUYERS)"
    elif pe > ce
