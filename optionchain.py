import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh
import ta  # Technical Analysis library

# =============================
# 1. CONFIG
# =============================
st.set_page_config(page_title="🔥 MANOHAR NSE AI PRO", layout="wide")
st_autorefresh(interval=60000, key="refresh")

st.title("🚀 MANOHAR NSE AI PRO TERMINAL")
st.markdown("---")

# =============================
# 2. ANALYSIS LOGIC (UPGRADED)
# =============================
def analyze_data(df):
    if df is None or len(df) < 10:
        return None

    # EMA
    e20 = df['Close'].ewm(span=20).mean()
    e50 = df['Close'].ewm(span=50).mean()

    # RSI
    rsi = ta.momentum.RSIIndicator(df['Close'], window=14).rsi().iloc[-1]

    # Volume
    vol = df['Volume']
    avg_vol = vol.rolling(window=20).mean()

    # Current values
    curr_price = df['Close'].iloc[-1]
    curr_e20, curr_e50 = e20.iloc[-1], e50.iloc[-1]
    curr_vol, curr_avg_vol = vol.iloc[-1], avg_vol.iloc[-1]

    # Candlestick confirmation
    last_candle = df.iloc[-1]
    candle_signal = "Bullish" if last_candle['Close'] > last_candle['Open'] else "Bearish"

    # Trend + Big Player
    cp_strength = "🔵 CALL STRONG" if curr_e20 > curr_e50 else "🔴 PUT STRONG"
    if curr_vol > curr_avg_vol * 2:
        big_player = "🔥 EXTREME INSTITUTIONAL"
    elif curr_vol > curr_avg_vol * 1.5:
        big_player = "🐋 BIG PLAYER ACTIVE"
    else:
        big_player = "💤 NORMAL"

    # Risk calculation
    recent_high = df['High'].iloc[-10:].max()
    recent_low = df['Low'].iloc[-10:].min()
    risk = (recent_high - recent_low) if (recent_high - recent_low) > 0 else curr_price * 0.01

    # Signal Logic
    observation, entry, sl, target = "WAIT", 0, 0, 0
    if curr_e20 > curr_e50 and curr_vol > curr_avg_vol and candle_signal == "Bullish" and rsi > 45:
        observation = "🚀 STRONG BUY"
        entry = curr_price
        sl = curr_price - (risk * 0.5)
        target = curr_price + risk
    elif curr_e20 < curr_e50 and curr_vol > curr_avg_vol and candle_signal == "Bearish" and rsi < 55:
        observation = "💀 STRONG SELL"
        entry = curr_price
        sl = curr_price + (risk * 0.5)
        target = curr_price - risk

    return (cp_strength, observation, big_player, round(entry,2), round(sl,2), round(target,2), round(rsi,2))

# =============================
# 3. NSE SECTORS
# =============================
all_sectors = {
    "Nifty 50": ["RELIANCE","TCS","INFY","HDFCBANK","ICICIBANK","SBIN","ITC","LT","AXISBANK","BHARTIARTL"],
    "Pharma": ["SUNPHARMA","DRREDDY","CIPLA","APOLLOHOSP","DIVISLAB"]
}

# =============================
# 4. SIDEBAR
# =============================
st.sidebar.title("📂 Backtest Panel")
bt_date = st.sidebar.date_input("Select Date", datetime.now() - timedelta(days=1))
bt_stock_input = st.sidebar.text_input("Stock (optional)", "").upper()

# =============================
# 5. MAIN SCANNER
# =============================
selected_sector = st.selectbox("📂 Select Sector", list(all_sectors.keys()))
stocks = all_sectors[selected_sector]

if st.button("🔍 START LIVE SCANNER", use_container_width=True):
    results = []
    with st.spinner("AI Scanning Market..."):
        for s in stocks:
            try:
                t = yf.Ticker(s + ".NS")
                df = t.history(period="2d", interval="15m")
                res = analyze_data(df)
                if res:
                    results.append({
                        "Stock": s,
                        "Price": round(df['Close'].iloc[-1], 2),
                        "Trend": res[0],
                        "Signal": res[1],
                        "Big Player": res[2],
                        "Entry": res[3],
                        "SL": res[4],
                        "Target": res[5],
                        "RSI": res[6],
                        "Time": df.index[-1].strftime('%H:%M')
                    })
            except:
                continue
    st.dataframe(pd.DataFrame(results), use_container_width=True)

# =============================
# 6. BACKTEST (FULL DAY FIX)
# =============================
st.markdown("---")
st.subheader(f"📅 Backtest Report - {bt_date}")

if st.sidebar.button("📊 RUN BACKTEST"):
    bt_results = []
    target_list = [bt_stock_input] if bt_stock_input else stocks
    with st.spinner("Running Backtest..."):
        for s in target_list:
            try:
                t = yf.Ticker(s + ".NS")
                df_hist = t.history(start=bt_date, end=bt_date + timedelta(days=1), interval="15m")
                if not df_hist.empty:
                    for i in range(5, len(df_hist)):   # ✅ full-day signals
                        sub_df = df_hist.iloc[:i+1]
                        res = analyze_data(sub_df)
                        if res and res[1] != "WAIT":
                            bt_results.append({
                                "Time": sub_df.index[-1].strftime('%H:%M'),
                                "Stock": s,
                                "Signal": res[1],
                                "Big Player": res[2],
                                "Entry": res[3],
                                "SL": res[4],
                                "Target": res[5],
                                "RSI": res[6]
                            })
            except:
                continue
    st.dataframe(pd.DataFrame(bt_results), use_container_width=True)
