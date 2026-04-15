import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# =============================
# 1. CONFIG
# =============================
st.set_page_config(page_title="🔥 MANOHAR NSE AI PRO + BOLT AI", layout="wide")
st_autorefresh(interval=60000, key="refresh")

st.title("🚀 MANOHAR NSE AI PRO TERMINAL + 🤖 BOLT AI")
st.markdown("---")

# =============================
# 2. BOLT AI (NEW LAYER - SAFE ADD)
# =============================
def bolt_ai(curr_e20, curr_e50, curr_vol, curr_avg_vol):
    """
    Simple AI prediction layer (probability style)
    """
    score = 50  # base neutral

    if curr_e20 > curr_e50:
        score += 20
    else:
        score -= 20

    if curr_vol > curr_avg_vol * 1.5:
        score += 15
    else:
        score -= 10

    if score >= 70:
        return "🚀 BOLT BUY (HIGH CONFIDENCE)", score
    elif score <= 40:
        return "💀 BOLT SELL (HIGH RISK DOWN)", score
    else:
        return "⚪ BOLT WAIT (NO CLEAR SIGNAL)", score

# =============================
# 3. ANALYSIS LOGIC (OLD SAFE + NO CHANGE)
# =============================
def analyze_data(df):
    if df is None or len(df) < 20:
        return None

    e20 = df['Close'].ewm(span=20).mean()
    e50 = df['Close'].ewm(span=50).mean()

    vol = df['Volume']
    avg_vol = vol.rolling(window=20).mean()

    curr_price = df['Close'].iloc[-1]
    curr_e20 = e20.iloc[-1]
    curr_e50 = e50.iloc[-1]
    curr_vol = vol.iloc[-1]
    curr_avg_vol = avg_vol.iloc[-1]

    # =============================
    # OLD TREND LOGIC
    # =============================
    cp_strength = "🔵 CALL STRONG" if curr_e20 > curr_e50 else "🔴 PUT STRONG"

    big_player = "🔥 ACTIVE" if curr_vol > (curr_avg_vol * 1.5) else "💤 NORMAL"

    observation = "WAIT"
    entry, sl, target = 0, 0, 0

    recent_high = df['High'].iloc[-10:].max()
    recent_low = df['Low'].iloc[-10:].min()
    risk = recent_high - recent_low if recent_high > recent_low else curr_price * 0.01

    if curr_e20 > curr_e50 and curr_vol > curr_avg_vol:
        observation = "🚀 STRONG BUY"
        entry = curr_price
        sl = curr_price - (risk * 0.5)
        target = curr_price + risk

    elif curr_e20 < curr_e50 and curr_vol > curr_avg_vol:
        observation = "💀 STRONG SELL"
        entry = curr_price
        sl = curr_price + (risk * 0.5)
        target = curr_price - risk

    # =============================
    # BOLT AI CALL (NEW ADDITION)
    # =============================
    bolt_signal, bolt_score = bolt_ai(curr_e20, curr_e50, curr_vol, curr_avg_vol)

    return (
        cp_strength,
        observation,
        big_player,
        bolt_signal,
        bolt_score,
        round(entry, 2),
        round(sl, 2),
        round(target, 2)
    )

# =============================
# 4. NSE SECTORS
# =============================
all_sectors = {
    "Nifty 50": ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "SBIN", "ITC", "LT"],
    "Banking": ["SBIN", "AXISBANK", "KOTAKBANK", "HDFCBANK", "ICICIBANK"],
    "Auto": ["TATAMOTORS", "MARUTI", "M&M"],
    "IT": ["TCS", "INFY", "WIPRO", "HCLTECH"],
    "Pharma": ["SUNPHARMA", "DRREDDY", "CIPLA"]
}

# =============================
# 5. LIVE SCANNER
# =============================
selected_sector = st.selectbox("📂 Select Sector", list(all_sectors.keys()))
stocks = all_sectors[selected_sector]

if st.button("🔍 START LIVE SCANNER", use_container_width=True):

    results = []

    with st.spinner("AI + BOLT Scanning..."):
        for s in stocks:
            try:
                df = yf.Ticker(s + ".NS").history(period="2d", interval="15m")
                res = analyze_data(df)

                if res:
                    results.append({
                        "Stock": s,
                        "Price": round(df['Close'].iloc[-1], 2),
                        "Trend":
