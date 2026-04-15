import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from streamlit_autorefresh import st_autorefresh
import requests

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(page_title="🔥 PRO NSE AI SCANNER V7 MAX", layout="wide")
st_autorefresh(interval=30000, key="refresh")

st.title("🔥 PRO NSE AI SCANNER (ULTIMATE VERSION)")
st.markdown("---")

# =============================
# SECTORS
# =============================
sectors = {
    "Nifty 50": ["RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS"],
    "Banking": ["SBIN.NS","AXISBANK.NS","KOTAKBANK.NS"],
    "IT": ["WIPRO.NS","HCLTECH.NS","TECHM.NS"],
    "Auto": ["MARUTI.NS","M&M.NS","TATAMOTORS.NS"]
}

selected_sector = st.selectbox("📊 Select Sector", list(sectors.keys()))
stocks_to_scan = sectors[selected_sector]

# =============================
# DATA FETCH & INDICATORS
# =============================
@st.cache_data(ttl=60)
def get_data(tickers):
    return yf.download(tickers, period="30d", interval="15m", group_by="ticker", threads=True)

def calculate_indicators(df):
    df = df.copy()
    df['EMA20'] = df['Close'].ewm(span=20).mean()
    df['EMA50'] = df['Close'].ewm(span=50).mean()
    df['EMA12'] = df['Close'].ewm(span=12).mean()
    df['EMA26'] = df['Close'].ewm(span=26).mean()
    df['MACD'] = df['EMA12'] - df['EMA26']
    
    delta = df['Close'].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = -delta.clip(upper=0).rolling(14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100/(1+rs))
    return df

# =============================
# AI & BACKTEST LOGIC
# =============================
def ai_predict(df):
    df = df.dropna()
    if len(df) < 30: return "N/A", 0
    df['Target'] = np.where(df['Close'].shift(-1) > df['Close'], 1, 0)
    features = ['RSI', 'MACD', 'EMA20']
    X = df[features].iloc[:-1]
    y = df['Target'].iloc[:-1]
    model = RandomForestClassifier(n_estimators=50, random_state=42)
    model.fit(X, y)
    last_row = df[features].tail(1)
    pred = model.predict(last_row)[0]
    prob = model.predict_proba(last_row).max()
    return ("BUY 🚀" if pred == 1 else "SELL 📉"), round(prob * 100, 2)

def backtest(df):
    correct, total = 0, 0
    if len(df) > 50:
        for i in range(len(df)-11, len(df)-1):
            if df['Close'].iloc[i] > df['EMA50'].iloc[i]:
                if df['Close'].iloc[i+1] > df['Close'].iloc[i]: correct += 1
                total += 1
    return round((correct/total)*100, 2) if total > 0 else 0

# =============================
# MAIN EXECUTION
# =============================
st.subheader(f"📊 Scanning {selected_sector} Stocks...")
raw_data = get_data(stocks_to_scan)

scan_results = []

for ticker in stocks_to_scan:
    try:
        # మల్టీ-ఇండెక్స్ డేటా హ్యాండ్లింగ్
        if len(stocks_to_scan) > 1:
            df_ticker = raw_data[ticker].copy()
        else:
            df_ticker = raw_data.copy()
            
        if df_ticker.empty: continue
            
        df_ticker = calculate_indicators(df_ticker)
        signal, confidence = ai_predict(df_ticker)
        accuracy = backtest(df_ticker)
        
        curr_p = round(df_ticker['Close'].iloc[-1], 2)
        prev_p = df_ticker['Close'].iloc[-2]
        chg = round(((curr_p - prev_p) / prev_p) * 100, 2)

        scan_results.append({
            "Ticker": ticker,
            "Price": curr_p,
            "Change %": chg,
            "RSI": round(df_ticker['RSI'].iloc[-1], 2),
            "AI Signal": signal,
            "Confidence": f"{confidence}%",
            "Accuracy": f"{accuracy}%"
        })
    except:
        continue

# DISPLAY TABLE
if scan_results:
    final_df = pd.DataFrame(scan_results)
    
    # ఎర్రర్ రాకుండా ఇక్కడ మార్పులు చేశాను (Pandas Styler Fix)
    def style_df(res_df):
        def apply_color(val):
            if 'BUY' in str(val): return 'background-color: #228B22; color: white'
            if 'SELL' in str(val): return 'background-color: #DC143C; color: white'
            return ''
        
        # applymap బదులుగా map వాడుతున్నాము (New Pandas Version)
        return res_df.style.map(apply_color, subset=['AI Signal'])

    st.table(style_df(final_df))
else:
    st.error("No data found. Please refresh or check connection.")
