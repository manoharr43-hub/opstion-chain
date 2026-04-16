import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# =============================
# 1. CONFIG
# =============================
st.set_page_config(page_title="🔥 MANOHAR NSE AI PRO", layout="wide")
st_autorefresh(interval=60000, key="refresh")

st.title("🚀 MANOHAR NSE AI PRO TERMINAL")
st.markdown("---")

# =============================
# 2. ANALYSIS LOGIC (SAFE)
# =============================
def analyze_data(df):
    if df is None or len(df) < 50:   # 🔥 increased safety
        return None

    df = df.copy()

    # EMA
    df['E20'] = df['Close'].ewm(span=20).mean()
    df['E50'] = df['Close'].ewm(span=50).mean()

    # Volume
    df['AVG_VOL'] = df['Volume'].rolling(window=20).mean()

    # Current values
    curr = df.iloc[-1]

    curr_price = curr['Close']
    curr_e20 = curr['E20']
    curr_e50 = curr['E50']
    curr_vol = curr['Volume']
    curr_avg_vol = curr['AVG_VOL']

    if pd.isna(curr_avg_vol):
        return None

    # =============================
    # TREND
    # =============================
    cp_strength = "🔵 CALL STRONG" if curr_e20 > curr_e50 else "🔴 PUT STRONG"

    # =============================
    # BIG PLAYER
    # =============================
    if curr_vol > curr_avg_vol * 2:
        big_player = "🔥 EXTREME INSTITUTIONAL"
    elif curr_vol > curr_avg_vol * 1.5:
        big_player = "🐋 BIG PLAYER ACTIVE"
    else:
        big_player = "💤 NORMAL"

    # =============================
    # SIGNAL
    # =============================
    observation = "WAIT"
    entry, sl, target = 0, 0, 0

    recent_high = df['High'].iloc[-10:].max()
    recent_low = df['Low'].iloc[-10:].min()

    risk = (recent_high - recent_low)
    if risk <= 0:
        risk = curr_price * 0.01

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

    return (
        cp_strength,
        observation,
        big_player,
        round(entry, 2),
        round(sl, 2),
        round(target, 2)
    )

# =============================
# 3. NSE SECTORS
# =============================
all_sectors = {
    "Nifty 50": ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK"],
    "Banking": ["SBIN", "AXISBANK", "KOTAKBANK", "HDFCBANK"],
    "Auto": ["TATAMOTORS", "MARUTI", "M&M"],
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
                df = yf.download(
                    s + ".NS",
                    period="5d",      # 🔥 FIXED
                    interval="15m",
                    progress=False
                )

                if df.empty:
                    st.warning(f"No data: {s}")
                    continue

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
                        "Time": df.index[-1].strftime('%H:%M')
                    })

            except Exception as e:
                st.error(f"{s} Error: {e}")   # 🔥 DEBUG ENABLED

    if results:
        df_res = pd.DataFrame(results)

        # 🔥 FILTER (only signals)
        df_res = df_res[df_res["Signal"] != "WAIT"]

        st.dataframe(df_res, use_container_width=True)

    else:
        st.error("❌ No Signals Found")

# =============================
# 6. BACKTEST
# =============================
st.markdown("---")
st.subheader(f"📅 Backtest Report - {bt_date}")

if st.sidebar.button("📊 RUN BACKTEST"):

    bt_results = []
    target_list = [bt_stock_input] if bt_stock_input else stocks

    with st.spinner("Running Backtest..."):

        for s in target_list:
            try:
                df_hist = yf.download(
                    s + ".NS",
                    start=bt_date,
                    end=bt_date + timedelta(days=1),
                    interval="15m",
                    progress=False
                )

                if df_hist.empty:
                    continue

                for i in range(50, len(df_hist)):
                    sub_df = df_hist.iloc[:i+1]
                    res = analyze_data(sub_df)

                    if res and res[1] != "WAIT":
                        bt_results.append({
                            "Time": sub_df.index[-1].strftime('%H:%M'),
                            "Stock": s,
                            "Signal": res[1],
                            "Entry": res[3],
                            "SL": res[4],
                            "Target": res[5]
                        })

            except Exception as e:
                st.error(f"{s} Backtest Error: {e}")

    if bt_results:
        st.dataframe(pd.DataFrame(bt_results), use_container_width=True)
    else:
        st.warning("No Signals Found")
