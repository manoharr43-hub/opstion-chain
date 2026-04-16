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
# 2. ANALYSIS LOGIC (UNCHANGED)
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

    if pd.isna(curr_avg_vol) or curr_avg_vol == 0:
        return None

    cp_strength = "🔵 CALL STRONG" if curr_e20 > curr_e50 else "🔴 PUT STRONG"

    if curr_vol > curr_avg_vol * 2:
        big_player = "🔥 EXTREME INSTITUTIONAL"
    elif curr_vol > curr_avg_vol * 1.5:
        big_player = "🐋 BIG PLAYER ACTIVE"
    else:
        big_player = "💤 NORMAL"

    observation = "WAIT"
    entry, sl, target = 0, 0, 0

    recent_high = df['High'].iloc[-10:].max()
    recent_low = df['Low'].iloc[-10:].min()
    risk = (recent_high - recent_low) if (recent_high - recent_low) > 0 else curr_price * 0.01

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
    "Nifty 50": ["RELIANCE","TCS","INFY","HDFCBANK","ICICIBANK","SBIN","ITC","LT","AXISBANK","BHARTIARTL"],
    "Banking": ["SBIN","AXISBANK","KOTAKBANK","HDFCBANK","ICICIBANK","PNB","CANBK","FEDERALBNK"],
    "Auto": ["TATAMOTORS","MARUTI","M&M","HEROMOTOCO","EICHERMOT","ASHOKLEY","TVSMOTOR"],
    "Metal": ["TATASTEEL","JINDALSTEL","HINDALCO","JSWSTEEL","NATIONALUM","SAIL","VEDL"],
    "IT Sector": ["TCS","INFY","WIPRO","HCLTECH","TECHM","LTIM","COFORGE"],
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
    breakout_day_list = []  # 🔥 NEW

    with st.spinner("AI Scanning Market..."):
        for s in stocks:
            try:
                t = yf.Ticker(s + ".NS")
                df = t.history(period="1d", interval="15m")

                if df is None or df.empty:
                    continue

                # ===== EXISTING LOGIC =====
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

                # ===== 🔥 FULL DAY BREAKOUT LOGIC =====
                opening_data = df.between_time("09:15", "09:30")

                if not opening_data.empty:
                    opening_high = opening_data['High'].max()
                    opening_low = opening_data['Low'].min()

                    for _, row in df.iterrows():
                        if row['High'] > opening_high:
                            breakout_day_list.append({
                                "Stock": s,
                                "Type": "🚀 BREAKOUT BUY",
                                "Level": round(opening_high, 2)
                            })
                            break

                        elif row['Low'] < opening_low:
                            breakout_day_list.append({
                                "Stock": s,
                                "Type": "💀 BREAKDOWN SELL",
                                "Level": round(opening_low, 2)
                            })
                            break

            except:
                continue

    # ===== MAIN RESULT =====
    if results:
        st.dataframe(pd.DataFrame(results), use_container_width=True)
    else:
        st.error("No Data Found")

    # ===== 🔥 BREAKOUT DISPLAY =====
    st.markdown("---")
    st.subheader("🔥 TODAY FULL DAY BREAKOUT STOCKS")

    if breakout_day_list:
        st.dataframe(pd.DataFrame(breakout_day_list), use_container_width=True)
    else:
        st.info("No Breakout Stocks Today")

# =============================
# 6. BACKTEST (UNCHANGED)
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

                df_hist = df_hist.between_time("09:15", "15:30")

                if not df_hist.empty:
                    for i in range(20, len(df_hist)):
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
                                "Target": res[5]
                            })

            except:
                continue

    if bt_results:
        st.dataframe(pd.DataFrame(bt_results), use_container_width=True)
    else:
        st.warning("No Signals Found")
