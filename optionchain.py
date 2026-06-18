import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import xgboost as xgb
import concurrent.futures
import warnings

# Warnings తీసేయడానికి
warnings.filterwarnings('ignore')

# ---------------------------------------------------------
# 1. PAGE CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(page_title="NSE AI PRO V11.4", layout="wide", page_icon="🚀")

st.title("🚀 NSE AI PRO V11.4 - Institutional Ultimate")
st.markdown("### Powered by XGBoost, Advanced SMC (BOS/CHOCH/CISD) & ATR Risk Management")
st.markdown("---")

# ---------------------------------------------------------
# 2. STOCK UNIVERSE (Sample Nifty 50 Stocks)
# ---------------------------------------------------------
nifty_stocks = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS", 
    "SBIN.NS", "BHARTIARTL.NS", "ITC.NS", "KOTAKBANK.NS", "LT.NS",
    "TRAVELFOOD.NS", "SYRMA.NS", "AEGISCHEM.NS", "SBICARD.NS"
]

# ---------------------------------------------------------
# 3. CORE FUNCTIONS (Indicators, SMC, CISD, XGBoost)
# ---------------------------------------------------------
def fetch_data(ticker, period="1y"):
    try:
        df = yf.download(ticker, period=period, progress=False)
        if df.empty: return None
        # MultiIndex fix for new yfinance versions
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    except:
        return None

def calculate_indicators(df):
    df = df.copy()
    # EMA for Old Score System
    df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
    df["EMA50"] = df["Close"].ewm(span=50, adjust=False).mean()
    
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # ATR for Target and Stoploss
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    df['ATR'] = true_range.rolling(14).mean()
    
    return df.dropna()

def get_advanced_smc(df):
    """Calculates BOS, CHOCH, and the new CISD (Change In State of Delivery)"""
    try:
        recent_high = float(df['High'].tail(20).max())
        recent_low = float(df['Low'].tail(20).min())
        current_close = float(df['Close'].iloc[-1])
        
        ema20 = float(df['EMA20'].iloc[-1])
        ema50 = float(df['EMA50'].iloc[-1])
        bullish_trend = ema20 > ema50
        
        # 1. BOS & CHOCH Logic
        smc_structure = "Range ➖"
        if current_close > recent_high:
            smc_structure = "BOS 📈" if bullish_trend else "CHOCH 🐂"
        elif current_close < recent_low:
            smc_structure = "BOS 📉" if not bullish_trend else "CHOCH 🐻"
            
        # 2. CISD Logic (Early Reversal Signal)
        prev_high = float(df['High'].iloc[-2])
        prev_low = float(df['Low'].iloc[-2])
        curr_high = float(df['High'].iloc[-1])
        curr_low = float(df['Low'].iloc[-1])
        
        cisd_signal = "None"
        # Bullish CISD: Sweeps previous low, but closes strongly above previous high
        if curr_low < prev_low and current_close > prev_high:
            cisd_signal = "Bullish CISD 🚀"
        # Bearish CISD: Sweeps previous high, but closes weakly below previous low
        elif curr_high > prev_high and current_close < prev_low:
            cisd_signal = "Bearish CISD 🩸"
            
        return smc_structure, cisd_signal
    except:
        return "Range ➖", "None"

def train_xgboost(df):
    try:
        df['Target_Dir'] = np.where(df['Close'].shift(-1) > df['Close'], 1, 0)
        features = ['Open', 'High', 'Low', 'Close', 'Volume', 'RSI', 'ATR']
        
        X = df[features].iloc[:-1]
        y = df['Target_Dir'].iloc[:-1]
        
        model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss', max_depth=3)
        model.fit(X, y)
        
        latest_data = df[features].iloc[-1:]
        prob = model.predict_proba(latest_data)[0]
        
        if prob[1] > 0.5: return "BULLISH 🚀", prob[1] * 100
        else: return "BEARISH 🔻", prob[0] * 100
    except:
        return "N/A", 0

# ---------------------------------------------------------
# 4. MAIN PROCESS ENGINE
# ---------------------------------------------------------
def process_stock(ticker):
    df = fetch_data(ticker)
    if df is None or len(df) < 50: return None
        
    df = calculate_indicators(df)
    
    ltp = float(df['Close'].iloc[-1])
    atr = float(df['ATR'].iloc[-1])
    rsi = float(df['RSI'].iloc[-1])
    
    # Dynamic Risk Management (1:2 Risk/Reward)
    target = ltp + (atr * 2)
    stoploss = ltp - (atr * 1)
    
    # Old Score Logic
    score = (1 if df["EMA20"].iloc[-1] > df["EMA50"].iloc[-1] else -1) + (1 if rsi > 55 else -1)
    signal = "STRONG BUY" if score >= 2 else ("STRONG SELL" if score <= -2 else "WAIT")
    
    # Alerts
    alert = ""
    if rsi > 70: alert = "🚨 RSI Overbought"
    elif rsi < 30: alert = "✅ RSI Oversold"
    
    smc, cisd = get_advanced_smc(df)
    xgb_trend, xgb_conf = train_xgboost(df)
    
    return {
        "Stock": ticker.replace('.NS', ''),
        "LTP": ltp,
        "Target": target,
        "Stoploss": stoploss,
        "Signal": signal,
        "SMC Structure": smc,
        "CISD (Early Signal)": cisd,
        "XGB Trend": xgb_trend,
        "XGB Conf": xgb_conf,
        "Alerts": alert
    }

# ---------------------------------------------------------
# 5. UI & EXECUTION
# ---------------------------------------------------------
if st.button("🔄 Scan Market Now (V11.4 PRO)"):
    with st.spinner("AI is analyzing Institutional Footprints and Liquidity Sweeps..."):
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(process_stock, ticker) for ticker in nifty_stocks]
            for future in concurrent.futures.as_completed(futures):
                res = future.result()
                if res is not None: results.append(res)
        
        if results:
            df_results = pd.DataFrame(results)
            df_results = df_results.sort_values(by="XGB Conf", ascending=False).reset_index(drop=True)
            
            # --- TOP CARDS ---
            st.markdown("### 🔥 Top 4 Institutional AI Picks")
            cols = st.columns(4)
            for i in range(min(4, len(df_results))):
                stock = df_results.iloc[i]
                
                # Show CISD in card if available, else show SMC
                card_tag = stock['CISD (Early Signal)'] if stock['CISD (Early Signal)'] != "None" else stock['SMC Structure']
                
                with cols[i]:
                    st.info(f"""
                    **{stock['Stock']} ({card_tag.replace(' ➖', '')})** ## ₹{stock['LTP']:.2f}  
                    🟢 TGT: ₹{stock['Target']:.2f}  
                    ---
                    SL: ₹{stock['Stoploss']:.2f} | XGB: {stock['XGB Trend'].split(' ')[0]} ({stock['XGB Conf']:.2f}%)
                    """)
            
            st.markdown("---")
            
            # --- RESULTS TABLE (Formatting Decimals) ---
            st.markdown("### 📊 Market Scanner Data")
            display_df = df_results.copy()
            
            # Formatting floats to 2 decimals
            display_df['LTP'] = display_df['LTP'].map('{:.2f}'.format)
            display_df['Target'] = display_df['Target'].map('{:.2f}'.format)
            display_df['Stoploss'] = display_df['Stoploss'].map('{:.2f}'.format)
            display_df['XGB Conf'] = display_df['XGB Conf'].apply(lambda x: f"{x:.2f}%")
            
            def highlight_cells(val):
                if isinstance(val, str):
                    if any(word in val for word in ["BULLISH", "STRONG BUY", "BOS 📈", "CHOCH 🐂", "Bullish CISD"]): 
                        return 'color: green; font-weight: bold'
                    if any(word in val for word in ["BEARISH", "STRONG SELL", "BOS 📉", "CHOCH 🐻", "Bearish CISD", "Overbought"]): 
                        return 'color: red; font-weight: bold'
                    if "Oversold" in val: return 'color: green'
                return ''
            
            st.dataframe(display_df.style.map(highlight_cells), use_container_width=True)
            
            # --- EXCEL / CSV DOWNLOAD BUTTON ---
            st.markdown("---")
            csv_data = df_results.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Excel/CSV Report",
                data=csv_data,
                file_name=f'NSE_AI_PRO_V11.4_Report.csv',
                mime='text/csv'
            )

        else:
            st.error("No data fetched. Please check your internet connection or stock list.")
