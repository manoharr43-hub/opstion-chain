# =========================================================
# 🚀 NSE AI PRO MAX V10.0 ULTRA
# =========================================================

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import requests
import plotly.graph_objects as go
import pytz
import io
import time
import urllib3

from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from streamlit_autorefresh import st_autorefresh

urllib3.disable_warnings()

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="NSE AI PRO MAX V10.0",
    page_icon="🚀",
    layout="wide"
)

# =========================================================
# AUTO REFRESH
# =========================================================

st_autorefresh(interval=60000, key="refresh")

# =========================================================
# DARK THEME - UPGRADED UI
# =========================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Exo+2:wght@300;400;600;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Exo 2', sans-serif;
}

.main {
    background: linear-gradient(135deg, #0a0e1a 0%, #0d1117 50%, #0a1628 100%);
    color: #e2e8f0;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1117 0%, #111827 100%);
    border-right: 1px solid #1e3a5f;
}

.stMetric {
    background: linear-gradient(135deg, #1a2332 0%, #1e2d42 100%);
    border: 1px solid #2563eb44;
    border-radius: 16px;
    padding: 18px;
    box-shadow: 0 4px 20px rgba(37, 99, 235, 0.1);
    transition: all 0.3s ease;
}

.stMetric:hover {
    border-color: #2563eb;
    box-shadow: 0 8px 30px rgba(37, 99, 235, 0.2);
    transform: translateY(-2px);
}

h1, h2, h3, h4 {
    color: #f0f9ff !important;
    font-family: 'Exo 2', sans-serif !important;
    font-weight: 800 !important;
    letter-spacing: 1px;
}

div.stButton > button:first-child {
    background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 50%, #3b82f6 100%);
    color: white;
    border-radius: 12px;
    border: none;
    width: 100%;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    padding: 12px;
    box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3);
    transition: all 0.3s ease;
}

div.stButton > button:first-child:hover {
    box-shadow: 0 8px 25px rgba(37, 99, 235, 0.5);
    transform: translateY(-2px);
}

.stAlert {
    border-radius: 12px;
    font-weight: 600;
}

.stSelectbox > div > div {
    background-color: #1a2332;
    border: 1px solid #2563eb44;
    border-radius: 10px;
}

.stDataFrame {
    border-radius: 12px;
    overflow: hidden;
}

.stTabs [data-baseweb="tab-list"] {
    background-color: #111827;
    border-radius: 12px;
    padding: 4px;
}

.stTabs [data-baseweb="tab"] {
    background-color: transparent;
    color: #94a3b8;
    border-radius: 8px;
    font-weight: 600;
    letter-spacing: 0.5px;
}

.stTabs [aria-selected="true"] {
    background-color: #1d4ed8 !important;
    color: white !important;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# TITLE
# =========================================================

st.markdown("""
<div style='text-align:center; padding: 20px 0;'>
    <h1 style='font-size: 2.5rem; background: linear-gradient(135deg, #3b82f6, #60a5fa, #93c5fd);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
    font-family: Exo 2, sans-serif; font-weight: 800; letter-spacing: 3px;'>
    🚀 NSE AI PRO MAX V10.0 ULTRA
    </h1>
    <p style='color: #64748b; letter-spacing: 4px; font-size: 0.85rem; text-transform: uppercase;'>
    Institutional AI Quantitative Trading System — NIFTY 500 Edition
    </p>
</div>
""", unsafe_allow_html=True)

# =========================================================
# NIFTY 500 STOCK DATABASE (Major stocks)
# =========================================================

nse_stocks = {
    # INDEX
    "NIFTY 50": "^NSEI",
    "BANKNIFTY": "^NSEBANK",
    "NIFTY IT": "^CNXIT",
    "NIFTY PHARMA": "^CNXPHARMA",
    "NIFTY AUTO": "^CNXAUTO",
    "NIFTY FMCG": "^CNXFMCG",
    "NIFTY METAL": "^CNXMETAL",
    "NIFTY ENERGY": "^CNXENERGY",
    "NIFTY REALTY": "^CNXREALTY",

    # LARGE CAP
    "RELIANCE": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "INFY": "INFY.NS",
    "HDFCBANK": "HDFCBANK.NS",
    "ICICIBANK": "ICICIBANK.NS",
    "SBIN": "SBIN.NS",
    "AXISBANK": "AXISBANK.NS",
    "ITC": "ITC.NS",
    "LT": "LT.NS",
    "BHARTIARTL": "BHARTIARTL.NS",
    "TATAMOTORS": "TATAMOTORS.NS",
    "MARUTI": "MARUTI.NS",
    "BAJFINANCE": "BAJFINANCE.NS",
    "HINDUNILVR": "HINDUNILVR.NS",
    "SUNPHARMA": "SUNPHARMA.NS",
    "WIPRO": "WIPRO.NS",
    "POWERGRID": "POWERGRID.NS",
    "NTPC": "NTPC.NS",
    "TATASTEEL": "TATASTEEL.NS",
    "JSWSTEEL": "JSWSTEEL.NS",
    "HINDALCO": "HINDALCO.NS",
    "ONGC": "ONGC.NS",
    "IOC": "IOC.NS",
    "ZOMATO": "ZOMATO.NS",
    "IRCTC": "IRCTC.NS",
    "HCLTECH": "HCLTECH.NS",
    "TECHM": "TECHM.NS",
    "BAJAJFINSV": "BAJAJFINSV.NS",
    "KOTAKBANK": "KOTAKBANK.NS",
    "TITAN": "TITAN.NS",
    "ASIANPAINT": "ASIANPAINT.NS",
    "ULTRACEMCO": "ULTRACEMCO.NS",
    "NESTLEIND": "NESTLEIND.NS",
    "DRREDDY": "DRREDDY.NS",
    "CIPLA": "CIPLA.NS",
    "DIVISLAB": "DIVISLAB.NS",
    "APOLLOHOSP": "APOLLOHOSP.NS",
    "EICHERMOT": "EICHERMOT.NS",
    "HEROMOTOCO": "HEROMOTOCO.NS",
    "BAJAJ-AUTO": "BAJAJ-AUTO.NS",
    "TATACONSUM": "TATACONSUM.NS",
    "BRITANNIA": "BRITANNIA.NS",
    "COALINDIA": "COALINDIA.NS",
    "BPCL": "BPCL.NS",
    "GRASIM": "GRASIM.NS",
    "INDUSINDBK": "INDUSINDBK.NS",
    "M&M": "M&M.NS",
    "HDFCLIFE": "HDFCLIFE.NS",
    "SBILIFE": "SBILIFE.NS",
    "ICICIPRULI": "ICICIPRULI.NS",

    # ADANI GROUP
    "ADANIENT": "ADANIENT.NS",
    "ADANIPORTS": "ADANIPORTS.NS",
    "ADANIPOWER": "ADANIPOWER.NS",
    "ADANIGREEN": "ADANIGREEN.NS",
    "ADANITRANS": "ADANITRANS.NS",
    "ADANIGAS": "ADANIGAS.NS",
    "ADANIWILMAR": "ADANIWILMAR.NS",
    "NDTV": "NDTV.NS",

    # TATA GROUP
    "TATACHEM": "TATACHEM.NS",
    "TATAPOWER": "TATAPOWER.NS",
    "TATACOMM": "TATACOMM.NS",
    "TATAINVEST": "TATAINVEST.NS",
    "TRENT": "TRENT.NS",
    "VOLTAS": "VOLTAS.NS",
    "TITAN": "TITAN.NS",

    # MIDCAP
    "PIDILITIND": "PIDILITIND.NS",
    "BERGEPAINT": "BERGEPAINT.NS",
    "HAVELLS": "HAVELLS.NS",
    "GODREJCP": "GODREJCP.NS",
    "MARICO": "MARICO.NS",
    "DABUR": "DABUR.NS",
    "COLPAL": "COLPAL.NS",
    "MCDOWELL-N": "MCDOWELL-N.NS",
    "PAGEIND": "PAGEIND.NS",
    "ABCAPITAL": "ABCAPITAL.NS",
    "BANKBARODA": "BANKBARODA.NS",
    "PNB": "PNB.NS",
    "CANBK": "CANBK.NS",
    "UNIONBANK": "UNIONBANK.NS",
    "FEDERALBNK": "FEDERALBNK.NS",
    "IDFCFIRSTB": "IDFCFIRSTB.NS",
    "BANDHANBNK": "BANDHANBNK.NS",
    "AUBANK": "AUBANK.NS",
    "RBLBANK": "RBLBANK.NS",
    "YESBANK": "YESBANK.NS",
    "LICHSGFIN": "LICHSGFIN.NS",
    "MUTHOOTFIN": "MUTHOOTFIN.NS",
    "CHOLAFIN": "CHOLAFIN.NS",
    "MANAPPURAM": "MANAPPURAM.NS",
    "RECLTD": "RECLTD.NS",
    "PFC": "PFC.NS",
    "IRFC": "IRFC.NS",
    "HAL": "HAL.NS",
    "BEL": "BEL.NS",
    "BHEL": "BHEL.NS",
    "RVNL": "RVNL.NS",
    "IRCON": "IRCON.NS",
    "RAILVIKAS": "RAILVIKAS.NS",
    "NHPC": "NHPC.NS",
    "SJVN": "SJVN.NS",
    "CESC": "CESC.NS",
    "TORNTPOWER": "TORNTPOWER.NS",
    "JSW ENERGY": "JSWENERGY.NS",
    "TATAELXSI": "TATAELXSI.NS",
    "LTTS": "LTTS.NS",
    "MPHASIS": "MPHASIS.NS",
    "COFORGE": "COFORGE.NS",
    "PERSISTENT": "PERSISTENT.NS",
    "LTIM": "LTIM.NS",
    "OFSS": "OFSS.NS",
    "KPIT": "KPIT.NS",
    "ZENSARTECH": "ZENSARTECH.NS",
    "NAUKRI": "NAUKRI.NS",
    "POLICYBZR": "POLICYBZR.NS",
    "PAYTM": "PAYTM.NS",
    "NYKAA": "NYKAA.NS",
    "CARTRADE": "CARTRADE.NS",
    "DELHIVERY": "DELHIVERY.NS",
    "INDIAMART": "INDIAMART.NS",
    "JUSTDIAL": "JUSTDIAL.NS",
    "APLAPOLLO": "APLAPOLLO.NS",
    "ASTRAL": "ASTRAL.NS",
    "SUPREMEIND": "SUPREMEIND.NS",
    "APOLLOTYRE": "APOLLOTYRE.NS",
    "MRF": "MRF.NS",
    "BALKRISIND": "BALKRISIND.NS",
    "CEAT": "CEAT.NS",
    "EXIDEIND": "EXIDEIND.NS",
    "AMARAJABAT": "AMARAJABAT.NS",
    "MOTHERSON": "MOTHERSON.NS",
    "BOSCHLTD": "BOSCHLTD.NS",
    "ESCORTS": "ESCORTS.NS",
    "ASHOKLEY": "ASHOKLEY.NS",
    "TVSMOTOR": "TVSMOTOR.NS",
    "ATUL": "ATUL.NS",
    "DEEPAKNTR": "DEEPAKNTR.NS",
    "NAVINFLUOR": "NAVINFLUOR.NS",
    "PIIND": "PIIND.NS",
    "UPL": "UPL.NS",
    "COROMANDEL": "COROMANDEL.NS",
    "CHAMBLFERT": "CHAMBLFERT.NS",
    "GNFC": "GNFC.NS",
    "GAIL": "GAIL.NS",
    "IGL": "IGL.NS",
    "MGL": "MGL.NS",
    "PETRONET": "PETRONET.NS",
    "CONCOR": "CONCOR.NS",
    "GMRINFRA": "GMRINFRA.NS",
    "INTERGLOBE": "INTERGLOBE.NS",
    "SPICEJET": "SPICEJET.NS",
    "OBEROIRLTY": "OBEROIRLTY.NS",
    "DLF": "DLF.NS",
    "GODREJPROP": "GODREJPROP.NS",
    "PRESTIGE": "PRESTIGE.NS",
    "SOBHA": "SOBHA.NS",
    "BRIGADE": "BRIGADE.NS",
    "SUNCLAYLT": "SUNCLAYLT.NS",
    "AMBER": "AMBER.NS",
    "DIXON": "DIXON.NS",
    "BLUESTARCO": "BLUESTARCO.NS",
    "KAJARIACER": "KAJARIACER.NS",
    "CENTURYPLY": "CENTURYPLY.NS",
    "GREENPLY": "GREENPLY.NS",
    "TRIDENT": "TRIDENT.NS",
    "RAYMOND": "RAYMOND.NS",
    "MANYAVAR": "MANYAVAR.NS",
    "TTKPRESTIG": "TTKPRESTIG.NS",
    "RELAXO": "RELAXO.NS",
    "BATAINDIA": "BATAINDIA.NS",
    "CAMPUS": "CAMPUS.NS",
}

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.markdown("## ⚙️ AI CONTROL PANEL")

# Category filter
category = st.sidebar.selectbox(
    "📂 CATEGORY",
    ["All Stocks", "INDEX", "Large Cap", "Adani Group", "Tata Group", "Midcap", "Banking", "IT", "Pharma"]
)

category_filters = {
    "INDEX": ["NIFTY 50", "BANKNIFTY", "NIFTY IT", "NIFTY PHARMA", "NIFTY AUTO", "NIFTY FMCG", "NIFTY METAL", "NIFTY ENERGY", "NIFTY REALTY"],
    "Large Cap": ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "SBIN", "AXISBANK", "ITC", "LT", "BHARTIARTL",
                  "TATAMOTORS", "MARUTI", "BAJFINANCE", "HINDUNILVR", "SUNPHARMA", "WIPRO", "HCLTECH", "TECHM",
                  "BAJAJFINSV", "KOTAKBANK", "TITAN", "ASIANPAINT", "NESTLEIND"],
    "Adani Group": ["ADANIENT", "ADANIPORTS", "ADANIPOWER", "ADANIGREEN", "ADANITRANS", "ADANIGAS", "ADANIWILMAR"],
    "Tata Group": ["TCS", "TATAMOTORS", "TATASTEEL", "TATACHEM", "TATAPOWER", "TATACOMM", "TRENT", "VOLTAS", "TITAN", "TATAELXSI", "TATACONSUM"],
    "Banking": ["HDFCBANK", "ICICIBANK", "SBIN", "AXISBANK", "KOTAKBANK", "INDUSINDBK", "BANKBARODA", "PNB", "CANBK", "FEDERALBNK", "IDFCFIRSTB", "BANDHANBNK"],
    "IT": ["TCS", "INFY", "WIPRO", "HCLTECH", "TECHM", "LTIM", "MPHASIS", "COFORGE", "PERSISTENT", "TATAELXSI", "LTTS", "OFSS", "KPIT"],
    "Pharma": ["SUNPHARMA", "DRREDDY", "CIPLA", "DIVISLAB", "APOLLOHOSP"],
}

if category == "All Stocks":
    filtered_stocks = nse_stocks
else:
    keys = category_filters.get(category, list(nse_stocks.keys()))
    filtered_stocks = {k: v for k, v in nse_stocks.items() if k in keys}

selected_stock = st.sidebar.selectbox(
    "📊 SELECT STOCK",
    sorted(list(filtered_stocks.keys()))
)

interval = st.sidebar.selectbox(
    "⏱ TIMEFRAME",
    ["5m", "15m", "30m", "1h"]
)

period = st.sidebar.selectbox(
    "📅 PERIOD",
    ["1d", "5d", "1mo"]
)

ticker = filtered_stocks[selected_stock]

# =========================================================
# INDIA TIME
# =========================================================

india = pytz.timezone("Asia/Kolkata")
current_time = datetime.now(india)

st.sidebar.markdown("---")
st.sidebar.info(current_time.strftime("🕒 %d-%m-%Y %H:%M:%S IST"))

hour = current_time.hour
minute = current_time.minute
weekday = current_time.weekday()

if weekday < 5 and (
    (hour == 9 and minute >= 15) or
    (10 <= hour <= 14) or
    (hour == 15 and minute <= 30)
):
    st.sidebar.success("🟢 MARKET OPEN")
else:
    st.sidebar.error("🔴 MARKET CLOSED")

# =========================================================
# DATA LOADER
# =========================================================

@st.cache_data(ttl=60)
def load_market_data(ticker, interval, period):
    try:
        df = yf.download(
            ticker,
            interval=interval,
            period=period,
            progress=False,
            auto_adjust=True,
            threads=True
        )
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    except:
        return pd.DataFrame()

# =========================================================
# ATR
# =========================================================

def calculate_atr(df, period=14):
    high_low = df["High"] - df["Low"]
    high_close = abs(df["High"] - df["Close"].shift())
    low_close = abs(df["Low"] - df["Close"].shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return tr.rolling(period).mean()

# =========================================================
# SUPERTREND
# =========================================================

def calculate_supertrend(df, period=10, multiplier=3.0):
    atr = calculate_atr(df, period)
    hl2 = (df["High"] + df["Low"]) / 2

    upper_band = hl2 + (multiplier * atr)
    lower_band = hl2 - (multiplier * atr)

    supertrend = pd.Series(index=df.index, dtype=float)
    direction = pd.Series(index=df.index, dtype=int)

    for i in range(1, len(df)):
        if df["Close"].iloc[i] > upper_band.iloc[i - 1]:
            direction.iloc[i] = 1
        elif df["Close"].iloc[i] < lower_band.iloc[i - 1]:
            direction.iloc[i] = -1
        else:
            direction.iloc[i] = direction.iloc[i - 1]

        if direction.iloc[i] == 1:
            supertrend.iloc[i] = lower_band.iloc[i]
        else:
            supertrend.iloc[i] = upper_band.iloc[i]

    return supertrend, direction

# =========================================================
# BOLLINGER BANDS
# =========================================================

def calculate_bollinger(df, period=20, std_dev=2):
    sma = df["Close"].rolling(period).mean()
    std = df["Close"].rolling(period).std()
    upper = sma + (std_dev * std)
    lower = sma - (std_dev * std)
    return upper, sma, lower

# =========================================================
# ALL INDICATORS
# =========================================================

def calculate_indicators(df):
    df = df.copy()

    # EMA
    df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
    df["EMA50"] = df["Close"].ewm(span=50, adjust=False).mean()

    # RSI
    delta = df["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / (avg_loss + 1e-10)
    df["RSI"] = 100 - (100 / (1 + rs))

    # MACD
    ema12 = df["Close"].ewm(span=12).mean()
    ema26 = df["Close"].ewm(span=26).mean()
    df["MACD"] = ema12 - ema26
    df["MACD_SIGNAL"] = df["MACD"].ewm(span=9).mean()
    df["MACD_HIST"] = df["MACD"] - df["MACD_SIGNAL"]

    # VWAP
    df["VWAP"] = (
        (df["Close"] * df["Volume"]).cumsum()
        / (df["Volume"].cumsum() + 1e-10)
    )

    # ATR
    df["ATR"] = calculate_atr(df)

    # BOLLINGER BANDS (NEW)
    df["BB_UPPER"], df["BB_MID"], df["BB_LOWER"] = calculate_bollinger(df)
    df["BB_WIDTH"] = (df["BB_UPPER"] - df["BB_LOWER"]) / df["BB_MID"]
    df["BB_SIGNAL"] = np.where(
        df["Close"] < df["BB_LOWER"], "OVERSOLD",
        np.where(df["Close"] > df["BB_UPPER"], "OVERBOUGHT", "NEUTRAL")
    )

    # SUPERTREND (NEW)
    df["SUPERTREND"], df["ST_DIRECTION"] = calculate_supertrend(df)

    # SMART MONEY
    df["VOL_AVG"] = df["Volume"].rolling(20).mean()
    df["SMART_MONEY"] = df["Volume"] > df["VOL_AVG"] * 2

    # STOCHASTIC
    low14 = df["Low"].rolling(14).min()
    high14 = df["High"].rolling(14).max()
    df["STOCH_K"] = 100 * (df["Close"] - low14) / (high14 - low14 + 1e-10)
    df["STOCH_D"] = df["STOCH_K"].rolling(3).mean()

    df.fillna(0, inplace=True)
    return df

# =========================================================
# AI SIGNAL ENGINE
# =========================================================

def generate_signal(latest):
    score = 0
    signals = []

    # EMA Trend
    if latest["EMA20"] > latest["EMA50"]:
        score += 25
        signals.append("✅ EMA Bullish")
    else:
        score -= 25
        signals.append("🔻 EMA Bearish")

    # RSI
    if 55 <= latest["RSI"] <= 70:
        score += 20
        signals.append("✅ RSI Bullish Zone")
    elif latest["RSI"] < 30:
        score += 15
        signals.append("⚡ RSI Oversold")
    elif latest["RSI"] > 75:
        score -= 15
        signals.append("⚠️ RSI Overbought")

    # MACD
    if latest["MACD"] > latest["MACD_SIGNAL"]:
        score += 20
        signals.append("✅ MACD Bullish")
    else:
        score -= 20
        signals.append("🔻 MACD Bearish")

    # VWAP
    if latest["Close"] > latest["VWAP"]:
        score += 15
        signals.append("✅ Above VWAP")
    else:
        score -= 15
        signals.append("🔻 Below VWAP")

    # SUPERTREND (NEW)
    if latest["ST_DIRECTION"] == 1:
        score += 15
        signals.append("🚀 Supertrend BUY")
    elif latest["ST_DIRECTION"] == -1:
        score -= 15
        signals.append("🔻 Supertrend SELL")

    # BOLLINGER BANDS (NEW)
    if latest["BB_SIGNAL"] == "OVERSOLD":
        score += 10
        signals.append("⚡ BB Oversold")
    elif latest["BB_SIGNAL"] == "OVERBOUGHT":
        score -= 10
        signals.append("⚠️ BB Overbought")

    # SMART MONEY
    if latest["SMART_MONEY"]:
        score += 10
        signals.append("💰 Smart Money Flow")

    # FINAL SIGNAL
    if score >= 70:
        signal = "🚀 STRONG BUY"
        color = "success"
    elif score >= 30:
        signal = "✅ BUY"
        color = "success"
    elif score <= -70:
        signal = "🚨 STRONG SELL"
        color = "error"
    elif score <= -30:
        signal = "🔻 SELL"
        color = "error"
    else:
        signal = "⚠️ SIDEWAYS"
        color = "warning"

    confidence = min(abs(score), 95)
    return signal, score, confidence, signals

# =========================================================
# OPTION CHAIN — FIXED WITH PROXY + RETRY
# =========================================================

@st.cache_data(ttl=60)
def get_option_chain(symbol="NIFTY"):
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "referer": "https://www.nseindia.com/option-chain",
        "x-requested-with": "XMLHttpRequest",
        "connection": "keep-alive",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
    }

    # Try multiple proxy/mirror approaches
    urls = [
        f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}",
        f"https://nseindia.com/api/option-chain-indices?symbol={symbol}",
    ]

    session = requests.Session()
    session.headers.update(headers)

    for attempt in range(3):
        try:
            # First get cookies from homepage
            home_resp = session.get(
                "https://www.nseindia.com",
                timeout=15,
                verify=False
            )
            time.sleep(1.5)

            # Get option chain page to set referer cookies
            session.get(
                "https://www.nseindia.com/option-chain",
                timeout=10,
                verify=False
            )
            time.sleep(1)

            # Fetch actual data
            response = session.get(
                urls[0],
                timeout=15,
                verify=False
            )

            if response.status_code == 200:
                data = response.json()
                records = data.get("records", {}).get("data", [])

                if records:
                    rows = []
                    for item in records:
                        strike = item.get("strikePrice", 0)
                        ce = item.get("CE", {})
                        pe = item.get("PE", {})
                        rows.append({
                            "STRIKE": strike,
                            "CALL_OI": ce.get("openInterest", 0),
                            "PUT_OI": pe.get("openInterest", 0),
                            "CALL_CHG_OI": ce.get("changeinOpenInterest", 0),
                            "PUT_CHG_OI": pe.get("changeinOpenInterest", 0),
                            "CALL_LTP": ce.get("lastPrice", 0),
                            "PUT_LTP": pe.get("lastPrice", 0),
                            "CALL_IV": ce.get("impliedVolatility", 0),
                            "PUT_IV": pe.get("impliedVolatility", 0),
                        })
                    return pd.DataFrame(rows), "live"

        except Exception as e:
            time.sleep(2)
            continue

    # FALLBACK — Simulated data (if NSE blocks)
    strikes = list(range(21000, 26000, 100)) if symbol == "NIFTY" else list(range(44000, 54000, 200))
    np.random.seed(42)
    rows = []
    for s in strikes:
        rows.append({
            "STRIKE": s,
            "CALL_OI": int(np.random.randint(1000, 500000)),
            "PUT_OI": int(np.random.randint(1000, 500000)),
            "CALL_CHG_OI": int(np.random.randint(-50000, 50000)),
            "PUT_CHG_OI": int(np.random.randint(-50000, 50000)),
            "CALL_LTP": round(np.random.uniform(5, 500), 2),
            "PUT_LTP": round(np.random.uniform(5, 500), 2),
            "CALL_IV": round(np.random.uniform(10, 40), 2),
            "PUT_IV": round(np.random.uniform(10, 40), 2),
        })
    return pd.DataFrame(rows), "demo"

# =========================================================
# TABS
# =========================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "📈 LIVE TECHNICAL",
    "📊 BOLLINGER + SUPERTREND",
    "📂 OPTION CHAIN",
    "🤖 AI SCANNER"
])

# =========================================================
# TAB 1 — TECHNICAL
# =========================================================

with tab1:
    data = load_market_data(ticker, interval, period)

    if not data.empty:
        data = calculate_indicators(data)
        latest = data.iloc[-1]
        signal, score, confidence, signal_list = generate_signal(latest)

        st.subheader("🤖 AI SIGNAL ENGINE")

        col_sig, col_conf = st.columns([2, 1])
        with col_sig:
            if "BUY" in signal:
                st.success(f"{signal} | CONFIDENCE: {confidence}%")
            elif "SELL" in signal:
                st.error(f"{signal} | CONFIDENCE: {confidence}%")
            else:
                st.warning(signal)

        with col_conf:
            st.markdown(f"""
            <div style='background: #1a2332; border: 1px solid #374151; border-radius: 12px; padding: 15px; text-align: center;'>
                <div style='color: #94a3b8; font-size: 0.75rem; letter-spacing: 2px;'>AI SCORE</div>
                <div style='color: {"#22c55e" if score > 0 else "#ef4444"}; font-size: 2rem; font-weight: 800;'>{score}</div>
            </div>
            """, unsafe_allow_html=True)

        # Signal breakdown
        with st.expander("🔍 SIGNAL BREAKDOWN"):
            cols = st.columns(4)
            for i, s in enumerate(signal_list):
                cols[i % 4].markdown(f"- {s}")

        # METRICS
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("PRICE", round(float(latest["Close"]), 2))
        c2.metric("RSI", round(float(latest["RSI"]), 2))
        c3.metric("VWAP", round(float(latest["VWAP"]), 2))
        c4.metric("MACD", round(float(latest["MACD"]), 4))
        c5.metric("STOCH %K", round(float(latest["STOCH_K"]), 2))

        # ATR Based Targets
        sl = latest["Close"] - latest["ATR"] * 1.5
        target1 = latest["Close"] + latest["ATR"] * 2
        target2 = latest["Close"] + latest["ATR"] * 4

        s1, s2, s3 = st.columns(3)
        s1.error(f"🛑 STOPLOSS : {round(float(sl), 2)}")
        s2.success(f"🎯 TARGET 1 : {round(float(target1), 2)}")
        s3.success(f"🎯 TARGET 2 : {round(float(target2), 2)}")

        # CHART
        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=data.index, open=data["Open"],
            high=data["High"], low=data["Low"],
            close=data["Close"], name="PRICE",
            increasing_line_color="#22c55e",
            decreasing_line_color="#ef4444"
        ))
        fig.add_trace(go.Scatter(x=data.index, y=data["EMA20"], mode="lines", name="EMA20", line=dict(color="#3b82f6", width=1.5)))
        fig.add_trace(go.Scatter(x=data.index, y=data["EMA50"], mode="lines", name="EMA50", line=dict(color="#f59e0b", width=1.5)))
        fig.add_trace(go.Scatter(x=data.index, y=data["VWAP"], mode="lines", name="VWAP", line=dict(color="#a78bfa", width=1.5, dash="dot")))

        fig.update_layout(
            template="plotly_dark",
            height=700,
            xaxis_rangeslider_visible=False,
            plot_bgcolor="#0d1117",
            paper_bgcolor="#0d1117",
            font=dict(family="Exo 2", color="#94a3b8"),
            showlegend=True,
            legend=dict(bgcolor="#1a2332", bordercolor="#374151"),
        )
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.error("❌ Data load అవ్వలేదు. వేరే stock try చేయండి.")

# =========================================================
# TAB 2 — BOLLINGER + SUPERTREND
# =========================================================

with tab2:
    st.subheader("📊 BOLLINGER BANDS + SUPERTREND")

    if not data.empty:
        bb_col1, bb_col2, bb_col3, bb_col4 = st.columns(4)
        bb_col1.metric("BB UPPER", round(float(latest["BB_UPPER"]), 2))
        bb_col2.metric("BB MID", round(float(latest["BB_MID"]), 2))
        bb_col3.metric("BB LOWER", round(float(latest["BB_LOWER"]), 2))
        bb_signal_val = str(latest["BB_SIGNAL"])
        if bb_signal_val == "OVERSOLD":
            bb_col4.success("⚡ OVERSOLD")
        elif bb_signal_val == "OVERBOUGHT":
            bb_col4.error("⚠️ OVERBOUGHT")
        else:
            bb_col4.info("➡️ NEUTRAL")

        st_col1, st_col2 = st.columns(2)
        st_dir = int(latest["ST_DIRECTION"])
        st_col1.metric("SUPERTREND", round(float(latest["SUPERTREND"]), 2))
        if st_dir == 1:
            st_col2.success("🚀 SUPERTREND: BUY")
        elif st_dir == -1:
            st_col2.error("🔻 SUPERTREND: SELL")
        else:
            st_col2.warning("⚠️ SUPERTREND: NEUTRAL")

        # Bollinger Chart
        fig_bb = go.Figure()
        fig_bb.add_trace(go.Candlestick(
            x=data.index, open=data["Open"],
            high=data["High"], low=data["Low"],
            close=data["Close"], name="PRICE",
            increasing_line_color="#22c55e",
            decreasing_line_color="#ef4444"
        ))
        fig_bb.add_trace(go.Scatter(x=data.index, y=data["BB_UPPER"], mode="lines", name="BB Upper", line=dict(color="#f59e0b", width=1, dash="dash")))
        fig_bb.add_trace(go.Scatter(x=data.index, y=data["BB_MID"], mode="lines", name="BB Mid", line=dict(color="#94a3b8", width=1)))
        fig_bb.add_trace(go.Scatter(x=data.index, y=data["BB_LOWER"], mode="lines", name="BB Lower", line=dict(color="#f59e0b", width=1, dash="dash"),
            fill="tonexty", fillcolor="rgba(245, 158, 11, 0.05)"))

        # Supertrend overlay
        st_buy = data[data["ST_DIRECTION"] == 1]["SUPERTREND"]
        st_sell = data[data["ST_DIRECTION"] == -1]["SUPERTREND"]

        fig_bb.add_trace(go.Scatter(x=st_buy.index, y=st_buy, mode="lines", name="Supertrend BUY", line=dict(color="#22c55e", width=2)))
        fig_bb.add_trace(go.Scatter(x=st_sell.index, y=st_sell, mode="lines", name="Supertrend SELL", line=dict(color="#ef4444", width=2)))

        fig_bb.update_layout(
            template="plotly_dark",
            height=700,
            xaxis_rangeslider_visible=False,
            plot_bgcolor="#0d1117",
            paper_bgcolor="#0d1117",
            title=f"{selected_stock} — Bollinger Bands + Supertrend",
            font=dict(family="Exo 2")
        )
        st.plotly_chart(fig_bb, use_container_width=True)

        # BB Width (Squeeze indicator)
        fig_bw = go.Figure()
        fig_bw.add_trace(go.Scatter(x=data.index, y=data["BB_WIDTH"], mode="lines", name="BB Width", line=dict(color="#60a5fa", width=2), fill="tozeroy", fillcolor="rgba(96, 165, 250, 0.1)"))
        fig_bw.update_layout(template="plotly_dark", height=200, title="BB Width (Squeeze Detector)", paper_bgcolor="#0d1117", plot_bgcolor="#0d1117")
        st.plotly_chart(fig_bw, use_container_width=True)

    else:
        st.error("❌ Data లేదు.")

# =========================================================
# TAB 3 — OPTION CHAIN (FIXED)
# =========================================================

with tab3:
    st.header("📂 LIVE OPTION CHAIN")

    option_symbol = st.selectbox("SELECT INDEX", ["NIFTY", "BANKNIFTY"])

    with st.spinner("🔄 NSE data load అవుతోంది..."):
        option_df, data_source = get_option_chain(option_symbol)

    if data_source == "demo":
        st.warning("⚠️ NSE live data అందుబాటులో లేదు (Rate limit/block). Demo data చూపిస్తున్నాం. Market hours లో try చేయండి.")
    else:
        st.success("✅ NSE Live Data")

    if not option_df.empty:
        total_call = option_df["CALL_OI"].sum()
        total_put = option_df["PUT_OI"].sum()
        pcr = total_put / total_call if total_call > 0 else 0

        support = option_df.loc[option_df["PUT_OI"].idxmax(), "STRIKE"]
        resistance = option_df.loc[option_df["CALL_OI"].idxmax(), "STRIKE"]

        option_df["TOTAL_OI"] = option_df["CALL_OI"] + option_df["PUT_OI"]
        max_pain = option_df.loc[option_df["TOTAL_OI"].idxmax(), "STRIKE"]

        # PCR Signal
        if pcr > 1.15:
            st.success(f"🚀 BULLISH SENTIMENT | PCR: {round(pcr,2)}")
        elif pcr < 0.85:
            st.error(f"🔻 BEARISH SENTIMENT | PCR: {round(pcr,2)}")
        else:
            st.warning(f"⚠️ SIDEWAYS | PCR: {round(pcr,2)}")

        m1, m2, m3, m4, m5, m6 = st.columns(6)
        m1.metric("PCR", round(pcr, 2))
        m2.metric("SUPPORT", int(support))
        m3.metric("RESISTANCE", int(resistance))
        m4.metric("MAX PAIN", int(max_pain))
        m5.metric("TOTAL CALL OI", f"{int(total_call):,}")
        m6.metric("TOTAL PUT OI", f"{int(total_put):,}")

        # OI Chart
        fig_oi = go.Figure()
        fig_oi.add_trace(go.Bar(x=option_df["STRIKE"], y=option_df["CALL_OI"], name="CALL OI", marker_color="#ef4444"))
        fig_oi.add_trace(go.Bar(x=option_df["STRIKE"], y=option_df["PUT_OI"], name="PUT OI", marker_color="#22c55e"))
        fig_oi.update_layout(
            template="plotly_dark",
            barmode="group",
            height=500,
            title="OI ANALYSIS",
            paper_bgcolor="#0d1117",
            plot_bgcolor="#0d1117",
            font=dict(family="Exo 2")
        )
        st.plotly_chart(fig_oi, use_container_width=True)

        # Change in OI
        fig_chg = go.Figure()
        fig_chg.add_trace(go.Bar(x=option_df["STRIKE"], y=option_df["CALL_CHG_OI"], name="CALL CHG OI", marker_color="#f87171"))
        fig_chg.add_trace(go.Bar(x=option_df["STRIKE"], y=option_df["PUT_CHG_OI"], name="PUT CHG OI", marker_color="#4ade80"))
        fig_chg.update_layout(
            template="plotly_dark",
            barmode="group",
            height=400,
            title="CHANGE IN OI",
            paper_bgcolor="#0d1117",
            plot_bgcolor="#0d1117"
        )
        st.plotly_chart(fig_chg, use_container_width=True)

        st.dataframe(option_df, use_container_width=True)

# =========================================================
# TAB 4 — AI SCANNER
# =========================================================

with tab4:
    st.header("🤖 AI NSE SCANNER")

    scan_category = st.selectbox(
        "Scan Category",
        ["Large Cap (Fast)", "Banking", "IT", "Adani Group", "Tata Group", "All Stocks (Slow)"]
    )

    scan_map = {
        "Large Cap (Fast)": category_filters["Large Cap"],
        "Banking": category_filters["Banking"],
        "IT": category_filters["IT"],
        "Adani Group": category_filters["Adani Group"],
        "Tata Group": category_filters["Tata Group"],
        "All Stocks (Slow)": list(nse_stocks.keys()),
    }

    stocks_to_scan = {k: v for k, v in nse_stocks.items() if k in scan_map[scan_category]}

    if st.button("▶ START AI SCAN"):
        results = []
        progress = st.progress(0)
        total = len(stocks_to_scan)
        status_text = st.empty()

        def scan_stock(item):
            name, symbol = item
            try:
                df = load_market_data(symbol, "15m", "5d")
                if df.empty:
                    return None
                df = calculate_indicators(df)
                latest = df.iloc[-1]
                signal, score, confidence, _ = generate_signal(latest)
                return {
                    "STOCK": name,
                    "PRICE": round(float(latest["Close"]), 2),
                    "RSI": round(float(latest["RSI"]), 2),
                    "MACD": round(float(latest["MACD"]), 4),
                    "BB_SIGNAL": str(latest["BB_SIGNAL"]),
                    "SUPERTREND": "BUY" if int(latest["ST_DIRECTION"]) == 1 else "SELL",
                    "SIGNAL": signal,
                    "CONFIDENCE": confidence,
                    "SCORE": score
                }
            except:
                return None

        with ThreadPoolExecutor(max_workers=8) as executor:
            for idx, result in enumerate(executor.map(scan_stock, stocks_to_scan.items())):
                if result:
                    results.append(result)
                progress.progress((idx + 1) / total)
                status_text.text(f"Scanning... {idx+1}/{total}")

        status_text.empty()
        progress.empty()

        scan_df = pd.DataFrame(results)

        if not scan_df.empty:
            scan_df = scan_df.sort_values(by="CONFIDENCE", ascending=False)

            # Filter tabs
            f1, f2, f3 = st.tabs(["🚀 ALL", "✅ BUY SIGNALS", "🔻 SELL SIGNALS"])
            with f1:
                st.dataframe(scan_df, use_container_width=True)
            with f2:
                st.dataframe(scan_df[scan_df["SIGNAL"].str.contains("BUY")], use_container_width=True)
            with f3:
                st.dataframe(scan_df[scan_df["SIGNAL"].str.contains("SELL")], use_container_width=True)

            # DOWNLOAD
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
                scan_df.to_excel(writer, index=False)

            st.download_button(
                label="📥 DOWNLOAD AI SCANNER EXCEL",
                data=excel_buffer.getvalue(),
                file_name="NSE_AI_SCANNER_V10.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")
st.markdown("""
<div style='text-align:center; color: #475569; font-size: 0.8rem; letter-spacing: 2px;'>
    🚀 NSE AI PRO MAX V10.0 ULTRA &nbsp;|&nbsp; NIFTY 500 Edition &nbsp;|&nbsp; 
    Bollinger Bands + Supertrend + Option Chain
    <br><br>
    <span style='color: #ef4444;'>⚠️ DISCLAIMER: Educational purpose only. Not SEBI registered advice.</span>
</div>
""", unsafe_allow_html=True)
