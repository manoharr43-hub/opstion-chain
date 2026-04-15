import streamlit as st
import yfinance as yf
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# =============================
# CONFIG
# =============================
st.set_page_config(page_title="🔥 PRO NSE AI DASHBOARD", layout="wide")
st_autorefresh(interval=15000, key="refresh")

st.title("🔥 PRO NSE AI DASHBOARD + SCANNER")
st.markdown("---")

# =============================
# TABS (SAFE ADD)
# =============================
tab1, tab2 = st.tabs(["📊 Dashboard", "🔥 Scanner"])

# =============================
# 📊 DASHBOARD (FIXED)
# =============================
with tab1:
    st.subheader("📊 Simple Dashboard")

    stock = st.text_input("Enter Stock (Example: RELIANCE)", "RELIANCE")

    # AUTO FIX SYMBOL
    if not stock.endswith(".NS"):
        stock = stock + ".NS"

    @st.cache_data(ttl=60)
    def get_data(symbol):
        try:
            df = yf.download(symbol, period="3mo", interval="1d", progress=False)
            if df is None or df.empty:
                return None
            return df
        except:
            return None

    df = get_data(stock)

    if df is not None and not df.empty:

        st.line_chart(df['Close'])

        df['SMA20'] = df['Close'].rolling(20).mean()
        df['SMA50'] = df['Close'].rolling(50).mean()

        # SAFE DROP NA
        df_clean = df.dropna()

        if len(df_clean) > 0:
            latest = df_clean.iloc[-1]

            col1, col2 = st.columns(2)
            col1.metric("Price", round(latest['Close'], 2))

            trend = "UP" if latest['SMA20'] > latest['SMA50'] else "DOWN"
            col2.metric("Trend", trend)

        else:
            st.warning("⚠️ Not enough data for SMA trend")

    else:
        st.error("❌ Data Not Loading (Check symbol / network)")

# =============================
# 🔥 SCANNER (FAST + SAFE)
# =============================
with tab2:
    st.subheader("🔥 NSE SCANNER")

    sectors = {
        "Nifty 50": ["RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS"],
        "Banking": ["SBIN.NS","AXISBANK.NS","KOTAKBANK.NS","PNB.NS"],
        "IT": ["WIPRO.NS","HCLTECH.NS","TECHM.NS"],
        "Auto": ["MARUTI.NS","TATAMOTORS.NS","M&M.NS"]
    }

    sector = st.selectbox("Select Sector", list(sectors.keys()))
    stocks = sectors[sector][:3]

    @st.cache_data(ttl=60)
    def get_multi_data(tickers):
        try:
            return yf.download(tickers, period="15d", interval="15m", group_by="ticker", progress=False)
        except:
            return None

    data = get_multi_data(stocks)

    results = []

    if data is not None:

        for stock in stocks:
            try:
                df = data[stock].dropna()

                if len(df) < 20:
                    continue

                df['EMA20'] = df['Close'].ewm(span=20).mean()
                df['EMA50'] = df['Close'].ewm(span=50).mean()

                signal = "🟢 BUY" if df['EMA20'].iloc[-1] > df['EMA50'].iloc[-1] else "🔴 SELL"

                price = df['Close'].iloc[-1]
                prev = df.iloc[-2]

                if "BUY" in signal:
                    entry = prev['High']
                    sl = prev['Low']
                    target = entry + (entry - sl)*1.5
                else:
                    entry = prev['Low']
                    sl = prev['High']
                    target = entry - (sl - entry)*1.5

                # MULTI TF SAFE
                t5 = "UP" if df['EMA20'].iloc[-1] > df['EMA50'].iloc[-1] else "DOWN"

                try:
                    df1h = df.resample("1h").last().dropna()

                    if len(df1h) > 20:
                        t1h = "UP" if df1h['Close'].iloc[-1] > df1h['Close'].rolling(20).mean().iloc[-1] else "DOWN"
                    else:
                        t1h = "N/A"
                except:
                    t1h = "N/A"

                results.append({
                    "Stock": stock,
                    "Signal": signal,
                    "Price": round(price,2),
                    "Entry": round(entry,2),
                    "SL": round(sl,2),
                    "Target": round(target,2),
                    "5M": t5,
                    "1H": t1h
                })

            except:
                continue

    df_res = pd.DataFrame(results)

    if df_res.empty:
        st.warning("⚠️ No Data (Try another sector)")
    else:
        st.dataframe(df_res, use_container_width=True)

        st.subheader("📦 Multi Timeframe")

        s = st.selectbox("Select Stock", df_res["Stock"])
        row = df_res[df_res["Stock"] == s].iloc[0]

        c1, c2 = st.columns(2)
        c1.metric("5M Trend", row["5M"])
        c2.metric("1H Trend", row["1H"])

        st.subheader("📈 Chart")
        st.line_chart(data[s]["Close"].resample("1D").last())
