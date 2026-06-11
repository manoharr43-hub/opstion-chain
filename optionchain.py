



102b1fd5-7ac3-4a81-9453-926dcda2d0e5.png

70595d0e-7d48-4c85-b885-8e2b9c176c45.png

5a208d04-c537-4550-b793-a011aa40c158.png

మీ app లో ఒక్క stock మాత్రమే show అవుతోంది అంటే కారణం సాధారణంగా ఇది:

మీ code లో ఎక్కడో ఇలా ఉంది:

selected_stocks = ["AAVAS"]
లేదా

selected_stocks = stocks[:1]
లేదా test కోసం పెట్టిన:

scan_stock("AAVAS")
ఇంకా remove చేయలేదు.

Fix
PART 3 లో ఈ section check చేయండి:

if sector == "All NSE500":
    selected_stocks = stocks
else:
    selected_stocks = sector_stocks[sector]
ఇది ఉండాలి.

Debug
RUN SCAN ముందు ఇది add చేయండి:

st.write("Total Stocks:", len(selected_stocks))
st.write(selected_stocks[:10])
Output:

Total Stocks: 500
లేదా

Total Stocks: 1
['AAVAS']
వస్తుంది.

ఇంకా ముఖ్యమైనది
మీ screenshot లో:

Strong Buy = 0
Buy = 0
Sell = 0
అంటే stock count problem మాత్రమే కాదు, scanner results కూడా empty ఉన్నాయి.

దయచేసి app.py లో ఈ block పంపండి:

if sector == "All NSE500":
    ...
నుండి

result_df = pd.DataFrame(results)
వరకు.

అప్పుడు ఎందుకు ఒక్క stock మాత్రమే వస్తుందో exact line చెబుతాను.



Pasted text.txt
Document

మీ code మొత్తం చూసాను. సమస్య PART 2 లో ఉంది.

Problem #1 (Major Bug)
scan_stock() లో:

latest = df.iloc[-1]

result = {
    "RSI": round(float(latest["RSI"]),2),
}
కానీ latest row లో RSI NaN ఉండొచ్చు.

Problem #2 (Main Reason Empty Results)
ఈ line:

if len(df) < 60:
    return pd.DataFrame()
15m + 5d data లో కొన్ని stocks కి 60 candles రావు.

మార్చండి:

if len(df) < 20:
    return pd.DataFrame()
Problem #3 (Error Hidden)
ప్రస్తుతం:

except:
    return None
అన్ని errors hide అవుతున్నాయి.

మార్చండి:

except Exception as e:
    st.error(f"{symbol}: {e}")
    return None
Problem #4 (NSE500 URL)
ఈ URL ఇప్పుడు చాలాసార్లు fail అవుతోంది:

https://archives.nseindia.com/content/indices/ind_nifty500list.csv
Test కోసం ఇలా పెట్టండి:

stocks = [
    "RELIANCE",
    "TCS",
    "INFY",
    "HDFCBANK",
    "ICICIBANK",
    "SBIN",
    "ITC",
    "LT",
    "AAVAS"
]
Problem #5 (Data Check)
get_data() తర్వాత add చేయండి:

required_cols = [
    "Open",
    "High",
    "Low",
    "Close",
    "Volume"
]

if not all(col in df.columns for col in required_cols):
    return pd.DataFrame()
Quick Test
scan_stock() చివర:

st.write(result)
return result
పెట్టండి.

Run Scan నొక్కినప్పుడు output వస్తే scanner OK.

Most Likely Fix
ఈ ఒక్క మార్పు ముందుగా చేయండి:

def add_indicators(df):

    if len(df) < 20:
        return pd.DataFrame()
మరియు

Period = 1mo
ఎంచుకోండి.

ఇప్పుడు results వచ్చే అవకాశం చాలా ఎక్కువ.

ఇంకా సమస్య ఉంటే scan_stock() లో error print చేసిన తర్వాత వచ్చిన exact error message పంపండి. అప్పుడు final corrected V7 code ఇస్తాను.


final corrected V7 code ఇస్తాను.

మీ code లో పెద్ద సమస్య ఏమిటంటే except: return None వల్ల అసలు errors కనిపించడం లేదు. అలాగే yfinance 15m data, NSE500 symbols, NaN RSI issues వల్ల results empty వస్తున్నాయి.

వెంటనే మార్చాల్సిన 5 fixes
1. add_indicators()
def add_indicators(df):

    if len(df) < 20:
        return pd.DataFrame()

    df = df.copy()

    df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
    df["EMA50"] = df["Close"].ewm(span=50, adjust=False).mean()
    df["RSI"] = calculate_rsi(df)
    df["AVG_VOL"] = df["Volume"].rolling(20).mean()

    return df
2. get_data()
def get_data(symbol, interval, period):

    try:
        df = yf.download(
            f"{symbol}.NS",
            interval=interval,
            period=period,
            auto_adjust=True,
            progress=False
        )

        if df.empty:
            return pd.DataFrame()

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        required = ["Open","High","Low","Close","Volume"]

        for col in required:
            if col not in df.columns:
                return pd.DataFrame()

        return df

    except Exception as e:
        st.error(f"{symbol}: {e}")
        return pd.DataFrame()
3. scan_stock()
def scan_stock(symbol):

    try:

        df = get_data(symbol, interval, period)

        if df.empty:
            return None

        df = add_indicators(df)

        if df.empty:
            return None

        latest = df.iloc[-1]

        if pd.isna(latest["RSI"]):
            return None

        score = calculate_score(df)

        return {
            "Stock": symbol,
            "Price": round(float(latest["Close"]),2),
            "EMA": ema_signal(df),
            "RSI": round(float(latest["RSI"]),2),
            "Breakout": breakout_signal(df),
            "Volume": volume_signal(df),
            "Score": score,
            "Signal": final_signal(score)
        }

    except Exception as e:
        st.error(f"{symbol}: {e}")
        return None
4. Test Mode
ముందు NSE500 కాకుండా:

selected_stocks = [
    "RELIANCE",
    "TCS",
    "INFY",
    "SBIN",
    "HDFCBANK",
    "AAVAS"
]
తో test చేయండి.

5. Settings
Interval = 15m
Period = 1mo

RSI Upper = 70
RSI Lower = 30

Volume Spike = 1.5
Breakout Window = 20

Show Strong Buy Only = OFF
Auto Refresh = OFF
ఒక ముఖ్యమైన bug
మీ code లో:

if show_strong_only:
    result_df = result_df[
        result_df["Signal"] == "STRONG BUY"
    ]
దీంతో table ఖాళీ అవుతుంది.

Testing సమయంలో:

show_strong_only = False
పెట్టండి.

Result
ఈ fixes తర్వాత:

Top 20 Opportunities show అవుతుంది

RSI Avg NaN పోతుంది

AAVAS మాత్రమే కాకుండా అన్ని scanned stocks వస్తాయి

Excel download పని చేస్తుంది

Empty table సమస్య తొలగిపోతుంది

మొదట ఈ fixes apply చేసి run చేయండి. Logs లో కొత్త error వస్తే ఆ error text పంపండి.


TOTAL NEW CODE GENRAT CHAYE

మీ codeలో చాలా issues ఉన్నాయి. అందుకే patchలు కాకుండా కొత్త clean V7 scanner architecture తో మొదలుపెట్టడం మంచిది.

కానీ "TOTAL NEW CODE" అంటే 400–700+ lines Streamlit application అవుతుంది. ఒకే replyలో అంత పెద్ద code ఇస్తే message truncate అయ్యే అవకాశం ఉంది మరియు copy-paste errors రావచ్చు.

అందుకే నేను పూర్తి code ఇవ్వడానికి ముందు ఈ 2 విషయాలు confirm చేయాలి:

V7 Features
NSE500 Full Scan

yfinance only

EMA20 / EMA50

RSI

Volume Spike

Breakout Detection

Top 20 Opportunities

Excel Download

Market Status

Multi-thread Scan

Sector Filter

Charts కూడా కావాలా?
Yes → Plotly charts

No → Scanner only

Deployment
Streamlit Cloud

Local PC

Replit

Reply:

YES CHARTS
STREAMLIT CLOUD
లేదా

NO CHARTS
STREAMLIT CLOUD
అంటే నేను పూర్తిగా కొత్త single-file V7 code structure ఇస్తాను.


==========================================================
🚀 HYBRID NSE PRO SCANNER V7
PART 1
==========================================================
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import pytz
import time

from io import BytesIO
from datetime import datetime
from concurrent.futures import (
ThreadPoolExecutor,
as_completed
)

==========================================================
PAGE CONFIG
==========================================================
st.set_page_config(
page_title="HYBRID NSE PRO SCANNER V7",
layout="wide"
)

==========================================================
TITLE
==========================================================
st.title("🚀 HYBRID NSE PRO SCANNER V7")

st.caption(
"EMA + RSI + Volume + Breakout + Institutional Scoring"
)

==========================================================
NSE500 LOADER
==========================================================
@st.cache_data(ttl=86400)
def load_nse500():

try:

    url = (
        "https://archives.nseindia.com/content/"
        "indices/ind_nifty500list.csv"
    )

    df = pd.read_csv(url)

    stocks = (
        df["Symbol"]
        .dropna()
        .unique()
        .tolist()
    )

    stocks = sorted(stocks)

    return stocks

except:

    return [
        "RELIANCE",
        "TCS",
        "INFY",
        "HDFCBANK",
        "ICICIBANK",
        "SBIN",
        "ITC",
        "LT"
    ]
stocks = load_nse500()

==========================================================
SECTOR WATCHLISTS
==========================================================
sector_stocks = {

"Banking": [
    "HDFCBANK",
    "ICICIBANK",
    "SBIN",
    "AXISBANK",
    "KOTAKBANK"
],

"IT": [
    "TCS",
    "INFY",
    "WIPRO",
    "HCLTECH",
    "TECHM"
],

"Pharma": [
    "SUNPHARMA",
    "CIPLA",
    "DIVISLAB",
    "DRREDDY"
],

"Energy": [
    "RELIANCE",
    "ONGC",
    "BPCL",
    "NTPC"
],

"Auto": [
    "TATAMOTORS",
    "M&M",
    "EICHERMOT",
    "HEROMOTOCO"
],

"FMCG": [
    "ITC",
    "HINDUNILVR",
    "BRITANNIA",
    "DABUR"
]
}

==========================================================
MARKET STATUS
==========================================================
ist = pytz.timezone("Asia/Kolkata")

now = datetime.now(ist)

market_open = (
now.weekday() < 5
and
now.strftime("%H:%M") >= "09:15"
and
now.strftime("%H:%M") <= "15:30"
)

if market_open:

st.success(
    f"🟢 MARKET OPEN | {now.strftime('%d-%b-%Y %I:%M:%S %p')}"
)
else:

st.error(
    f"🔴 MARKET CLOSED | {now.strftime('%d-%b-%Y %I:%M:%S %p')}"
)
==========================================================
SIDEBAR SETTINGS
==========================================================
st.sidebar.header("⚙️ Scanner Settings")

interval = st.sidebar.selectbox(
"Interval",
[
"5m",
"15m",
"30m",
"60m",
"1d"
],
index=1
)

period = st.sidebar.selectbox(
"Period",
[
"5d",
"1mo",
"3mo",
"6mo"
],
index=1
)

sector = st.sidebar.selectbox(
"Sector",
list(sector_stocks.keys())
+ ["All NSE500"]
)

rsi_upper = st.sidebar.slider(
"RSI Upper",
50,
90,
70
)

rsi_lower = st.sidebar.slider(
"RSI Lower",
10,
50,
30
)

vol_multiplier = st.sidebar.slider(
"Volume Spike Multiplier",
1.0,
5.0,
1.5
)

breakout_window = st.sidebar.slider(
"Breakout Window",
10,
50,
20
)

show_strong_only = st.sidebar.checkbox(
"Show Strong Buy Only"
)

auto_refresh = st.sidebar.checkbox(
"Auto Refresh"
)

==========================================================
AUTO REFRESH
==========================================================
if auto_refresh:

st.warning(
    "Auto Refresh Enabled"
)

time.sleep(60)

st.rerun()# ==========================================================
PART 2
DATA FETCH + INDICATORS + SCORE ENGINE
==========================================================
==========================================================
DATA FETCH
==========================================================
@st.cache_data(ttl=300)
def get_data(symbol, interval, period):

try:

    df = yf.download(
        f"{symbol}.NS",
        interval=interval,
        period=period,
        auto_adjust=True,
        progress=False,
        threads=False
    )

    if df is None:
        return pd.DataFrame()

    if len(df) == 0:
        return pd.DataFrame()

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    return df

except:
    return pd.DataFrame()
==========================================================
RSI CALCULATION
==========================================================
def calculate_rsi(df, period=14):

delta = df["Close"].diff()

gain = delta.where(
    delta > 0,
    0
)

loss = -delta.where(
    delta < 0,
    0
)

avg_gain = gain.rolling(
    period
).mean()

avg_loss = loss.rolling(
    period
).mean()

rs = avg_gain / avg_loss

rsi = 100 - (
    100 / (1 + rs)
)

return rsi
==========================================================
INDICATORS
==========================================================
def add_indicators(df):

if len(df) < 60:
    return pd.DataFrame()

df = df.copy()

df["EMA20"] = (
    df["Close"]
    .ewm(span=20, adjust=False)
    .mean()
)

df["EMA50"] = (
    df["Close"]
    .ewm(span=50, adjust=False)
    .mean()
)

df["RSI"] = calculate_rsi(df)

df["AVG_VOL"] = (
    df["Volume"]
    .rolling(20)
    .mean()
)

return df
==========================================================
BREAKOUT DETECTION
==========================================================
def breakout_signal(df):

try:

    latest_close = float(
        df["Close"].iloc[-1]
    )

    breakout_high = (
        df["High"]
        .rolling(breakout_window)
        .max()
        .shift(1)
        .iloc[-1]
    )

    breakout_low = (
        df["Low"]
        .rolling(breakout_window)
        .min()
        .shift(1)
        .iloc[-1]
    )

    if pd.isna(breakout_high):
        return "NO"

    if latest_close > breakout_high:
        return "BULLISH"

    if latest_close < breakout_low:
        return "BEARISH"

    return "NO"

except:
    return "NO"
==========================================================
VOLUME SPIKE
==========================================================
def volume_signal(df):

try:

    avg_vol = float(
        df["AVG_VOL"].iloc[-1]
    )

    current_vol = float(
        df["Volume"].iloc[-1]
    )

    if avg_vol <= 0:
        return "NO"

    if current_vol > (
        avg_vol * vol_multiplier
    ):
        return "SPIKE"

    return "NO"

except:
    return "NO"
==========================================================
EMA SIGNAL
==========================================================
def ema_signal(df):

try:

    ema20 = float(
        df["EMA20"].iloc[-1]
    )

    ema50 = float(
        df["EMA50"].iloc[-1]
    )

    if ema20 > ema50:
        return "BUY"

    return "SELL"

except:
    return "WAIT"
==========================================================
RSI SIGNAL
==========================================================
def rsi_signal(df):

try:

    rsi = float(
        df["RSI"].iloc[-1]
    )

    if rsi > rsi_upper:
        return "OVERBOUGHT"

    if rsi < rsi_lower:
        return "OVERSOLD"

    return "NEUTRAL"

except:
    return "NEUTRAL"
==========================================================
INSTITUTIONAL SCORE ENGINE
==========================================================
def calculate_score(df):

score = 0

try:

    # EMA

    ema = ema_signal(df)

    if ema == "BUY":
        score += 1
    else:
        score -= 1

    # RSI

    rsi = float(
        df["RSI"].iloc[-1]
    )

    if rsi > rsi_upper:
        score += 1

    elif rsi < rsi_lower:
        score -= 1

    # BREAKOUT

    bo = breakout_signal(df)

    if bo == "BULLISH":
        score += 1

    elif bo == "BEARISH":
        score -= 1

    # VOLUME

    vol = volume_signal(df)

    if vol == "SPIKE":
        score += 1

    return score

except:
    return 0
==========================================================
FINAL SIGNAL
==========================================================
def final_signal(score):

if score >= 4:
    return "STRONG BUY"

if score == 3:
    return "BUY"

if score == 2:
    return "WATCH"

if score == 1:
    return "WAIT"

if score == 0:
    return "NEUTRAL"

if score == -1:
    return "WEAK SELL"

if score == -2:
    return "SELL"

return "STRONG SELL"
==========================================================
SINGLE STOCK SCAN
==========================================================
def scan_stock(symbol):

try:

    df = get_data(
        symbol,
        interval,
        period
    )

    if df.empty:
        return None

    df = add_indicators(df)

    if df.empty:
        return None

    score = calculate_score(df)

    signal = final_signal(score)

    latest = df.iloc[-1]

    result = {

        "Stock":
            symbol,

        "Price":
            round(
                float(latest["Close"]),
                2
            ),

        "EMA":
            ema_signal(df),

        "RSI":
            round(
                float(
                    latest["RSI"]
                ),
                2
            ),

        "Breakout":
            breakout_signal(df),

        "Volume":
            volume_signal(df),

        "Score":
            score,

        "Signal":
            signal

    }

    return result

except:
    return None# ==========================================================
PART 3
MULTI THREAD SCAN + DASHBOARD + DOWNLOAD
==========================================================
st.markdown("---")

scan_btn = st.button(
"🚀 RUN SCAN",
use_container_width=True
)

==========================================================
SCAN
==========================================================
if scan_btn:

results = []

if sector == "All NSE500":

    selected_stocks = stocks

else:

    selected_stocks = sector_stocks.get(
        sector,
        []
    )

total = len(selected_stocks)

st.info(
    f"Scanning {total} Stocks..."
)

progress_bar = st.progress(0)

status_text = st.empty()

completed = 0

max_workers = 10

with ThreadPoolExecutor(
    max_workers=max_workers
) as executor:

    futures = {

        executor.submit(
            scan_stock,
            symbol
        ): symbol

        for symbol in selected_stocks

    }

    for future in as_completed(futures):

        completed += 1

        symbol = futures[future]

        try:

            result = future.result()

            if result:

                results.append(
                    result
                )

        except:

            pass

        progress_bar.progress(
            completed / total
        )

        status_text.write(
            f"Processed {completed}/{total}"
        )

# ======================================================
# DATAFRAME
# ======================================================

result_df = pd.DataFrame(
    results
)

if result_df.empty:

    st.warning(
        "No Results Found"
    )

    st.stop()

# ======================================================
# STRONG BUY FILTER
# ======================================================

if show_strong_only:

    result_df = result_df[
        result_df["Signal"]
        == "STRONG BUY"
    ]

# ======================================================
# SORT
# ======================================================

result_df = result_df.sort_values(
    by="Score",
    ascending=False
)

# ======================================================
# METRICS
# ======================================================

st.markdown("---")

c1, c2, c3, c4 = st.columns(4)

strong_buy_count = len(
    result_df[
        result_df["Signal"]
        == "STRONG BUY"
    ]
)

buy_count = len(
    result_df[
        result_df["Signal"]
        == "BUY"
    ]
)

sell_count = len(
    result_df[
        result_df["Signal"]
        == "SELL"
    ]
)

avg_rsi = round(
    result_df["RSI"].mean(),
    2
)

c1.metric(
    "🚀 Strong Buy",
    strong_buy_count
)

c2.metric(
    "📈 Buy",
    buy_count
)

c3.metric(
    "📉 Sell",
    sell_count
)

c4.metric(
    "RSI Avg",
    avg_rsi
)

# ======================================================
# TOP 20 OPPORTUNITIES
# ======================================================

st.markdown("## 🏆 Top 20 Opportunities")

top20 = result_df.head(20)

st.dataframe(
    top20,
    use_container_width=True,
    height=500
)

# ======================================================
# FULL RESULTS
# ======================================================

st.markdown("## 📊 Full Scan Results")

st.dataframe(
    result_df,
    use_container_width=True,
    height=700
)

# ======================================================
# SIGNAL COUNTS
# ======================================================

st.markdown("## 📌 Signal Distribution")

signal_counts = (
    result_df["Signal"]
    .value_counts()
    .reset_index()
)

signal_counts.columns = [
    "Signal",
    "Count"
]

st.dataframe(
    signal_counts,
    use_container_width=True
)

# ======================================================
# STRONG BUY TABLE
# ======================================================

strong_buy_df = result_df[
    result_df["Signal"]
    == "STRONG BUY"
]

if len(strong_buy_df) > 0:

    st.markdown(
        "## 🚀 Strong Buy Stocks"
    )

    st.dataframe(
        strong_buy_df,
        use_container_width=True
    )

# ======================================================
# EXCEL DOWNLOAD
# ======================================================

excel_buffer = BytesIO()

with pd.ExcelWriter(
    excel_buffer,
    engine="openpyxl"
) as writer:

    result_df.to_excel(
        writer,
        sheet_name="Scanner",
        index=False
    )

    top20.to_excel(
        writer,
        sheet_name="Top20",
        index=False
    )

st.download_button(
    label="📥 Download Excel",
    data=excel_buffer.getvalue(),
    file_name="HYBRID_NSE_PRO_V7.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.success(
    f"✅ Scan Completed | {len(result_df)} Results"
)

Close
