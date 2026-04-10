import streamlit as st
import pandas as pd
import numpy as np

# =========================
# APP CONFIG
# =========================
st.set_page_config(page_title="🔥 NSE BIG PLAYER AI", layout="wide")

# =========================
# INDEX DATA
# =========================
def get_ltp(index):
    data = {
        "NIFTY": 24015,
        "BANKNIFTY": 48250,
        "FINNIFTY": 20250
    }
    return data.get(index, 24000)

# =========================
# OPTION CHAIN SIM DATA
# =========================
def option_chain(index):
    if index == "NIFTY":
        base, step = 24000, 50
    elif index == "BANKNIFTY":
        base, step = 48200, 100
    else:
        base, step = 20200, 50

    strikes = [base + i * step for i in range(-4, 5)]

    df = pd.DataFrame({
        "Strike": strikes,
        "CE_OI": np.random.randint(1000, 6000, len(strikes)),
        "PE_OI": np.random.randint(1000, 6000, len(strikes)),
    })

    return df

# =========================
# ATM LOGIC
# =========================
def find_atm(df, ltp):
    return min(df["Strike"], key=lambda x: abs(x - ltp))

# =========================
# VOLUME ADD
# =========================
def add_volume(df):
    df = df.copy()
    df["VOLUME"] = np.random.randint(2000, 15000, len(df))
    return df

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
    return "🟡
