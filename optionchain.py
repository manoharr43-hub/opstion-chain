# =========================================================
# 🚀 NSE AI PRO MAX V4.1 - ULTRA STABLE ENGINE
# =========================================================

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import pytz
from datetime import datetime

# =========================================================
# OPTIONAL AUTO REFRESH
# =========================================================

try:
    from streamlit_autorefresh import st_autorefresh
except:
    st_autorefresh = None

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="NSE AI PRO MAX V4.1",
    page_icon="🚀",
    layout="wide"
)

# =========================================================
# DARK UI
# =========================================================

st.markdown("""
<style>

.main {
    background-color: #0E1117;
    color: white;
}

[data-testid="stSidebar"] {
    background-color: #111827;
}

.stMetric {
    background-color: #1F2937;
    padding: 15px;
    border-radius: 12px;
    border: 1px solid #374151;
}

h1,h2,h3,h4 {
    color: white !important;
}

div.stButton > button:first-child {
    background-color: #2563EB;
    color: white;
    border-radius: 8px;
    border: none;
    font-weight: bold;
    width: 100%;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# HEADER
# =========================================================

st.title("🚀 NSE AI PRO MAX V4.1")
st.caption("Institutional Quant AI Dashboard + Option Chain Intelligence")

# =========================================================
# NSE STOCK LIST
# =========================================================

nse_stocks = {
    "RELIANCE": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "INFY": "INFY.NS",
    "HDFCBANK": "HDFCBANK.NS",
    "ICICIBANK": "ICICIBANK.NS",
    "SBIN": "SBIN.NS",
    "LT": "LT.NS",
    "ITC": "ITC.NS",
    "AXISBANK": "AXISBANK.NS",
    "KOTAKBANK": "KOTAKBANK.NS",
    "BAJFINANCE": "BAJFINANCE.NS",
    "SUNPHARMA": "SUNPHARMA.NS",
    "MARUTI": "MARUTI.NS",
    "HINDUNILVR": "HINDUNILVR.NS",
    "NIFTY 50": "^NSEI",
    "BANKNIFTY": "^NSEBANK"
}

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.header("⚙️ CONTROL PANEL")

selected_stock = st.sidebar.selectbox(
    "SELECT STOCK",
    list(nse_stocks.keys())
)

interval = st.sidebar.selectbox(
    "TIMEFRAME",
    ["5m", "15m", "30m", "1h"]
)

period = st.sidebar.selectbox(
    "PERIOD",
    ["1d", "5d", "1mo"]
)

ticker = nse_stocks[selected_stock]

# =========================================================
# AUTO REFRESH
# =========================================================

if st_autorefresh:
    st_autorefresh(interval=60000, key="refresh")
    st.sidebar.success("🟢 LIVE AUTO REFRESH ACTIVE")
else:
    st.sidebar.warning("⚠️ Install streamlit-autorefresh")

# =========================================================
# TIMEZONE
# =========================================================

india_tz = pytz.timezone("Asia/Kolkata")

st.sidebar.info(
    datetime.now(india_tz).strftime(
        "🕒 %d-%m-%Y %H:%M:%S IST"
    )
)

# =========================================================
# MARKET STATUS
# =========================================================

current_hour = datetime.now(india_tz).hour

if 9 <= current_hour <= 15:
    st.sidebar.success("🟢 MARKET OPEN")
else:
    st.sidebar.error("🔴 MARKET CLOSED")

# =========================================================
# INDICATOR ENGINE
# =========================================================

def calculate_indicators(df):

    df = df.copy()

    # EMA

    df["EMA20"] = df["Close"].ewm(
        span=20,
        adjust=False
    ).mean()

    df["EMA50"] = df["Close"].ewm(
        span=50,
        adjust=False
    ).mean()

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

    # VWAP

    df["VWAP"] = (
        (df["Close"] * df["Volume"]).cumsum()
        /
        (df["Volume"].cumsum() + 1e-10)
    )

    df = df.fillna(method="bfill")
    df = df.fillna(0)

    return df

# =========================================================
# AI SIGNAL ENGINE
# =========================================================

def generate_signal(latest):

    score = 0

    # EMA

    if latest["EMA20"] > latest["EMA50"]:
        score += 25
    else:
        score -= 25

    # RSI

    if 55 <= latest["RSI"] <= 70:
        score += 20

    elif latest["RSI"] > 75:
        score -= 15

    elif latest["RSI"] < 30:
        score += 15

    # MACD

    if latest["MACD"] > latest["MACD_SIGNAL"]:
        score += 25
    else:
        score -= 25

    # VWAP

    if latest["Close"] > latest["VWAP"]:
        score += 20
    else:
        score -= 20

    # SIGNAL

    if score >= 70:
        return "🚀 STRONG BUY", score

    elif score >= 30:
        return "✅ BUY", score

    elif score <= -70:
        return "🚨 STRONG SELL", score

    elif score <= -30:
        return "🔻 SELL", score

    return "⚠️ SIDEWAYS", score

# =========================================================
# TABS
# =========================================================

tab1, tab2 = st.tabs([
    "📈 LIVE TECHNICAL DASHBOARD",
    "📂 OPTION CHAIN ANALYZER"
])

# =========================================================
# TAB 1
# =========================================================

with tab1:

    try:

        data = yf.download(
            ticker,
            interval=interval,
            period=period,
            progress=False,
            auto_adjust=True,
            threads=True
        )

        if data.empty:
            st.error("❌ No market data found.")
            st.stop()

        # MultiIndex Fix

        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        data = calculate_indicators(data)

        latest = data.iloc[-1]

        signal, score = generate_signal(latest)

        # =====================================================
        # SIGNAL DISPLAY
        # =====================================================

        st.subheader("🤖 AI QUANT SIGNAL")

        if "BUY" in signal:
            st.success(f"{signal} | SCORE = {score}")

        elif "SELL" in signal:
            st.error(f"{signal} | SCORE = {score}")

        else:
            st.warning(f"{signal} | SCORE = {score}")

        # =====================================================
        # METRICS
        # =====================================================

        c1, c2, c3, c4, c5 = st.columns(5)

        c1.metric(
            "PRICE",
            f"₹ {round(float(latest['Close']),2)}"
        )

        c2.metric(
            "RSI",
            round(float(latest["RSI"]),2)
        )

        c3.metric(
            "VWAP",
            round(float(latest["VWAP"]),2)
        )

        c4.metric(
            "MACD",
            round(float(latest["MACD"]),2)
        )

        c5.metric(
            "AI SCORE",
            score
        )

        # =====================================================
        # CHART
        # =====================================================

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=data.index,
            y=data["Close"],
            mode="lines",
            name="PRICE"
        ))

        fig.add_trace(go.Scatter(
            x=data.index,
            y=data["EMA20"],
            mode="lines",
            name="EMA20"
        ))

        fig.add_trace(go.Scatter(
            x=data.index,
            y=data["EMA50"],
            mode="lines",
            name="EMA50"
        ))

        fig.update_layout(
            template="plotly_dark",
            height=550,
            hovermode="x unified"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    except Exception as e:
        st.error(f"🔴 LIVE ENGINE ERROR : {e}")

# =========================================================
# TAB 2 - OPTION CHAIN ANALYZER
# =========================================================

with tab2:

    st.header("📂 NSE OPTION CHAIN ANALYZER")

    uploaded_file = st.file_uploader(
        "UPLOAD NSE OPTION CHAIN FILE",
        type=["csv", "xlsx", "xls"]
    )

    # =====================================================
    # SAFE NUMERIC CONVERTER
    # =====================================================

    def clean_numeric(series):

        return pd.to_numeric(
            series.astype(str)
            .str.replace(",", "")
            .str.replace("--", "0")
            .str.strip(),
            errors="coerce"
        ).fillna(0)

    # =====================================================
    # FILE PROCESS
    # =====================================================

    if uploaded_file is not None:

        try:

            # =================================================
            # READ FILE
            # =================================================

            if uploaded_file.name.endswith(".csv"):

                raw_df = pd.read_csv(
                    uploaded_file,
                    header=None,
                    engine="python",
                    on_bad_lines="skip"
                )

            else:

                raw_df = pd.read_excel(
                    uploaded_file,
                    header=None
                )

            # =================================================
            # EMPTY CHECK
            # =================================================

            if raw_df.empty:
                st.error("❌ EMPTY FILE")
                st.stop()

            # =================================================
            # HEADER DETECTION
            # =================================================

            header_idx = 0
            best_score = 0

            for i in range(min(20, len(raw_df))):

                row = raw_df.iloc[i].astype(str)

                score = (
                    row.str.contains(
                        "OI|STRIKE|VOLUME|PRICE",
                        case=False,
                        regex=True
                    ).sum()
                )

                if score > best_score:
                    best_score = score
                    header_idx = i

            # =================================================
            # CREATE DATAFRAME
            # =================================================

            headers = raw_df.iloc[header_idx].astype(str)

            headers = [
                h.strip().upper().replace(" ", "_")
                for h in headers
            ]

            # DUPLICATE FIX

            unique_headers = []
            counts = {}

            for h in headers:

                if h in counts:
                    counts[h] += 1
                    h = f"{h}_{counts[h]}"
                else:
                    counts[h] = 0

                unique_headers.append(h)

            data_df = raw_df.iloc[header_idx + 1:].copy()

            data_df.columns = unique_headers

            data_df.dropna(
                how="all",
                inplace=True
            )

            data_df.reset_index(
                drop=True,
                inplace=True
            )

            # =================================================
            # STRIKE DETECTION
            # =================================================

            strike_col = next(
                (
                    c for c in data_df.columns
                    if "STRIKE" in c
                ),
                data_df.columns[0]
            )

            call_col = next(
                (
                    c for c in data_df.columns
                    if "OI" in c
                ),
                data_df.columns[1]
            )

            put_col = next(
                (
                    c for c in reversed(data_df.columns)
                    if "OI" in c
                ),
                data_df.columns[-1]
            )

            # =================================================
            # COLUMN UI
            # =================================================

            c1, c2, c3 = st.columns(3)

            selected_strike = c1.selectbox(
                "STRIKE",
                data_df.columns,
                index=list(data_df.columns).index(strike_col)
            )

            selected_call = c2.selectbox(
                "CALL OI",
                data_df.columns,
                index=list(data_df.columns).index(call_col)
            )

            selected_put = c3.selectbox(
                "PUT OI",
                data_df.columns,
                index=list(data_df.columns).index(put_col)
            )

            # =================================================
            # SHOW DATA
            # =================================================

            with st.expander("📊 VIEW CLEANED DATA"):

                st.dataframe(
                    data_df.head(20),
                    use_container_width=True
                )

            # =================================================
            # EXECUTION
            # =================================================

            if st.button("🚀 EXECUTE AI OPTION ANALYSIS"):

                strikes = clean_numeric(
                    data_df[selected_strike]
                )

                call_oi = clean_numeric(
                    data_df[selected_call]
                )

                put_oi = clean_numeric(
                    data_df[selected_put]
                )

                valid_mask = (
                    (strikes > 0)
                )

                strikes = strikes[valid_mask].reset_index(drop=True)
                call_oi = call_oi[valid_mask].reset_index(drop=True)
                put_oi = put_oi[valid_mask].reset_index(drop=True)

                # =============================================
                # EMPTY CHECK
                # =============================================

                if len(strikes) == 0:
                    st.error("❌ NO VALID STRIKE DATA")
                    st.stop()

                # =============================================
                # PCR
                # =============================================

                total_call = call_oi.sum()
                total_put = put_oi.sum()

                pcr = (
                    total_put / total_call
                    if total_call > 0
                    else 0
                )

                # =============================================
                # SUPPORT / RESISTANCE
                # =============================================

                support_idx = put_oi.idxmax()
                resistance_idx = call_oi.idxmax()

                support = strikes.iloc[support_idx]
                resistance = strikes.iloc[resistance_idx]

                # =============================================
                # SIGNAL
                # =============================================

                if pcr > 1.15:
                    signal = "🚀 BULLISH"

                elif pcr < 0.85:
                    signal = "🔻 BEARISH"

                else:
                    signal = "⚠️ SIDEWAYS"

                # =============================================
                # REPORT
                # =============================================

                st.subheader("🤖 OPTION CHAIN REPORT")

                if "BULLISH" in signal:
                    st.success(signal)

                elif "BEARISH" in signal:
                    st.error(signal)

                else:
                    st.warning(signal)

                m1, m2, m3, m4 = st.columns(4)

                m1.metric(
                    "PCR",
                    round(pcr, 2)
                )

                m2.metric(
                    "SUPPORT",
                    f"₹ {int(support)}"
                )

                m3.metric(
                    "RESISTANCE",
                    f"₹ {int(resistance)}"
                )

                m4.metric(
                    "TOTAL OI",
                    f"{int(total_call + total_put):,}"
                )

                # =============================================
                # CHART
                # =============================================

                fig2 = go.Figure()

                fig2.add_trace(go.Bar(
                    x=strikes,
                    y=call_oi,
                    name="CALL OI"
                ))

                fig2.add_trace(go.Bar(
                    x=strikes,
                    y=put_oi,
                    name="PUT OI"
                ))

                fig2.update_layout(
                    template="plotly_dark",
                    barmode="group",
                    height=550,
                    title="OI WALL ANALYSIS"
                )

                st.plotly_chart(
                    fig2,
                    use_container_width=True
                )

                # =============================================
                # DOWNLOAD CLEAN DATA
                # =============================================

                csv = data_df.to_csv(index=False)

                st.download_button(
                    "📥 DOWNLOAD CLEAN DATA",
                    csv,
                    file_name="clean_option_chain.csv",
                    mime="text/csv"
                )

        except Exception as e:

            st.error(f"🔴 OPTION ENGINE ERROR : {e}")

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption(
    "🚀 NSE AI PRO MAX V4.1 | Institutional AI Quant Engine"
)
