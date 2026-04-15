import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from streamlit_autorefresh import st_autorefresh

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(page_title="🔥 PRO NSE AI SCANNER V3", layout="wide")
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
    # Need at least 200 days for EMA200
    return yf.download(tickers, period="300d", interval="1d", group_by="ticker")

# =============================
# MODEL TRAINING
# =============================
@st.cache_resource
def train_model(X, y):
    model = RandomForestClassifier(n_estimators=80, max_depth=6)
    model.fit(X, y)
    return model

# =============================
# ANALYSIS ENGINE (Unchanged Logic)
# =============================
def analyze(df):
    if len(df) < 200: return None
    df = df.copy()
    
    # EMA Indicators for Trend
    df['EMA20'] = df['Close'].ewm(span=20).mean()
    df['EMA50'] = df['Close'].ewm(span=50).mean()
    df['EMA200'] = df['Close'].ewm(span=200).mean() # Long term trend
    
    # RSI & MACD
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
    if len(df) < 50: return None

    # Trend Logic
    price = df['Close'].iloc[-1]
    ema50 = df['EMA50'].iloc[-1]
    ema200 = df['EMA200'].iloc[-1]
    
    if price > ema50 > ema200:
        trend = "🚀 STRONG BULLISH"
    elif price < ema50 < ema200:
        trend = "🔻 STRONG BEARISH"
    else:
        trend = "⚖️ SIDEWAYS"

    # Big Player Logic (Volume Analysis)
    avg_vol = df['Volume'].rolling(20).mean().iloc[-1]
    current_vol = df['Volume'].iloc[-1]
    vol_ratio = current_vol / (avg_vol + 1e-9)
    
    if vol_ratio > 3.0:
        big_player = "🐋 WHALE ENTRY"
    elif vol_ratio > 2.0:
        big_player = "👔 INSTITUTIONAL"
    elif vol_ratio > 1.2:
        big_player = "👥 RETAIL+"
    else:
        big_player = "❄️ LOW INTEREST"

    # AI Target
    df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
    features = ['EMA20','EMA50','RSI','MACD']
    X = df[features]
    y = df['Target']
    
    model = train_model(X, y)
    pred = model.predict(X.iloc[[-1]])[0]

    # Confidence Score
    confidence = 0
    if "BULLISH" in trend: confidence += 25
    if vol_ratio > 1.8: confidence += 25
    if 40 < df['RSI'].iloc[-1] < 60: confidence += 10
    if pred == 1: confidence += 20
    if df['MACD'].iloc[-1] > df['Signal'].iloc[-1]: confidence += 20

    # Final Status based on Confidence
    if confidence >= 80: final_signal = "🔥 HIGH PROBABILITY"
    elif confidence >= 60: final_signal = "⚡ WATCH"
    else: final_signal = "❌ AVOID"
    
    # Calculate Entry, Target, Stoploss
    entry = round(price,2)
    support = df['Low'].tail(50).min()
    resistance = df['High'].tail(50).max()
    risk = abs(entry - support) if pred == 1 else abs(resistance - entry)
    
    target = round(entry + (risk * 2), 2) if pred == 1 else round(entry - (risk * risk), 2)
    stoploss = round(support, 2) if pred == 1 else round(resistance, 2)

    return trend, big_player, round(price,2), confidence, final_signal, ("🟢 BUY" if pred == 1 else "🔴 SELL"), entry, target, stoploss

# =============================
# SCANNER EXECUTION
# =============================
# We need more data (period="300d") for robust EMA200 calculation on daily interval
data = get_data(stocks_to_scan)
results = []

if data is not None:
    for stock in stocks_to_scan:
        try:
            # Handle MultiIndex if present
            if isinstance(data.columns, pd.MultiIndex):
                df = data.xs(stock, level='Ticker', axis=1).dropna()
            else:
                df = data[stock].dropna()
                
            if len(df) < 200: # We need 200 days of data for EMA200 trend
                continue

            out = analyze(df)
            if out:
                trend, big, price, conf, status, sig, ent, tg, sl = out
                results.append({
                    "Stock": stock,
                    "Price": price,
                    "Trend": trend,
                    "Big Player": big,
                    "Signal": sig,
                    "Confidence": conf,
                    "Entry": ent,
                    "Target": tg,
                    "Stoploss": sl,
                    "Final Status": status
                })
        except Exception as e:
            # print(f"Error analyzing {stock}: {e}") # Debug only
            continue

    # =============================
    # FIX APPLIED HERE
    # =============================
    # Create DataFrame from results
    result_df = pd.DataFrame(results)

    # Check if the DataFrame is not empty before sorting or displaying metrics
    if not result_df.empty:
        # Sort by Confidence (The operation that was causing the crash)
        result_df = result_df.sort_values(by="Confidence", ascending=False)

        # UI
        st.subheader(f"📊 {selected_sector} TREND & VOLUME ANALYSIS")
        st.dataframe(result_df, use_container_width=True)

        # Summary Metrics
        c1, c2 = st.columns(2)
        with c1:
            st.success("📈 TRENDING STOCKS")
            trending = result_df[result_df["Trend"].str.contains("BULLISH")]
            if not trending.empty:
                st.dataframe(trending[["Stock", "Trend"]], use_container_width=True)
            else:
                st.write("No trending stocks found in this sector.")
        with c2:
            st.info("🐋 BIG PLAYER ACTIVITY")
            whales = result_df[result_df["Big Player"].str.contains("WHALE|INSTITUTIONAL")]
            if not whales.empty:
                st.dataframe(whales[["Stock", "Big Player"]], use_container_width=True)
            else:
                st.write("No Big Player activity detected.")

        st.subheader("📈 LIVE CHART & DETAILS")
        stock_choice = st.selectbox("Pick a stock to see live updates", result_df["Stock"])
        
        # Display live price and selected stock details
        current_data = result_df[result_df["Stock"] == stock_choice]
        m1, m2, m3 = st.columns(3)
        m1.metric("Current Price", current_data.iloc[0]["Price"])
        m2.metric("Option Sentiment", current_data.iloc[0]["Big Player"])
        m3.metric("Win Rate Status", current_data.iloc[0]["Final Status"])

        # Live Chart using the full downloaded data
        live_df = data.xs(stock_choice, level='Ticker', axis=1).dropna().tail(50)
        st.line_chart(live_df["Close"])
        
    else:
        # If no stocks had enough data or calculations failed
        st.warning(f"No valid data found for stocks in {selected_sector}. Ensure these stocks have at least 200 days of trading history.")

else:
    st.error("Could not fetch data from Yahoo Finance. Please check your internet connection or try again later.")
