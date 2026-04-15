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
# FAST MODE & SECTORS
# =============================
fast_mode = st.checkbox("⚡ Fast Mode", value=True)

sectors = {
    "Nifty 50": ["RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS"],
    "Banking": ["SBIN.NS","AXISBANK.NS","KOTAKBANK.NS","ICICIBANK.NS","HDFCBANK.NS"],
    "IT": ["WIPRO.NS","HCLTECH.NS","TECHM.NS","LTIM.NS","TCS.NS"],
    "Auto": ["MARUTI.NS","M&M.NS","TATAMOTORS.NS","EICHERMOT.NS"]
}

selected_sector = st.selectbox("📊 Select Sector", list(sectors.keys()))
stocks_to_scan = sectors[selected_sector]

# =============================
# TELEGRAM ALERT (Optional)
# =============================
TELEGRAM_TOKEN = "" # మీ టోకెన్ ఇక్కడ ఇవ్వండి
CHAT_ID = ""        # మీ చాట్ ఐడి ఇక్కడ ఇవ్వండి

def send_telegram(msg):
    if TELEGRAM_TOKEN and CHAT_ID:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
        except:
            pass

# =============================
# DATA FETCH & INDICATORS
# =============================
@st.cache_data(ttl=120)
def get_data(tickers):
    return yf.download(tickers, period="30d", interval="15m", group_by="ticker", threads=True)

def calculate_indicators(df):
    df = df.copy()
    # EMAs
    df['EMA20'] = df['Close'].ewm(span=20).mean()
    df['EMA50'] = df['Close'].ewm(span=50).mean()
    # MACD
    df['EMA12'] = df['Close'].ewm(span=12).mean()
    df['EMA26'] = df['Close'].ewm(span=26).mean()
    df['MACD'] = df['EMA12'] - df['EMA26']
    df['Signal_Line'] = df['MACD'].ewm(span=9).mean()
    # RSI
    delta = df['Close'].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = -delta.clip(upper=0).rolling(14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100/(1+rs))
    return df

# =============================
# BACKTEST & AI ENGINE
# =============================
def backtest(df):
    correct, total = 0, 0
    for i in range(50, len(df)-1):
        if df['Close'].iloc[i] > df['EMA50'].iloc[i]:
            if df['Close'].iloc[i+1] > df['Close'].iloc[i]:
                correct += 1
            total += 1
    return round((correct/total)*100, 2) if total > 0 else 0

def ai_prediction(df):
    df = df.dropna()
    if len(df) < 50: return "N/A", 0
    
    # Feature engineering for AI
    df['Target'] = np.where(df['Close'].shift(-1) > df['Close'], 1, 0)
    features = ['RSI', 'MACD', 'EMA20']
    X = df[features].iloc[:-1]
    y = df['Target'].iloc[:-1]
    
    model = RandomForestClassifier(n_estimators=50, random_state=42)
    model.fit(X, y)
    
    latest_feat = df[features].tail(1)
    pred = model.predict(latest_feat)[0]
    prob = model.predict_proba(latest_feat).max()
    
    res = "BUY 🚀" if pred == 1 else "SELL 📉"
    return res, round(prob*100, 2)

# =============================
# MAIN SCANNER LOOP
# =============================
st.subheader(f"🔍 AI Scanning: {selected_sector}")
data = get_data(stocks_to_scan)

results = []
for ticker in stocks_to_scan:
    try:
        # Handle Multi-index or Single index
        df = data[ticker].copy() if len(stocks_to_scan) > 1 else data.copy()
        df = calculate_indicators(df)
        
        sig, conf = ai_prediction(df)
        acc = backtest(df)
        curr_p = round(df['Close'].iloc[-1], 2)
        chg = round(((df['Close'].iloc[-1] - df['Close'].iloc[-2])/df['Close'].iloc[-2])*100, 2)
        
        results.append({
            "Stock": ticker,
            "Price": curr_p,
            "Change %": chg,
            "RSI": round(df['RSI'].iloc[-1], 2),
            "AI Signal": sig,
            "Confidence": f"{conf}%",
            "Accuracy": f"{acc}%"
        })
    except:
        continue

# Display Results
if results:
    res_df = pd.DataFrame(results)
    
    def style_sig(v):
        c = 'background-color: #228B22; color: white' if 'BUY' in str(v) else 'background-color: #DC143C; color: white'
        return c

    st.dataframe(res_df.style.applymap(style_sig, subset=['AI Signal']), use_container_width=True)
else:
    st.error("No Data Received. Please check your internet or tickers.")

st.info("💡 Note: This AI Scanner refreshes every 30 seconds.")
