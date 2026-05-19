# =========================================================
# 🚀 NSE AI PRO MAX V2.2 - FIXED DATE/DATETIME KEYERROR
# OLD CODE DISTURB KAKUNDA NEW COLUMNS ADDED
# =========================================================

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from concurrent.futures import ThreadPoolExecutor

# =========================================================
# PAGE CONFIG & AUTO REFRESH
# =========================================================

st.set_page_config(
    page_title="NSE AI PRO MAX V2.2",
    layout="wide"
)

st.fragment(run_every=60)

st.title("🚀 NSE AI PRO MAX V2.2")
st.caption("AI BASED NSE SCANNER + CALL SIDE OI ANALYSIS")

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

# =========================================================
# INDICATOR FUNCTION (OLD LOGIC PRESERVED)
# =========================================================

def calculate_indicators(df):
    if df.empty: return df
    
    # Safety Check for MultiIndex Columns
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    df = df.reset_index()
    df['EMA20'] = df['Close'].ewm(span=20).mean()
    df['EMA50'] = df['Close'].ewm(span=50).mean()
    df['VWAP'] = ((df['Close'] * df['Volume']).cumsum()) / df['Volume'].cumsum()
    
    delta = df['Close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    df['RSI'] = 100 - (100 / (1 + (gain.rolling(14).mean() / loss.rolling(14).mean())))
    df['RSI'] = df['RSI'].fillna(50)
    
    df['H-L'] = df['High'] - df['Low']
    df['H-PC'] = abs(df['High'] - df['Close'].shift(1))
    df['L-PC'] = abs(df['Low'] - df['Close'].shift(1))
    df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1)
    df['ATR'] = df['TR'].rolling(14).mean()
    
    df['MACD'] = df['Close'].ewm(span=12).mean() - df['Close'].ewm(span=26).mean()
    df['MACD_SIGNAL'] = df['MACD'].ewm(span=9).mean()
    df['VOL_AVG'] = df['Volume'].rolling(20).mean()
    df['VOL_BREAKOUT'] = df['Volume'] > df['VOL_AVG'] * 1.5
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
# SINGLE STOCK & OPTION DATA DISPLAY
# =========================================================

try:
    # 1. Fetch Technical Data
    df = yf.download(ticker, interval=interval, period=period, progress=False, auto_adjust=True)
    if df.empty:
        st.error("NO DATA FOUND")
        st.stop()

    # Fix MultiIndex immediately after download
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = calculate_indicators(df)
    signal, score = generate_signal(df)
    latest = df.iloc[-1]
    
    # Extract as clean scalar float value
    current_price = float(latest['Close'].iloc[0]) if isinstance(latest['Close'], pd.Series) else float(latest['Close'])

    # Display Technical Signal & Metrics
    st.subheader("🤖 AI SIGNAL")
    if "BUY" in signal: st.success(f"{signal} (SCORE: {score})")
    elif "SELL" in signal: st.error(f"{signal} (SCORE: {score})")
    else: st.warning(f"{signal} (SCORE: {score})")

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("PRICE", f"₹ {round(current_price, 2)}")
    col2.metric("RSI", round(float(latest['RSI']), 2))
    col3.metric("VWAP", round(float(latest['VWAP']), 2))
    col4.metric("ATR", round(float(latest['ATR']), 2))
    col5.metric("AI SCORE", f"{score} PTS")

    # =====================================================
    # 🌟 CALL SIDE OPTION CHAIN ANALYSIS
    # =====================================================
    st.subheader(f"🔥 {selected_stock} CALL SIDE OPTION CHAIN (OI ANALYSIS)")
    
    with st.spinner("Fetching Option Chain Data..."):
        yf_ticker = yf.Ticker(ticker)
        try:
            expiries = yf_ticker.options
        except:
            expiries = []
        
        if expiries:
            nearest_expiry = expiries[0]
            st.caption(f"📅 Showing Nearest Expiry Data: **{nearest_expiry}**")
            
            opt_chain = yf_ticker.option_chain(nearest_expiry)
            calls_df = opt_chain.calls
            
            # Filter rows near current spot price (+/- 10% range)
            buffer = current_price * 0.10
            filtered_calls = calls_df[
                (calls_df['strike'] >= (current_price - buffer)) & 
                (calls_df['strike'] <= (current_price + buffer))
            ].copy()
            
            if not filtered_calls.empty:
                filtered_calls = filtered_calls.rename(columns={
                    'strike': 'STRIKE PRICE',
                    'openInterest': 'CALL OI (Total)',
                    'volume': 'CALL VOLUME',
                    'lastPrice': 'CALL LTP (Price)'
                })
                
                filtered_calls = filtered_calls.fillna(0)
                
                # Formatter
                filtered_calls['STRIKE PRICE'] = filtered_calls['STRIKE PRICE'].astype(float).round(2)
                filtered_calls['CALL LTP (Price)'] = filtered_calls['CALL LTP (Price)'].astype(float).round(2)
                filtered_calls['CALL OI (Total)'] = filtered_calls['CALL OI (Total)'].astype(int)
                filtered_calls['CALL VOLUME'] = filtered_calls['CALL VOLUME'].astype(int)
                
                # Find Highest OI Strike
                max_oi_idx = filtered_calls['CALL OI (Total)'].idxmax()
                highest_oi_strike = filtered_calls.loc[max_oi_idx, 'STRIKE PRICE']
                
                st.info(f"🎯 **Highest Call OI Concentration:** Strike **{highest_oi_strike}** (Acts as a strong Resistance line)")
                
                st.dataframe(
                    filtered_calls[['STRIKE PRICE', 'CALL LTP (Price)', 'CALL OI (Total)', 'CALL VOLUME']], 
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.warning("No call options data available in this price range.")
        else:
            st.warning("Option chain data not available for this stock on Yahoo Finance.")

    # =====================================================
    # CHART & DATA TABLES (FIXED DATE/DATETIME DYNAMICALLY)
    # =====================================================
    st.subheader(f"📈 {selected_stock} LIVE CHART")
    fig = go.Figure()
    
    # 🛠️ FIXED: Auto detect the time column regardless of what yfinance names it
    time_col = df.columns[0] 
    if 'index' in df.columns:
        time_col = 'index'
    elif 'Date' in df.columns:
        time_col = 'Date'
    elif 'Datetime' in df.columns:
        time_col = 'Datetime'
    
    fig.add_trace(go.Scatter(x=df[time_col], y=df['Close'], mode='lines', name='Close'))
    fig.add_trace(go.Scatter(x=df[time_col], y=df['EMA20'], mode='lines', name='EMA20'))
    fig.add_trace(go.Scatter(x=df[time_col], y=df['EMA50'], mode='lines', name='EMA50'))
    fig.update_layout(height=400, hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

    # LIVE AI SCANNER SECTION
    st.subheader("🔥 LIVE AI NIFTY 50 SCANNER")
    def scan_stock(item):
        s_name, s_ticker = item
        try:
            data = yf.download(s_ticker, interval=interval, period=period, progress=False, auto_adjust=True)
            if data.empty: return None
            
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)
                
            data = calculate_indicators(data)
            sig, scr = generate_signal(data)
            lat = data.iloc[-1]
            
            c_p = float(lat['Close'].iloc[0]) if isinstance(lat['Close'], pd.Series) else float(lat['Close'])
            r_s = float(lat['RSI'].iloc[0]) if isinstance(lat['RSI'], pd.Series) else float(lat['RSI'])
            
            return {"STOCK": s_name, "PRICE": round(c_p, 2), "RSI": round(r_s, 2), "SIGNAL": sig, "SCORE": scr}
        except: return None

    results = []
    with ThreadPoolExecutor(max_workers=15) as executor:
        scanned = executor.map(scan_stock, nse_stocks.items())
    for item in scanned:
        if item is not None: results.append(item)
    
    scanner_df = pd.DataFrame(results).sort_values(by="SCORE", ascending=False)
    st.dataframe(scanner_df, use_container_width=True, hide_index=True)

except Exception as e:
    st.error("APP ERROR")
    st.code(str(e))
