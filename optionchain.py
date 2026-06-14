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

st.title("🚀 HYBRID NSE PRO SCANNER - V10.0 (Institutional Edition)")
st.markdown("**Cloud Stable | AI Target & Stoploss | Top 20 Ranked Dashboard**")

# ==========================================
# 2. CACHED FUNCTIONS (To ensure Cloud Stability & Speed)
# ==========================================
@st.cache_data(ttl=3600)
def get_nifty_stocks():
    # NSE టాప్ స్టాక్స్ లిస్ట్ (క్లౌడ్ స్టెబిలిటీ కోసం హార్డ్-కోడెడ్ లిస్ట్ వాడటం బెస్ట్)
    # ఉదాహరణకు టాప్ 50 స్టాక్స్ ఇక్కడ ఇచ్చాను. మీరు మీ ఫుల్ 500 లిస్ట్ యాడ్ చేసుకోవచ్చు.
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

def calculate_technical_indicators(df):
    """ఇండికేటర్స్ మరియు V10.0 ATR లాజిక్ క్యాలిక్యులేషన్"""
    if df.empty or len(df) < 50:
        return None
        
    # EMAs
    df['EMA_9'] = df['Close'].ewm(span=9, adjust=False).mean()
    df['EMA_21'] = df['Close'].ewm(span=21, adjust=False).mean()
    df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()
    
    # RSI (14)
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # MACD
    df['MACD'] = df['Close'].ewm(span=12, adjust=False).mean() - df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    
    # Volume Average
    df['Vol_Avg'] = df['Volume'].rolling(window=20).mean()
    
    # [V10 FEATURE]: ATR (Average True Range) for AI Target & Stoploss
    df['High-Low'] = df['High'] - df['Low']
    df['High-PrevClose'] = abs(df['High'] - df['Close'].shift(1))
    df['Low-PrevClose'] = abs(df['Low'] - df['Close'].shift(1))
    df['TR'] = df[['High-Low', 'High-PrevClose', 'Low-PrevClose']].max(axis=1)
    df['ATR'] = df['TR'].rolling(window=14).mean()
    df.drop(['High-Low', 'High-PrevClose', 'Low-PrevClose', 'TR'], axis=1, inplace=True)
    
    return df

def evaluate_strategy(df, ticker):
    """స్కోరింగ్ సిస్టమ్ & AI టార్గెట్ జనరేటర్"""
    if df is None:
        return None
        
    last_row = df.iloc[-1]
    
    # Scoring System (0 to 5 for simplicity in this demo)
    score = 0
    if last_row['EMA_9'] > last_row['EMA_21']: score += 1
    if last_row['Close'] > last_row['EMA_50']: score += 1
    if 50 < last_row['RSI'] < 70: score += 1
    if last_row['MACD'] > last_row['MACD_Signal']: score += 1
    if last_row['Volume'] > last_row['Vol_Avg'] * 1.5: score += 1
    
    # AI Signal Generation
    if score >= 4:
        signal = "STRONG BUY"
    elif score <= 1:
        signal = "STRONG SELL"
    else:
        signal = "NEUTRAL"
        
    # [V10 FEATURE]: AI Target and Stoploss Logic
    target = "-"
    stoploss = "-"
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
        'Close': round(last_row['Close'], 2),
        'Score': score,
        'Signal': signal,
        'Target': target,
        'Stoploss': stoploss,
        'RSI': round(last_row['RSI'], 2),
        'ATR': round(atr_val, 2) if pd.notna(atr_val) else "-",
        'Volume': int(last_row['Volume'])
    }

# ==========================================
# 3. SIDEBAR CONTROLS
# ==========================================
st.sidebar.header("⚙️ Scanner Settings")
trading_style = st.sidebar.radio("Trading Style:", ["Intraday (15m)", "Swing (1d)"])

if trading_style == "Intraday (15m)":
    interval = "15m"
    period = "5d"
    st.sidebar.success("Optimal Settings for Intraday selected!")
else:
    interval = "1d"
    period = "6mo"

if st.sidebar.button("🚀 Run AI Scanner", type="primary"):
    with st.spinner(f"Scanning NSE Stocks for {trading_style}... Please wait."):
        tickers = get_nifty_stocks()
        results = []
        
        progress_bar = st.progress(0)
        for i, ticker in enumerate(tickers):
            try:
                # Fetch Data
                df = yf.download(ticker, period=period, interval=interval, progress=False)
                
                # Check if data exists
                if not df.empty and len(df) > 50:
                    # Flatten multi-index columns if they exist (yfinance newer versions)
                    if isinstance(df.columns, pd.MultiIndex):
                        df.columns = df.columns.get_level_values(0)
                        
                    # Calculate & Evaluate
                    df_ta = calculate_technical_indicators(df)
                    scan_result = evaluate_strategy(df_ta, ticker)
                    
                    if scan_result:
                        results.append(scan_result)
            except Exception as e:
                pass # Skip problematic tickers silently
                
            progress_bar.progress((i + 1) / len(tickers))
            
        progress_bar.empty()
        
        if results:
            # Store results in session state to prevent clearing
            st.session_state['scan_results'] = pd.DataFrame(results)

# ==========================================
# 4. MAIN DASHBOARD & TABS
# ==========================================
tab1, tab2, tab3 = st.tabs(["🚀 Live AI Scanner", "📈 Backtest & Analytics", "📘 Strategy Rules"])

with tab1:
    if 'scan_results' in st.session_state and not st.session_state['scan_results'].empty:
        final_df = st.session_state['scan_results']
        
        # [V10 FEATURE]: TOP 20 RANKED DASHBOARD
        st.markdown("### 🏆 V10 Institutional: Top AI Picks")
        
        # Filter for STRONG BUY and sort by Score
        top_stocks = final_df[final_df['Signal'] == 'STRONG BUY'].sort_values(by=['Score', 'RSI'], ascending=[False, True])
        
        if not top_stocks.empty:
            # Display Top 4 as Metrics Cards
            st.markdown("##### 🔥 Top 4 Breakout Opportunities")
            cols = st.columns(4)
            for i, (index, row) in enumerate(top_stocks.head(4).iterrows()):
                with cols[i]:
                    st.metric(label=f"🟢 {row['Stock']}", 
                              value=f"₹{row['Close']}", 
                              delta=f"TGT: ₹{row['Target']}")
                    st.caption(f"**SL:** ₹{row['Stoploss']} | **Score:** {row['Score']}/5")
            
            st.markdown("---")
            
            # Display Full Data Table
            st.markdown("#### 📊 Complete Scanner Results")
            
            def color_signals(val):
                color = 'green' if val == 'STRONG BUY' else 'red' if val == 'STRONG SELL' else 'gray'
                return f'color: {color}; font-weight: bold;'
                
            st.dataframe(
                final_df.style.map(color_signals, subset=['Signal']),
                use_container_width=True,
                hide_index=True
            )
            
            # Excel Download Button Setup (Cloud Stable)
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                final_df.to_excel(writer, sheet_name='Scan_Results', index=False)
            
            st.download_button(
                label="📥 Download Scanner Results (Excel)",
                data=buffer.getvalue(),
                file_name=f"V10_Scan_Results_{dt.datetime.now().strftime('%Y-%m-%d')}.xlsx",
                mime="application/vnd.ms-excel",
                type="secondary"
            )
        else:
            st.info("No 'STRONG BUY' signals found right now. Wait for the next 15-min candle.")
            st.dataframe(final_df, use_container_width=True)
            
    else:
        st.warning("👈 Please click 'Run AI Scanner' from the sidebar to generate signals.")

with tab2:
    st.markdown("### Vectorized Backtesting Engine")
    st.info("V10 Backtesting logic will populate here based on ATR calculations. Currently scanning real-time signals in Tab 1.")

with tab3:
    st.markdown("### 📘 V10.0 Strategy Rules (Institutional Edition)")
    st.markdown("""
    **Indicators Used:**
    * **EMA (9, 21, 50):** Trend identification.
    * **RSI (14):** Momentum tracking.
    * **MACD:** Trend confirmation.
    * **ATR (14):** Volatility measurement for dynamic Targets & Stoplosses.
    
    **Risk Management (V10):**
    * **Stoploss:** Calculated at 1.5x ATR below the entry point.
    * **Target:** Calculated at 3.0x ATR above the entry point.
    * **Risk/Reward Ratio:** 1:2
    """)
