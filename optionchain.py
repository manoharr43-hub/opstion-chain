import streamlit as st
import yfinance as yf
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# =============================
# CONFIG
# =============================
st.set_page_config(page_title="🔥 SAFE NSE AI DASHBOARD", layout="wide")
st_autorefresh(interval=15000, key="refresh")

st.title("🔥 SAFE NSE AI DASHBOARD (NO HANG VERSION)")
st.markdown("---")

tab1, tab2 = st.tabs(["📊 Dashboard", "🔥 Scanner"])

# =============================
# SAFE DATA LOADER (NO FREEZE FIX)
# =============================
@st.cache_data(ttl=60)
def get_data(symbol):
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="3mo", interval="1d")

        if df is None or df.empty:
            return None

        return df

    except:
        return None


@st.cache_data(ttl=60)
def get_multi_data(tickers):
    try:
        data = yf.download(
            tickers,
            period="10d",
            interval="15m",
            group_by="ticker",
            threads=True,
            progress=False
        )

        if data is None or len(data) == 0:
            return None

        return data

    except:
        return None


# =============================
# 📊 DASHBOARD
# =============================
with tab1:
    st.subheader("📊 Stock Dashboard (Stable)")

    stock = st.text_input("Enter Stock (Example: RELIANCE)", "RELIANCE")

    if not stock.endswith(".NS"):
        stock = stock + ".NS"

    with st.spinner("📡 Loading data..."):
        df = get_data(stock)

    if df is not None and not df.empty:

        st.line_chart(df['Close'])

        df['SMA20'] = df['Close'].rolling(20).mean()
        df['SMA50'] = df['Close'].rolling(50).mean()

        col1, col2 = st.columns(2)

        price = df['Close'].iloc[-1]
        col1.metric("Price", round(price, 2))

        sma20 = df['SMA20'].dropna()
        sma50 = df['SMA50'].dropna()

        trend = "UP" if sma20.iloc[-1] > sma50.iloc[-1] else "DOWN" if len(sma20) > 0 else "N/A"

        col2.metric("Trend", trend)

    else:
        st.error("❌ Data Not Available")


# =============================
# 🔥 SCANNER (SAFE + SIMPLE)
# =============================
with tab2:
    st.subheader("🔥 NSE SCANNER (NO CRASH VERSION)")

    sectors = {
        "Nifty 50": ["RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS"],
        "Banking": ["SBIN.NS","AXISBANK.NS","KOTAKBANK.NS"],
        "IT": ["WIPRO.NS","HCLTECH.NS","TECHM.NS"],
        "Auto": ["MARUTI.NS","TATAMOTORS.NS","M&M.NS"],
        "FMCG": ["HINDUNILVR.NS","ITC.NS","NESTLEIND.NS"],
        "Pharma": ["SUNPHARMA.NS","DRREDDY.NS","CIPLA.NS"]
    }

    sector = st.selectbox("Select Sector", list(sectors.keys()))
    stocks = sectors[sector]

    data = get_multi_data(stocks)

    results = []

    if data is not None:

        for stock in stocks:
            try:

                if stock not in data.columns.get_level_values(0):
                    continue

                df = data[stock].dropna()

                if df is None or len(df) < 20:
                    continue

                df['EMA20'] = df['Close'].ewm(span=20).mean()
                df['EMA50'] = df['Close'].ewm(span=50).mean()

                price = df['Close'].iloc[-1]

                if df['EMA20'].iloc[-1] > df['EMA50'].iloc[-1]:
                    signal = "🟢 BUY"
                else:
                    signal = "🔴 SELL"

                prev = df.iloc[-2]

                if signal == "🟢 BUY":
                    entry = prev['High']
                    sl = prev['Low']
                    target = entry + (entry - sl) * 1.5
                else:
                    entry = prev['Low']
                    sl = prev['High']
                    target = entry - (sl - entry) * 1.5

                results.append({
                    "Stock": stock,
                    "Signal": signal,
                    "Price": round(price, 2),
                    "Entry": round(entry, 2),
                    "SL": round(sl, 2),
                    "Target": round(target, 2)
                })

            except:
                continue

    df_res = pd.DataFrame(results)

    if df_res.empty:
        st.warning("⚠️ No Data Found")
    else:
        st.dataframe(df_res, use_container_width=True)

        s = st.selectbox("Select Stock", df_res["Stock"])
        row = df_res[df_res["Stock"] == s].iloc[0]

        st.subheader("📊 Selected Stock")
        st.metric("Signal", row["Signal"])
        st.metric("Price", row["Price"])
