import streamlit as st
import pandas as pd
import numpy as np

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="Stable Option Chain AI with Greeks", layout="wide")


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
        # Adding Greeks Logic (Simulated for Education)
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
# UI
# =========================
st.title("🚀 ULTRA STABLE OPTION CHAIN + GREEKS")
st.write("ఈ స్కానర్ ఇప్పుడు Delta, Theta, Gamma మరియు Vega వాల్యూస్‌ను కూడా చూపిస్తుంది.")

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

    # SAFE CALCULATION
    df["OI Diff"] = df["PE OI"] - df["CE OI"]
    df["Trend"] = np.where(df["OI Diff"] > 0, "Bullish", "Bearish")

    st.success("✅ Data Loaded Successfully with Greeks")

    # METRICS ROW
    col1, col2, col3, col4 = st.columns(4)
    avg_delta = df["Delta"].mean().round(2)
    avg_theta = df["Theta"].mean().round(2)
    
    col1.metric("Avg Delta", avg_delta)
    col2.metric("Avg Theta (Time Decay)", avg_theta)
    col3.metric("Total CE OI", df["CE OI"].sum())
    col4.metric("Total PE OI", df["PE OI"].sum())

    # TABLE
    st.subheader("📊 Option Chain & Greeks Data")
    # Styling for better visibility
    st.dataframe(df.style.background_gradient(subset=['OI Diff'], cmap='RdYlGn'), use_container_width=True)

    # CHART SECTION
    st.divider()
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("📈 OI Difference Heat")
        st.bar_chart(df["OI Diff"])
    
    with c2:
        st.subheader("📉 Theta Decay Impact")
        st.line_chart(df["Theta"])

    # SUMMARY
    ce_total = df["CE OI"].sum()
    pe_total = df["PE OI"].sum()

    st.subheader("🧠 Market Summary")
    if pe_total > ce_total:
        st.markdown("### 🟢 Bullish Market Bias (Put Writers are Strong)")
    else:
        st.markdown("### 🔴 Bearish Market Bias (Call Writers are Strong)")

# =========================
# INFO
# =========================
st.sidebar.header("Options Greeks Guide")
st.sidebar.info("""
- **Delta:** ధర ఎంత మారుతుందో చెబుతుంది.
- **Theta:** సమయం గడిచేకొద్దీ ప్రీమియం ఎంత తగ్గుతుందో చెబుతుంది.
- **Gamma:** డెల్టా మారే వేగాన్ని చెబుతుంది.
- **Vega:** వోలటాలిటీ (Volatility) ప్రభావాన్ని చెబుతుంది.
""")
st.info("⚠️ Educational Purpose Only - Greeks values are simulated for display stability.")
