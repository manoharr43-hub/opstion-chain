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
    page_title="HYBRID NSE PRO SCANNER V5.3",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .css-1r6slp0 { padding: 2rem; }
    .stSidebar { background-color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 HYBRID NSE PRO SCANNER V5.3 (Full NSE500)")
st.write("EMA + RSI + Volume + Breakout + 52W High/Low & Backtesting")

# -------------------------------
# Sidebar Configuration
# -------------------------------
with st.sidebar:
    st.header("⚙️ Configuration")
    st.info("Scanner V5.3 is optimized to scan all Nifty 500 assets rapidly.")
    st.write("---")
    st.write("• **EMA:** 20/50 Cross")
    st.write("• **RSI:** 14-period")
    st.write("• **Volume:** 20-period SMA")

# -------------------------------
# Load NSE500 Stocks
# -------------------------------
@st.cache_data(ttl=86400)
def load_nse500():
    try:
        url = "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        df = pd.read_csv(io.StringIO(response.text))
        return sorted(df["Symbol"].dropna().unique().tolist())
    except Exception as e:
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
        df = yf.download(
            f"{symbol}.NS",
            interval=interval,
            period=period,
            auto_adjust=True,
            progress=False
        )
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    except Exception as e:
        return pd.DataFrame()

# -------------------------------
# RSI Calculation
# -------------------------------
def calculate_rsi(df, period=14):
    delta = df["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(com=period - 1, adjust=False).mean()
    avg_loss = loss.ewm(com=period - 1, adjust=False).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# -------------------------------
# Add Indicators
# -------------------------------
def add_indicators(df):
    if len(df) < 60:
        return df
    df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
    df["EMA50"] = df["Close"].ewm(span=50, adjust=False).mean()
    df["RSI"] = calculate_rsi(df)
    df["AVG_VOL"] = df["Volume"].rolling(20).mean()
    return df

# -------------------------------
# Scanner Logic
# -------------------------------
def scan_stock(df):
    if len(df) < 60:
        return None

    score = 0
    close = float(df["Close"].iloc[-1])

    ist = pytz.timezone("Asia/Kolkata")
    last_index = df.index[-1]
    
    if last_index.tzinfo is None:
        last_index = last_index.tz_localize("UTC")
        
    signal_time = last_index.astimezone(ist).strftime("%d-%b %Y %I:%M %p")

    ema_signal = "NEUTRAL"
    breakout_signal = "NO"
    volume_signal = "NO"

    if df["EMA20"].iloc[-1] > df["EMA50"].iloc[-1]:
        score += 1
        ema_signal = "BUY"
    else:
        score -= 1
        ema_signal = "SELL"

    rsi = float(df["RSI"].iloc[-1])
    if rsi > 60:
        score += 1
    elif rsi < 40:
        score -= 1

    breakout_high = df["High"].rolling(20).max().shift(1).iloc[-1]
    breakout_low = df["Low"].rolling(20).min().shift(1).iloc[-1]
    if close > breakout_high:
        score += 1
        breakout_signal = "BULLISH"
    elif close < breakout_low:
        score -= 1
        breakout_signal = "BEARISH"

    avg_vol = float(df["AVG_VOL"].iloc[-1])
    current_vol = float(df["Volume"].iloc[-1])
    is_green = df["Close"].iloc[-1] > df["Open"].iloc[-1]

    if avg_vol > 0 and current_vol > avg_vol * 1.5:
        volume_signal = "SPIKE"
        if is_green:
            score += 1 
        else:
            score -= 1 

    if score >= 3:
        final_signal = "STRONG BUY"
    elif score == 2:
        final_signal = "BUY"
    elif score <= -3:
        final_signal = "STRONG SELL" 
    elif score == -2:
        final_signal = "SELL"
    else:
        final_signal = "WAIT"

    return {
        "Price": round(close, 2),
        "EMA": ema_signal,
        "RSI": round(rsi, 2),
        "Breakout": breakout_signal,
        "Volume": volume_signal,
        "Score": score,
        "Signal": final_signal,
        "Time": signal_time
    }

# -------------------------------
# Threading Process with 52W Logic
# -------------------------------
def process_stock_thread(symbol, interval, period):
    df = get_data(symbol, interval, period)
    if df.empty:
        return None
    df = add_indicators(df)
    signal = scan_stock(df)
    
    if signal:
        current_price = signal["Price"]
        
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
            symbol,
            signal["Price"],
            status_52w,          
            signal["EMA"],
            signal["RSI"],
            signal["Breakout"],
            signal["Volume"],
            signal["Score"],
            signal["Signal"],
            signal["Time"]
        ]
    return None

# -------------------------------
# UI Layout Tabs
# -------------------------------
tab1, tab2 = st.tabs(["🚀 Live Scanner", "📈 Strategy Backtest"])

# ==========================================
# TAB 1: LIVE SCANNER 
# ==========================================
with tab1:
    if st.button("🚀 RUN SCAN"):
        results = []
        if sector == "All NSE500":
            selected_stocks = stocks  # మార్పు: ఇక్కడ [:100] లిమిట్‌ను పూర్తిగా తీసేశాము
        else:
            selected_stocks = sector_stocks[sector]

        progress = st.progress(0)
        status_text = st.empty()
        status_text.text(f"⚡ మొత్తం {len(selected_stocks)} స్టాక్స్ స్కాన్ అవుతున్నాయి... దయచేసి కొన్ని సెకన్లు ఆగండి...")

        # మార్పు: 500 స్టాక్స్ వేగంగా అవ్వడానికి max_workers ను 10 నుండి 15 కి పెంచాము
        with ThreadPoolExecutor(max_workers=15) as executor:
            future_to_stock = {
                executor.submit(process_stock_thread, symbol, interval, period): symbol 
                for symbol in selected_stocks
            }
            
            for i, future in enumerate(as_completed(future_to_stock)):
                res = future.result()
                if res:
                    results.append(res)
                progress.progress((i + 1) / len(selected_stocks))

        status_text.empty() 

        result_df = pd.DataFrame(
            results,
            columns=["Stock", "Price", "52W Status", "EMA", "RSI", "Breakout", "Volume", "Score", "Signal", "Time"]
        )

        if not result_df.empty:
            result_df = result_df.sort_values(by="Score", ascending=False)
            st.success(f"Scan Completed : {len(result_df)} Stocks Found")
            
            def highlight_signals(val):
                if val == "STRONG BUY": return 'background-color: lightgreen; color: black;'
                elif val == "STRONG SELL": return 'background-color: lightcoral; color: black;'
                elif val == "BUY": return 'color: green;'
                elif val == "SELL": return 'color: red;'
                return ''
                
            st.dataframe(result_df.style.map(highlight_signals, subset=['Signal']), use_container_width=True)

            csv = result_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name="HybridScanner_All_NSE500.csv",
                mime="text/csv"
            )
        else:
            st.warning("No signals found.")

# ==========================================
# TAB 2: BACKTESTING MODULE
# ==========================================
with tab2:
    st.subheader("Historical Strategy Backtest")
    st.info("⚠️ Tip: Backtest sathi varati Period '6mo' kinva '1y' nivida, mhanje data kami padnar nahi.")
    
    test_stock = st.selectbox("Select a Stock to Backtest:", stocks, index=0)
    
    if st.button("📈 RUN BACKTEST"):
        with st.spinner("Calculating Historical Data..."):
            df_bt = get_data(test_stock, interval, period)
            
            if df_bt.empty or len(df_bt) < 60:
                st.error(f"Data khup kami ahe ({len(df_bt)} candles). Backtest sathi kiman 60 candles pahijet. Krupaya varati Period badlun '6mo' kinva '1y' kara.")
            else:
                df_bt = add_indicators(df_bt)
                df_bt.dropna(inplace=True)
                
                ema_score = np.where(df_bt['EMA20'] > df_bt['EMA50'], 1, -1)
                rsi_score = np.where(df_bt['RSI'] > 60, 1, np.where(df_bt['RSI'] < 40, -1, 0))
                
                breakout_high = df_bt['High'].rolling(20).max().shift(1)
                breakout_low = df_bt['Low'].rolling(20).min().shift(1)
                brk_score = np.where(df_bt['Close'] > breakout_high, 1, np.where(df_bt['Close'] < breakout_low, -1, 0))
                
                vol_condition = df_bt['Volume'] > (df_bt['AVG_VOL'] * 1.5)
                green_candle = df_bt['Close'] > df_bt['Open']
                red_candle = df_bt['Close'] < df_bt['Open']
                
                vol_score = np.where(vol_condition & green_candle, 1, np.where(vol_condition & red_candle, -1, 0))
                
                total_score = ema_score + rsi_score + brk_score + vol_score
                
                positions = np.where(total_score >= 2, 1, np.where(total_score <= -2, -1, np.nan))
                df_bt['Position'] = pd.Series(positions, index=df_bt.index).ffill().fillna(0)
                
                df_bt['Market_Return'] = df_bt['Close'].pct_change()
                df_bt['Strategy_Return'] = df_bt['Position'].shift(1) * df_bt['Market_Return']
                
                plot_data = pd.DataFrame({
                    "Buy & Hold Return": (1 + df_bt['Market_Return']).cumprod() * 100,
                    "Strategy Return": (1 + df_bt['Strategy_Return']).cumprod() * 100
                })
                
                st.line_chart(plot_data)
                
                final_market = plot_data["Buy & Hold Return"].iloc[-1] - 100
                final_strategy = plot_data["Strategy Return"].iloc[-1] - 100
                
                m1, m2, m3 = st.columns(3)
                m1.metric("Strategy Net Return", f"{final_strategy:.2f}%")
                m2.metric("Buy & Hold Return", f"{final_market:.2f}%")
                
                if final_strategy > final_market:
                    m3.success("✅ Strategy ne market peksha jast return dila!")
                else:
                    m3.error("❌ Strategy market peksha kami raheli.")
