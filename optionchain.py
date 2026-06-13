import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import pytz
import requests
import io
from concurrent.futures import ThreadPoolExecutor, as_completed

# -------------------------------
# Streamlit Page Setup
# -------------------------------
st.set_page_config(
    page_title="HYBRID NSE PRO SCANNER V6.3",
    layout="wide"
)

st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .css-1r6slp0 { padding: 2rem; }
    .stSidebar { background-color: #ffffff; }
    .metric-card { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 HYBRID NSE PRO SCANNER V6.3")
st.write("EMA + RSI + Breakout + MACD + VWAP + Supertrend + 52W Range | Excel & Time")

# -------------------------------
# Sidebar Configuration
# -------------------------------
with st.sidebar:
    st.header("⚙️ Configuration")
    st.info("Scanner V6.3 includes all indicators, Breakout logic & Excel Export.")
    st.write("---")
    st.write("• **EMA:** 20/50 Cross")
    st.write("• **RSI:** 14-period")
    st.write("• **Breakout:** 20-period High/Low")
    st.write("• **MACD:** 12, 26, 9")
    st.write("• **Supertrend:** 10, 3")
    st.write("• **VWAP:** Intraday Anchored")

# -------------------------------
# Load NSE500 Stocks
# -------------------------------
@st.cache_data(ttl=86400)
def load_nse500():
    try:
        url = "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        df = pd.read_csv(io.StringIO(response.text))
        return sorted(df["Symbol"].dropna().unique().tolist())
    except:
        return ["RELIANCE","TCS","INFY","HDFCBANK","ICICIBANK","SBIN","ITC","LT","AXISBANK","KOTAKBANK"]

stocks = load_nse500()

sector_stocks = {
    "Banking": ["HDFCBANK","ICICIBANK","SBIN","AXISBANK","KOTAKBANK"],
    "IT": ["TCS","INFY","WIPRO","HCLTECH","TECHM"],
    "Pharma": ["SUNPHARMA","CIPLA","DIVISLAB","DRREDDY"],
    "Energy": ["RELIANCE","ONGC","BPCL","NTPC"],
    "Auto": ["TATAMOTORS","M&M","EICHERMOT","HEROMOTOCO"],
    "FMCG": ["ITC","HINDUNILVR","BRITANNIA","DABUR"]
}

# -------------------------------
# User Inputs
# -------------------------------
col1, col2, col3 = st.columns(3)

with col1:
    interval = st.selectbox("Interval", ["5m","15m","30m","1h","1d"], index=1)

with col2:
    period = st.selectbox("Period", ["5d","1mo","3mo","6mo", "1y"], index=1)

with col3:
    sector = st.selectbox("Sector", list(sector_stocks.keys()) + ["All NSE500"])

# -------------------------------
# Data Fetch
# -------------------------------
@st.cache_data(ttl=300)
def get_data(symbol, interval, period):
    try:
        df = yf.download(f"{symbol}.NS", interval=interval, period=period, auto_adjust=True, progress=False)
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
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

def add_indicators(df):
    if len(df) < 60: return df
    
    # EMA & RSI
    df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
    df["EMA50"] = df["Close"].ewm(span=50, adjust=False).mean()
    
    delta = df["Close"].diff()
    df["RSI"] = 100 - (100 / (1 + (delta.clip(lower=0).ewm(com=13, adjust=False).mean() / -delta.clip(upper=0).ewm(com=13, adjust=False).mean())))
    
    # MACD
    df["MACD_Line"] = df["Close"].ewm(span=12, adjust=False).mean() - df["Close"].ewm(span=26, adjust=False).mean()
    df["Signal_Line"] = df["MACD_Line"].ewm(span=9, adjust=False).mean()
    df["MACD_Hist"] = df["MACD_Line"] - df["Signal_Line"]
    
    # VWAP 
    tp = (df['High'] + df['Low'] + df['Close']) / 3
    if 'd' not in interval and 'wk' not in interval and 'mo' not in interval:
        df['Date'] = df.index.date
        df['VWAP'] = (df['Volume'] * tp).groupby(df['Date']).cumsum() / df['Volume'].groupby(df['Date']).cumsum()
    else:
        df['VWAP'] = (df['Volume'] * tp).rolling(20).sum() / df['Volume'].rolling(20).sum()

    # Supertrend
    df = calculate_supertrend(df)
    
    df["AVG_VOL"] = df["Volume"].rolling(20).mean()
    return df

# -------------------------------
# Scanner Logic 
# -------------------------------
def scan_stock(df):
    if len(df) < 60: return None

    score = 0
    close = float(df["Close"].iloc[-1])
    
    ist = pytz.timezone("Asia/Kolkata")
    last_index = df.index[-1]
    if last_index.tzinfo is None:
        last_index = last_index.tz_localize("UTC")
    signal_time = last_index.astimezone(ist).strftime("%d-%b %Y %I:%M %p")
    
    # 1. EMA
    if df["EMA20"].iloc[-1] > df["EMA50"].iloc[-1]: score += 1
    else: score -= 1

    # 2. RSI
    rsi = float(df["RSI"].iloc[-1])
    if rsi > 60: score += 1
    elif rsi < 40: score -= 1

    # 3. Breakout
    breakout_high = df["High"].rolling(20).max().shift(1).iloc[-1]
    breakout_low = df["Low"].rolling(20).min().shift(1).iloc[-1]
    breakout_signal = "NO"
    if close > breakout_high:
        score += 1
        breakout_signal = "BULLISH"
    elif close < breakout_low:
        score -= 1
        breakout_signal = "BEARISH"

    # 4. MACD
    macd = "BULLISH" if df["MACD_Line"].iloc[-1] > df["Signal_Line"].iloc[-1] else "BEARISH"
    if macd == "BULLISH": score += 1
    else: score -= 1
        
    # 5. Supertrend
    st_dir = "UP" if df["ST_Direction"].iloc[-1] == 1 else "DOWN"
    if st_dir == "UP": score += 1
    else: score -= 1
        
    # 6. VWAP Cross
    vwap_val = float(df["VWAP"].iloc[-1])
    vwap_sig = "ABOVE" if close > vwap_val else "BELOW"
    if vwap_sig == "ABOVE": score += 1
    else: score -= 1

    # 7. Volume
    if float(df["Volume"].iloc[-1]) > float(df["AVG_VOL"].iloc[-1]) * 1.5:
        if close > df["Open"].iloc[-1]: score += 1 
        else: score -= 1 

    if score >= 4: signal = "STRONG BUY"
    elif score >= 2: signal = "BUY"
    elif score <= -4: signal = "STRONG SELL" 
    elif score <= -2: signal = "SELL"
    else: signal = "WAIT"

    return {
        "Price": round(close, 2), "RSI": round(rsi, 2), "Breakout": breakout_signal,
        "Score": score, "Signal": signal, "MACD": macd, 
        "Supertrend": st_dir, "VWAP": vwap_sig, "Time": signal_time
    }

def process_stock_thread(symbol, interval, period):
    df = get_data(symbol, interval, period)
    if df.empty: return None
    df = add_indicators(df)
    signal = scan_stock(df)
    
    if signal:
        current_price = signal["Price"]
        
        # 52 Week Logic
        try:
            ticker = yf.Ticker(f"{symbol}.NS")
            high_52w = ticker.fast_info.year_high
            low_52w = ticker.fast_info.year_low
            
            if current_price >= high_52w * 0.97:
                status_52w = "🟢 Near 52W High"
            elif current_price <= low_52w * 1.03:
                status_52w = "🔴 Near 52W Low"
            else:
                status_52w = "⚪ Mid Range"
        except:
            status_52w = "N/A"
            
        return [
            symbol, signal["Price"], status_52w, signal["RSI"], signal["Breakout"],
            signal["MACD"], signal["Supertrend"], signal["VWAP"], 
            signal["Score"], signal["Signal"], signal["Time"]
        ]
    return None

# -------------------------------
# UI Layout
# -------------------------------
tab1, tab2 = st.tabs(["🚀 Live Scanner", "📈 Advanced Backtest"])

# ==========================================
# TAB 1: LIVE SCANNER
# ==========================================
with tab1:
    if st.button("🚀 RUN SCAN"):
        results = []
        selected_stocks = stocks if sector == "All NSE500" else sector_stocks[sector]

        progress = st.progress(0)
        st.write("⚡ Scanning in progress...")

        with ThreadPoolExecutor(max_workers=15) as executor:
            future_to_stock = {executor.submit(process_stock_thread, sym, interval, period): sym for sym in selected_stocks}
            for i, future in enumerate(as_completed(future_to_stock)):
                res = future.result()
                if res: results.append(res)
                progress.progress((i + 1) / len(selected_stocks))

        result_df = pd.DataFrame(
            results, 
            columns=["Stock", "Price", "52W Status", "RSI", "Breakout", "MACD", "Supertrend", "VWAP", "Score", "Signal", "Time"]
        )

        if not result_df.empty:
            result_df = result_df.sort_values(by="Score", ascending=False)
            
            def color_code(val):
                if val in ["STRONG BUY", "BULLISH", "UP", "ABOVE"]: return 'color: green; font-weight: bold;'
                if val in ["STRONG SELL", "BEARISH", "DOWN", "BELOW"]: return 'color: red; font-weight: bold;'
                return ''
                
            st.dataframe(result_df.style.map(color_code, subset=['Signal', 'Breakout', 'MACD', 'Supertrend', 'VWAP']), use_container_width=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                csv = result_df.to_csv(index=False).encode("utf-8")
                st.download_button("📥 Download CSV", data=csv, file_name="HybridScanner_V6_3.csv", mime="text/csv")
            
            with col2:
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    result_df.to_excel(writer, index=False, sheet_name='Scanner Results')
                
                st.download_button(
                    label="📊 Download Excel (.xlsx)",
                    data=buffer,
                    file_name="HybridScanner_V6_3.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            st.warning("No signals found.")

# ==========================================
# TAB 2: ADVANCED BACKTESTING
# ==========================================
with tab2:
    st.subheader("Historical Advanced Strategy Backtest")
    test_stock = st.selectbox("Select a Stock to Backtest:", stocks, index=0)
    
    if st.button("📈 RUN ADVANCED BACKTEST"):
        with st.spinner("Calculating Multi-Indicator Backtest & Metrics..."):
            df_bt = get_data(test_stock, interval, period)
            
            if df_bt.empty or len(df_bt) < 60:
                st.error("Insufficient data. Please increase the period.")
            else:
                df_bt = add_indicators(df_bt)
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
                
                trade_signals = df_bt['Position'].diff().fillna(0)
                total_trades = len(trade_signals[trade_signals != 0])
                
                winning_days = len(df_bt[df_bt['Strategy_Return'] > 0])
                losing_days = len(df_bt[df_bt['Strategy_Return'] < 0])
                win_rate = (winning_days / (winning_days + losing_days) * 100) if (winning_days + losing_days) > 0 else 0
                
                cum_market = (1 + df_bt['Market_Return']).cumprod()
                cum_strategy = (1 + df_bt['Strategy_Return']).cumprod()
                
                peak = cum_strategy.cummax()
                drawdown = (cum_strategy - peak) / peak
                # ఇక్కడ ఎర్రర్ రాకుండా పూర్తిగా సరిచేయబడింది (* 100)
                max_drawdown = drawdown.min() * 100
                
                final_market = (cum_market.iloc[-1] - 1) * 100
                final_strategy = (cum_strategy.iloc[-1] - 1) * 100
                
                st.markdown("### 📊 Strategy Performance Overview")
                m1, m2, m3, m4, m5 = st.columns(5)
                
                m1.metric("Strategy Return", f"{final_strategy:.2f}%")
                m2.metric("Market Return", f"{final_market:.2f}%")
                m3.metric("Win Rate", f"{win_rate:.1f}%")
                m4.metric("Total Trades", f"{total_trades}")
                m5.metric("Max Drawdown", f"{max_drawdown:.2f}%")
                
                plot_data = pd.DataFrame({
                    "Buy & Hold": cum_market * 100,
                    "Strategy (Breakout+MACD+VWAP+ST)": cum_strategy * 100
                })
                st.line_chart(plot_data)
                
                st.subheader("🗓️ Date-wise Entry & Exit Log")
                display_df = df_bt[['Close', 'Supertrend', 'MACD_Line', 'VWAP', 'Position', 'Strategy_Return']].copy()
                display_df.reset_index(inplace=True)
                display_df.columns = ['Date', 'Close', 'Supertrend', 'MACD', 'VWAP', 'Position', 'Net Return']
                display_df['Net Return'] = (display_df['Net Return'] * 100).round(2).astype(str) + '%'
                st.dataframe(display_df, use_container_width=True)
