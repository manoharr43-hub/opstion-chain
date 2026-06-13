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
    page_title="HYBRID NSE PRO SCANNER V8.0",
    layout="wide"
)

st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .css-1r6slp0 { padding: 2rem; }
    .stSidebar { background-color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 HYBRID NSE PRO SCANNER V8.0 (ULTIMATE)")
st.write("AI Prediction + RS Ranking + Option Chain OI + FII/DII + 52W High/Low + S/R")

# -------------------------------
# 1. LIVE NSE API CACHE (Feature 1)
# -------------------------------
@st.cache_resource(ttl=300)
def get_nse_session():
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    session.headers.update(headers)
    try:
        # Pinging homepage to generate valid cookies
        session.get("https://www.nseindia.com", timeout=5)
    except:
        pass
    return session

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
        df = yf.download(f"{symbol}.NS" if "^" not in symbol else symbol, interval=interval, period=period, auto_adjust=True, progress=False)
        if isinstance(df.columns, pd.MultiIndex): 
            df.columns = df.columns.get_level_values(0)
        return df
    except:
        return pd.DataFrame()

# -------------------------------
# 5. AI PREDICTION ENGINE (Feature 5)
# -------------------------------
def predict_trend_ai(prices):
    if len(prices) < 20: return "Neutral", 0
    y = prices[-20:].values
    x = np.arange(len(y))
    # Linear Regression using numpy polyfit
    slope, intercept = np.polyfit(x, y, 1)
    correlation_matrix = np.corrcoef(x, y)
    correlation = correlation_matrix[0,1]
    confidence = min(round(abs(correlation) * 100, 2), 99)
    
    if slope > 0 and confidence > 50: return "UP 🚀", confidence
    elif slope < 0 and confidence > 50: return "DOWN 🔻", confidence
    else: return "SIDEWAYS ➖", confidence

# -------------------------------
# Indicators Logic
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

    df = calculate_supertrend(df)
    df['Pivot'] = (df['High'].shift(1) + df['Low'].shift(1) + df['Close'].shift(1)) / 3
    df['Resistance_1'] = (2 * df['Pivot']) - df['Low'].shift(1)
    df['Support_1'] = (2 * df['Pivot']) - df['High'].shift(1)
    df["AVG_VOL"] = df["Volume"].rolling(20).mean()
    return df

# -------------------------------
# Scanner Core Thread
# -------------------------------
def process_stock_thread(symbol, interval, period, h52w, l52w, nifty_return):
    df = get_data(symbol, interval, period)
    if df.empty or len(df) < 60: return None
    df = add_indicators(df, interval)
    close = float(df["Close"].iloc[-1])
    score = 0
    
    # 4. Relative Strength Ranking Logic
    stock_return = ((close - df['Close'].iloc[0]) / df['Close'].iloc[0]) * 100
    rs_score = round(stock_return - nifty_return, 2) if nifty_return is not None else 0
    rs_status = "💪 Outperform" if rs_score > 0 else "📉 Underperform"

    # 5. AI Prediction Call
    ai_trend, ai_conf = predict_trend_ai(df["Close"])
    
    vol_spike = "🔥 SPIKE" if float(df["Volume"].iloc[-1]) > float(df["AVG_VOL"].iloc[-1]) * 3 else "Normal"
    pattern = get_candlestick_pattern(df)
    
    breakout_high = df["High"].rolling(20).max().shift(1).iloc[-1]
    breakout_low = df["Low"].rolling(20).min().shift(1).iloc[-1]
    brk_sig = "BULLISH" if close > breakout_high else ("BEARISH" if close < breakout_low else "NO")
    
    macd_val = "BULLISH" if df["MACD_Line"].iloc[-1] > df["Signal_Line"].iloc[-1] else "BEARISH"
    st_dir = "UP" if df["ST_Direction"].iloc[-1] == 1 else "DOWN"
    vwap_sig = "ABOVE" if close > float(df["VWAP"].iloc[-1]) else "BELOW"
    
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

    status_52w = "Mid Range"
    if h52w and l52w:
        if close >= h52w * 0.97: status_52w = "🟢 Near High"
        elif close <= l52w * 1.03: status_52w = "🔴 Near Low"

    return [
        symbol, round(close, 2), ai_trend, f"{ai_conf}%", f"{rs_score}% ({rs_status})",
        round(float(df["Support_1"].iloc[-1]), 2), round(float(df["Resistance_1"].iloc[-1]), 2),
        round(h52w, 2) if h52w else "N/A", round(l52w, 2) if l52w else "N/A", status_52w,
        round(df["RSI"].iloc[-1], 2), brk_sig, macd_val, st_dir, vwap_sig,
        pattern, vol_spike, score, signal
    ]

# -------------------------------
# Tabs Setup
# -------------------------------
tab1, tab2, tab3, tab4 = st.tabs(["🚀 Live AI Scanner", "📊 Interactive Charts", "📉 Option Chain OI (Pro)", "🏢 FII/DII Data"])

# ==========================================
# TAB 1: LIVE SCANNER
# ==========================================
with tab1:
    if st.button("🚀 RUN AI SCAN") or auto_refresh:
        selected_stocks = stocks if sector == "All NSE500" else sector_stocks[sector]
        
        # Calculate Nifty Return for RS (Feature 4)
        nifty_df = get_data("^NSEI", interval, period)
        nifty_return = None
        if not nifty_df.empty:
            nifty_return = ((nifty_df['Close'].iloc[-1] - nifty_df['Close'].iloc[0]) / nifty_df['Close'].iloc[0]) * 100

        st.write("⚡ Fetching 52-Week High/Low Data in Bulk...")
        high_52w_dict, low_52w_dict = {}, {}
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
        st.write("🧠 AI Computing Trend, RS Rank & S/R Levels...")
        results = []

        with ThreadPoolExecutor(max_workers=15) as executor:
            future_to_stock = {
                executor.submit(
                    process_stock_thread, sym, interval, period, 
                    high_52w_dict.get(sym), low_52w_dict.get(sym), nifty_return
                ): sym for sym in selected_stocks
            }
            for i, future in enumerate(as_completed(future_to_stock)):
                res = future.result()
                if res: results.append(res)
                progress.progress((i + 1) / len(selected_stocks))

        if results:
            df_res = pd.DataFrame(
                results, 
                columns=["Stock", "Price", "AI Trend", "Conf %", "RS vs NIFTY", "Support", "Resistance", "52W High", "52W Low", "52W Status", "RSI", "Breakout", "MACD", "Supertrend", "VWAP", "Pattern", "Volume", "Score", "Signal"]
            )
            df_res = df_res.sort_values(by="Score", ascending=False)
            
            def color_code(val):
                if isinstance(val, str):
                    if "STRONG BUY" in val or "BULLISH" in val or "UP" in val or "ABOVE" in val or "🔥" in val or "Outperform" in val: 
                        return 'color: green; font-weight: bold;'
                    if "STRONG SELL" in val or "BEARISH" in val or "DOWN" in val or "BELOW" in val or "Underperform" in val: 
                        return 'color: red; font-weight: bold;'
                return ''
                
            st.dataframe(df_res.style.map(color_code, subset=['Signal', 'AI Trend', 'RS vs NIFTY', 'Breakout', 'MACD', 'Supertrend', 'VWAP', 'Volume', 'Pattern']), use_container_width=True)
            
            csv = df_res.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download AI Report (CSV)", data=csv, file_name="AI_Pro_Scanner_V8.csv", mime="text/csv")
        
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
            fig.add_trace(go.Candlestick(x=df_chart.index, open=df_chart['Open'], high=df_chart['High'], low=df_chart['Low'], close=df_chart['Close'], name='Price'))
            fig.add_trace(go.Scatter(x=df_chart.index, y=df_chart['EMA20'], line=dict(color='blue', width=1.5), name='EMA 20'))
            fig.add_trace(go.Scatter(x=df_chart.index, y=df_chart['EMA50'], line=dict(color='orange', width=1.5), name='EMA 50'))
            fig.add_trace(go.Scatter(x=df_chart.index, y=df_chart['VWAP'], line=dict(color='purple', width=1, dash='dash'), name='VWAP'))
            fig.update_layout(title=f"{chart_stock} Live Dashboard", xaxis_rangeslider_visible=False, height=600, template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)

# ==========================================
# TAB 3: OPTION CHAIN OI (Feature 2)
# ==========================================
with tab3:
    st.subheader("📉 Advanced Option Chain OI Analysis (NIFTY)")
    st.write("Identifies the real-time Max Pain, Strongest Resistance (Max Call OI), and Strongest Support (Max Put OI).")
    
    if st.button("Fetch Live OI Data"):
        try:
            url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
            session = get_nse_session()
            response = session.get(url, timeout=5)
            data = response.json()
            
            records = data['records']['data']
            tot_ce_vol = data['filtered']['CE']['totVol']
            tot_pe_vol = data['filtered']['PE']['totVol']
            pcr = tot_pe_vol / tot_ce_vol if tot_ce_vol > 0 else 0
            
            # Find Resistance & Support based on Max OI
            max_ce_oi, max_pe_oi = 0, 0
            res_strike, sup_strike = 0, 0
            
            for item in records:
                if 'CE' in item and item['CE']['openInterest'] > max_ce_oi:
                    max_ce_oi = item['CE']['openInterest']
                    res_strike = item['strikePrice']
                if 'PE' in item and item['PE']['openInterest'] > max_pe_oi:
                    max_pe_oi = item['PE']['openInterest']
                    sup_strike = item['strikePrice']

            col1, col2, col3 = st.columns(3)
            col1.metric("Live NIFTY PCR", round(pcr, 4))
            col2.metric("🛡️ Max Support (Put OI)", f"{sup_strike} Strike", f"{max_pe_oi} Contracts OI")
            col3.metric("🧱 Max Resistance (Call OI)", f"{res_strike} Strike", f"-{max_ce_oi} Contracts OI")
            
            if pcr > 1.2: st.success("Sentiment: BULLISH (More Puts Written - Strong Base)")
            elif pcr < 0.8: st.error("Sentiment: BEARISH (More Calls Written - Heavy Resistance)")
            else: st.warning("Sentiment: NEUTRAL")
        except Exception as e:
            st.error("NSE server blocked the OI request. Try again later or use VPN.")

# ==========================================
# TAB 4: FII / DII DATA (Feature 3)
# ==========================================
with tab4:
    st.subheader("🏢 FII/DII Trading Activity (Cash Market)")
    st.write("Watch what the Big Institutions are doing in the Live/Latest Market.")
    
    if st.button("Fetch Institutional Data"):
        try:
            url = "https://www.nseindia.com/api/fiidiiTradeReact"
            session = get_nse_session()
            response = session.get(url, timeout=5)
            data = response.json()
            
            if data:
                fii_dii_df = pd.DataFrame(data)
                # Keep only necessary columns if available
                if 'category' in fii_dii_df.columns:
                    st.dataframe(fii_dii_df[['date', 'category', 'buyValue', 'sellValue', 'netValue']], use_container_width=True)
                    
                    st.info("💡 Note: Positive Net Value means Institutions are pumping money into the market (Bullish). Negative means they are pulling out (Bearish).")
        except Exception as e:
            st.error("NSE Security Blocked FII/DII API fetch. Please check the official NSE India website for end-of-day reports.")
