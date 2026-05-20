# =========================================================
# 🚀 NSE AI PRO MAX V2.7 - BUG FIXED & FULLY OPTIMIZED
# =========================================================

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import io 
import datetime
import pytz  
from concurrent.futures import ThreadPoolExecutor

# =========================================================
# PAGE CONFIG & AUTO REFRESH
# =========================================================

st.set_page_config(page_title="NSE AI PRO MAX V2.7", layout="wide")
st.fragment(run_every=60)

st.title("🚀 NSE AI PRO MAX V2.7")
st.caption("AI BASED NSE SCANNER + OPTIONS MOMENTUM + CUSTOM CSV SETUP")

# =========================================================
# FULL NIFTY 50 STOCK LIST
# =========================================================

nse_stocks = {
    "ADANIENT": "ADANIENT.NS", "ADANIPORTS": "ADANIPORTS.NS", "APOLLOHOSP": "APOLLOHOSP.NS",
    "ASIANPAINT": "ASIANPAINT.NS", "AXISBANK": "AXISBANK.NS", "BAJAJ-AUTO": "BAJAJ-AUTO.NS",
    "BAJAJFINSV": "BAJAJFINSV.NS", "BAJFINANCE": "BAJFINANCE.NS", "BEL": "BEL.NS",
    "BHARTIARTL": "BHARTIARTL.NS", "BPCL": "BPCL.NS", "BRITANNIA": "BRITANNIA.NS",
    "CIPLA": "CIPLA.NS", "COALINDIA": "COALINDIA.NS", "DIVISLAB": "DIVISLAB.NS",
    "DRREDDY": "DRREDDY.NS", "EICHERMOT": "EICHERMOT.NS", "GRASIM": "GRASIM.NS",
    "HCLTECH": "HCLTECH.NS", "HDFCBANK": "HDFCBANK.NS", "HDFCLIFE": "HDFCLIFE.NS",
    "HEROMOTOCO": "HEROMOTOCO.NS", "HINDALCO": "HINDALCO.NS", "HINDUNILVR": "HINDUNILVR.NS",
    "ICICIBANK": "ICICIBANK.NS", "INDUSINDBK": "INDUSINDBK.NS", "INFY": "INFY.NS",
    "ITC": "ITC.NS", "JSWSTEEL": "JSWSTEEL.NS", "KOTAKBANK": "KOTAKBANK.NS",
    "LT": "LT.NS", "M&M": "M&M.NS", "MARUTI": "MARUTI.NS", "NESTLEIND": "NESTLEIND.NS",
    "NTPC": "NTPC.NS", "ONGC": "ONGC.NS", "POWERGRID": "POWERGRID.NS", "RELIANCE": "RELIANCE.NS",
    "SBILIFE": "SBILIFE.NS", "SBIN": "SBIN.NS", "SUNPHARMA": "SUNPHARMA.NS",
    "TATACONSUM": "TATACONSUM.NS", "TATAMOTORS": "TATAMOTORS.NS", "TATASTEEL": "TATASTEEL.NS",
    "TCS": "TCS.NS", "TECHM": "TECHM.NS", "TITAN": "TITAN.NS", "ULTRACEMCO": "ULTRACEMCO.NS",
    "WIPRO": "WIPRO.NS", "TRENT": "TRENT.NS"
}

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.header("⚙️ SETTINGS")
selected_stock = st.sidebar.selectbox("SELECT STOCK", list(nse_stocks.keys()))
interval = st.sidebar.selectbox("INTERVAL", ["5m", "15m", "30m", "1h"])
period = st.sidebar.selectbox("PERIOD", ["1d", "5d", "1mo"])
ticker = nse_stocks[selected_stock]

st.sidebar.markdown("---")
st.sidebar.subheader("🔗 QUICK LINKS")
screener_link = "INSERT_YOUR_LINK_HERE" # మీ లింక్ ఇక్కడ పెట్టండి

st.sidebar.markdown(f'''
<a href="{screener_link}" target="_blank" style="text-decoration: none;">
    <div style="background-color: #2E86C1; padding: 10px; border-radius: 5px; text-align: center; color: white; font-weight: bold; margin-bottom: 15px;">
        📊 Open NSE Screener Kit
    </div>
</a>
''', unsafe_allow_html=True)

# =========================================================
# HELPER FUNCTIONS
# =========================================================
def get_current_ist_time():
    return datetime.datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')

def get_current_ist_time_only():
    return datetime.datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%H:%M:%S')

def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    return output.getvalue()

def calculate_indicators(df):
    if df.empty: return df
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    df = df.reset_index()
    df['EMA20'] = df['Close'].ewm(span=20).mean()
    df['EMA50'] = df['Close'].ewm(span=50).mean()
    df['VWAP'] = ((df['Close'] * df['Volume']).cumsum()) / df['Volume'].cumsum()
    delta = df['Close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    df['RSI'] = 100 - (100 / (1 + (gain.rolling(14).mean() / loss.rolling(14).mean())))
    df['RSI'] = df['RSI'].fillna(50)
    df['MACD'] = df['Close'].ewm(span=12).mean() - df['Close'].ewm(span=26).mean()
    df['MACD_SIGNAL'] = df['MACD'].ewm(span=9).mean()
    return df

def generate_signal(df):
    latest = df.iloc[-1]
    score = 0
    if latest['EMA20'] > latest['EMA50']: score += 25
    else: score -= 25
    if latest['Close'] > latest['VWAP']: score += 25
    else: score -= 25
    if 55 < latest['RSI'] < 70: score += 25
    elif latest['RSI'] > 70: score -= 10
    elif latest['RSI'] < 30: score += 15
    else: score -= 10
    if latest['MACD'] > latest['MACD_SIGNAL']: score += 25
    else: score -= 25

    if score >= 75: signal = "🚀 STRONG BUY"
    elif score >= 25: signal = "✅ BUY"
    elif score <= -75: signal = "🚨 STRONG SELL"
    elif score <= -25: signal = "🔻 SELL"
    else: signal = "⚠️ SIDEWAYS"
    return signal, score

# =========================================================
# TABS SETUP
# =========================================================
tab1, tab2 = st.tabs(["📈 AI Scanner & Live Setup", "📂 Upload CSV & Extract AI Target"])

# =========================================================
# TAB 1: LIVE SCANNER
# =========================================================
with tab1:
    try: # <--- ఇక్కడ మొదలైన try బ్లాక్ చివరలో except తో ఎండ్ అవుతుంది (ఎర్రర్ రాకుండా)
        df = yf.download(ticker, interval=interval, period=period, progress=False, auto_adjust=True)
        if df.empty:
            st.error("NO DATA FOUND")
        else:
            df = calculate_indicators(df)
            signal, score = generate_signal(df)
            latest = df.iloc[-1]
            current_price = float(latest['Close'].iloc[0]) if isinstance(latest['Close'], pd.Series) else float(latest['Close'])

            # 1. AI SIGNAL
            st.subheader("🤖 AI SIGNAL")
            if "BUY" in signal: st.success(f"{signal} (SCORE: {score})")
            elif "SELL" in signal: st.error(f"{signal} (SCORE: {score})")
            else: st.warning(f"{signal} (SCORE: {score})")
            
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("PRICE", f"₹ {round(current_price, 2)}")
            col2.metric("RSI", round(float(latest['RSI']), 2))
            col3.metric("VWAP", round(float(latest['VWAP']), 2))
            col4.metric("MACD", round(float(latest['MACD']), 2))
            col5.metric("AI SCORE", f"{score} PTS")

            # 2. OPTION CHAIN
            st.subheader(f"🔥 {selected_stock} OPTION CHAIN & AI SETUP")
            with st.spinner("Fetching Option Chain Data..."):
                yf_ticker = yf.Ticker(ticker)
                try:
                    expiries = yf_ticker.options
                except:
                    expiries = []
                
                if expiries:
                    nearest_expiry = expiries[0]
                    st.caption(f"📅 Expiry: **{nearest_expiry}**")
                    opt_chain = yf_ticker.option_chain(nearest_expiry)
                    calls_df = opt_chain.calls
                    puts_df = opt_chain.puts
                    
                    buffer = current_price * 0.05 
                    filtered_calls = calls_df[(calls_df['strike'] >= (current_price - buffer)) & (calls_df['strike'] <= (current_price + buffer))].copy()
                    filtered_puts = puts_df[(puts_df['strike'] >= (current_price - buffer)) & (puts_df['strike'] <= (current_price + buffer))].copy()
                    
                    if not filtered_calls.empty:
                        # Call Data Display
                        st.dataframe(filtered_calls[['strike', 'lastPrice', 'openInterest', 'volume']], use_container_width=True, hide_index=True)
                        
                        st.markdown("---")
                        st.subheader("🤖 AI MOMENTUM TRADE SETUP (LIVE)")
                        col_call, col_put = st.columns(2)
                        
                        # Call Box
                        with col_call:
                            with st.container(border=True):
                                c_idx = filtered_calls['volume'].idxmax()
                                c_data = filtered_calls.loc[c_idx]
                                c_ltp = float(c_data['lastPrice'])
                                st.markdown(f"<h4 style='text-align: center; color: #4CAF50;'>🟢 CALL SIDE: {float(c_data['strike'])} CE</h4>", unsafe_allow_html=True)
                                st.info(f"Highest Volume: {int(c_data['volume'])}")
                                ct1, ct2 = st.columns(2)
                                ct1.metric("ENTRY", f"₹ {round(c_ltp, 2)}")
                                ct2.metric("STOPLOSS", f"₹ {round(c_ltp * 0.85, 2)}")
                                ct3, ct4 = st.columns(2)
                                ct3.metric("TARGET 1", f"₹ {round(c_ltp * 1.15, 2)}")
                                ct4.metric("TARGET 2", f"₹ {round(c_ltp * 1.30, 2)}")

                        # Put Box
                        with col_put:
                            with st.container(border=True):
                                if not filtered_puts.empty:
                                    p_idx = filtered_puts['volume'].idxmax()
                                    p_data = filtered_puts.loc[p_idx]
                                    p_ltp = float(p_data['lastPrice'])
                                    st.markdown(f"<h4 style='text-align: center; color: #FF5252;'>🔴 PUT SIDE: {float(p_data['strike'])} PE</h4>", unsafe_allow_html=True)
                                    st.info(f"Highest Volume: {int(p_data['volume'])}")
                                    pt1, pt2 = st.columns(2)
                                    pt1.metric("ENTRY", f"₹ {round(p_ltp, 2)}")
                                    pt2.metric("STOPLOSS", f"₹ {round(p_ltp * 0.85, 2)}")
                                    pt3, pt4 = st.columns(2)
                                    pt3.metric("TARGET 1", f"₹ {round(p_ltp * 1.15, 2)}")
                                    pt4.metric("TARGET 2", f"₹ {round(p_ltp * 1.30, 2)}")
                                else:
                                    st.warning("No Put Data")
                    else:
                        st.warning("No Options Data found for this range.")
                else:
                    st.warning("Yahoo Finance options data not available.")

            # 3. LIVE CHART
            st.markdown("---")
            st.subheader(f"📈 {selected_stock} LIVE CHART")
            fig = go.Figure()
            time_col = df.columns[0] if 'index' not in df.columns and 'Date' not in df.columns else ('index' if 'index' in df.columns else 'Date')
            fig.add_trace(go.Scatter(x=df[time_col], y=df['Close'], mode='lines', name='Close'))
            fig.add_trace(go.Scatter(x=df[time_col], y=df['EMA20'], mode='lines', name='EMA20'))
            fig.update_layout(height=400, hovermode="x unified")
            st.plotly_chart(fig, use_container_width=True)

            # 4. SCANNER
            st.subheader("🔥 LIVE AI NIFTY 50 SCANNER")
            def scan_stock(item):
                s_name, s_ticker = item
                try:
                    data = yf.download(s_ticker, interval=interval, period=period, progress=False, auto_adjust=True)
                    if data.empty: return None
                    data = calculate_indicators(data)
                    sig, scr = generate_signal(data)
                    return {"STOCK": s_name, "PRICE": round(float(data.iloc[-1]['Close']), 2), "SIGNAL": sig, "SCORE": scr}
                except: return None

            results = []
            with ThreadPoolExecutor(max_workers=10) as executor:
                scanned = executor.map(scan_stock, nse_stocks.items())
            for item in scanned:
                if item is not None: results.append(item)
            
            st.dataframe(pd.DataFrame(results).sort_values(by="SCORE", ascending=False), use_container_width=True, hide_index=True)

    except Exception as e: # <--- కరెక్ట్ except బ్లాక్ ఇక్కడ ఉంది.
        st.error(f"App Error: {str(e)}")

# =========================================================
# TAB 2: UPLOADED CSV TO CALL/PUT AI BOXES
# =========================================================
with tab2:
    try: # <--- Tab 2 లో కూడా try బ్లాక్ మొదలు
        st.header("📂 Screener Kit Data Processing")
        st.write("మీరు డౌన్‌లోడ్ చేసిన Screener Excel/CSV ఫైల్ ని ఇక్కడ అప్లో
