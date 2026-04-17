import streamlit as st
import requests
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

# =============================
# CONFIG
# =============================
st.set_page_config(page_title="🔥 NSE OPTION CHAIN", layout="wide")
st.title("📊 NSE Option Chain + Intraday Dashboard")

# =============================
# FUNCTION: Fetch Option Chain
# =============================
def get_option_chain(symbol="NIFTY"):
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Referer": "https://www.nseindia.com/option-chain"
    }
    session = requests.Session()
    # First request to NSE homepage for cookies
    session.get("https://www.nseindia.com", headers=headers)
    response = session.get(url, headers=headers)
    data = response.json()

    # Safe access: check both records and filtered
    if "records" in data and "data" in data["records"]:
        return data["records"]["data"]
    elif "filtered" in data and "data" in data["filtered"]:
        return data["filtered"]["data"]
    else:
        return []

# =============================
# USER INPUT
# =============================
symbol = st.sidebar.selectbox("Select Index", ["NIFTY", "BANKNIFTY"])

# =============================
# OPTION CHAIN DATA
# =============================
try:
    option_data = get_option_chain(symbol)
    calls, puts = [], []

    for row in option_data:
        ce = row.get("CE")
        pe = row.get("PE")
        if ce:
            calls.append([ce["strikePrice"], ce["openInterest"], ce["changeinOpenInterest"], ce["lastPrice"]])
        if pe:
            puts.append([pe["strikePrice"], pe["openInterest"], pe["changeinOpenInterest"], pe["lastPrice"]])

    call_df = pd.DataFrame(calls, columns=["Strike", "OI", "Chg OI", "LTP"])
    put_df = pd.DataFrame(puts, columns=["Strike", "OI", "Chg OI", "LTP"])

    st.subheader(f"📈 {symbol} CALLS")
    if not call_df.empty:
        st.dataframe(call_df, width="stretch")
    else:
        st.warning("No CALL data available (Market closed or API empty).")

    st.subheader(f"📉 {symbol} PUTS")
    if not put_df.empty:
        st.dataframe(put_df, width="stretch")
    else:
        st.warning("No PUT data available (Market closed or API empty).")

    # PCR Calculation
    total_calls = call_df["OI"].sum() if not call_df.empty else 0
    total_puts = put_df["OI"].sum() if not put_df.empty else 0
    pcr = round(total_puts / total_calls, 2) if total_calls != 0 else 0
    st.metric(label=f"{symbol} PCR (Put/Call Ratio)", value=pcr)

except Exception as e:
    st.error(f"Error fetching option chain data: {e}")

# =============================
# INTRADAY SIGNALS (YFinance Example)
# =============================
st.subheader(f"⏱️ Intraday Signals - {symbol} (5 min data)")

try:
    # Example ticker for intraday (replace with actual stock/index)
    bt_date = datetime.today() - timedelta(days=1)
    ticker = yf.Ticker("^NSEI") if symbol == "NIFTY" else yf.Ticker("^NSEBANK")

    df_hist = ticker.history(start=bt_date, end=bt_date + timedelta(days=1), interval="5m")

    # Ensure index is datetime
    df_hist.index = pd.to_datetime(df_hist.index)

    # Filter trading hours
    df_hist = df_hist.between_time("09:15", "15:30")

    # Example signals (mock logic)
    intraday_data = []
    for i in range(len(df_hist)):
        intraday_data.append([
            df_hist.index[i].strftime("%H:%M"),
            round(df_hist["Close"].iloc[i] - df_hist["Open"].iloc[i], 2),
            pcr,
            "BUY" if df_hist["Close"].iloc[i] > df_hist["Open"].iloc[i] else "SELL"
        ])

    intraday_df = pd.DataFrame(intraday_data, columns=["Time", "Diff", "PCR", "Signal"])
    st.dataframe(intraday_df, width="stretch")

except Exception as e:
    st.error(f"Error fetching intraday data: {e}")
