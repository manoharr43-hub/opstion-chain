import streamlit as st
import pandas as pd
import numpy as np

# --- UI Layout ---
st.set_page_config(page_title="NSE AI PRO - Individual View", layout="wide")
st.title("🚀 NSE AI PRO - Individual Analyzer")

uploaded_file = st.file_uploader("NSE CSV ఫైల్‌ను ఇక్కడ అప్‌లోడ్ చేయండి", type="csv")

if uploaded_file is not None:
    try:
        # NSE CSV రీడింగ్
        df = pd.read_csv(uploaded_file, skiprows=1)
        df.columns = df.columns.str.strip()

        # Strike Price కాలమ్ ని గుర్తించడం
        strike_col = [col for col in df.columns if 'STRIKE' in col.upper()][0]
        
        # డేటాను నంబర్స్ లోకి మార్చడం (Cleaning)
        def clean_data(val):
            if isinstance(val, str):
                val = val.replace(',', '').replace('-', '0')
            try:
                return pd.to_numeric(val)
            except:
                return 0

        df = df.applymap(clean_data)

        # మధ్యలో ఉండే Strike Price కి ఇటు అటు డేటాను విడదీయడం
        strike_idx = df.columns.get_loc(strike_col)
        ce_df = df.iloc[:, :strike_idx]
        pe_df = df.iloc[:, strike_idx+1:]

        # --- మార్కెట్ ట్రెండ్ అనాలిసిస్ ---
        # సాధారణంగా 2వ కాలమ్ OI ఉంటుంది
        total_ce_oi = ce_df.iloc[:, 1].sum() 
        total_pe_oi = pe_df.iloc[:, 1].sum()
        pcr = round(total_pe_oi / total_ce_oi, 2) if total_ce_oi > 0 else 0
        
        direction = "SIDEWAYS"
        color = "white"
        if pcr > 1.2:
            direction = "BULLISH (పైకి)"
            color = "#00FF00"
        elif pcr < 0.8:
            direction = "BEARISH (కిందకి)"
            color = "#FF0000"

        st.markdown(f"""
            <div style="background-color:{color}; padding:15px; border-radius:10px; text-align:center;">
                <h2 style="color:black; margin:0;">Market Direction: {direction} | PCR: {pcr}</h2>
            </div>
        """, unsafe_allow_html=True)
        st.divider()

        # --- ఇండివిడ్యువల్ షో (CE | STRIKE | PE) ---
        st.subheader("📋 Option Chain (Individual View)")
        
        final_view = pd.DataFrame({
            "CALLS_OI": ce_df.iloc[:, 1],
            "CALLS_CHNG_OI": ce_df.iloc[:, 2],
            "CALLS_LTP": ce_df.iloc[:, 5],
            "STRIKE": df[strike_col],
            "PUTS_LTP": pe_df.iloc[:, 5],
            "PUTS_CHNG_OI": pe_df.iloc[:, 2],
            "PUTS_OI": pe_df.iloc[:, 1]
        })

        # టేబుల్ ని అందంగా చూపడం
        def color_oi(val):
            color = 'green' if val > 0 else 'red'
            return f'color: {color}'

        st.dataframe(final_view.style.applymap(color_oi, subset=['CALLS_CHNG_OI', 'PUTS_CHNG_OI']), use_container_width=True)

        # --- Buy/Sell సిగ్నల్స్ ---
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            st.success("🟢 Buy Zone (Strong Support)")
            buy_zone = final_view.nlargest(5, 'PUTS_CHNG_OI')[['STRIKE', 'PUTS_CHNG_OI', 'PUTS_LTP']]
            st.table(buy_zone)
        with col2:
            st.error("🔴 Sell Zone (Strong Resistance)")
            sell_zone = final_view.nlargest(5, 'CALLS_CHNG_OI')[['STRIKE', 'CALLS_CHNG_OI', 'CALLS_LTP']]
            st.table(sell_zone)

    except Exception as e:
        st.error(f"Analysis Error: {e}")
else:
    st.info("NSE CSV ఫైల్‌ను అప్‌లోడ్ చేయండి. అప్పుడు మీకు Calls మరియు Puts విడివిడిగా కనిపిస్తాయి.")
    
