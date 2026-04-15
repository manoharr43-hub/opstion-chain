import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# =============================
# 1. CONFIG
# =============================
st.set_page_config(page_title="🔥 MANOHAR AI TERMINAL PRO", layout="wide")
st_autorefresh(interval=60000, key="refresh") 

st.title("🚀 MANOHAR NSE AI PRO TERMINAL")
st.markdown("---")

# =============================
# 2. ANALYSIS LOGIC
# =============================
def analyze_data(df):
    if df is None or len(df) < 20: return None
    
    e20 = df['Close'].ewm(span=20).mean()
    e50 = df['Close'].ewm(span=50).mean()
    vol = df['Volume']
    avg_vol = vol.rolling(window=20).mean()
    
    curr_e20 = e20.iloc[-1]
    curr_e50 = e50.iloc[-1]
    curr_vol = vol.iloc[-1]
    curr_avg_vol = avg_vol.iloc[-1]
    
    cp_strength = "🔵 CALL STRONG" if curr_e20 > curr_e50 else "🔴 PUT STRONG"
    big_player = "🔥 ACTIVE" if curr_vol > (curr_avg_vol * 1.5) else "💤 NORMAL"
    
    observation = "WAIT"
    if curr_e20 > curr_e50 and curr_vol > curr_avg_vol: observation = "🚀 STRONG BUY"
    elif curr_e20 < curr_e50 and curr_vol > curr_avg_vol: observation = "💀 STRONG SELL"
    
    return cp_strength, observation, big_player

# =============================
# 3. SECTORS
# =============================
all_sectors = {
    "Nifty 50": ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "SBIN", "ITC", "LT"],
    "Banking": ["SBIN", "AXISBANK", "KOTAKBANK", "HDFCBANK", "ICICIBANK", "PNB"],
    "Auto": ["TATAMOTORS", "MARUTI", "M&M", "HEROMOTOCO", "ASHOKLEY"]
}

# =============================
# 4. SIDEBAR - BACKTEST FOLDER
# =============================
st.sidebar.title("📂 Backtest Folder")
bt_date = st.sidebar.date_input("Select History Date", datetime.now() - timedelta(days=1))
bt_stock = st.sidebar.text_input("Search Stock (Optional)", "").upper()

# =============================
# 5. MAIN DASHBOARD (LIVE)
# =============================
selected_sector = st.selectbox("📂 Select Sector", list(all_sectors.keys()))
stocks = all_sectors[selected_sector]

if st.button("🔍 START LIVE SCANNER", use_container_width=True):
    results = []
    for s in stocks:
        t = yf.Ticker(s + ".NS")
        df = t.history(period="2d", interval="15m")
        res = analyze_data(df)
        if res:
            cp = df['Close'].iloc[-1]
            results.append({
                "Stock": s, "Call/Put Strength": res[0], "Price": round(cp, 2),
                "Observation": res[1], "Big Players": res[2], "Time": df.index[-1].strftime('%H:%M')
            })
    if results:
        st.dataframe(pd.DataFrame(results), use_container_width=True)

# =============================
# 6. FULL DAY BACKTEST REPORT (FIXED TIME ISSUE)
# =============================
st.markdown("---")
st.subheader(f"📅 Backtest Report for {bt_date} (Full Day Signals)")

if st.sidebar.button("📊 Run Full Day Backtest"):
    bt_results = []
    target_list = [bt_stock] if bt_stock else stocks
    
    with st.spinner("Searching through past data..."):
        for s in target_stocks:
            t = yf.Ticker(s + ".NS")
            # ఆ రోజు మొత్తం డేటా తీసుకుంటుంది
            start_bt = bt_date
            end_bt = bt_date + timedelta(days=1)
            df_hist = t.history(start=start_bt, end=end_bt, interval="15m")
            
            if not df_hist.empty:
                # ప్రతి 15 నిమిషాల క్యాండిల్ ని చెక్ చేస్తుంది
                for i in range(20, len(df_hist)):
                    sub_df = df_hist.iloc[:i+1]
                    res = analyze_data(sub_df)
                    if res and res[1] != "WAIT": # Strong Buy/Sell ఉంటేనే
                        bt_results.append({
                            "Time": sub_df.index[-1].strftime('%H:%M'),
                            "Stock": s,
                            "Signal": res[1],
                            "Price": round(sub_df['Close'].iloc[-1], 2),
                            "Volume Status": res[2]
                        })
    
    if bt_results:
        bt_df = pd.DataFrame(bt_results)
        # టైమ్ ప్రకారం సార్ట్ చేస్తుంది
        st.table(bt_df.sort_values(by="Time"))
    else:
        st.warning("ఆ రోజు ఎటువంటి 'Strong' సిగ్నల్స్ రాలేదు.")
