import streamlit as st
import pandas as pd

# --- UI సెటప్ ---
st.set_page_config(page_title="NSE AI PRO Terminal", layout="wide")
st.title("🚀 NSE AI PRO - Multi-Table Analyzer")

# --- డేటా క్లీనింగ్ ఫంక్షన్ ---
def clean_numeric(val):
    if isinstance(val, str):
        val = val.replace(',', '').replace('-', '0')
    try:
        return pd.to_numeric(val)
    except:
        return 0

# --- సైడ్ బార్ లో ఫైల్ అప్‌లోడ్స్ ---
st.sidebar.header("📁 Upload Data Files")
file1 = st.sidebar.file_uploader("1. ఆప్షన్ చైన్ CSV అప్‌లోడ్ చేయండి", type="csv", key="file1")
file2 = st.sidebar.file_uploader("2. ఇతర ఇండికేటర్ CSV అప్‌లోడ్ చేయండి", type="csv", key="file2")

# --- ఫైల్ 1: ఆప్షన్ చైన్ అనాలిసిస్ ---
if file1 is not None:
    try:
        df1 = pd.read_csv(file1, skiprows=1)
        df1.columns = df1.columns.str.strip()
        df1 = df1.map(clean_numeric) # నంబర్స్ లోకి మార్చడం

        st.subheader("📊 Option Chain Analysis & Signals")
        
        # Strike Price కాలమ్ గుర్తించడం
        strike_col = [col for col in df1.columns if 'STRIKE' in col.upper()][0]
        
        # కాల్ మరియు పుట్ డేటా విడదీయడం
        strike_idx = df1.columns.get_loc(strike_col)
        ce_df = df1.iloc[:, :strike_idx]
        pe_df = df1.iloc[:, strike_idx+1:]

        # మెయిన్ టేబుల్ సెట్ చేయడం
        display_df = pd.DataFrame({
            "CALL_OI": ce_df.iloc[:, 1],
            "CALL_CHNG": ce_df.iloc[:, 2],
            "STRIKE": df1[strike_col],
            "PUT_CHNG": pe_df.iloc[:, 2],
            "PUT_OI": pe_df.iloc[:, 1]
        })

        # --- Buy/Sell సిగ్నల్ లాజిక్ ---
        def get_signal(row):
            if row['PUT_CHNG'] > row['CALL_CHNG'] * 1.5:
                return "🟢 BUY"
            elif row['CALL_CHNG'] > row['PUT_CHNG'] * 1.5:
                return "🔴 SELL"
            else:
                return "⚪ WAIT"

        display_df['SIGNAL'] = display_df.apply(get_signal, axis=1)

        # టేబుల్ ప్రదర్శన
        st.dataframe(display_df.style.map(lambda x: 'background-color: #2e7d32; color: white' if x == '🟢 BUY' else ('background-color: #c62828; color: white' if x == '🔴 SELL' else ''), subset=['SIGNAL']), use_container_width=True)

    except Exception as e:
        st.error(f"Option Chain Error: {e}")

# --- ఫైల్ 2: ఇతర ఇండికేటర్స్ (VWAP, RSI, మొదలైనవి) ---
if file2 is not None:
    st.divider()
    try:
        df2 = pd.read_csv(file2)
        st.subheader("📈 Other Indicators Data")
        st.write("రెండవ ఫైల్ లోని డేటా ఇక్కడ విడిగా కనిపిస్తుంది:")
        st.dataframe(df2, use_container_width=True)
    except Exception as e:
        st.error(f"Indicator File Error: {e}")

if file1 is None and file2 is None:
    st.info("మనోహర్ గారు, విశ్లేషణ ప్రారంభించడానికి ఎడమ వైపున ఉన్న సైడ్ బార్ లో ఫైల్స్ అప్‌లోడ్ చేయండి.")
    
