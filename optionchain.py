import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from streamlit_autorefresh import st_autorefresh

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(page_title="🔥 PRO NSE AI SCANNER V3 (TREND + BIG PLAYER)", layout="wide")
st_autorefresh(interval=8000, key="refresh")

st.title("🔥 PRO NSE AI SCANNER (TREND + BIG PLAYER EDITION)")

# =============================
# SECTORS
# =============================
sectors = {
    "Nifty 50": ["RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS"],
    "Banking": ["SBIN.NS","AXISBANK.NS","KOTAKBANK.NS","PNB.NS"],
    "IT": ["WIPRO.NS","HCLTECH.NS","TECHM.NS"],
    "Auto": ["MARUTI.NS","M&M.NS","TATAMOTORS.NS"],
    "Pharma": ["SUNPHARMA.NS","DRREDDY.NS","CIPLA.NS"],
    "Energy": ["ONGC.NS","IOC.NS"],
    "FMCG": ["ITC.NS","NESTLEIND.NS"],
    "Metals": ["TATASTEEL.NS","JSWSTEEL.NS"],
    "Power": ["NTPC.NS","POWERGRID.NS"],
    "Finance": ["BAJFINANCE.NS","BAJAJFINSV.NS"]
}

selected_sector = st.selectbox("📊 Select Sector", list(sectors.keys()))
stocks_to_scan = sectors[selected_sector]

# =============================
# DATA FETCH
# =============================
@st.cache_data(ttl=120)
def get_data(tickers):
    # Error fixed in V3: Ensure multi-ticker download is clean
    return yf.download(tickers, period="60d", interval="15m", group_by="ticker", threads=True)

# =============================
# MODEL TRAINING
# =============================
@st.cache_resource
def train_model(X, y):
    model = RandomForestClassifier(n_estimators=80, max_depth=6)
    model.fit(X, y)
    return model

# =============================
# ANALYSIS ENGINE
# =============================
def analyze(df):
    df = df.copy()
    
    # Indicators
    df['EMA20'] = df['Close'].ewm(span=20).mean()
    df['EMA50'] = df['Close'].ewm(span=50).mean()
    df['EMA200'] = df['Close'].ewm(span=200).mean()
    
    delta = df['Close'].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = -delta.clip(upper=0).rolling(14).mean()
    rs = gain / (loss + 1e-9)
    df['RSI'] = 100 - (100 / (1 + rs))
    
    df['EMA12'] = df['Close'].ewm(span=12).mean()
    df['EMA26'] = df['Close'].ewm(span=26).mean()
    df['MACD'] = df['EMA12'] - df['EMA26']
    df['Signal'] = df['MACD'].ewm(span=9).mean()

    df.dropna(inplace=True)

    # Values for analysis
    price = df['Close'].iloc[-1]
    ema50 = df['EMA50'].iloc[-1]
    ema200 = df['EMA200'].iloc[-1]
    avg_vol = df['Volume'].rolling(20).mean().iloc[-1]
    current_vol = df['Volume'].iloc[-1]
    vol_ratio = current_vol / (avg_vol + 1e-9)
    rsi = df['RSI'].iloc[-1]
    macd = df['MACD'].iloc[-1]
    signal = df['Signal'].iloc[-1]

    # Trend and Big Player
    trend = "🚀 STRONG BULLISH" if price > ema50 > ema200 else "🔻 STRONG BEARISH" if price < ema50 < ema200 else "⚖️ SIDEWAYS"
    big_player = "🐋 WHALE ENTRY" if vol_ratio > 3.0 else "👔 INSTITUTIONAL" if vol_ratio > 2.0 else "👥 RETAIL+" if vol_ratio > 1.2 else "❄️ LOW INTEREST"

    # AI Target (Need enough data)
    if len(df) < 60: return None
    
    df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
    features = ['EMA20','EMA50','RSI','MACD']
    X = df[features]
    y = df['Target']
    
    model = train_model(X, y)
    pred = model.predict(X.iloc[[-1]])[0]

    # Confidence Score
    confidence = 0
    if "BULLISH" in trend: confidence += 25
    if vol_ratio > 2: confidence += 25
    if 40 < rsi < 60: confidence += 10
    if pred == 1: confidence += 20
    if macd > signal: confidence += 20

    final_signal = "🔥 HIGH PROBABILITY" if confidence >= 80 else "⚡ WATCH" if confidence >= 60 else "❌ AVOID"
    
    return trend, big_player, round(price,2), confidence, final_signal, ("🟢 BUY" if pred == 1 else "🔴 SELL")

# =============================
# SCANNER EXECUTION
# =============================
with st.spinner(f"Scanning {selected_sector} stocks..."):
    data = get_data(stocks_to_scan)
    results = []

    if data is not None:
        for stock in stocks_to_scan:
            try:
                # Fixed multi-ticker indexing error:
                if isinstance(data.columns, pd.MultiIndex):
                    df_stock = data[stock].dropna()
                else:
                    df_stock = data.dropna() # Single stock download case

                if len(df_stock) > 100: # Need enough historical data for 200 EMA
                    out = analyze(df_stock)
                    if out:
                        trend, big, price, conf, status, sig = out
                        results.append({
                            "Stock": stock,
                            "Price": price,
                            "Trend": trend,
                            "Big Player": big,
                            "Signal": sig,
                            "Confidence": conf,
                            "Final Status": status
                        })
            except Exception as e:
                continue

    # =============================
    # UI and ERROR HANDLING (NEW V3)
    # =============================
    if len(results) > 0:
        # Results successfully fetched
        result_df = pd.DataFrame(results).sort_values(by="Confidence", ascending=False)

        st.subheader(f"📊 {selected_sector} TREND & VOLUME ANALYSIS")
        st.dataframe(result_df, use_container_width=True)

        st.subheader("🐋 BIG PLAYER SUMMARY")
        st.dataframe(result_df[result_df["Big Player"].str.contains("WHALE|INSTITUTIONAL")][["Stock", "Big Player", "Final Status"]], use_container_width=True)

    else:
        # Handling the KeyError: Confidence scenario
        st.error(f"⚠️ **ERROR:** Could not analyze any stocks in the **{selected_sector}** sector right now.")
        st.warning("This can happen during market off-hours, when data download fails, or if there is not enough historical data for indicators (like 200 EMA) on 15m intervals. Try refreshing or switching sectors.")
        st.info("Ensure you are requesting enough data. Try changing period to '60d' and interval to '15m'.")
