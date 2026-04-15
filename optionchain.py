import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from datetime import datetime, timedelta

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(page_title="🔥 PRO NSE OPTIONCHAIN ULTIMATE", layout="wide")
st.title("🔥 PRO NSE AI SIMULATION (OptionChain Edition)")
st.markdown("---")

# =============================
# SECTORS
# =============================
sectors = {
    "Nifty 50": ["RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS","BHARTIARTL.NS","SBIN.NS"],
    "Banking": ["SBIN.NS","AXISBANK.NS","KOTAKBANK.NS","PNB.NS","HDFCBANK.NS","ICICIBANK.NS"],
    "IT": ["WIPRO.NS","HCLTECH.NS","TECHM.NS","INFY.NS","TCS.NS"],
    "Auto": ["MARUTI.NS","M&M.NS","TATAMOTORS.NS","HEROMOTOCO.NS"],
    "Pharma": ["SUNPHARMA.NS","DRREDDY.NS","CIPLA.NS","APOLLOHOSP.NS"],
    "Energy": ["ONGC.NS","IOC.NS","BPCL.NS","GAIL.NS"],
    "FMCG": ["ITC.NS","NESTLEIND.NS","HINDUNILVR.NS"],
    "Metals": ["TATASTEEL.NS","JSWSTEEL.NS","HINDALCO.NS"],
    "Power": ["NTPC.NS","POWERGRID.NS","TATAPOWER.NS"],
    "Finance": ["BAJFINANCE.NS","BAJAJFINSV.NS","CHOLAFIN.NS"]
}

selected_sector = st.selectbox("📊 Select Sector to Scan", list(sectors.keys()))
stocks_to_scan = sectors[selected_sector]

# =============================
# DATA FETCH
# =============================
@st.cache_data(ttl=120)
def get_data(tickers):
    return yf.download(tickers, period="60d", interval="15m", group_by="ticker", threads=True)

# =============================
# MODEL TRAINING
# =============================
@st.cache_resource
def train_model(X, y):
    model = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
    model.fit(X, y)
    return model

# =============================
# SAFE ACCURACY FUNCTION
# =============================
def calculate_accuracy(correct, total):
    """
    Calculate accuracy percentage safely.
    Returns 0 if total is zero.
    """
    return round((correct / total) * 100, 2) if total else 0

# =============================
# CORE ANALYSIS ENGINE
# =============================
def analyze(df):
    if len(df) < 100: return None
    df['EMA20'] = df['Close'].ewm(span=20).mean()
    df['EMA50'] = df['Close'].ewm(span=50).mean()
    df['EMA200'] = df['Close'].ewm(span=200).mean()
    df.dropna(inplace=True)

    price = df['Close'].iloc[-1]
    df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
    features = ['EMA20','EMA50']
    X, y = df[features].tail(60), df['Target'].tail(60)
    if len(X) < 30: return None
    model = train_model(X, y)
    pred = model.predict(X.iloc[[-1]])[0]

    confidence = calculate_accuracy(y.sum(), len(y))
    signal_text = "🟢 BUY" if pred == 1 else "🔴 SELL"

    return signal_text, confidence, round(price, 2)

# =============================
# SCANNER EXECUTION
# =============================
with st.spinner(f"Scanning {selected_sector} stocks..."):
    data = get_data(stocks_to_scan)
    results = []
    if data is not None:
        for stock in stocks_to_scan:
            try:
                df_stock = data[stock].dropna() if isinstance(data.columns, pd.MultiIndex) else data.dropna()
                out = analyze(df_stock)
                if out:
                    sig, conf, price = out
                    results.append({
                        "Stock": stock,
                        "Price": price,
                        "Signal": sig,
                        "Confidence": conf
                    })
            except Exception as e:
                continue

    if len(results) > 0:
        st.subheader(f"📊 {selected_sector} OptionChain Live Analysis")
        st.dataframe(pd.DataFrame(results), use_container_width=True)
    else:
        st.error(f"⚠️ ERROR: Could not analyze any stocks in {selected_sector} sector right now.")
        st.warning("Ensure there is enough historical data. Try changing period to '60d' and interval to '15m'.")
