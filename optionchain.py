import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from streamlit_autorefresh import st_autorefresh

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(page_title="🔥 PRO NSE AI SCANNER V7", layout="wide")
st_autorefresh(interval=10000, key="refresh")

st.title("🔥 PRO NSE AI SCANNER V7 (OPTIMIZED ENGINE)")
st.markdown("---")

# =============================
# SECTORS
# =============================
sectors = {
    "Nifty 50": ["RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS"],
    "Banking": ["SBIN.NS","AXISBANK.NS","KOTAKBANK.NS","PNB.NS"],
    "IT": ["WIPRO.NS","HCLTECH.NS","TECHM.NS","INFY.NS","TCS.NS"],
    "Auto": ["MARUTI.NS","M&M.NS","TATAMOTORS.NS"],
    "Pharma": ["SUNPHARMA.NS","DRREDDY.NS","CIPLA.NS"],
}

selected_sector = st.selectbox("📊 Select Sector", list(sectors.keys()))
stocks_to_scan = sectors[selected_sector]

# =============================
# DATA FETCH (FAST + SAFE)
# =============================
@st.cache_data(ttl=120)
def get_data(tickers):
    return yf.download(
        tickers,
        period="60d",
        interval="15m",
        group_by="ticker",
        threads=True
    )

# =============================
# GLOBAL MODEL (TRAIN ONCE)
# =============================
@st.cache_resource
def train_model(X, y):
    model = RandomForestClassifier(
        n_estimators=120,
        max_depth=10,
        random_state=42
    )
    model.fit(X, y)
    return model

# =============================
# INDICATORS
# =============================
def add_indicators(df):
    df = df.copy()

    df['EMA20'] = df['Close'].ewm(span=20).mean()
    df['EMA50'] = df['Close'].ewm(span=50).mean()

    delta = df['Close'].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = -delta.clip(upper=0).rolling(14).mean()
    rs = gain / (loss + 1e-9)
    df['RSI'] = 100 - (100 / (1 + rs))

    df['MACD'] = df['Close'].ewm(span=12).mean() - df['Close'].ewm(span=26).mean()
    df['Signal'] = df['MACD'].ewm(span=9).mean()

    return df.dropna()

# =============================
# PIVOT
# =============================
def pivots(df):
    h, l, c = df['High'].iloc[-10:].max(), df['Low'].iloc[-10:].min(), df['Close'].iloc[-1]
    p = (h + l + c) / 3
    return (2*p - h), (2*p - l)

# =============================
# SHORT COVERING
# =============================
def short_cover(df):
    if len(df) < 20:
        return "NA", 0

    vol_ratio = df['Volume'].iloc[-1] / (df['Volume'].rolling(20).mean().iloc[-1] + 1e-9)
    price_change = df['Close'].pct_change().iloc[-1] * 100

    if price_change > 1 and vol_ratio > 2:
        return "⚡ SHORT COVERING", 30
    elif vol_ratio > 1.5:
        return "⚖️ BREAKOUT VOL", 10
    return "NORMAL", 0

# =============================
# ANALYZE ENGINE
# =============================
def analyze(df):

    if len(df) < 120:
        return None

    df = add_indicators(df)

    s1, r1 = pivots(df)
    cover, boost = short_cover(df)

    price = df['Close'].iloc[-1]

    # ML TARGET
    df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)

    features = ['EMA20','EMA50','RSI','MACD']
    X = df[features].tail(80)
    y = df['Target'].tail(80)

    if len(X) < 30:
        return None

    model = train_model(X, y)
    pred = model.predict(X.iloc[[-1]])[0]

    confidence = 0

    if price > df['EMA50'].iloc[-1]:
        confidence += 20
    if pred == 1:
        confidence += 25
    if cover == "⚡ SHORT COVERING":
        confidence += 30
    if df['MACD'].iloc[-1] > df['Signal'].iloc[-1]:
        confidence += 15

    signal = "🟢 BUY" if pred == 1 else "🔴 SELL"

    sl = s1 if pred == 1 else r1
    risk = abs(price - sl)
    target = price + (risk * 2) if pred == 1 else price - (risk * 2)

    return {
        "Price": round(price,2),
        "Signal": signal,
        "Confidence": confidence,
        "Cover": cover,
        "SL": round(sl,2),
        "Target": round(target,2)
    }

# =============================
# RUN SCANNER
# =============================
with st.spinner("Scanning market..."):
    data = get_data(stocks_to_scan)
    results = []

    for stock in stocks_to_scan:
        try:
            if stock not in data.columns.levels[0]:
                continue

            df = data[stock].dropna()
            out = analyze(df)

            if out:
                out["Stock"] = stock
                results.append(out)

        except:
            continue

# =============================
# UI
# =============================
if results:
    df = pd.DataFrame(results).sort_values("Confidence", ascending=False)

    st.subheader("📊 Results")
    st.dataframe(df, use_container_width=True)

    st.subheader("🔥 Top Picks")
    st.dataframe(df.head(5), use_container_width=True)

else:
    st.warning("No signals found")
