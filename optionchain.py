import streamlit as st
import pandas as pd
import numpy as np

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="Stable Option Chain AI", layout="wide")


# =========================
# DATA GENERATOR (SAFE WITH GREEKS)
# =========================
def generate_data(symbol):
    base = 22000 if symbol == "NIFTY" else 45000
    
    # Strikes list
    strikes = [base + i * 50 for i in range(20)]
    
    df = pd.DataFrame({
        "Strike Price": strikes,
        "CE OI": np.random.randint(500, 2000, 20),
        "PE OI": np.random.randint(500, 2000, 20),
        # Adding Greeks Logic (Simulated)
        "Delta": np.random.uniform(0.1, 0.9, 20).round(2),
        "Theta": np.random.uniform(-50, -10, 20).round(2),
        "Gamma": np.random.uniform(0.001, 0.005, 20).round(4),
        "Vega": np.random.uniform(5, 15, 20).round(2)
    })

    return df


# =========================
# SESSION STATE INIT
# =========================
if "data_loaded" not in st.session_state:
    st.session_state.data_loaded = False

if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame()


# =========================
# UI HEADER
# =========================
st.title("🚀 ULTRA STABLE OPTION CHAIN + GREEKS")
st.write("ఈ వెర్షన్‌లో ఎర్రర్స్ రాకుండా స్టైలింగ్ ఫిక్స్ చేయబడింది.")

symbol = st.selectbox("Select Index", ["NIFTY", "BANKNIFTY", "FINNIFTY"])

# =========================
# LOAD BUTTON
# =========================
if st.button("LOAD OPTION CHAIN WITH GREEKS"):
    st.session_state.data_loaded = True
    st.session_state.df = generate_data(symbol)


# =========================
# DISPLAY DATA (PERSISTENT)
# =========================
if st.session_state.data_loaded:

    df = st.session_state.df.copy()

    # CALCULATIONS
    df["OI Diff"] = df["PE OI"] - df["CE OI"]
    df["Trend"] = np.where(df["OI Diff"] > 0, "Bullish", "Bearish")

    st.success(f"✅ {symbol} Data Loaded Successfully")

    # TOP METRICS
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total CE OI", f"{df['CE OI'].sum():,}")
    m2.metric("Total PE OI", f"{df['PE OI'].sum():,}")
    m3.metric("Avg Delta", df["Delta"].mean().round(2))
    m4.metric("Avg Theta", df["Theta"].mean().round(2))

    # DATA TABLE (Fixed: No background_gradient to avoid errors)
    st.subheader("📊 Option Chain & Greeks Table")
    st.dataframe(df, use_container_width=True)

    # VISUAL CHARTS
    st.divider()
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("📈 OI Difference (Strength)")
        st.bar_chart(df.set_index("Strike Price")["OI Diff"])
    
    with col_b:
        st.subheader("⏳ Theta Decay (Time Value)")
        st.line_chart(df.set_index("Strike Price")["Theta"])

    # MARKET SENTIMENT
    st.divider()
    ce_total = df["CE OI"].sum()
    pe_total = df["PE OI"].sum()

    if pe_total > ce_total:
        st.markdown("### 🟢 Market Sentiment: **BULLISH**")
        st.info("పుట్ రైటర్లు (PE) ఎక్కువగా ఉన్నారు, మార్కెట్ సపోర్ట్ తీసుకునే అవకాశం ఉంది.")
    else:
        st.markdown("### 🔴 Market Sentiment: **BEARISH**")
        st.warning("కాల్ రైటర్లు (CE) ఎక్కువగా ఉన్నారు, మార్కెట్ రెసిస్టెన్స్ ఫేస్ చేసే అవకాశం ఉంది.")

# =========================
# SIDEBAR INFO
# =========================
with st.sidebar:
    st.header("Greeks Guide")
    st.write("**Delta:** దిశను సూచిస్తుంది.")
    st.write("**Theta:** టైమ్ డికే (Time Decay).")
    st.write("**Gamma:** వేగాన్ని సూచిస్తుంది.")
    st.write("**Vega:** వోలటాలిటీని సూచిస్తుంది.")
    st.divider()
    st.info("Developed for Manohar's NSE Pro Scanner")

st.info("⚠️ Educational Purpose Only - Stable Version")
