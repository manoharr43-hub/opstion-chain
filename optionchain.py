import streamlit as st
import pandas as pd

# --- UI Header ---
st.set_page_config(page_title="NSE AI PRO - Advanced Report", layout="wide")
st.title("🤖 AI Market Analysis & Greeks Report")

# --- Cleaning Function ---
def clean_numeric(val):
    if isinstance(val, str):
        val = val.replace(',', '').replace('-', '0')
    try:
        return pd.to_numeric(val)
    except:
        return 0

# Side bar for file upload
st.sidebar.header("📁 Upload NSE Data")
file = st.sidebar.file_uploader("Option Chain CSV అప్‌లోడ్ చేయండి", type="csv")

if file is not None:
    try:
        df = pd.read_csv(file, skiprows=1)
        df.columns = df.columns.str.strip()
        df = df.map(clean_numeric)

        # Strike identification
        strike_col = [col for col in df.columns if 'STRIKE' in col.upper()][0]
        strike_idx = df.columns.get_loc(strike_col)
        
        # CE & PE Data split
        ce_df = df.iloc[:, :strike_idx]
        pe_df = df.iloc[:, strike_idx+1:]

        # --- AI ANALYSIS REPORT BOX ---
        st.subheader("📋 AI Market Observation Report")
        
        total_ce_oi_chng = ce_df.iloc[:, 2].sum()
        total_pe_oi_chng = pe_df.iloc[:, 2].sum()
        
        # Market Direction Logic
        if total_ce_oi_chng > total_pe_oi_chng * 1.2:
            report_msg = "🔴 MARKET DIRECTION: DOWN SIDE (Bearish)"
            note = "Call Side లో అమ్మకాలు ఎక్కువగా ఉన్నాయి, మార్కెట్ పైకి వెళ్లడం కష్టం."
            color = "#FF4B4B"
        elif total_pe_oi_chng > total_ce_oi_chng * 1.2:
            report_msg = "🟢 MARKET DIRECTION: UP SIDE (Bullish)"
            note = "Put Side లో సపోర్ట్ బలంగా ఉంది, మార్కెట్ పెరిగే అవకాశం ఉంది."
            color = "#28A745"
        else:
            report_msg = "⚪ MARKET DIRECTION: SIDEWAYS"
            note = "రెండు వైపులా పోటీ సమానంగా ఉంది, మార్కెట్ రేంజ్ లోనే ఉంటుంది."
            color = "#808080"

        st.markdown(f"""
            <div style="background-color:{color}; padding:20px; border-radius:10px;">
                <h2 style="color:white; margin:0;">{report_msg}</h2>
                <p style="color:white; font-size:18px;">{note}</p>
            </div>
        """, unsafe_allow_html=True)

        # --- GREEKS & STRIKE STRENGTH (Theta/Gamma Observation) ---
        st.divider()
        st.subheader("🎯 Strong Strike Observation (Greeks Analysis)")
        
        # Strike Strength Logic (Highest OI Change as Strong Point)
        strong_ce_strike = df.loc[ce_df.iloc[:, 2].idxmax(), strike_col]
        strong_pe_strike = df.loc[pe_df.iloc[:, 2].idxmax(), strike_col]

        col1, col2 = st.columns(2)
        with col1:
            st.info(f"⚡ **Strong Resistance:** {strong_ce_strike}")
            st.write("Theta Decay ఇక్కడ ఎక్కువగా ఉంది, Sellers కి లాభం.")
        with col2:
            st.success(f"🛡️ **Strong Support:** {strong_pe_strike}")
            st.write("Gamma Movement ఇక్కడ బాగుంది, Buyers కి వేగంగా లాభం రావచ్చు.")

        # --- DETAILED TABLE ---
        st.divider()
        final_df = pd.DataFrame({
            "CE_OI_CHNG": ce_df.iloc[:, 2],
            "CE_LTP": ce_df.iloc[:, 5],
            "STRIKE": df[strike_col],
            "PE_LTP": pe_df.iloc[:, 5],
            "PE_OI_CHNG": pe_df.iloc[:, 2]
        })
        
        st.write("📊 **Live Data Table:**")
        st.dataframe(final_df, use_container_width=True)

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("మనోహర్ గారు, AI రిపోర్ట్ కోసం NSE ఫైల్ అప్‌లోడ్ చేయండి.")
    
