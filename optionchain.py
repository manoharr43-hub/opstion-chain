import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import datetime as dt
import io

# ==========================================
# 1. PAGE SETUP & CONFIGURATION
# ==========================================
st.set_page_config(page_title="HYBRID NSE PRO SCANNER V10", layout="wide", page_icon="🚀")

st.title("🚀 HYBRID NSE PRO SCANNER - V10.0 (Master Edition)")
st.markdown("**Cloud Stable | Supertrend + VWAP | AI Target & SL | 52W H/L | Support & Resistance**")

# ==========================================
# 2. CORE FUNCTIONS
# ==========================================
@st.cache_data(ttl=3600)
def get_nifty_stocks():
    return [
        "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS", "ITC.NS",
        "SBIN.NS", "BHARTIARTL.NS", "BAJFINANCE.NS", "L&T.NS", "HUL.NS", "AXISBANK.NS",
        "KOTAKBANK.NS", "ONGC.NS", "TATAMOTORS.NS", "NTPC.NS", "TATASTEEL.NS", "MARUTI.NS",
        "M&M.NS", "SUNPHARMA.NS", "HCLTECH.NS", "WIPRO.NS", "ASIANPAINT.NS", "ULTRACEMCO.NS",
        "TITAN.NS", "BAJAJFINSV.NS", "NESTLEIND.NS", "POWERGRID.NS", "TECHM.NS", "JSWSTEEL.NS",
        "GRASIM.NS", "HINDALCO.NS", "ADANIPORTS.NS", "ADANIENT.NS", "DIVISLAB.NS", "DRREDDY.NS",
        "INDUSINDBK.NS", "BRITANNIA.NS", "CIPLA.NS", "EICHERMOT.NS", "APOLLOHOSP.NS", "TATACONSUM.NS",
        "COALINDIA.NS", "BAJAJ-AUTO.NS", "HEROMOTOCO.NS", "BPCL.NS", "UPL.NS", "SBILIFE.NS", "HDFCLIFE.NS"
    ]

def calculate_supertrend(df, period=10, multiplier=3):
    """Supertrend Calculation"""
    hl2 = (df['High'] + df['Low']) / 2
    df['Basic_UB'] = hl2 + (multiplier * df['ATR'])
    df['Basic_LB'] = hl2 - (multiplier * df['ATR'])
    df['Final_UB'] = df['Basic_UB']
    df['Final_LB'] = df['Basic_LB']
    df['Supertrend'] = 0.0
    
    for i in range(period, len(df)):
        if df['Basic_UB'].iloc[i] < df['Final_UB'].iloc[i-1] or df['Close'].iloc[i-1] > df['Final_UB'].iloc[i-1]:
            df['Final_UB'].iloc[i] = df['Basic_UB'].iloc[i]
        else:
            df['Final_UB'].iloc[i] = df['Final_UB'].iloc[i-1]
            
        if df['Basic_LB'].iloc[i] > df['Final_LB'].iloc[i-1] or df['Close'].iloc[i-1] < df['Final_LB'].iloc[i-1]:
            df['Final_LB'].iloc[i] = df['Basic_LB'].iloc[i]
        else:
            df['Final_LB'].iloc[i] = df['Final_LB'].iloc[i-1]
            
        if df['Close'].iloc[i] <= df['Final_UB'].iloc[i]:
            df['Supertrend'].iloc[i] = df['Final_UB'].iloc[i]
        else:
            df['Supertrend'].iloc[i] = df['Final_LB'].iloc[i]
            
    return df

def calculate_technical_indicators(df):
    if df.empty or len(df) < 50:
        return None
        
    # ATR
    df['High-Low'] = df['High'] - df['Low']
    df['High-PrevClose'] = abs(df['High'] - df['Close'].shift(1))
    df['Low-PrevClose'] = abs(df['Low'] - df['Close'].shift(1))
    df['TR'] = df[['High-Low', 'High-PrevClose', 'Low-PrevClose']].max(axis=1)
    df['ATR'] = df['TR'].rolling(window=14).mean()
    
    # EMAs (MTF Trend Approximation)
    df['EMA_9'] = df['Close'].ewm(span=9, adjust=False).mean()
    df['EMA_21'] = df['Close'].ewm(span=21, adjust=False).mean()
    df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()
    df['EMA_200'] = df['Close'].ewm(span=200, adjust=False).mean()
    
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # MACD
    df['MACD'] = df['Close'].ewm(span=12, adjust=False).mean() - df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    
    # VWAP (Intraday cumulative)
    df['Typical_Price'] = (df['High'] + df['Low'] + df['Close']) / 3
    df['VWAP'] = (df['Typical_Price'] * df['Volume']).cumsum() / df['Volume'].cumsum()
    
    # Supertrend
    df = calculate_supertrend(df)
    
    # Volume Spikes
    df['Vol_Avg'] = df['Volume'].rolling(window=20).mean()
    df['Vol_Spike'] = df['Volume'] > (df['Vol_Avg'] * 2)
    
    # Support & Resistance (Pivot Points)
    df['PP'] = (df['High'].shift(1) + df['Low'].shift(1) + df['Close'].shift(1)) / 3
    df['R1'] = (2 * df['PP']) - df['Low'].shift(1)
    df['S1'] = (2 * df['PP']) - df['High'].shift(1)
    
    # 52-Week High & Low Approximation (Using 252 periods on daily, proxy on 15m)
    df['Period_High'] = df['High'].rolling(252).max()
    df['Period_Low'] = df['Low'].rolling(252).min()
    
    return df

def evaluate_strategy(df, ticker):
    if df is None:
        return None
        
    last_row = df.iloc[-1]
    
    # V10 Comprehensive Scoring System (Max Score: 8)
    score = 0
    if last_row['Close'] > last_row['VWAP']: score += 1
    if last_row['Close'] > last_row['Supertrend']: score += 1
    if last_row['RSI'] > 60: score += 1 # RSI Breakout
    if last_row['MACD'] > last_row['MACD_Signal']: score += 1
    if last_row['EMA_9'] > last_row['EMA_21']: score += 1
    if last_row['Close'] > last_row['EMA_50']: score += 1 # Trend
    if last_row['Vol_Spike']: score += 1
    if last_row['Close'] > last_row['PP']: score += 1
    
    # AI Signal
    signal = "STRONG BUY" if score >= 6 else "STRONG SELL" if score <= 2 else "NEUTRAL"
        
    # AI Target & SL
    target, stoploss = "-", "-"
    atr_val = last_row['ATR']
    if pd.notna(atr_val) and atr_val > 0:
        if signal == "STRONG BUY":
            stoploss = round(last_row['Close'] - (1.5 * atr_val), 2)
            target = round(last_row['Close'] + (3.0 * atr_val), 2)
        elif signal == "STRONG SELL":
            stoploss = round(last_row['Close'] + (1.5 * atr_val), 2)
            target = round(last_row['Close'] - (3.0 * atr_val), 2)

    return {
        'Stock': ticker.replace('.NS', ''),
        'LTP': round(last_row['Close'], 2),
        'Score': score,
        'Signal': signal,
        'Target': target,
        'Stoploss': stoploss,
        'RSI': round(last_row['RSI'], 2),
        'VWAP': round(last_row['VWAP'], 2),
        'Sup_Trend': round(last_row['Supertrend'], 2),
        'Support(S1)': round(last_row['S1'], 2),
        'Resist(R1)': round(last_row['R1'], 2),
        'High_Val': round(last_row['Period_High'], 2),
        'Vol_Spike': "Yes 🚀" if last_row['Vol_Spike'] else "No"
    }

# ==========================================
# 3. SIDEBAR & RUN ENGINE
# ==========================================
st.sidebar.header("⚙️ Scanner Settings")
trading_style = st.sidebar.radio("Trading Style:", ["Intraday (15m)", "Swing (1d)"])
interval = "15m" if trading_style == "Intraday (15m)" else "1d"
period = "6mo" if interval == "1d" else "1mo" 

if st.sidebar.button("🚀 Run AI Scanner", type="primary"):
    with st.spinner("Scanning NSE Stocks with V10 Institutional Engine..."):
        tickers = get_nifty_stocks()
        results = []
        progress_bar = st.progress(0)
        
        for i, ticker in enumerate(tickers):
            try:
                df = yf.download(ticker, period=period, interval=interval, progress=False)
                if not df.empty and len(df) > 50:
                    if isinstance(df.columns, pd.MultiIndex):
                        df.columns = df.columns.get_level_values(0)
                    df_ta = calculate_technical_indicators(df)
                    scan_result = evaluate_strategy(df_ta, ticker)
                    if scan_result:
                        results.append(scan_result)
            except Exception:
                pass 
            progress_bar.progress((i + 1) / len(tickers))
            
        progress_bar.empty()
        
        if results:
            st.session_state['scan_results'] = pd.DataFrame(results)
            # ACTION ALERT TOAST
            buy_count = sum(1 for r in results if r['Signal'] == 'STRONG BUY')
            if buy_count > 0:
                st.toast(f"🔥 Action Alert: {buy_count} STRONG BUY Signals Generated!", icon='🚀')

# ==========================================
# 4. MAIN DASHBOARD
# ==========================================
if 'scan_results' in st.session_state and not st.session_state['scan_results'].empty:
    final_df = st.session_state['scan_results']
    
    st.markdown("### 🏆 V10 Top Ranked Institutional Dashboard")
    
    top_stocks = final_df[final_df['Signal'] == 'STRONG BUY'].sort_values(by='Score', ascending=False)
    
    if not top_stocks.empty:
        cols = st.columns(4)
        for i, (index, row) in enumerate(top_stocks.head(4).iterrows()):
            with cols[i]:
                st.metric(label=f"🟢 {row['Stock']}", value=f"₹{row['LTP']}", delta=f"TGT: ₹{row['Target']}")
                st.caption(f"**SL:** ₹{row['Stoploss']} | **Score:** {row['Score']}/8")
        
        st.markdown("---")
        st.markdown("#### 📊 Complete Master Results")
        
        def highlight_cols(val):
            if val == 'STRONG BUY': return 'color: green; font-weight: bold; background-color: #e6ffe6;'
            elif val == 'STRONG SELL': return 'color: red; font-weight: bold; background-color: #ffe6e6;'
            return ''
            
        st.dataframe(final_df.style.applymap(highlight_cols, subset=['Signal']), use_container_width=True, hide_index=True)
        
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            final_df.to_excel(writer, sheet_name='Master_Scan', index=False)
            
        st.download_button("📥 Download Master Report", data=buffer.getvalue(), file_name="V10_Master_Report.xlsx")
    else:
        st.info("No STRONG BUY signals found at this moment.")
        st.dataframe(final_df, use_container_width=True)
else:
    st.warning("👈 Please click 'Run AI Scanner' to start the Master Engine.")
