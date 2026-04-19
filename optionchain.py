import streamlit as st
import pandas as pd
import time
from NorenRestApiPy import ShoonyaApiPy

st.set_page_config(page_title="NSE AI ULTRA PRO", layout="wide")
st.title("🚀 NSE AI ULTRA PRO (Shoonya Direct API)")

# ==============================
# LOAD SECRETS
# ==============================
try:
    creds = st.secrets["shoonyasecrets"]
except Exception as e:
    st.error("❌ secrets.toml not configured properly")
    st.stop()

# ==============================
# LOGIN FUNCTION (Single Session)
# ==============================
def login():
    if "api" in st.session_state and st.session_state.api is not None:
        return st.session_state.api
    api = ShoonyaApiPy()
    ret = api.login(
        userid=creds["user_id"],
        password=creds["password"],
        twoFA=creds["totp"],
        vendor_code=creds.get("vendor_code", ""),
        api_secret=creds["api_secret"],
        imei=creds.get("imei", "")
    )
    if ret:
        st.session_state.api = api
        return api
    return None

# ==============================
# MAIN APP
# ==============================
st.sidebar.header("⚙️ Settings")
symbol = st.sidebar.text_input("Symbol", "NIFTY").strip().upper()
refresh = st.sidebar.checkbox("🔄 Auto Refresh (10s)", value=False)

if st.sidebar.button("🔑 Login & Fetch"):
    if not symbol:
        st.warning("Please enter a symbol.")
        st.stop()

    api = login()
    if not api:
        st.error("❌ Login Failed – check credentials in secrets.toml")
        st.stop()

    st.success("✅ Login Successful")

    # Auto refresh loop
    while True:
        try:
            data = api.get_option_chain(exchange="NSE", tradingsymbol=symbol)
            if not data:
                st.warning("No option chain data returned.")
            else:
                df = pd.DataFrame(data)

                # Sort by strike
                if "strprc" in df.columns:
                    df["strprc"] = pd.to_numeric(df["strprc"], errors="coerce")
                    df = df.sort_values("strprc")

                # Split CE/PE
                ce = df[df["optt"] == "CE"]
                pe = df[df["optt"] == "PE"]

                st.subheader("📈 Calls (CE)")
                st.dataframe(ce)

                st.subheader("📉 Puts (PE)")
                st.dataframe(pe)

                # Basic Greeks (example: Delta, Gamma placeholders)
                if "iv" in df.columns:
                    st.subheader("⚙️ Greeks (Sample)")
                    df["Delta"] = df["iv"].apply(lambda x: round(0.5, 2))  # placeholder
                    df["Gamma"] = df["iv"].apply(lambda x: round(0.1, 2))  # placeholder
                    st.dataframe(df[["strprc", "optt", "iv", "Delta", "Gamma"]])

                # Chart (Open Interest vs Strike)
                if "strprc" in df.columns and "openint" in df.columns:
                    st.subheader("📊 Open Interest Chart")
                    st.bar_chart(df.set_index("strprc")["openint"])

            if not refresh:
                break
            time.sleep(10)
            st.experimental_rerun()

        except Exception as e:
            st.error(f"Error fetching option chain: {e}")
            break

# ==============================
# ORDER PLACEMENT (Demo)
# ==============================
st.sidebar.subheader("🛒 Place Order")
order_symbol = st.sidebar.text_input("Order Symbol", "")
qty = st.sidebar.number_input("Quantity", min_value=1, value=1)
side = st.sidebar.selectbox("Side", ["BUY", "SELL"])

if st.sidebar.button("🚀 Submit Order"):
    api = login()
    if api and order_symbol:
        try:
            ret = api.place_order(
                buy_or_sell=side,
                product_type="I",
                exchange="NSE",
                tradingsymbol=order_symbol,
                quantity=qty,
                discloseqty=0,
                price_type="MKT",
                price=0,
                remarks="Streamlit Order"
            )
            st.success(f"✅ Order Placed: {ret}")
        except Exception as e:
            st.error(f"Order Error: {e}")
