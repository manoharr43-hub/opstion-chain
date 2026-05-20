# =========================================================
# 🚀 NSE AI PRO MAX V2.2 - FIXED SIGNAL TIME & OPTION CHAIN
# + SCREENER KIT LINK & DATA PROCESSING ADDED
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

st.set_page_config(
    page_title="NSE AI PRO MAX V2.2",
    layout="wide"
)

st.fragment(run_every=60)

st.title("🚀 NSE AI PRO MAX V2.2")
st.caption("AI BASED NSE SCANNER + CALL SIDE OI ANALYSIS + SCREENER KIT")

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

# --- SCREENER KIT LINK ---
st.sidebar.markdown("---")
st.sidebar.subheader("🔗 QUICK LINKS")
screener_link = "INSERT_YOUR_LINK_HERE"  # <--- MEERU IKKADA SCREENER LINK UPDATE CHEYANDI

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
    ist = pytz.timezone('Asia/Kolkata')
    return datetime.datetime.now(ist).strftime('%Y-%m-%d %H:%M:%S')

def get_current_ist_time_only():
    ist = pytz.timezone('Asia/Kolkata')
    return datetime.datetime.now(ist).strftime('%H:%M:%S')

def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    return output.getvalue()

def calculate_indicators(df):
    if df.empty: return df
    
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
# TABS SETUP
# =========================================================
tab1, tab2 = st.tabs(["📈 AI Scanner & Option Chain", "📂 Screener Kit Data Processing"])

# =========================================================
# TAB 1: ORIGINAL AI SCANNER & OPTION CHAIN
# =========================================================
with tab1:
    try:
        # Fetch Technical Data
        df = yf.download(ticker, interval=interval, period=period, progress=False, auto_adjust=True)
        if df.empty:
            st.error("NO DATA FOUND")
        else:
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            df = calculate_indicators(df)
            signal, score = generate_signal(df)
            latest = df.iloc[-1]
            
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

            # CALL SIDE OPTION CHAIN ANALYSIS
            st.subheader(f"🔥 {selected_stock} CALL SIDE OPTION CHAIN (OI ANALYSIS)")
            
            with st.spinner("Fetching Option Chain Data..."):
                yf_ticker = yf.Ticker(ticker)
                try:
                    expiries = yf_ticker.options
                except:
                    expiries = []
                
                if expiries:
                    nearest_expiry = expiries[0]
                    option_fetched_time = get_current_ist_time()
                    st.caption(f"📅 Expiry: **{nearest_expiry}** | 🕒 Last Updated (IST): `{option_fetched_time}`")
                    
                    try:
                        opt_chain = yf_ticker.option_chain(nearest_expiry)
                        calls_df = opt_chain.calls
                        
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
                            
                            filtered_calls['STRIKE PRICE'] = filtered_calls['STRIKE PRICE'].astype(float).round(2)
                            filtered_calls['CALL LTP (Price)'] = filtered_calls['CALL LTP (Price)'].astype(float).round(2)
                            filtered_calls['CALL OI (Total)'] = filtered_calls['CALL OI (Total)'].astype(int)
                            filtered_calls['CALL VOLUME'] = filtered_calls['CALL VOLUME'].astype(int)
                            
                            max_oi_idx = filtered_calls['CALL OI (Total)'].idxmax()
                            highest_oi_strike = filtered_calls.loc[max_oi_idx, 'STRIKE PRICE']
                            
                            st.info(f"🎯 **Highest Call OI Concentration:** Strike **{highest_oi_strike}** (Acts as a strong Resistance line)")
                            
                            option_excel_df = filtered_calls[['STRIKE PRICE', 'CALL LTP (Price)', 'CALL OI (Total)', 'CALL VOLUME']].copy()
                            
                            st.dataframe(
                                option_excel_df, 
                                use_container_width=True,
                                hide_index=True
                            )
                            
                            option_excel_df['FETCHED TIME (IST)'] = option_fetched_time
                            option_excel_data = to_excel(option_excel_df)
                            st.download_button(
                                label="📥 DOWNLOAD OPTION CHAIN AS EXCEL",
                                data=option_excel_data,
                                file_name=f"{selected_stock}_call_oi_{nearest_expiry}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                        else:
                            st.warning("No call options data available in this price range.")
                    except Exception as opt_err:
                        st.warning("Yahoo Finance లో ఈ స్టాక్‌కు సంబంధించిన ఆప్షన్ చైన్ డేటా దొరకలేదు లేదా ప్రస్తుతం లోడ్ అవ్వడం లేదు.")
                else:
                    st.warning("Yahoo Finance లో ఈ స్టాక్‌కు సంబంధించిన ఆప్షన్ చైన్ డేటా దొరకలేదు.")

            # CHART & DATA TABLES
            st.subheader(f"📈 {selected_stock} LIVE CHART")
            fig = go.Figure()
            
            time_col = df.columns[0] 
            if 'index' in df.columns: time_col = 'index'
            elif 'Date' in df.columns: time_col = 'Date'
            elif 'Datetime' in df.columns: time_col = 'Datetime'
            
            fig.add_trace(go.Scatter(x=df[time_col], y=df['Close'], mode='lines', name='Close'))
            fig.add_trace(go.Scatter(x=df[time_col], y=df['EMA20'], mode='lines', name='EMA20'))
            fig.add_trace(go.Scatter(x=df[time_col], y=df['EMA50'], mode='lines', name='EMA50'))
            fig.update_layout(height=400, hovermode="x unified")
            st.plotly_chart(fig, use_container_width=True)

            # LIVE AI SCANNER SECTION
            scanner_fetched_time = get_current_ist_time()
            st.subheader("🔥 LIVE AI NIFTY 50 SCANNER")
            st.caption(f"🕒 Scanner Last Run (IST): `{scanner_fetched_time}`")
            
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
                    
                    sig_time = get_current_ist_time_only()
                    
                    c_p = float(lat['Close'].iloc[0]) if isinstance(lat['Close'], pd.Series) else float(lat['Close'])
                    r_s = float(lat['RSI'].iloc[0]) if isinstance(lat['RSI'], pd.Series) else float(lat['RSI'])
                    
                    return {
                        "STOCK": s_name, 
                        "PRICE": round(c_p, 2), 
                        "RSI": round(r_s, 2), 
                        "SIGNAL": sig, 
                        "SCORE": scr,
                        "SIGNAL TIME": sig_time 
                    }
                except: return None

            results = []
            with ThreadPoolExecutor(max_workers=15) as executor:
                scanned = executor.map(scan_stock, nse_stocks.items())
            for item in scanned:
                if item is not None: results.append(item)
            
            scanner_df = pd.DataFrame(results).sort_values(by="SCORE", ascending=False)
            
            ordered_cols = ["STOCK", "PRICE", "RSI", "SIGNAL", "SCORE", "SIGNAL TIME"]
            scanner_df = scanner_df[ordered_cols]
            
            st.dataframe(scanner_df, use_container_width=True, hide_index=True)
            
            scanner_df['REPORT GENERATED (IST)'] = scanner_fetched_time
            scanner_excel_data = to_excel(scanner_df)
            st.download_button(
                label="📥 DOWNLOAD SCANNER REPORT AS EXCEL",
                data=scanner_excel_data,
                file_name=f"Nifty50_AI_Scanner_Report_{scanner_fetched_time.replace(' ', '_').replace(':', '-')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except Exception as e:
        st.error("APP ERROR")
        st.code(str(e))

# =========================================================
# TAB 2: NEW SCREENER KIT DATA PROCESSING
# =========================================================
with tab2:
    st.header("📂 Screener Kit Data Processing")
    st.write("Meeru Screener nunchi download chesina Excel leda CSV file ni ikkada upload cheyandi.")
    
    uploaded_file = st.file_uploader("Upload Your File (CSV or Excel)", type=["csv", "xlsx", "xls"])
    
    if uploaded_file is not None:
        try:
            # File read cheyadam
            if uploaded_file.name.endswith('.csv'):
                screener_df = pd.read_csv(uploaded_file)
            else:
                screener_df = pd.read_excel(uploaded_file)
                
            st.success("✅ File Successfully Loaded!")
            
            # Processing Options: Null values remove cheyadam (Basic Cleaning)
            clean_data = st.checkbox("Clean Data (Remove empty rows)", value=True)
            if clean_data:
                screener_df = screener_df.dropna(how='all') # Anni khali ga unna rows theeseyali
            
            st.subheader("📊 Preview of Screener Data")
            st.dataframe(screener_df, use_container_width=True)
            
            st.info("💡 Note: Meeru ee data meeda further conditions (like volume breakout, price filter) apply cheyali anukunte akkada unna columns batti code adjust cheyochu.")
            
        except Exception as e:
            st.error("File read cheyadam lo error vachindi. Please check the file format.")
            st.code(str(e))
