import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# =============================
# 1. CONFIG & UI
# =============================
st.set_page_config(page_title="🔥 MANOHAR AI TERMINAL", layout="wide")
st_autorefresh(interval=60000, key="refresh")

st.title("🚀 MANOHAR NSE AI PRO TERMINAL")

# --- SIDEBAR: SEARCH & HISTORY ---
st.sidebar.title("🔍 Backtest & Search")
search_date = st.sidebar.date_input("Select Date for History", datetime.now())
search_stock = st.sidebar.text_input("Search Specific Stock (Ex: TCS)", "").upper()

# =============================
# 2. ANALYSIS ENGINE
# =============================
def get_detailed_analysis(symbol, target_date=None):
    try:
        t = yf.Ticker(symbol + ".NS" if not symbol.endswith(".NS") else symbol)
        
        # డేట్ సెలెక్ట్ చేస్తే బ్యాక్‌టెస్ట్ డేటా వస్తుంది
        if target_date and target_date < datetime.now().date():
            end_dt = datetime.combine(target_date, datetime.max.time())
            start_dt = end_dt - timedelta(days=5)
            df = t.history(start=start_dt, end=end_dt, interval="15m")
        else:
            df = t.history(period="5d", interval="15m")

        if df.empty: return None

        # Call/Put Strength Logic (Simulated based on Volume/Price for Backtest)
        avg_vol = df['Volume'].mean()
        curr_vol = df['Volume'].iloc[-1]
        
        # EMA Trend
        e20 = df['Close'].ewm(span=20).mean().iloc[-1]
        e50 = df['Close'].ewm(span=50).mean().iloc[-1]
        
        trend_status = "🔵 CALL STRONG" if e20 > e50 else "🔴 PUT STRONG"
        observation = "🚀 STRONG BUY" if (e20 > e50 and curr_vol > avg_vol) else "💀 STRONG SELL" if (e20 < e50 and curr_vol > avg_vol) else "WAIT"

        cp = df['Close'].iloc[-1]
        return {
            "Time": df.index[-1].strftime('%H:%M'),
            "Stock": symbol.replace(".NS", ""),
            "Price": round(cp, 2),
            "Call/Put Strength": trend_status,
            "Observation": observation,
            "Entry": round(cp * 1.002, 2),
            "SL": round(cp * 0.995, 2),
            "Target": round(cp * 1.01, 2)
        }
    except: return None

# =============================
# 3. MAIN DASHBOARD LAYOUT
# =============================
col_left, col_right = st.columns([2, 1])

sectors = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "SBIN", "ICICIBANK", "AXISBANK", "TATAMOTORS", "MARUTI", "ITC"]

with col_left:
    st.subheader("📊 Live Market Scanner")
    results = []
    for s in sectors:
        res = get_detailed_analysis(s)
        if res: results.append(res)
    
    if results:
        df_res = pd.DataFrame(results)
        # మీరు అడిగినట్లు మెయిన్ కాలమ్ Call/Put Strength
        st.dataframe(df_res[["Stock", "Call/Put Strength", "Price", "Observation", "Entry", "SL", "Target"]], use_container_width=True)
    
    # --- BOTTOM LISTS ---
    st.markdown("---")
    l_col, r_col = st.columns(2)
    with l_col:
        st.success("✅ **STRONG BUY LIST**")
        s_buy = [r['Stock'] for r in results if r['Observation'] == "🚀 STRONG BUY"]
        for b in s_buy: st.write(f"🚀 {b}")
    with r_col:
        st.error("❌ **STRONG SELL LIST**")
        s_sell = [r['Stock'] for r in results if r['Observation'] == "💀 STRONG SELL"]
        for s in s_sell: st.write(f"💀 {s}")

with col_right:
    st.subheader("📈 Time-wise Chart")
    selected_chart = st.selectbox("Select Stock for Chart", sectors)
    t_chart = yf.Ticker(selected_chart + ".NS")
    df_chart = t_chart.history(period="1d", interval="5m")
    
    if not df_chart.empty:
        fig = go.Figure(data=[go.Candlestick(x=df_chart.index,
                open=df_chart['Open'], high=df_chart['High'],
                low=df_chart['Low'], close=df_chart['Close'])])
        fig.update_layout(height=400, margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig, use_container_width=True)

# =============================
# 4. PREVIOUS DATES / FOLDER SEARCH
# =============================
if search_stock or (search_date < datetime.now().date()):
    st.markdown("---")
    st.subheader(f"📅 History Results for {search_date}")
    history_res = []
    target_stocks = [search_stock] if search_stock else sectors
    
    for s in target_stocks:
        h_res = get_detailed_analysis(s, target_date=search_date)
        if h_res: history_res.append(h_res)
    
    if history_res:
        st.table(pd.DataFrame(history_res))
    else:
        st.write("No historical data found for this selection.")
