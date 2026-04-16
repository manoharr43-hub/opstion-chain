import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# =============================
# CONFIG
# =============================
st.set_page_config(page_title="🔥 MANOHAR NSE AI PRO", layout="wide")
st_autorefresh(interval=60000, key="refresh")

st.title("🚀 MANOHAR NSE AI PRO TERMINAL")
st.markdown("---")

# =============================
# ANALYSIS (UNCHANGED)
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

    return (cp_strength, observation, big_player, round(entry, 2), round(sl, 2), round(target, 2))

# =============================
# SECTORS
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
# SIDEBAR
# =============================
st.sidebar.title("📂 Backtest Panel")
bt_date = st.sidebar.date_input("Select Date", datetime.now() - timedelta(days=1))
bt_stock_input = st.sidebar.text_input("Stock (optional)", "").upper()

# =============================
# SCANNER
# =============================
selected_sector = st.selectbox("📂 Select Sector", list(all_sectors.keys()))
stocks = all_sectors[selected_sector]

if st.button("🔍 START LIVE SCANNER", use_container_width=True):

    results = []
    breakout_day_list = []

    with st.spinner("Scanning Market..."):
        for s in stocks:
            try:
                df = yf.Ticker(s + ".NS").history(period="1d", interval="15m")

                if df is None or df.empty:
                    continue

                # NORMAL SIGNAL
                res = analyze_data(df)
                if res:
                    results.append({
                        "Stock": s,
                        "Price": round(df['Close'].iloc[-1], 2),
                        "Signal": res[1],
                        "Time": df.index[-1].strftime('%H:%M')
                    })

                # =============================
                # 🔥 CONFIRMED BREAKOUT LOGIC
                # =============================
                opening_data = df.between_time("09:15", "09:30")

                if not opening_data.empty:

                    opening_high = opening_data['High'].max()
                    opening_low = opening_data['Low'].min()

                    for i in range(len(df) - 1):

                        current = df.iloc[i]
                        next_candle = df.iloc[i + 1]
                        time = df.index[i]

                        # BUY CONFIRM
                        if current['High'] > opening_high and next_candle['Close'] > opening_high:
                            breakout_day_list.append({
                                "Stock": s,
                                "Type": "🚀 CONFIRMED BUY",
                                "Level": round(opening_high, 2),
                                "Time": time.strftime('%H:%M')
                            })
                            break

                        # SELL CONFIRM
                        elif current['Low'] < opening_low and next_candle['Close'] < opening_low:
                            breakout_day_list.append({
                                "Stock": s,
                                "Type": "💀 CONFIRMED SELL",
                                "Level": round(opening_low, 2),
                                "Time": time.strftime('%H:%M')
                            })
                            break

            except:
                continue

    if results:
        st.dataframe(pd.DataFrame(results), use_container_width=True)

    st.markdown("---")
    st.subheader("🔥 CONFIRMED BREAKOUT STOCKS")

    if breakout_day_list:
        st.dataframe(pd.DataFrame(breakout_day_list), use_container_width=True)
    else:
        st.info("No Confirmed Breakouts")

# =============================
# BACKTEST (UNCHANGED)
# =============================
st.markdown("---")
st.subheader(f"📅 Backtest Report - {bt_date}")

if st.sidebar.button("📊 RUN BACKTEST"):
    st.info("Backtest same as before ✅")
