# =========================================================
# 🚀 NSE AI PRO MAX V9.0 ULTRA + SHOONYA INTEGRATION
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
import hashlib
import json

from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from streamlit_autorefresh import st_autorefresh

urllib3.disable_warnings()

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="NSE AI PRO MAX V9.0 + SHOONYA",
    page_icon="🚀",
    layout="wide"
)

# =========================================================
# AUTO REFRESH
# =========================================================

st_autorefresh(interval=60000, key="refresh")

# =========================================================
# DARK THEME
# =========================================================

st.markdown("""
<style>
.main { background-color: #0E1117; color: white; }
[data-testid="stSidebar"] { background-color: #111827; }
.stMetric {
    background-color: #1F2937;
    border: 1px solid #374151;
    border-radius: 12px;
    padding: 15px;
}
h1,h2,h3,h4 { color: white !important; }
div.stButton > button:first-child {
    background-color: #2563EB;
    color: white;
    border-radius: 10px;
    border: none;
    width: 100%;
    font-weight: bold;
}
.shoonya-box {
    background: linear-gradient(135deg, #1a2332, #1e3a5f);
    border: 1px solid #2563eb;
    border-radius: 12px;
    padding: 15px;
    margin: 10px 0;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# TITLE
# =========================================================

st.title("🚀 NSE AI PRO MAX V9.0 ULTRA")
st.caption("Institutional AI Quantitative Trading System + Shoonya Live Data")

# =========================================================
# NSE STOCK DATABASE
# =========================================================

nse_stocks = {
    "NIFTY 50": "^NSEI",
    "BANKNIFTY": "^NSEBANK",
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
    "IRCTC": "IRCTC.NS"
}

# Shoonya exchange symbol mapping (NSE)
shoonya_symbols = {
    "RELIANCE": "RELIANCE",
    "TCS": "TCS",
    "INFY": "INFY",
    "HDFCBANK": "HDFCBANK",
    "ICICIBANK": "ICICIBANK",
    "SBIN": "SBIN",
    "AXISBANK": "AXISBANK",
    "ITC": "ITC",
    "LT": "LT",
    "BHARTIARTL": "BHARTIARTL",
    "TATAMOTORS": "TATAMOTORS",
    "MARUTI": "MARUTI",
    "BAJFINANCE": "BAJFINANCE",
    "HINDUNILVR": "HINDUNILVR",
    "SUNPHARMA": "SUNPHARMA",
    "WIPRO": "WIPRO",
    "POWERGRID": "POWERGRID",
    "NTPC": "NTPC",
    "TATASTEEL": "TATASTEEL",
    "JSWSTEEL": "JSWSTEEL",
    "HINDALCO": "HINDALCO",
    "ONGC": "ONGC",
    "IOC": "IOC",
    "ZOMATO": "ZOMATO",
    "IRCTC": "IRCTC",
}

# =========================================================
# SHOONYA API CLASS
# =========================================================

class ShoonyaAPI:
    """
    Shoonya (Finvasia) REST API Integration
    Docs: https://shoonya.com/api-documentation
    """

    BASE_URL = "https://api.shoonya.com/NorenWClientTP"

    def __init__(self):
        self.session_token = None
        self.user_id = None
        self.headers = {"Content-Type": "application/x-www-form-urlencoded"}

    def login(self, user_id, password, totp, vendor_code, api_secret, imei="abc1234"):
        """
        Shoonya Login — SHA256 password hash కావాలి
        """
        try:
            pwd_hash = hashlib.sha256(password.encode()).hexdigest()
            app_key = f"{user_id}|{api_secret}"
            app_key_hash = hashlib.sha256(app_key.encode()).hexdigest()

            payload = (
                f"jData={{\"uid\":\"{user_id}\","
                f"\"pwd\":\"{pwd_hash}\","
                f"\"factor2\":\"{totp}\","
                f"\"vc\":\"{vendor_code}\","
                f"\"appkey\":\"{app_key_hash}\","
                f"\"imei\":\"{imei}\","
                f"\"source\":\"API\"}}"
            )

            response = requests.post(
                f"{self.BASE_URL}/QuickAuth",
                data=payload,
                headers=self.headers,
                timeout=15
            )

            data = response.json()

            if data.get("stat") == "Ok":
                self.session_token = data.get("susertoken")
                self.user_id = user_id
                return True, "✅ Login Successful"
            else:
                return False, f"❌ Login Failed: {data.get('emsg', 'Unknown error')}"

        except Exception as e:
            return False, f"❌ Error: {str(e)}"

    def _post(self, endpoint, jdata):
        """Internal POST helper"""
        try:
            payload = f"jData={json.dumps(jdata)}&jKey={self.session_token}"
            response = requests.post(
                f"{self.BASE_URL}/{endpoint}",
                data=payload,
                headers=self.headers,
                timeout=15
            )
            return response.json()
        except Exception as e:
            return {"stat": "Not_Ok", "emsg": str(e)}

    def get_quote(self, exchange, symbol):
        """
        Live Quote తీసుకోండి
        exchange: NSE, BSE, NFO
        """
        if not self.session_token:
            return None
        data = self._post("GetQuotes", {
            "uid": self.user_id,
            "exch": exchange,
            "token": symbol
        })
        return data if data.get("stat") == "Ok" else None

    def get_option_chain(self, symbol, expiry, strike_count=10):
        """
        Option Chain data తీసుకోండి
        symbol: NIFTY or BANKNIFTY
        expiry: format like 24-Oct-2024
        """
        if not self.session_token:
            return pd.DataFrame()

        try:
            data = self._post("GetOptionChain", {
                "uid": self.user_id,
                "tsym": symbol,
                "exch": "NFO",
                "expd": expiry,
                "strprc": "0",
                "cnt": str(strike_count)
            })

            if data.get("stat") != "Ok":
                return pd.DataFrame()

            rows = []
            values = data.get("values", [])

            for item in values:
                optt = item.get("optt", "")
                rows.append({
                    "STRIKE": float(item.get("strprc", 0)),
                    "EXPIRY": item.get("expd", ""),
                    "TYPE": optt,
                    "LTP": float(item.get("lp", 0)),
                    "OI": float(item.get("oi", 0)),
                    "CHG_OI": float(item.get("oic", 0)),
                    "VOLUME": float(item.get("v", 0)),
                    "IV": float(item.get("iv", 0)) if item.get("iv") else 0,
                    "DELTA": float(item.get("delta", 0)) if item.get("delta") else 0,
                })

            df = pd.DataFrame(rows)

            if df.empty:
                return df

            # CALL / PUT split
            calls = df[df["TYPE"] == "CE"].rename(columns={
                "LTP": "CALL_LTP", "OI": "CALL_OI",
                "CHG_OI": "CALL_CHG_OI", "IV": "CALL_IV",
                "DELTA": "CALL_DELTA", "VOLUME": "CALL_VOL"
            }).drop(columns=["TYPE", "EXPIRY"])

            puts = df[df["TYPE"] == "PE"].rename(columns={
                "LTP": "PUT_LTP", "OI": "PUT_OI",
                "CHG_OI": "PUT_CHG_OI", "IV": "PUT_IV",
                "DELTA": "PUT_DELTA", "VOLUME": "PUT_VOL"
            }).drop(columns=["TYPE", "EXPIRY"])

            merged = pd.merge(calls, puts, on="STRIKE", how="outer")
            merged = merged.sort_values("STRIKE").reset_index(drop=True)
            merged = merged.fillna(0)

            return merged

        except Exception as e:
            return pd.DataFrame()

    def get_live_ltp_bulk(self, symbols_list):
        """
        Scanner కోసం bulk LTP fetch
        symbols_list: [("NSE", "RELIANCE"), ("NSE", "TCS"), ...]
        """
        if not self.session_token:
            return {}

        results = {}
        for exch, sym in symbols_list:
            try:
                quote = self.get_quote(exch, sym)
                if quote:
                    results[sym] = {
                        "ltp": float(quote.get("lp", 0)),
                        "open": float(quote.get("o", 0)),
                        "high": float(quote.get("h", 0)),
                        "low": float(quote.get("l", 0)),
                        "close": float(quote.get("c", 0)),
                        "volume": float(quote.get("v", 0)),
                        "change_pct": float(quote.get("pc", 0)),
                    }
                time.sleep(0.1)  # Rate limit avoid
            except:
                pass
        return results

    def get_expiry_list(self, symbol):
        """Option expiry dates తీసుకోండి"""
        if not self.session_token:
            return []
        data = self._post("GetExpiryDates", {
            "uid": self.user_id,
            "exch": "NFO",
            "tsym": symbol
        })
        if data.get("stat") == "Ok":
            return data.get("exd", [])
        return []


# =========================================================
# SESSION STATE — Shoonya instance store
# =========================================================

if "shoonya" not in st.session_state:
    st.session_state.shoonya = ShoonyaAPI()

if "shoonya_logged_in" not in st.session_state:
    st.session_state.shoonya_logged_in = False

if "shoonya_live_data" not in st.session_state:
    st.session_state.shoonya_live_data = {}

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.header("⚙️ AI CONTROL PANEL")

# --- SHOONYA LOGIN SECTION ---
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔐 SHOONYA LOGIN")

if not st.session_state.shoonya_logged_in:
    with st.sidebar.expander("🔑 Login Credentials", expanded=True):
        sh_user = st.text_input("User ID", placeholder="SH12345")
        sh_pass = st.text_input("Password", type="password")
        sh_totp = st.text_input("TOTP (Google Authenticator)", placeholder="123456")
        sh_vc = st.text_input("Vendor Code", placeholder="SH12345_U")
        sh_secret = st.text_input("API Secret", type="password")

        if st.button("🚀 SHOONYA LOGIN"):
            if sh_user and sh_pass and sh_totp and sh_vc and sh_secret:
                with st.spinner("Logging in..."):
                    success, msg = st.session_state.shoonya.login(
                        user_id=sh_user,
                        password=sh_pass,
                        totp=sh_totp,
                        vendor_code=sh_vc,
                        api_secret=sh_secret
                    )
                if success:
                    st.session_state.shoonya_logged_in = True
                    st.sidebar.success(msg)
                    st.rerun()
                else:
                    st.sidebar.error(msg)
            else:
                st.sidebar.warning("⚠️ అన్ని fields fill చేయండి!")

        st.caption("Shoonya credentials: [shoonya.com](https://shoonya.com)")

else:
    st.sidebar.success("✅ Shoonya Connected")
    if st.sidebar.button("🔓 Logout"):
        st.session_state.shoonya_logged_in = False
        st.session_state.shoonya = ShoonyaAPI()
        st.session_state.shoonya_live_data = {}
        st.rerun()

st.sidebar.markdown("---")

selected_stock = st.sidebar.selectbox(
    "SELECT STOCK",
    sorted(list(nse_stocks.keys()))
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
# INDIA TIME + MARKET STATUS
# =========================================================

india = pytz.timezone("Asia/Kolkata")
current_time = datetime.now(india)
st.sidebar.info(current_time.strftime("🕒 %d-%m-%Y %H:%M:%S IST"))

hour = current_time.hour
minute = current_time.minute
weekday = current_time.weekday()

market_open = (
    weekday < 5 and
    ((hour == 9 and minute >= 15) or
     (10 <= hour <= 14) or
     (hour == 15 and minute <= 30))
)

if market_open:
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
            ticker, interval=interval,
            period=period, progress=False,
            auto_adjust=True, threads=True
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
# INDICATORS
# =========================================================

def calculate_indicators(df):
    df = df.copy()

    df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
    df["EMA50"] = df["Close"].ewm(span=50, adjust=False).mean()

    delta = df["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / (avg_loss + 1e-10)
    df["RSI"] = 100 - (100 / (1 + rs))

    ema12 = df["Close"].ewm(span=12).mean()
    ema26 = df["Close"].ewm(span=26).mean()
    df["MACD"] = ema12 - ema26
    df["MACD_SIGNAL"] = df["MACD"].ewm(span=9).mean()

    df["VWAP"] = (
        (df["Close"] * df["Volume"]).cumsum()
        / (df["Volume"].cumsum() + 1e-10)
    )

    df["ATR"] = calculate_atr(df)

    df["VOL_AVG"] = df["Volume"].rolling(20).mean()
    df["SMART_MONEY"] = df["Volume"] > df["VOL_AVG"] * 2

    df.fillna(0, inplace=True)
    return df

# =========================================================
# AI SIGNAL
# =========================================================

def generate_signal(latest):
    score = 0

    if latest["EMA20"] > latest["EMA50"]:
        score += 25
    else:
        score -= 25

    if 55 <= latest["RSI"] <= 70:
        score += 20
    elif latest["RSI"] < 30:
        score += 15
    elif latest["RSI"] > 75:
        score -= 15

    if latest["MACD"] > latest["MACD_SIGNAL"]:
        score += 25
    else:
        score -= 25

    if latest["Close"] > latest["VWAP"]:
        score += 20
    else:
        score -= 20

    if latest["SMART_MONEY"]:
        score += 10

    if score >= 70:
        signal = "🚀 STRONG BUY"
    elif score >= 30:
        signal = "✅ BUY"
    elif score <= -70:
        signal = "🚨 STRONG SELL"
    elif score <= -30:
        signal = "🔻 SELL"
    else:
        signal = "⚠️ SIDEWAYS"

    confidence = min(abs(score), 95)
    return signal, score, confidence

# =========================================================
# TABS
# =========================================================

tab1, tab2, tab3 = st.tabs([
    "📈 LIVE TECHNICAL",
    "📂 OPTION CHAIN",
    "🤖 AI SCANNER"
])

# =========================================================
# TAB 1 — TECHNICAL
# =========================================================

with tab1:
    data = load_market_data(ticker, interval, period)

    # Shoonya live price override
    if st.session_state.shoonya_logged_in and selected_stock in shoonya_symbols:
        sh_sym = shoonya_symbols[selected_stock]
        live = st.session_state.shoonya.get_quote("NSE", sh_sym)
        if live:
            ltp = float(live.get("lp", 0))
            chg = float(live.get("pc", 0))
            col_a, col_b, col_c = st.columns(3)
            col_a.metric("🟢 SHOONYA LIVE LTP", f"₹{ltp}", f"{chg}%")
            col_b.metric("HIGH", f"₹{float(live.get('h', 0))}")
            col_c.metric("LOW", f"₹{float(live.get('l', 0))}")
            st.caption(f"Volume: {float(live.get('v', 0)):,.0f} | Open: ₹{float(live.get('o', 0))}")

    if not data.empty:
        data = calculate_indicators(data)
        latest = data.iloc[-1]
        signal, score, confidence = generate_signal(latest)

        st.subheader("🤖 AI SIGNAL ENGINE")

        if "BUY" in signal:
            st.success(f"{signal} | CONFIDENCE {confidence}%")
        elif "SELL" in signal:
            st.error(f"{signal} | CONFIDENCE {confidence}%")
        else:
            st.warning(signal)

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("PRICE", round(float(latest["Close"]), 2))
        c2.metric("RSI", round(float(latest["RSI"]), 2))
        c3.metric("VWAP", round(float(latest["VWAP"]), 2))
        c4.metric("MACD", round(float(latest["MACD"]), 2))
        c5.metric("AI SCORE", score)

        sl = latest["Close"] - latest["ATR"] * 1.5
        target = latest["Close"] + latest["ATR"] * 3

        s1, s2 = st.columns(2)
        s1.error(f"🛑 STOPLOSS : {round(float(sl), 2)}")
        s2.success(f"🎯 TARGET : {round(float(target), 2)}")

        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=data.index, open=data["Open"],
            high=data["High"], low=data["Low"],
            close=data["Close"], name="PRICE"
        ))
        fig.add_trace(go.Scatter(x=data.index, y=data["EMA20"], mode="lines", name="EMA20"))
        fig.add_trace(go.Scatter(x=data.index, y=data["EMA50"], mode="lines", name="EMA50"))
        fig.update_layout(template="plotly_dark", height=700, xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

# =========================================================
# TAB 2 — OPTION CHAIN (SHOONYA)
# =========================================================

with tab2:
    st.header("📂 LIVE OPTION CHAIN")

    option_symbol = st.selectbox("SELECT INDEX", ["NIFTY", "BANKNIFTY"])

    if st.session_state.shoonya_logged_in:

        st.success("✅ Shoonya Live Option Chain")

        # Expiry dates fetch
        expiry_list = st.session_state.shoonya.get_expiry_list(option_symbol)

        if expiry_list:
            selected_expiry = st.selectbox("EXPIRY DATE", expiry_list)
            strike_count = st.slider("STRIKE COUNT (each side)", 5, 20, 10)

            if st.button("🔄 LOAD OPTION CHAIN"):
                with st.spinner("Shoonya నుండి Option Chain load అవుతోంది..."):
                    option_df = st.session_state.shoonya.get_option_chain(
                        option_symbol, selected_expiry, strike_count
                    )

                if not option_df.empty:
                    total_call = option_df["CALL_OI"].sum()
                    total_put = option_df["PUT_OI"].sum()
                    pcr = total_put / total_call if total_call > 0 else 0

                    support = option_df.loc[option_df["PUT_OI"].idxmax(), "STRIKE"] if total_put > 0 else 0
                    resistance = option_df.loc[option_df["CALL_OI"].idxmax(), "STRIKE"] if total_call > 0 else 0

                    option_df["TOTAL_OI"] = option_df["CALL_OI"] + option_df["PUT_OI"]
                    max_pain = option_df.loc[option_df["TOTAL_OI"].idxmax(), "STRIKE"]

                    if pcr > 1.15:
                        st.success(f"🚀 BULLISH | PCR: {round(pcr, 2)}")
                    elif pcr < 0.85:
                        st.error(f"🔻 BEARISH | PCR: {round(pcr, 2)}")
                    else:
                        st.warning(f"⚠️ SIDEWAYS | PCR: {round(pcr, 2)}")

                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("PCR", round(pcr, 2))
                    m2.metric("SUPPORT", int(support))
                    m3.metric("RESISTANCE", int(resistance))
                    m4.metric("MAX PAIN", int(max_pain))

                    # OI Chart
                    fig2 = go.Figure()
                    fig2.add_trace(go.Bar(x=option_df["STRIKE"], y=option_df["CALL_OI"], name="CALL OI", marker_color="#ef4444"))
                    fig2.add_trace(go.Bar(x=option_df["STRIKE"], y=option_df["PUT_OI"], name="PUT OI", marker_color="#22c55e"))
                    fig2.update_layout(template="plotly_dark", barmode="group", height=500, title="OI ANALYSIS")
                    st.plotly_chart(fig2, use_container_width=True)

                    # IV Chart
                    if "CALL_IV" in option_df.columns:
                        fig_iv = go.Figure()
                        fig_iv.add_trace(go.Scatter(x=option_df["STRIKE"], y=option_df["CALL_IV"], mode="lines+markers", name="CALL IV", line=dict(color="#f59e0b")))
                        fig_iv.add_trace(go.Scatter(x=option_df["STRIKE"], y=option_df["PUT_IV"], mode="lines+markers", name="PUT IV", line=dict(color="#a78bfa")))
                        fig_iv.update_layout(template="plotly_dark", height=300, title="IMPLIED VOLATILITY")
                        st.plotly_chart(fig_iv, use_container_width=True)

                    st.dataframe(option_df, use_container_width=True)
                else:
                    st.warning("⚠️ Option Chain data రాలేదు. Expiry check చేయండి.")
        else:
            st.warning("⚠️ Expiry dates రాలేదు. Symbol check చేయండి.")

    else:
        # Fallback — NSE scraping
        st.warning("⚠️ Shoonya login చేయండి — Live Option Chain కోసం. NSE fallback try చేస్తున్నాం...")

        try:
            headers = {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "accept": "*/*",
                "accept-language": "en-US,en;q=0.9",
                "referer": "https://www.nseindia.com/option-chain",
            }
            session = requests.Session()
            session.get("https://www.nseindia.com", headers=headers, timeout=10, verify=False)
            time.sleep(1)
            resp = session.get(
                f"https://www.nseindia.com/api/option-chain-indices?symbol={option_symbol}",
                headers=headers, timeout=10, verify=False
            )
            data_oc = resp.json()
            records = data_oc.get("records", {}).get("data", [])

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
                })

            option_df = pd.DataFrame(rows)

            if not option_df.empty:
                total_call = option_df["CALL_OI"].sum()
                total_put = option_df["PUT_OI"].sum()
                pcr = total_put / total_call if total_call > 0 else 0

                support = option_df.loc[option_df["PUT_OI"].idxmax(), "STRIKE"]
                resistance = option_df.loc[option_df["CALL_OI"].idxmax(), "STRIKE"]
                option_df["TOTAL_OI"] = option_df["CALL_OI"] + option_df["PUT_OI"]
                max_pain = option_df.loc[option_df["TOTAL_OI"].idxmax(), "STRIKE"]

                if pcr > 1.15:
                    st.success(f"🚀 BULLISH | PCR: {round(pcr, 2)}")
                elif pcr < 0.85:
                    st.error(f"🔻 BEARISH | PCR: {round(pcr, 2)}")
                else:
                    st.warning(f"⚠️ SIDEWAYS | PCR: {round(pcr, 2)}")

                m1, m2, m3, m4 = st.columns(4)
                m1.metric("PCR", round(pcr, 2))
                m2.metric("SUPPORT", int(support))
                m3.metric("RESISTANCE", int(resistance))
                m4.metric("MAX PAIN", int(max_pain))

                fig2 = go.Figure()
                fig2.add_trace(go.Bar(x=option_df["STRIKE"], y=option_df["CALL_OI"], name="CALL OI"))
                fig2.add_trace(go.Bar(x=option_df["STRIKE"], y=option_df["PUT_OI"], name="PUT OI"))
                fig2.update_layout(template="plotly_dark", barmode="group", height=500, title="OI ANALYSIS (NSE Fallback)")
                st.plotly_chart(fig2, use_container_width=True)
                st.dataframe(option_df, use_container_width=True)

        except Exception as e:
            st.error(f"NSE fallback కూడా పని చేయలేదు: {e}")
            st.info("💡 Shoonya login చేస్తే guaranteed live data వస్తుంది!")

# =========================================================
# TAB 3 — AI SCANNER (SHOONYA LIVE PRICES)
# =========================================================

with tab3:
    st.header("🤖 AI NSE SCANNER")

    # Data source selector
    data_source_choice = st.radio(
        "📡 DATA SOURCE",
        ["Yahoo Finance (Free)", "Shoonya Live Data (More Accurate)"],
        horizontal=True
    )

    use_shoonya = (
        data_source_choice == "Shoonya Live Data (More Accurate)"
        and st.session_state.shoonya_logged_in
    )

    if data_source_choice == "Shoonya Live Data (More Accurate)" and not st.session_state.shoonya_logged_in:
        st.warning("⚠️ Shoonya login చేయండి sidebar లో!")

    results = []
    progress = st.progress(0)
    total = len(nse_stocks)

    # Fetch Shoonya live prices bulk (if logged in)
    shoonya_prices = {}
    if use_shoonya:
        with st.spinner("🔄 Shoonya నుండి live prices fetch చేస్తున్నాం..."):
            syms = [(("NSE", v)) for k, v in shoonya_symbols.items()]
            shoonya_prices = st.session_state.shoonya.get_live_ltp_bulk(syms)
        st.success(f"✅ {len(shoonya_prices)} stocks live price వచ్చింది!")

    def scan_stock(item):
        name, symbol = item
        try:
            df = load_market_data(symbol, "15m", "5d")
            if df.empty:
                return None

            df = calculate_indicators(df)
            latest = df.iloc[-1]
            signal, score, confidence = generate_signal(latest)

            price = round(float(latest["Close"]), 2)
            price_source = "Yahoo"

            # Shoonya live price override
            sh_sym = shoonya_symbols.get(name, "")
            if use_shoonya and sh_sym in shoonya_prices:
                price = shoonya_prices[sh_sym]["ltp"]
                price_source = "🟢 Live"

            return {
                "STOCK": name,
                "PRICE": price,
                "SOURCE": price_source,
                "RSI": round(float(latest["RSI"]), 2),
                "SIGNAL": signal,
                "CONFIDENCE": confidence,
                "SCORE": score
            }
        except:
            return None

    with ThreadPoolExecutor(max_workers=10) as executor:
        for idx, result in enumerate(
            executor.map(scan_stock, nse_stocks.items())
        ):
            if result:
                results.append(result)
            progress.progress((idx + 1) / total)

    scan_df = pd.DataFrame(results)

    if not scan_df.empty:
        scan_df = scan_df.sort_values(by="CONFIDENCE", ascending=False)

        # Filter tabs
        f1, f2, f3 = st.tabs(["🚀 ALL", "✅ BUY", "🔻 SELL"])
        with f1:
            st.dataframe(scan_df, use_container_width=True)
        with f2:
            st.dataframe(scan_df[scan_df["SIGNAL"].str.contains("BUY")], use_container_width=True)
        with f3:
            st.dataframe(scan_df[scan_df["SIGNAL"].str.contains("SELL")], use_container_width=True)

        # Download
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
            scan_df.to_excel(writer, index=False)

        st.download_button(
            label="📥 DOWNLOAD AI SCANNER",
            data=excel_buffer.getvalue(),
            file_name="NSE_AI_SCANNER_SHOONYA.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")
st.caption("🚀 NSE AI PRO MAX V9.0 ULTRA + Shoonya Live Integration")
st.caption("⚠️ Educational purpose only. Not SEBI registered advice.")
