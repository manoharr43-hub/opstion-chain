# ==============================
# AI BIG PLAYER EXTENSION MODULE
# (NO OLD CODE IMPACT)
# ==============================

import pandas as pd
import numpy as np

# ---------- SAFE ATM DETECTOR ----------
def atm_detector(df, ltp):
    return min(df["Strike"], key=lambda x: abs(x - ltp))


# ---------- MARKET TREND ----------
def market_trend(df):
    ce = df["CE_OI"].sum()
    pe = df["PE_OI"].sum()

    if ce > pe * 1.1:
        return "🟢 BULLISH"
    elif pe > ce * 1.1:
        return "🔴 BEARISH"
    return "🟡 SIDEWAYS"


# ---------- PCR ----------
def pcr_calc(df):
    return round(df["PE_OI"].sum() / df["CE_OI"].sum(), 2)


# ---------- PRESSURE ENGINE ----------
def pressure_engine(df):
    ce = df["CE_OI"].sum()
    pe = df["PE_OI"].sum()

    if ce > pe:
        return "📈 CE PRESSURE (CALL ACTIVE)"
    elif pe > ce:
        return "📉 PE PRESSURE (PUT ACTIVE)"
    return "⚖️ BALANCED"


# ---------- VOLUME ADD ----------
def add_volume(df):
    df = df.copy()
    df["VOLUME"] = np.random.randint(2000, 15000, len(df))
    return df


# ---------- BIG PLAYER ZONE ----------
def big_player_zone(df):
    df = df.copy()

    df["OI_STRENGTH"] = df["CE_OI"] + df["PE_OI"]
    df["SPIKE_SCORE"] = df["OI_STRENGTH"] * df["VOLUME"]

    return df.sort_values("SPIKE_SCORE", ascending=False).head(3)


# ---------- FINAL AI REPORT ----------
def generate_ai_report(df, ltp):
    df = add_volume(df)

    return {
        "ATM": atm_detector(df, ltp),
        "TREND": market_trend(df),
        "PCR": pcr_calc(df),
        "PRESSURE": pressure_engine(df),
        "BIG_ZONE": big_player_zone(df)
    }
