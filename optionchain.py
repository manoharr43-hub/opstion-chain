import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import pytz
import requests
import io
import time
import plotly.graph_objects as go
from concurrent.futures import ThreadPoolExecutor, as_completed

# -------------------------------
# Streamlit Page Setup
# -------------------------------
st.set_page_config(
    page_title="HYBRID NSE PRO SCANNER V7.0",
    layout="wide"
)

st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .css-1r6slp0 { padding: 2rem; }
    .stSidebar { background-color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 HYBRID NSE PRO SCANNER V7.0 (ULTRA MAX)")
st.write("Candlestick Patterns + Volume Spikes + Live Charts + PCR + Auto Refresh")

# -------------------------------
# Sidebar Configuration
# -------------------------------
with st.sidebar:
    st.header("⚙️ Configuration")
    auto_refresh = st.checkbox("🔄 Auto Refresh (Every 3 Mins)")
    interval = st.selectbox("Interval", ["5m","15m","30m","1h","1d"], index=1)
    period = st.selectbox("Period", ["5d","1mo","3mo","6mo", "1y"], index=1)
    
    sector_stocks = {
        "Banking": ["HDFCBANK","ICICIBANK","SBIN","AXISBANK","KOTAKBANK"],
        "IT": ["TCS","INFY","WIPRO","HCLTECH","TECHM"],
        "Pharma": ["SUNPHARMA","CIPLA","DIVISLAB","DRREDDY"],
        "Energy": ["RELIANCE","ONGC","BPCL","NTPC"],
        "Auto": ["TATAMOTORS","M&M","EICHERMOT","HEROMOTOCO"]
    }
    sector = st.selectbox("Sector", ["All NSE500"] + list(sector_stocks.keys()))

# -------------------------------
# Data Fetching Logic
# -------------------------------
@st.cache_data(ttl=86400)
def load_nse500():
    try:
        url = "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=5)
        df = pd.read_csv(io.StringIO(response.text))
        return sorted(df["Symbol"].dropna().unique().tolist())
    except:
        return ["RELIANCE","TCS","INFY","HDFCBANK","ICICIBANK","SBIN","ITC","LT"]

stocks = load_nse500()

@st.cache_data(ttl=120)  # Cached for 2 mins
def get_data(symbol, interval, period):
    try:
        df = yf.download(f"{symbol}.NS", interval=interval, period=period, auto_adjust=True, progress=False)
        if isinstance(df.columns, pd.MultiIndex): 
            df.columns = df.columns.get_level_values(0)
        return df
    except:
        return pd.DataFrame()

# -------------------------------
# Candlestick Pattern Logic
# -------------------------------
def get_candlestick_pattern(df):
    if len(df) < 2: return "None"
    
    O1, C1, H1, L1 = df['Open'].iloc[-2], df['Close'].iloc[-2], df['High'].iloc[-2], df['Low'].iloc[-2]
    O2, C2, H2, L2 = df['Open'].iloc[-1], df['Close'].iloc[-1], df['High'].iloc[-1], df['Low'].iloc[-1]
    
    body = abs(C2 - O2)
    rng = H2 - L2
    if rng == 0: rng = 0.001
    
    # Doji
    if body <= (rng * 0.1): return "Doji"
    # Bullish Engulfing
    if C1 < O1 and C2 > O2 and O2 < C1 and C2 > O1: return "Bullish Engulfing"
    # Bearish Engulfing
    if C1 > O1 and C2 < O2 and O2 > C1 and C2 < O1: return "Bearish Engulfing"
    # Hammer
    lower_shadow = min(O2, C2) - L2
    upper_shadow = H2 - max(O2, C2)
    if lower_shadow > 2 * body and upper_shadow < 0.2 * body: return "Hammer"
    
    return "Normal"

# -------------------------------
# Indicators Setup
# -------------------------------
def add_indicators(df, interval):
    if len(df) < 60: return df
    
    df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
    df["EMA50"] = df["Close"].ewm(span=50, adjust=False).mean()
    
    delta = df["Close"].diff()
    df["RSI"] = 100 - (100 / (1 + (delta.clip(lower=0).ewm(com=13, adjust=False).mean() / -delta.clip(upper=0).ewm(com=13, adjust=False).mean())))
    
    df["MACD_Line"] = df["Close"].ewm(span=12, adjust=False).mean() - df["Close"].ewm(span=26, adjust=False).mean()
    df["Signal_Line"] = df["MACD_Line"].ewm(span=9, adjust=False).mean()
    
    tp = (df['High'] + df['Low'] + df['Close']) / 3
    if 'd' not in interval and 'wk' not in interval and 'mo' not in interval:
        df['Date'] = df.index.date
        df['VWAP'] = (df['Volume'] * tp).groupby(df['Date']).cumsum() / df['Volume'].groupby(df['Date']).cumsum()
    else:
        df['VWAP'] = (df['Volume'] * tp).rolling(20).sum() / df['Volume'].rolling(20).sum()

    df['Pivot'] = (df['High'].shift(1) + df['Low'].shift(1) + df['Close'].shift(1)) / 3
    df['Resistance_1'] = (2 * df['Pivot']) - df['Low'].shift(1)
    df['Support_1'] = (2 * df['Pivot']) - df['High'].shift(1)
    
    df["AVG_VOL"] = df["Volume"].rolling(20).mean()
    return df

# -------------------------------
# Scanner Core
# -------------------------------
def process_stock_thread(symbol, interval, period):
    df = get_data(symbol, interval, period)
    if df.empty or len(df) < 60: return None
    
    df = add_indicators(df, interval)
    close = float(df["Close"].iloc[-1])
    score = 0
    
    # Check Volume Spike (3x average volume)
    vol_spike = "🔥 SPIKE" if float(df["Volume"].iloc[-1]) > float(df["AVG_VOL"].iloc[-1]) * 3 else "Normal"
    
    # Candlestick Pattern
    pattern = get_candlestick_pattern(df)
    
    # Breakout
    breakout_high = df["High"].rolling(20).max().shift(1).iloc[-1]
    breakout_low = df["Low"].rolling(20).min().shift(1).iloc[-1]
    brk_sig = "BULLISH" if close > breakout_high else ("BEARISH" if close < breakout_low else "NO")
    
    # Scoring Logic
    if df["EMA20"].iloc[-1] > df["EMA50"].iloc[-1]: score += 1
    else: score -= 1
    if float(df["RSI"].iloc[-1]) > 60: score += 1
    elif float(df["RSI"].iloc[-1]) < 40: score -= 1
    if df["MACD_Line"].iloc[-1] > df["Signal_Line"].iloc[-1]: score += 1
    else: score -= 1
    if close > float(df["VWAP"].iloc[-1]): score += 1
    else: score -= 1
    if brk_sig == "BULLISH": score += 1
    elif brk_sig == "BEARISH": score -= 1

    if score >= 4: signal = "STRONG BUY"
    elif score >= 2: signal = "BUY"
    elif score <= -4: signal = "STRONG SELL" 
    elif score <= -2: signal = "SELL"
    else: signal = "WAIT"

    return [
        symbol, round(close, 2), vol_spike, pattern, brk_sig, 
        round(df["RSI"].iloc[-1], 2), score, signal
    ]

# -------------------------------
# Tabs setup
# -------------------------------
tab1, tab2, tab3 = st.tabs(["🚀 Scanner", "📊 Live Charts", "📉 Nifty PCR Data"])

# ==========================================
# TAB 1: SCANNER
# ==========================================
with tab1:
    if st.button("🚀 RUN SCAN") or auto_refresh:
        selected_stocks = stocks if sector == "All NSE500" else sector_stocks[sector]
        progress = st.progress(0)
        results = []

        with ThreadPoolExecutor(max_workers=15) as executor:
            future_to_stock = {executor.submit(process_stock_thread, sym, interval, period): sym for sym in selected_stocks}
            for i, future in enumerate(as_completed(future_to_stock)):
                res = future.result()
                if res: results.append(res)
                progress.progress((i + 1) / len(selected_stocks))

        if results:
            df_res = pd.DataFrame(results, columns=["Stock", "Price", "Volume", "Pattern", "Breakout", "RSI", "Score", "Signal"])
            df_res = df_res.sort_values(by="Score", ascending=False)
            
            def color_code(val):
                if val in ["STRONG BUY", "BULLISH", "🔥 SPIKE", "Bullish Engulfing"]: return 'color: green; font-weight: bold;'
                if val in ["STRONG SELL", "BEARISH", "Bearish Engulfing"]: return 'color: red; font-weight: bold;'
                return ''
                
            st.dataframe(df_res.style.map(color_code, subset=['Signal', 'Volume', 'Pattern', 'Breakout']), use_container_width=True)
            
            csv = df_res.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download Data", data=csv, file_name="Scanner_V7.csv", mime="text/csv")
        
        if auto_refresh:
            st.warning("⏳ Auto-Refresh is ON. Scanning again in 3 minutes...")
            time.sleep(180)
            st.rerun()

# ==========================================
# TAB 2: LIVE INTERACTIVE CHARTS
# ==========================================
with tab2:
    st.subheader("📈 Interactive Candlestick Charts")
    chart_stock = st.selectbox("Select Stock for Chart:", stocks)
    
    if chart_stock:
        df_chart = get_data(chart_stock, interval, period)
        if not df_chart.empty:
            df_chart = add_indicators(df_chart, interval)
            
            fig = go.Figure()
            # Candlestick
            fig.add_trace(go.Candlestick(
                x=df_chart.index, open=df_chart['Open'], high=df_chart['High'], 
                low=df_chart['Low'], close=df_chart['Close'], name='Price'
            ))
            # EMA lines
            fig.add_trace(go.Scatter(x=df_chart.index, y=df_chart['EMA20'], line=dict(color='blue', width=1), name='EMA 20'))
            fig.add_trace(go.Scatter(x=df_chart.index, y=df_chart['EMA50'], line=dict(color='orange', width=1), name='EMA 50'))
            
            fig.update_layout(title=f"{chart_stock} - Interactive Chart", xaxis_rangeslider_visible=False, height=600, template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)

# ==========================================
# TAB 3: OPTIONS F&O / PCR DATA
# ==========================================
with tab3:
    st.subheader("📉 Nifty Put-Call Ratio (PCR)")
    st.info("Fetches live PCR data directly from NSE. (May occasionally fail due to NSE security blocks)")
    
    if st.button("Fetch Nifty PCR"):
        try:
            url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.5'
            }
            # Start a session to get cookies
            session = requests.Session()
            session.get("https://www.nseindia.com", headers=headers, timeout=5)
            # Fetch data
            response = session.get(url, headers=headers, timeout=5)
            data = response.json()
            
            tot_ce_vol = data['filtered']['CE']['totVol']
            tot_pe_vol = data['filtered']['PE']['totVol']
            pcr = tot_pe_vol / tot_ce_vol if tot_ce_vol > 0 else 0
            
            st.metric("Live NIFTY PCR", round(pcr, 4))
            
            if pcr > 1.2: st.success("Market Sentiment: BULLISH (More Puts Written)")
            elif pcr < 0.8: st.error("Market Sentiment: BEARISH (More Calls Written)")
            else: st.warning("Market Sentiment: NEUTRAL")
            
        except Exception as e:
            st.error("Failed to fetch F&O data. NSE server blocked the request. Try again later.")
