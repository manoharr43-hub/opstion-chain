import streamlit as st
import pandas as pd
import pyotp
from NorenRestApiPy import NorenApi
from streamlit_autorefresh import st_autorefresh

# =========================
# AUTO REFRESH
# =========================
st_autorefresh(interval=5000, key="refresh")

# =========================
# API CLASS
# =========================
class ShoonyaApiPy(NorenApi):
    def __init__(self):
        super().__init__(
            host='https://api.shoonya.com/NorenWSTP/',
            websocket='wss://api.shoonya.com/NorenWS/'
        )

# =========================
# LOGIN
# =========================
@st.cache_resource
def login():
    creds = st.secrets["shoonya"]
    otp = pyotp.TOTP(creds["totp_key"]).now()

    api = ShoonyaApiPy()
    ret = api.login(
        userid=creds["user_id"],
        password=creds["password"],
        twoFA=otp,
        vendor_code=creds["vendor_code"],
        api_secret=creds["api_secret"],
        imei=creds["imei"]
    )

    if ret and ret.get("stat") == "Ok":
        return api
    else:
        st.error(ret)
        return None

# =========================
# FETCH DATA
# =========================
def fetch(api, symbol):
    idx_map = {"NIFTY": "NIFTY", "BANKNIFTY": "BANKNIFTY"}
    quote = api.get_quotes("NSE", idx_map[symbol])
    spot = float(quote["lp"])

    chain = api.get_option_chain("NFO", symbol, int(spot), 10)

    rows = []
    for i in chain["values"]:
        rows.append({
            "Strike": float(i["stlk"]),
            "Type": i["optt"],
            "LTP": float(i.get("lp", 0)),
            "OI": int(i.get("oi", 0))
        })

    df = pd.DataFrame(rows)

    ce = df[df["Type"] == "CE"].rename(columns={"LTP": "CE_LTP", "OI": "CE_OI"})
    pe = df[df["Type"] == "PE"].rename(columns={"LTP": "PE_LTP", "OI": "PE_OI"})

    final = pd.merge(
        ce[["Strike", "CE_LTP", "CE_OI"]],
        pe[["Strike", "PE_LTP", "PE_OI"]],
        on="Strike"
    ).sort_values("Strike")

    return spot, final

# =========================
# SIGNAL LOGIC
# =========================
def get_signal(df):
    total_ce_oi = df["CE_OI"].sum()
    total_pe_oi = df["PE_OI"].sum()

    pcr = total_pe_oi / total_ce_oi if total_ce_oi != 0 else 0

    if pcr > 1.2:
        return "🟢 STRONG BUY"
    elif pcr < 0.8:
        return "🔴 STRONG SELL"
    else:
        return "⚪ SIDEWAYS"

# =========================
# UI
# =========================
st.set_page_config(layout="wide")
st.title("🚀 Shoonya AI Trading Dashboard PRO")

api = login()

if api:
    st.success("✅ Connected")

    symbol = st.selectbox("Select Index", ["NIFTY", "BANKNIFTY"])

    spot, df = fetch(api, symbol)

    if spot:
        st.subheader(f"{symbol} Spot: ₹{spot}")

    if not df.empty:

        # PCR
        total_ce = df["CE_OI"].sum()
        total_pe = df["PE_OI"].sum()
        pcr = total_pe / total_ce if total_ce != 0 else 0

        col1, col2, col3 = st.columns(3)
        col1.metric("PCR", round(pcr, 2))
        col2.metric("Total CE OI", total_ce)
        col3.metric("Total PE OI", total_pe)

        # SIGNAL
        signal = get_signal(df)
        st.subheader(f"AI Signal: {signal}")

        # ATM Highlight
        atm = min(df["Strike"], key=lambda x: abs(x - spot))
        st.write(f"ATM Strike: {atm}")

        def highlight(row):
            if row["Strike"] == atm:
                return ["background-color: yellow"] * len(row)
            return [""] * len(row)

        st.dataframe(df.style.apply(highlight, axis=1), use_container_width=True)

    else:
        st.warning("No Data")
else:
    st.error("Login Failed")
