import streamlit as st
import pandas as pd
import numpy as np

# SAFE FALLBACK (addon missing ayina app break avvadhu)
try:
    from big_player_ai_addon import generate_report_ai
except:
    def generate_report_ai(df, ltp):
        df = df.copy()

        ce = df.get("CE_OI", pd.Series([0]*len(df))).sum()
        pe = df.get("PE_OI", pd.Series([0]*len(df))).sum()

        return {
            "ATM": ltp,
            "TREND": "🟡 DEMO MODE (Addon Missing)",
            "PCR": round(pe / ce, 2) if ce != 0 else 0,
            "PRESSURE": "⚠ BASIC MODE",
            "BIG_ZONE": df.head(5)
        }
