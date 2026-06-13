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
    page_title="HYBRID NSE PRO SCANNER V7.1",
    layout="wide"
)

st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .css-1r6slp0 { padding: 2rem; }
    .stSidebar { background-color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 HYBRID NSE PRO SCANNER V7.1 (ALL-IN-ONE)")
st.write("52W High/Low + MACD + Supertrend + VWAP + Support/Resistance + Candlestick Patterns")

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
        "Auto": ["TATAMOTORS","M&M","EICHERMOT","HEROMOTOCO"],
        "FMCG": ["ITC","HINDUNILVR","BRITANNIA","DABUR"]
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
        return ["RELIANCE","TCS","INFY","HDFCBANK","ICICIBANK","SBIN","ITC","LT","AXISBANK","KOTAKBANK"]

stocks = load_nse500()

@st.cache_data(ttl=120)
def get_data(symbol, interval, period):
    try:
        df = yf.download(f"{symbol}.NS", interval=interval, period=period, auto_adjust=True, progress=False)
        if isinstance(df.columns, pd.MultiIndex): 
            df.columns = df.columns.get_level_values(0)
        return df
    except:
        return pd.DataFrame()

# -------------------------------
# Advanced Indicators Logic
# -------------------------------
def calculate_supertrend(df, period=10, multiplier=3):
    high = df['High']
    low = df['Low']
    close = df['Close']
    
    tr = np.maximum(high - low, np.maximum(abs(high - close.shift(1)), abs(low - close.shift(1))))
    atr = tr.rolling(window=period).mean()
    
    hl2 = (high + low) / 2
    upperband = hl2 + (multiplier * atr)
    lowerband = hl2 - (multiplier * atr)
    
    supertrend = np.zeros(len(df))
    direction = np.zeros(len(df))
    
    for i in range(1, len(df)):
        if close.iloc[i] > upperband.iloc[i-1]: direction[i] = 1
        elif close.iloc[i] < lowerband.iloc[i-1]: direction[i] = -1
        else: direction[i] = direction[i-1]
            
        if direction[i] == 1:
            lowerband.iloc[i] = max(lowerband.iloc[i], lowerband.iloc[i-1])
            supertrend[i] = lowerband.iloc[i]
        else:
            upperband.iloc[i] = min(upperband.iloc[i], upperband.iloc[i-1])
            supertrend[i] = upperband.iloc[i]
            
    df['Supertrend'] = supertrend
    df['ST_Direction'] = direction
    return df

def get_candlestick_pattern(df):
    if len(df) < 2: return "None"
    O1, C1 = df['Open'].iloc[-2], df['Close'].iloc[-2]
    O2, C2, H2, L2 = df['Open'].iloc[-1], df['Close'].iloc[-1], df['High'].iloc[-1], df['Low'].iloc[-1]
    
    body = abs(C2 - O2)
    rng = H2 - L2 if (H2 - L2) > 0 else 0.001
    
    if body <= (rng * 0.1): return "Doji"
    if C1 < O1 and C2 > O2 and O2 < C1 and C2 > O1: return "Bullish Engulfing"
    if C1 > O1 and C2 < O2 and O2 > C1 and C2 < O1: return "Bearish Engulfing"
    
    lower_shadow = min(O2, C2) - L2
    upper_shadow = H2 - max(O2, C2)
    if lower_shadow > 2 * body and upper_shadow < 0.2 * body: return "Hammer"
    
    return "Normal"

def add_indicators(df, interval):
    if len(df) < 60: return df
    
    # EMA & RSI
    df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
    df["EMA50"] = df["Close"].ewm(span=50, adjust=False).mean()
    
    delta = df["Close"].diff()
    df["RSI"] = 100 - (100 / (1 + (delta.clip(lower=0).ewm(com=13, adjust=False).mean() / -delta.clip(upper=0).ewm(com=13, adjust=False).mean())))
    
    # MACD
    df["MACD_Line"] = df["Close"].ewm(span=12, adjust=False).mean() - df["Close"].ewm(span=26, adjust=False).mean()
    df["Signal_Line"] = df["MACD_Line"].ewm(span=9, adjust=False).mean()
    
    # VWAP 
    tp = (df['High'] + df['Low'] + df['Close']) / 3
    if 'd' not in interval and 'wk' not in interval and 'mo' not in interval:
        df['Date'] = df.index.date
        df['VWAP'] = (df['Volume'] * tp).groupby(df['Date']).cumsum() / df['Volume'].groupby(df['Date']).cumsum()
    else:
        df['VWAP'] = (df['Volume'] * tp).rolling(20).sum() / df['Volume'].rolling(20).sum()

    # Supertrend
    df = calculate_supertrend(df)
    
    # Support & Resistance (Pivot Points S1 & R1)
    df['Pivot'] = (df['High'].shift(1) + df['Low'].shift(1) + df['Close'].shift(1)) / 3
    df['Resistance_1'] = (2 * df['Pivot']) - df['Low'].shift(1)
    df['Support_1'] = (2 * df['Pivot']) - df['High'].shift(1)
    
    df["AVG_VOL"] = df["Volume"].rolling(20).mean()
    return df

# -------------------------------
# Scanner Core Thread
# -------------------------------
def process_stock_thread(symbol, interval, period, h52w, l52w):
    df = get_data(symbol, interval, period)
    if df.empty or len(df) < 60: return None
    
    df = add_indicators(df, interval)
    close = float(df["Close"].iloc[-1])
    score = 0
    
    vol_spike = "🔥 SPIKE" if float(df["Volume"].iloc[-1]) > float(df["AVG_VOL"].iloc[-1]) * 3 else "Normal"
    pattern = get_candlestick_pattern(df)
    
    breakout_high = df["High"].rolling(20).max().shift(1).iloc[-1]
    breakout_low = df["Low"].rolling(20).min().shift(1).iloc[-1]
    brk_sig = "BULLISH" if close > breakout_high else ("BEARISH" if close < breakout_low else "NO")
    
    macd_val = "BULLISH" if df["MACD_Line"].iloc[-1] > df["Signal_Line"].iloc[-1] else "BEARISH"
    st_dir = "UP" if df["ST_Direction"].iloc[-1] == 1 else "DOWN"
    vwap_sig = "ABOVE" if close > float(df["VWAP"].iloc[-1]) else "BELOW"
    
    # Scoring
    if df["EMA20"].iloc[-1] > df["EMA50"].iloc[-1]: score += 1
    else: score -= 1
    if float(df["RSI"].iloc[-1]) > 60: score += 1
    elif float(df["RSI"].iloc[-1]) < 40: score -= 1
    if macd_val == "BULLISH": score += 1
    else: score -= 1
    if st_dir == "UP": score += 1
    else: score -= 1
    if vwap_sig == "ABOVE": score += 1
    else: score -= 1
    if brk_sig == "BULLISH": score += 1
    elif brk_sig == "BEARISH": score -= 1

    if score >= 4: signal = "STRONG BUY"
    elif score >= 2: signal = "BUY"
    elif score <= -4: signal = "STRONG SELL" 
    elif score <= -2: signal = "SELL"
    else: signal = "WAIT"

    support = float(df["Support_1"].iloc[-1])
    resistance = float(df["Resistance_1"].iloc[-1])
    
    # 52W Range Status Logic
    status_52w = "Mid Range"
    if h52w and l52w:
        if close >= h52w * 0.97: status_52w = "🟢 Near High"
        elif close <= l52w * 1.03: status_52w = "🔴 Near Low"

    return [
        symbol, round(close, 2), round(support, 2), round(resistance, 2),
        round(h52w, 2) if h52w else "N/A", round(l52w, 2) if l52w else "N/A", status_52w,
        round(df["RSI"].iloc[-1], 2), brk_sig, macd_val, st_dir, vwap_sig,
        pattern, vol_spike, score, signal
    ]

# -------------------------------
# Tabs Setup
# -------------------------------
tab1, tab2, tab3 = st.tabs(["🚀 Live Scanner", "📊 Interactive Charts", "📉 Nifty PCR Data"])

# ==========================================
# TAB 1: LIVE SCANNER
# ==========================================
with tab1:
    if st.button("🚀 RUN SCAN") or auto_refresh:
        selected_stocks = stocks if sector == "All NSE500" else sector_stocks[sector]
        
        st.write("⚡ Fetching 52-Week High/Low Data in Bulk...")
        high_52w_dict = {}
        low_52w_dict = {}
        
        # Fast Bulk 52W Downloader
        try:
            tickers_list = [f"{s}.NS" for s in selected_stocks]
            bulk_df = yf.download(tickers_list, period="1y", interval="1d", progress=False, auto_adjust=True)
            for s in selected_stocks:
                t = f"{s}.NS"
                try:
                    if isinstance(bulk_df.columns, pd.MultiIndex):
                        high_52w_dict[s] = bulk_df['High'][t].max()
                        low_52w_dict[s] = bulk_df['Low'][t].min()
                    else:
                        high_52w_dict[s] = bulk_df['High'].max()
                        low_52w_dict[s] = bulk_df['Low'].min()
                except:
                    high_52w_dict[s] = None
                    low_52w_dict[s] = None
        except:
            st.warning("Failed to batch fetch 52W data. Using live fallbacks.")

        progress = st.progress(0)
        st.write("🔍 Computing Tech Indicators & S/R Levels...")
        results = []

        with ThreadPoolExecutor(max_workers=15) as executor:
            future_to_stock = {
                executor.submit(
                    process_stock_thread, sym, interval, period, 
                    high_52w_dict.get(sym), low_52w_dict.get(sym)
                ): sym for sym in selected_stocks
            }
            for i, future in enumerate(as_completed(future_to_stock)):
                res = future.result()
                if res: results.append(res)
                progress.progress((i + 1) / len(selected_stocks))

        if results:
            df_res = pd.DataFrame(
                results, 
                columns=["Stock", "Price", "Support", "Resistance", "52W High", "52W Low", "52W Status", "RSI", "Breakout", "MACD", "Supertrend", "VWAP", "Pattern", "Volume", "Score", "Signal"]
            )
            df_res = df_res.sort_values(by="Score", ascending=False)
            
            def color_code(val):
                if val in ["STRONG BUY", "BULLISH", "UP", "ABOVE", "🔥 SPIKE", "Bullish Engulfing"]: return 'color: green; font-weight: bold;'
                if val in ["STRONG SELL", "BEARISH", "DOWN", "BELOW", "Bearish Engulfing"]: return 'color: red; font-weight: bold;'
                return ''
                
            st.dataframe(df_res.style.map(color_code, subset=['Signal', 'Breakout', 'MACD', 'Supertrend', 'VWAP', 'Volume', 'Pattern']), use_container_width=True)
            
            csv = df_res.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download Pro Report (CSV)", data=csv, file_name="Pro_Scanner_V7_1.csv", mime="text/csv")
        
        if auto_refresh:
            st.warning("⏳ Auto-Refresh active. Scanning again in 3 minutes...")
            time.sleep(180)
            st.rerun()

# ==========================================
# TAB 2: LIVE CHARTS
# ==========================================
with tab2:
    st.subheader("📈 Pro Candlestick Charts with Indicators")
    chart_stock = st.selectbox("Select Stock for Chart Analysis:", stocks)
    
    if chart_stock:
        df_chart = get_data(chart_stock, interval, period)
        if not df_chart.empty:
            df_chart = add_indicators(df_chart, interval)
            
            fig = go.Figure()
            fig.add_trace(go.Candlestick(
                x=df_chart.index, open=df_chart['Open'], high=df_chart['High'], 
                low=df_chart['Low'], close=df_chart['Close'], name='Price'
            ))
            fig.add_trace(go.Scatter(x=df_chart.index, y=df_chart['EMA20'], line=dict(color='blue', width=1.5), name='EMA 20'))
            fig.add_trace(go.Scatter(x=df_chart.index, y=df_chart['EMA50'], line=dict(color='orange', width=1.5), name='EMA 50'))
            fig.add_trace(go.Scatter(x=df_chart.index, y=df_chart['VWAP'], line=dict(color='purple', width=1, dash='dash'), name='VWAP'))
            
            fig.update_layout(title=f"{chart_stock} Live Dashboard", xaxis_rangeslider_visible=False, height=600, template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)

# ==========================================
# TAB 3: PCR DATA
# ==========================================
with tab3:
    st.subheader("📉 Nifty Option Chain Sentiment (PCR)")
    if st.button("Fetch Live PCR"):
        try:
            url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
            headers = {'User-Agent': 'Mozilla/5.0', 'Accept': '*/*', 'Accept-Language': 'en-US,en;q=0.5'}
            session = requests.Session()
            session.get("https://www.nseindia.com", headers=headers, timeout=5)
            response = session.get(url, headers=headers, timeout=5)
            data = response.json()
            
            pcr = data['filtered']['PE']['totVol'] / data['filtered']['CE']['totVol']
            st.metric("Live NIFTY PCR", round(pcr, 4))
            
            if pcr > 1.2: st.success("Sentiment: BULLISH")
            elif pcr < 0.8: st.error("Sentiment: BEARISH")
            else: st.warning("Sentiment: NEUTRAL")
        except Exception as e:
            st.error("NSE server busy. Please try again in a few moments.")
