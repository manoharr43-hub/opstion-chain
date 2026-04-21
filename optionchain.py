import streamlit as st
import pandas as pd
import numpy as np

# --- UI Layout ---
st.set_page_config(page_title="NSE AI PRO - Individual Analyzer", layout="wide")
st.title("🚀 NSE AI PRO - Individual Analyzer")

uploaded_file = st.file_uploader("NSE CSV ఫైల్‌ను ఇక్కడ అప్‌లోడ్ చేయండి", type="csv")

if uploaded_file is not None:
    try:
        # NSE CSV రీడింగ్
        df = pd.read_csv(uploaded_file, skiprows=1)
        df.columns = df.columns.str.strip()

        # Strike Price కాలమ్ ని గుర్తించడం
        strike_col = [col for col in df.columns if 'STRIKE' in col.upper()][0]
        
        # డేటాను నంబర్స్ లోకి మార్చడం (Cleaning Logic)
        def clean_data(val):
            if isinstance(val, str):
                val = val.replace(',', '').replace('-', '0')
            try:
                num = pd.to_numeric(val)
                return num
            except:
                return 0

        # ఇక్కడ 'applymap' బదులు 'map' వాడుతున్నాను (కొత్త Pandas వెర్షన్ కోసం)
        df = df.map(clean_data)

        # Strike Price ఆధారంగా డేటాను విడదీయడం
        strike_idx = df.columns.get_loc(strike_col)
        ce_df = df.iloc[:, :strike_idx]
        pe_df = df.iloc[:, strike_idx+1:]

        # --- మార్కెట్ అనాలిసిస్ ---
        total_ce_oi = ce_df.iloc[:, 1].sum() 
        total_pe_oi = pe_df.iloc[:, 1].sum()
        pcr = round(total_pe_oi / total_ce_oi, 2) if total_ce_oi > 0 else 0
        
        direction = "SIDEWAYS"
        color = "#808080" # Gray
        if pcr > 1.2:
            direction = "BULLISH (మార్కెట్ పైకి వెళ్ళవచ్చు)"
            color = "#008000" # Green
        elif pcr < 0.8:
            direction = "BEARISH (మార్కెట్ కిందకి పడవచ్చు)"
            color = "#FF0000" # Red

        st.markdown(f"""
            <div style="background-color:{color}; padding:15px; border-radius:10px; text-align:center;">
                <h2 style="color:white; margin:0;">Trend: {direction} | PCR: {pcr}</h2>
            </div>
        """, unsafe_allow_html=True)
        st.divider()

        # --- టేబుల్ షో ---
        st.subheader("📋 Individual Option Chain View")
        
        final_view = pd.DataFrame({
            "CALLS_OI": ce_df.iloc[:, 1],
            "CALLS_CHNG_OI": ce_df.iloc[:, 2],
            "CALLS_LTP": ce_df.iloc[:, 5],
            "STRIKE": df[strike_col],
            "PUTS_LTP": pe_df.iloc[:, 5],
            "PUTS_CHNG_OI": pe_df.iloc[:, 2],
            "PUTS_OI": pe_df.iloc[:, 1]
        })

        # కలరింగ్ లాజిక్
        def color_values(val):
            if isinstance(val, (int, float)):
                return 'color: green' if val > 0 else 'color: red'
            return ''

        # ఇక్కడ కూడా కొత్త పద్ధతిలో స్టైలింగ్
        st.dataframe(final_view.style.map(color_values, subset=['CALLS_CHNG_OI', 'PUTS_CHNG_OI']), use_container_width=True)

        # --- Top 5 సిగ్నల్స్ ---
        st.divider()
        c1, c2 = st.columns(2)
        with c1:
            st.success("🟢 Buy/Support Zone")
            st.table(final_view.nlargest(5, 'PUTS_CHNG_OI')[['STRIKE', 'PUTS_CHNG_OI', 'PUTS_LTP']])
        with c2:
            st.error("🔴 Sell/Resistance Zone")
            st.table(final_view.nlargest(5, 'CALLS_CHNG_OI')[['STRIKE', 'CALLS_CHNG_OI', 'CALLS_LTP']])

    except Exception as e:
        st.error(f"Analysis Error: {str(e)}")
else:
    st.info("NSE ఆప్షన్ చైన్ ఫైల్‌ను అప్‌లోడ్ చేయండి.")
    
