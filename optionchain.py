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
# FAST MODE
# =============================
fast_mode = st.checkbox("⚡ Fast Mode", value=True)

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
# TELEGRAM (OPTIONAL)
# =============================
TELEGRAM_TOKEN = ""
CHAT_ID = ""

def send_telegram(msg):
    if TELEGRAM_TOKEN == "" or CHAT_ID == "":
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except:
        pass

# =============================
# DATA FETCH
# =============================
@st.cache_data(ttl=120)
def get_data(tickers):
    # తాజా డేటాను డౌన్‌లోడ్ చేస్తుంది
    return yf.download(tickers, period="30d", interval="15m", group_by="ticker", threads=True)

# =============================
# INDICATORS
# =============================
def calculate_indicators(df):
    df = df.copy()
    df['EMA20'] = df['Close'].ewm(span=20).mean()
    df['EMA50'] = df['Close'].ewm(span=50).mean()
    df['EMA12'] = df['Close'].ewm(span=12).mean()
    df['EMA26'] = df['Close'].ewm(span=26).mean()
    df['MACD'] = df['EMA12'] - df['EMA26']
    df['Signal'] = df['MACD'].ewm(span=9).mean()

    delta = df['Close'].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = -delta.clip(upper=0).rolling(14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100/(1+rs))
    return df

# =============================
# BACKTEST (Symmetry fixed here)
# =============================
def backtest(df):
    correct = 0
    total = 0
    # కనీసం 50 క్యాండిల్స్ ఉంటేనే బ్యాక్ టెస్ట్ చేస్తుంది
    if len(df) > 50:
        for i in range(50, len(df)-1):
            if df['Close'].iloc[i] > df['EMA50'].iloc[i]:
                if df['Close'].iloc[i+1] > df['Close'].iloc[i]:
                    correct += 1
                total += 1
    # ఇక్కడ 'else 0' యాడ్ చేసి ఎర్రర్ సరిచేసాను
    return round((correct/total)*100, 2) if total > 0 else 0

# =============================
# AI PREDICTION LOGIC
# =============================
def ai_predict(df):
    df = df.dropna()
    if len(df) < 50:
        return "N/A", 0
    
    # Target: ధర పెరిగితే 1, తగ్గితే 0
    df['Target'] = np.where(df['Close'].shift(-1) > df['Close'], 1, 0)
    features = ['RSI', 'MACD', 'EMA20']
    X = df[features].iloc[:-1]
    y = df['Target'].iloc[:-1]
    
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X, y)
    
    last_row = df[features].tail(1)
    prediction = clf.predict(last_row)[0]
    prob = clf.predict_proba(last_row).max()
    
    signal = "BUY 🚀" if prediction == 1 else "SELL 📉"
    return signal, round(prob * 100, 2)

# =============================
# MAIN EXECUTION
# =============================
st.subheader(f"📊 Scanning {selected_sector} Stocks...")
raw_data = get_data(stocks_to_scan)

scan_results = []

for ticker in stocks_to_scan:
    try:
        # సింగిల్ లేదా మల్టీ ఇండెక్స్ డేటా హ్యాండ్లింగ్
        df_ticker = raw_data[ticker].copy() if len(stocks_to_scan) > 1 else raw_data.copy()
        df_ticker = calculate_indicators(df_ticker)
        
        signal, confidence = ai_predict(df_ticker)
        accuracy = backtest(df_ticker)
        
        current_price = round(df_ticker['Close'].iloc[-1], 2)
        price_change = round(((df_ticker['Close'].iloc[-1] - df_ticker['Close'].iloc[-2]) / df_ticker['Close'].iloc[-2]) * 100, 2)

        scan_results.append({
            "Ticker": ticker,
            "Price": current_price,
            "Change %": price_change,
            "RSI": round(df_ticker['RSI'].iloc[-1], 2),
            "AI Signal": signal,
            "AI Conf.": f"{confidence}%",
            "Strategy Acc.": f"{accuracy}%"
        })
    except Exception as e:
        continue

# ఫలితాలను చూపించడం
if scan_results:
    final_df = pd.DataFrame(scan_results)
    
    def highlight_signal(val):
        color = 'background-color: #228B22; color: white' if 'BUY' in str(val) else 'background-color: #DC143C; color: white'
        return color

    st.table(final_df.style.applymap(highlight_signal, subset=['AI Signal']))
else:
    st.warning("No data found or symbols are incorrect.")

st.markdown("---")
st.caption("AI Scanner v7.0 Max | Data updated every 30 seconds.")
