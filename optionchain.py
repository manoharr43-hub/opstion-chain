import streamlit as st
import pandas as pd
import numpy as np

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="🔥 BIG PLAYER AI SCANNER", layout="wide")

# =========================
# INDEX LTP
# =========================
def get_ltp(index):
    return {
        "NIFTY": 24015,
        "BANKNIFTY": 48250,
        "FINNIFTY": 20250
    }.get(index, 24000)

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

    strikes = [base + i * step for i in range(-4, 5)]

    df = pd.DataFrame({
        "Strike": strikes,
        "CE_OI": np.random.randint(1000, 6000, len(strikes)),
        "PE_OI": np.random.randint(1000, 6000, len(strikes)),
    })

    return df

# =========================
# ATM FIND
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
def trend(df):
    ce = df["CE_OI"].sum()
    pe = df["PE_OI"].sum()

    if ce > pe * 1.1:
        return "🟢 BULLISH"
    elif pe > ce * 1.1:
        return "🔴 BEARISH"
    else:
        return "🟡 SIDEWAYS"

# =========================
# PCR
# =========================
def pcr(df):
    return round(df["PE_OI"].sum() / df["CE_OI"].sum(), 2)

# =========================
# PRESSURE ENGINE
# =========================
def pressure(df):
    ce = df["CE_OI"].sum()
    pe = df["PE_OI"].sum()

    if ce > pe:
        return "📈 CE PRESSURE (CALL BUYERS ACTIVE)"
    elif pe > ce:
        return "📉 PE PRESSURE (PUT BUYERS ACTIVE)"
    return "⚖️ BALANCED"

# =========================
# BIG PLAYER ENGINE
# =========================
def big_player(df):
    df = df.copy()

    df["OI_STRENGTH"] = df["CE_OI"] + df["PE_OI"]
    df["SPIKE_SCORE"] = df["OI_STRENGTH"] * df["VOLUME"]

    return df.sort_values("SPIKE_SCORE", ascending=False).head(3)

# =========================
# UI
# =========================
st.title("🔥 NEXT LEVEL BIG PLAYER AI SCANNER")

# Sidebar
st.sidebar.title("📊 Controls")

index = st.sidebar.selectbox("Select Index", ["NIFTY", "BANKNIFTY", "FINNIFTY"])
expiry = st.sidebar.radio("Expiry Type", ["Weekly", "Monthly"])

# Data
ltp = get_ltp(index)
df = option_chain(index)
df = add_volume(df)

atm = find_atm(df, ltp)

trend_value = trend(df)
pcr_value = pcr(df)
pressure_value = pressure(df)
big_zone = big_player(df)

# =========================
# METRICS
# =========================
c1, c2, c3, c4 = st.columns(4)

c1.metric("Index", index)
c2.metric("ATM", atm)
c
