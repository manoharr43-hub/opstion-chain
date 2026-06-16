import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import io
import time
import joblib
from concurrent.futures import ThreadPoolExecutor, as_completed
from xgboost import XGBClassifier

# ==========================================
# 1. PAGE SETUP
# ==========================================
st.set_page_config(page_title="HYBRID NSE PRO SCANNER V11.2", layout="wide", page_icon="⚡")
st.title("⚡ HYBRID NSE PRO SCANNER - V11.2 PRO")
st.markdown("**Optimized Edition | Smart Money Concepts (BOS/CHOCH) | Pre-trained XGBoost Predictive Engine**")

if 'v11_data' not in st.session_state:
    st.session_state.v11_data = pd.DataFrame()

# ==========================================
# 2. SIDEBAR
# ==========================================
with st.sidebar:
    st.header("⚙️ Settings & Controls")
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
    st.markdown("---")
    run_button = st.button("🚀 RUN V11.2 PRO SCANNER", type="primary", use_container_width=True)

# ==========================================
# 3. DATA FUNCTIONS
# ==========================================
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
        return ["RELIANCE","TCS","INFY","HDFCBANK","ICICIBANK","SBIN","ITC","LT","AXISBANK"]

stocks = load_nse500()

@st.cache_data(ttl=120)
def get_data(symbol, interval, period):
    try:
        df = yf.download(f"{symbol}.NS" if "^" not in symbol else symbol,
                         interval=interval, period=period,
                         auto_adjust=True, progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    except:
        return pd.DataFrame()

# ==========================================
# 4. AI & INDICATORS
# ==========================================
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

def calculate_smc_structures(df):
    if len(df) < 30: return "Normal", "Normal"
    df['Local_High'] = df['High'].rolling(window=10, center=True).max()
    df['Local_Low'] = df['Low'].rolling(window=10, center=True).min()
    last_high = df['Local_High'].ffill().iloc[-2]
    last_low = df['Local_Low'].ffill().iloc[-2]
    current_close = df['Close'].iloc[-1]
    ema20 = df['Close'].ewm(span=20).mean().iloc[-1]
    ema50 = df['Close'].ewm(span=50).mean().iloc[-1]
    bullish_trend = ema20 > ema50
    if current_close > last_high:
        return ("BOS 📈","Structure Broken Upward") if bullish_trend else ("CHOCH 🔄","Trend Reversal Bullish")
    elif current_close < last_low:
        return ("BOS 📉","Structure Broken Downward") if not bullish_trend else ("CHOCH 🔄","Trend Reversal Bearish")
    return "Range","Normal"

@st.cache_resource
def load_xgb_model():
    try:
        return joblib.load("xgb_nse500.pkl")
    except:
        return None

xgb_model = load_xgb_model()

def run_xgb_inference(df, model):
    if model is None or len(df) < 50: return "Neutral", 0.0
    df['Return'] = df['Close'].pct_change()
    df['RSI_Norm'] = df['RSI'] / 100.0
    df['Vol_Ratio'] = df['Volume'] / df['AVG_VOL']
    df['EMA_Gap'] = (df['EMA20'] - df['EMA50']) / df['EMA50']
    df.dropna(inplace=True)
    if len(df) < 30: return "Neutral", 0.0
    latest_vector = df[['Return','RSI_Norm','Vol_Ratio','EMA_Gap']].iloc[-1].values.reshape(1,-1)
    prediction = model.predict(latest_vector)[0]
    confidence = round(model.predict_proba(latest_vector)[0][prediction]*100,2)
    return ("BULLISH 🚀" if prediction==1 else "BEARISH 🔻", confidence)

def add_indicators(df, interval):
    if len(df) < 60: return df
    df["EMA20"] = df["Close"].ewm(span=20).mean()
    df["EMA50"] = df["Close"].ewm(span=50).mean()
    delta = df["Close"].diff()
    df["RSI"] = 100 - (100 / (1 + (delta.clip(lower=0).ewm(com=13).mean() / -delta.clip(upper=0).ewm(com=13).mean())))
    df["MACD_Line"] = df["Close"].ewm(span=12).mean() - df["Close"].ewm(span=26).mean()
    df["Signal_Line"] = df["MACD_Line"].ewm(span=9).mean()
    df["AVG_VOL"] = df["Volume"].rolling(20).mean()
    df['TR'] = df[['High','Low','Close']].max(axis=1) - df[['High','Low','Close']].min(axis=1)
    df['ATR'] = df['TR'].rolling(window=14).mean()
    return df

# ==========================================
# 5. MASTER THREAD
# ==========================================
def process_stock_thread(symbol, interval, period, nifty_return):
    df = get_data(symbol, interval, period)
    if df.empty or len(df) < 60: return None
    df = add_indicators(df, interval)
    close = float(df["Close"].iloc[-1])
    ai_trend, ai_conf = predict_trend_ai(df["Close"])
    smc_structure, smc_alert = calculate_smc_structures(df)
    xgb_prediction, xgb_confidence = run_xgb_inference(df, xgb_model)
    return [symbol, close, smc_structure, xgb_prediction, f"{xgb_confidence}%", ai_trend, f"{ai_conf}%"]

# ==========================================
# 6. UI EXECUTION
# ==========================================
tab1, tab2 = st.tabs(["🚀 V11.2 Dashboard", "🔍 Custom Stock Search"])

with tab1:
    if run_button or auto_refresh:
        selected_stocks = stocks if sector=="All NSE500" else sector_stocks[sector]
        results = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_stock = {
                executor.submit(process_stock_thread, sym, interval, period, 0): sym for sym in selected_stocks
            }
            progress
