import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import pytz
import io
import time
import plotly.graph_objects as go
from concurrent.futures import ThreadPoolExecutor, as_completed

# -------------------------------
# Streamlit Page Setup
# -------------------------------
st.set_page_config(
    page_title="HYBRID NSE PRO SCANNER V9.1",
    layout="wide"
)

st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .css-1r6slp0 { padding: 2rem; }
    .stSidebar { background-color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 HYBRID NSE PRO SCANNER V9.1 (100% CLOUD STABLE)")
st.write("yfinance Powered | AI Trend + Relative Strength + Multi-Timeframe + Backtesting + Live Alerts")

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
# Data Fetching Logic (Pure yfinance)
# -------------------------------
@st.cache_data(ttl=86400)
def load_nse500():
    import requests
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
# Math & Indicators Engines
# -------------------------------
def predict_trend_ai(prices):
    if len(prices) < 20: return "Neutral", 0
    y = prices[-20:].values
    x = np.arange(len(y))
    slope, intercept = np.polyfit(x, y, 1)
    correlation = np.corrcoef(x, y)[0,1]
    confidence = min(round(abs(correlation) * 100, 2), 99)
    
    if slope > 0 and confidence > 50: return "UP 🚀", confidence
    elif slope < 0 and confidence > 50: return "DOWN 🔻", confidence
    else: return "SIDEWAYS ➖", confidence

def calculate_supertrend(df, period=10, multiplier=3):
    high, low, close = df['High'], df['Low'], df['Close']
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
# Core Thread Processor
# -------------------------------
def process_stock_thread(symbol, interval, period, h52w, l52w, nifty_return, daily_close_series):
    df = get_data(symbol, interval, period)
    if df.empty or len(df) < 60: return None
    df = add_indicators(df, interval)
    close = float(df["Close"].iloc[-1])
    score = 0
    
    stock_return = ((close - df['Close'].iloc[0]) / df['Close'].iloc[0]) * 100
    rs_score = round(stock_return - nifty_return, 2) if nifty_return is not None else 0
    rs_status = "💪 Outperform" if rs_score > 0 else "📉 Underperform"

    ai_trend, ai_conf = predict_trend_ai(df["Close"])
    
    mtf_status = "Not Aligned"
    if daily_close_series is not None and len(daily_close_series) >= 50:
        d_ema20 = daily_close_series.ewm(span=20, adjust=False).mean().iloc[-1]
        d_ema50 = daily_close_series.ewm(span=50, adjust=False).mean().iloc[-1]
        daily_bullish = d_ema20 > d_ema50
        current_bullish = df["EMA20"].iloc[-1] > df["EMA50"].iloc[-1]
        if daily_bullish == current_bullish:
            mtf_status = "ALIGNED 🟢" if current_bullish else "ALIGNED 🔻"

    alerts = []
    vol_spike = "Normal"
    if float(df["Volume"].iloc[-1]) > float(df["AVG_VOL"].iloc[-1]) * 3:
        vol_spike = "🔥 SPIKE"
        alerts.append("🔥 Vol Spike")
        
    rsi_val = float(df["RSI"].iloc[-1])
    if rsi_val > 70: alerts.append("🚨 RSI Overbought")
    elif rsi_val < 30: alerts.append("⚠️ RSI Oversold")
    
    breakout_high = df["High"].rolling(20).max().shift(1).iloc[-1]
    breakout_low = df["Low"].rolling(20).min().shift(1).iloc[-1]
    brk_sig = "NO"
    if close > breakout_high:
        brk_sig = "BULLISH"
        alerts.append("📈 Breakout High")
    elif close < breakout_low:
        brk_sig = "BEARISH"
        alerts.append("📉 Breakout Low")
        
    pattern = get_candlestick_pattern(df)
    if pattern in ["Bullish Engulfing", "Hammer"]: alerts.append(f"✨ {pattern}")
    
    alert_str = ", ".join(alerts) if alerts else "No Alerts"

    macd_val = "BULLISH" if df["MACD_Line"].iloc[-1] > df["Signal_Line"].iloc[-1] else "BEARISH"
    st_dir = "UP" if df["ST_Direction"].iloc[-1] == 1 else "DOWN"
    vwap_sig = "ABOVE" if close > float(df["VWAP"].iloc[-1]) else "BELOW"
    
    if df["EMA20"].iloc[-1] > df["EMA50"].iloc[-1]: score += 1
    else: score -= 1
    if rsi_val > 60: score += 1
    elif rsi_val < 40: score -= 1
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
        symbol, round(close, 2), alert_str, mtf_status, ai_trend, f"{ai_conf}%", f"{rs_score}% ({rs_status})",
        round(float(df["Support_1"].iloc[-1]), 2), round(float(df["Resistance_1"].iloc[-1]), 2),
        round(h52w, 2) if h52w else "N/A", round(l52w, 2) if l52w else "N/A", status_52w,
        round(rsi_val, 2), brk_sig, macd_val, st_dir, vwap_sig, pattern, vol_spike, score, signal
    ]

# -------------------------------
# App Tabs Setup
# -------------------------------
tab1, tab2, tab3 = st.tabs(["🚀 Live AI Scanner", "📈 Vectorized Backtest", "🔔 Active Strategy Rules"])

# ==========================================
# TAB 1: LIVE SCANNER
# ==========================================
with tab1:
    if st.button("🚀 RUN SCAN") or auto_refresh:
        selected_stocks = stocks if sector == "All NSE500" else sector_stocks[sector]
        
        nifty_df = get_data("^NSEI", interval, period)
        nifty_return = ((nifty_df['Close'].iloc[-1] - nifty_df['Close'].iloc[0]) / nifty_df['Close'].iloc[0]) * 100 if not nifty_df.empty else 0

        st.write("⚡ Processing Multi-Timeframe Bulk Matrix...")
        high_52w_dict, low_52w_dict, daily_series_dict = {}, {}, {}
        try:
            tickers_list = [f"{s}.NS" for s in selected_stocks]
            bulk_df = yf.download(tickers_list, period="1y", interval="1d", progress=False, auto_adjust=True)
            for s in selected_stocks:
                t = f"{s}.NS"
                try:
                    if isinstance(bulk_df.columns, pd.MultiIndex):
                        high_52w_dict[s] = bulk_df['High'][t].max()
                        low_52w_dict[s] = bulk_df['Low'][t].min()
                        daily_series_dict[s] = bulk_df['Close'][t].dropna()
                    else:
                        high_52w_dict[s] = bulk_df['High'].max()
                        low_52w_dict[s] = bulk_df['Low'].min()
                        daily_series_dict[s] = bulk_df['Close'].dropna()
                except:
                    high_52w_dict[s], low_52w_dict[s], daily_series_dict[s] = None, None, None
        except:
            st.warning("Bulk framework error. Running standalone metrics.")

        progress = st.progress(0)
        results = []

        with ThreadPoolExecutor(max_workers=15) as executor:
            future_to_stock = {
                executor.submit(
                    process_stock_thread, sym, interval, period, 
                    high_52w_dict.get(sym), low_52w_dict.get(sym), nifty_return, daily_series_dict.get(sym)
                ): sym for sym in selected_stocks
            }
            for i, future in enumerate(as_completed(future_to_stock)):
                res = future.result()
                if res: results.append(res)
                progress.progress((i + 1) / len(selected_stocks))

        if results:
            df_res = pd.DataFrame(
                results, 
                columns=["Stock", "Price", "⚡ Active Alerts", "MTF Trend", "AI Trend", "Conf %", "RS vs NIFTY", "Support", "Resistance", "52W High", "52W Low", "52W Status", "RSI", "Breakout", "MACD", "Supertrend", "VWAP", "Pattern", "Volume", "Score", "Signal"]
            )
            df_res = df_res.sort_values(by="Score", ascending=False)
            
            def color_code(val):
                if isinstance(val, str):
                    if any(x in val for x in ["STRONG BUY", "BULLISH", "UP", "ABOVE", "SPIKE", "Outperform", "🟢"]): 
                        return 'color: green; font-weight: bold;'
                    if any(x in val for x in ["STRONG SELL", "BEARISH", "DOWN", "BELOW", "Underperform", "🔻", "🚨"]): 
                        return 'color: red; font-weight: bold;'
                return ''
                
            st.dataframe(df_res.style.map(color_code, subset=['Signal', '⚡ Active Alerts', 'MTF Trend', 'AI Trend', 'RS vs NIFTY', 'Breakout', 'MACD', 'Supertrend', 'VWAP', 'Volume']), use_container_width=True)
            
            csv = df_res.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download Cloud Stable Report (CSV)", data=csv, file_name="Cloud_Stable_Scanner_V9_1.csv", mime="text/csv")
        
        if auto_refresh:
            st.warning("⏳ Auto-Refresh running. Scanning again in 3 minutes...")
            time.sleep(180)
            st.rerun()

# ==========================================
# TAB 2: ADVANCED BACKTESTING
# ==========================================
with tab2:
    st.subheader("📈 Vectorized Strategy Performance Analytics")
    test_stock = st.selectbox("Select Asset to Backtest:", stocks, index=0)
    
    if st.button("📈 RUN STRATEGY BACKTEST"):
        with st.spinner("Processing historical vectors..."):
            df_bt = get_data(test_stock, interval, period)
            if df_bt.empty or len(df_bt) < 60:
                st.error("Insufficient historical vector density. Increase period parameters.")
            else:
                df_bt = add_indicators(df_bt, interval)
                df_bt.dropna(inplace=True)
                
                st_score = np.where(df_bt['ST_Direction'] == 1, 1, -1)
                macd_score = np.where(df_bt['MACD_Line'] > df_bt['Signal_Line'], 1, -1)
                vwap_score = np.where(df_bt['Close'] > df_bt['VWAP'], 1, -1)
                ema_score = np.where(df_bt['EMA20'] > df_bt['EMA50'], 1, -1)
                
                breakout_high = df_bt['High'].rolling(20).max().shift(1)
                breakout_low = df_bt['Low'].rolling(20).min().shift(1)
                brk_score = np.where(df_bt['Close'] > breakout_high, 1, np.where(df_bt['Close'] < breakout_low, -1, 0))
                
                total_score = st_score + macd_score + vwap_score + ema_score + brk_score
                positions = np.where(total_score >= 2, 1, np.where(total_score <= -2, -1, np.nan))
                df_bt['Position'] = pd.Series(positions, index=df_bt.index).ffill().fillna(0)
                
                df_bt['Market_Return'] = df_bt['Close'].pct_change()
                trade_friction = np.where(df_bt['Position'].diff() != 0, 0.001, 0)
                df_bt['Strategy_Return'] = (df_bt['Position'].shift(1) * df_bt['Market_Return']) - trade_friction
                
                # 🟢 FIXED: Removed .nonzero() and used the correct pandas boolean sum
                total_trades = int((df_bt['Position'].diff().fillna(0) != 0).sum())
                
                win_rate = (len(df_bt[df_bt['Strategy_Return'] > 0]) / max(1, len(df_bt[df_bt['Strategy_Return'] != 0]))) * 100
                
                cum_market = (1 + df_bt['Market_Return'].fillna(0)).cumprod()
                cum_strategy = (1 + df_bt['Strategy_Return'].fillna(0)).cumprod()
                max_drawdown = (((cum_strategy - cum_strategy.cummax()) / cum_strategy.cummax()).min()) * 100
                
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Strategy Return", f"{((cum_strategy.iloc[-1] - 1) * 100):.2f}%")
                m2.metric("Market Return", f"{((cum_market.iloc[-1] - 1) * 100):.2f}%")
                m3.metric("Win Rate Metric", f"{win_rate:.1f}%")
                m4.metric("Total Trades Executed", f"{total_trades}")
                
                st.line_chart(pd.DataFrame({"Buy & Hold": cum_market * 100, "Hybrid Strategy": cum_strategy * 100}))

with tab3:
    st.subheader("🔔 Cloud Core Strategy Engine Rules")
    st.info("This engine processes mathematics without external scrapers, ensuring 100% cloud runtime stability.")
    st.markdown("""
    *   **Relative Strength Metrics:** Dynamically tracks baseline alpha separation vs NIFTY index calculations.
    *   **Multi-Timeframe Engine:** Automatically samples the daily trend matrix to confirm micro-interval triggers.
    *   **AI Predictor Framework:** Employs recursive linear slope regression to evaluate current predictive probability vectors.
    *   **Vectorized Backtesting:** Instantly simulates historical strategy performance and calculates win-rate metrics.
    """)
