import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# =============================
# 1. CONFIG & REFRESH
# =============================
st.set_page_config(page_title="🔥 MANOHAR NSE AI TERMINAL", layout="wide")
st_autorefresh(interval=60000, key="refresh") 

st.title("🚀 MANOHAR NSE AI PRO TERMINAL")
st.markdown("---")

# =============================
# 2. CORE ANALYSIS ENGINE
# =============================
def get_detailed_analysis(symbol, target_date=None):
    try:
        # Stock symbol check
        ticker_sym = symbol + ".NS" if not symbol.endswith(".NS") else symbol
        t = yf.Ticker(ticker_sym)
        
        # History logic for Backtest
        if target_date and target_date < datetime.now().date():
            end_dt = datetime.combine(target_date, datetime.max.time())
            start_dt = end_dt - timedelta(days=5)
            df = t.history(start=start_dt, end=end_dt, interval="15m")
        else:
            df = t.history(period="5d", interval="15m")

        if df.empty or len(df) < 20: return None

        # EMA Trend Logic
        e20 = df['Close'].ewm(span=20).mean().iloc[-1]
        e50 = df['Close'].ewm(span=50).mean().iloc[-1]
        
        # Call/Put Strength
        avg_vol = df['Volume'].mean()
        curr_vol = df['Volume'].iloc[-1]
        cp_strength = "🔵 CALL STRONG" if e20 > e50 else "🔴 PUT STRONG"
        
        # Big Players & Observation
        big_player = "🔥 ACTIVE" if curr_vol > (avg_vol * 1.5) else "💤 NORMAL"
        observation = "WAIT"
        if e20 > e50 and curr_vol > avg_vol: observation = "🚀 STRONG BUY"
        elif e20 < e50 and curr_vol > avg_vol: observation = "💀 STRONG SELL"

        cp = df['Close'].iloc[-1]
        high, low = df['High'].iloc[-5:].max(), df['Low'].iloc[-5:].min()
        range_val = max(high - low, cp * 0.01)

        # Entry, SL, Target
        if e20 > e50:
            entry, sl, target = high + (range_val * 0.1), low - (range_val * 0.2), cp * 1.015
        else:
            entry, sl, target = low - (range_val * 0.1), high + (range_val * 0.2), cp * 0.985

        return {
            "Time": df.index[-1].strftime('%H:%M'),
            "Stock": symbol.replace(".NS", ""),
            "Call/Put Strength": cp_strength,
            "Price": round(cp, 2),
            "Observation": observation,
            "Big Players": big_player,
            "Entry": round(entry, 2),
            "StopLoss": round(sl, 2),
            "Target": round(target, 2)
        }
    except: return None

# =============================
# 3. SECTOR DEFINITIONS (Added Back)
# =============================
all_sectors = {
    "Nifty 50": ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "SBIN", "ITC", "LT", "AXISBANK", "BHARTIARTL"],
    "Banking": ["SBIN", "AXISBANK", "KOTAKBANK", "HDFCBANK", "ICICIBANK", "BAJFINANCE", "PNB", "CANBK"],
    "IT Sector": ["TCS", "INFY", "WIPRO", "HCLTECH", "TECHM", "LTIM", "COFORGE"],
    "Auto": ["TATAMOTORS", "MARUTI", "M&M", "HEROMOTOCO", "EICHERMOT", "ASHOKLEY", "TVSMOTOR"],
    "Pharma": ["SUNPHARMA", "DRREDDY", "CIPLA", "APOLLOHOSP", "DIVISLAB"],
    "Energy": ["NTPC", "POWERGRID", "ONGC", "BPCL", "TATAPOWER", "ADANIGREEN"]
}

# =============================
# 4. SIDEBAR & SEARCH
# =============================
st.sidebar.title("📂 History & Search")
search_date = st.sidebar.date_input("Select Date for History", datetime.now())
search_stock = st.sidebar.text_input("Search Specific Stock (Ex: TCS)", "").upper()

# =============================
# 5. MAIN DASHBOARD UI
# =============================
# Sector selection dropdown
selected_sector_name = st.selectbox("📂 Select Sector to Scan", list(all_sectors.keys()))
stocks_to_scan = all_sectors[selected_sector_name]

if st.button("🔍 START SCANNER", use_container_width=True):
    with st.spinner(f"AI Analyzing {selected_sector_name}..."):
        results = [res for s in stocks_to_scan if (res := get_detailed_analysis(s))]
        
        if results:
            df_res = pd.DataFrame(results)
            # మెయిన్ కాలమ్ Call/Put Strength
            st.dataframe(df_res[["Stock", "Call/Put Strength", "Price", "Observation", "Big Players", "Entry", "StopLoss", "Target", "Time"]], use_container_width=True)

            # --- BOTTOM SUMMARY LISTS ---
            st.markdown("---")
            st.subheader("🏁 Live Signal Summary")
            col1, col2, col3 = st.columns(3)

            with col1:
                st.success("🚀 **STRONG BUY LIST**")
                for r in results:
                    if r['Observation'] == "🚀 STRONG BUY": st.write(f"✅ {r['Stock']} @ {r['Time']}")

            with col2:
                st.error("💀 **STRONG SELL LIST**")
                for r in results:
                    if r['Observation'] == "💀 STRONG SELL": st.write(f"❌ {r['Stock']} @ {r['Time']}")

            with col3:
                st.warning("🔥 **BIG PLAYERS ACTIVE**")
                for r in results:
                    if r['Big Players'] == "🔥 ACTIVE": st.write(f"⚡ {r['Stock']}")
        else:
            st.error("No data found for this sector. Please try again.")

# --- HISTORY SECTION ---
if search_stock or (search_date < datetime.now().date()):
    st.markdown("---")
    st.subheader(f"📅 Backtest Results: {search_date}")
    h_list = [search_stock] if search_stock else stocks_to_scan
    h_results = [res for s in h_list if (res := get_detailed_analysis(s, target_date=search_date))]
    if h_results:
        st.table(pd.DataFrame(h_results))
