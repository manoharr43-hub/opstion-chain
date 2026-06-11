# ==========================================================
# 🚀 HYBRID NSE PRO SCANNER V7
# PART 1
# ==========================================================

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

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="HYBRID NSE PRO SCANNER V7",
    layout="wide"
)

# ==========================================================
# TITLE
# ==========================================================

st.title("🚀 HYBRID NSE PRO SCANNER V7")

st.caption(
    "EMA + RSI + Volume + Breakout + Institutional Scoring"
)

# ==========================================================
# NSE500 LOADER
# ==========================================================

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

# ==========================================================
# SECTOR WATCHLISTS
# ==========================================================

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

# ==========================================================
# MARKET STATUS
# ==========================================================

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

# ==========================================================
# SIDEBAR SETTINGS
# ==========================================================

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

# ==========================================================
# AUTO REFRESH
# ==========================================================

if auto_refresh:

    st.warning(
        "Auto Refresh Enabled"
    )

    time.sleep(60)

    st.rerun()# ==========================================================
# PART 2
# DATA FETCH + INDICATORS + SCORE ENGINE
# ==========================================================

# ==========================================================
# DATA FETCH
# ==========================================================

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


# ==========================================================
# RSI CALCULATION
# ==========================================================

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


# ==========================================================
# INDICATORS
# ==========================================================

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


# ==========================================================
# BREAKOUT DETECTION
# ==========================================================

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


# ==========================================================
# VOLUME SPIKE
# ==========================================================

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


# ==========================================================
# EMA SIGNAL
# ==========================================================

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


# ==========================================================
# RSI SIGNAL
# ==========================================================

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


# ==========================================================
# INSTITUTIONAL SCORE ENGINE
# ==========================================================

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


# ==========================================================
# FINAL SIGNAL
# ==========================================================

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


# ==========================================================
# SINGLE STOCK SCAN
# ==========================================================

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
# PART 3
# MULTI THREAD SCAN + DASHBOARD + DOWNLOAD
# ==========================================================

st.markdown("---")

scan_btn = st.button(
    "🚀 RUN SCAN",
    use_container_width=True
)

# ==========================================================
# SCAN
# ==========================================================

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
