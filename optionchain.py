import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import io
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Machine Learning Modules
from xgboost import XGBClassifier
from sklearn.preprocessing import StandardScaler

# ==========================================
# 1. PAGE SETUP & CONFIGURATION
# ==========================================
st.set_page_config(page_title="HYBRID NSE PRO SCANNER V11.0", layout="wide", page_icon="⚡")

st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .css-1r6slp0 { padding: 2rem; }
    .stSidebar { background-color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

st.title("⚡ HYBRID NSE PRO SCANNER - V11.0 PRO")
st.markdown("**Institutional Edition | Smart Money Concepts (BOS/CHOCH) | XGBoost Machine Learning Predictive Engine**")

if 'v11_data' not in st.session_state:
    st.session_state.v11_data = pd.DataFrame()

# ==========================================
# 2. SIDEBAR CONFIGURATION
# ==========================================
with st.sidebar:
    st.header("⚙️ Settings & Controls")
    auto_refresh = st.checkbox("🔄 Auto Refresh (Every 3 Mins)")
    interval = st.selectbox("Interval", ["5m","15m","30m","1h","1d"], index=1)
    period = st.selectbox("Period", ["5d","1mo","3mo","6mo", "1y"], index=1)
    
    sector_stocks = {
        "Banking": ["HDFCBANK","ICICIBANK","SBIN","AXISBANK","KOTAKBANK"],
        "IT": ["TCS","INFY","WIPRO","HCLTECH","TECHM"],
        "Pharma": ["SUNPHARMA","CIPLA","DIVISLAB","DRREDDY"],
        "Energy": ["RELIANCE","ONGC","BPCL","NTPC"],
        "Auto": ["TATAMOTORS","M&M","EICHERMOT","HEROMOTOCO"],
        "FMCG": ["ITC","HINDUNILVR","BRITANNIA","DABUR"]
    }
    sector = st.selectbox("Sector", ["All NSE500"] + list(sector_stocks.keys()))
    
    st.markdown("---")
    run_button = st.button("🚀 RUN V11 PRO SCANNER", type="primary", use_container_width=True)

# ==========================================
# 3. CORE MATHEMATICS & AI ENGINE
# ==========================================
@st.cache_data(ttl=86400)
def load_nse500():
    import requests
    try:
        url = "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=5)
        df = pd.read_csv(io.StringIO(response.text))
        return sorted(df["Symbol"].dropna().unique().tolist())
    except:
        return ["RELIANCE","TCS","INFY","HDFCBANK","ICICIBANK","SBIN","ITC","LT","AXISBANK"]

stocks = load_nse500()

@st.cache_data(ttl=120)
def get_data(symbol, interval, period):
    try:
        df = yf.download(f"{symbol}.NS" if "^" not in symbol else symbol, interval=interval, period=period, auto_adjust=True, progress=False)
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        return df
    except:
        return pd.DataFrame()

def calculate_smc_structures(df):
    """Smart Money Concepts: BOS & CHOCH Engine"""
    if len(df) < 30:
        return "Normal", "Normal"
        
    # Swing Highs / Lows detection using rolling thresholds
    df['Local_High'] = df['High'].rolling(window=10, center=True).max()
    df['Local_Low'] = df['Low'].rolling(window=10, center=True).min()
    
    last_high = df['Local_High'].ffill().iloc[-2]
    last_low = df['Local_Low'].ffill().iloc[-2]
    current_close = df['Close'].iloc[-1]
    current_open = df['Open'].iloc[-1]
    
    smc_structure = "Range"
    smc_alert = "Normal"
    
    # Trend alignment logic for BOS vs CHOCH
    ema20 = df['Close'].ewm(span=20).mean().iloc[-1]
    ema50 = df['Close'].ewm(span=50).mean().iloc[-1]
    bullish_trend = ema20 > ema50
    
    if current_close > last_high:
        if bullish_trend:
            smc_structure = "BOS 📈"  # Break of Structure (Continuation)
            smc_alert = "Structure Broken Upward"
        else:
            smc_structure = "CHOCH 🔄" # Change of Character (Reversal)
            smc_alert = "Trend Reversal Bullish"
            
    elif current_close < last_low:
        if not bullish_trend:
            smc_structure = "BOS 📉"  # Break of Structure Downward
            smc_alert = "Structure Broken Downward"
        else:
            smc_structure = "CHOCH 🔄" # Change of Character Bearish
            smc_alert = "Trend Reversal Bearish"
            
    return smc_structure, smc_alert

def train_xgboost_predictor(df):
    """XGBoost Predictive Intelligence Vector Engine"""
    if len(df) < 50:
        return "Neutral", 0.0
        
    try:
        # Features building matrix
        df_ml = df.copy()
        df_ml['Return'] = df_ml['Close'].pct_change()
        df_ml['RSI_Norm'] = df_ml['RSI'] / 100.0
        df_ml['Vol_Ratio'] = df_ml['Volume'] / df_ml['AVG_VOL']
        df_ml['EMA_Gap'] = (df_ml['EMA20'] - df_ml['EMA50']) / df_ml['EMA50']
        
        # Target Binary Classification (1 if next close is higher, 0 if lower)
        df_ml['Target_Direction'] = np.where(df_ml['Close'].shift(-1) > df_ml['Close'], 1, 0)
        df_ml.dropna(inplace=True)
        
        if len(df_ml) < 30:
            return "Neutral", 0.0
            
        feature_cols = ['Return', 'RSI_Norm', 'Vol_Ratio', 'EMA_Gap']
        X = df_ml[feature_cols].values
        y = df_ml['Target_Direction'].values
        
        # Super fast optimized training execution sequence for cloud metrics
        model = XGBClassifier(n_estimators=15, max_depth=3, learning_rate=0.1, eval_metric='logloss', random_state=42)
        model.fit(X[:-1], y[:-1])
        
        # Predict latest row vector
        latest_vector = X[-1].reshape(1, -1)
        prediction = model.predict(latest_vector)[0]
        probabilities = model.predict_proba(latest_vector)[0]
        confidence = round(probabilities[prediction] * 100, 2)
        
        ai_signal = "BULLISH 🚀" if prediction == 1 else "BEARISH 🔻"
        return ai_signal, confidence
    except:
        return "Neural", 0.0

def calculate_supertrend(df, period=10, multiplier=3):
    high, low, close = df['High'], df['Low'], df['Close']
    tr = np.maximum(high - low, np.maximum(abs(high - close.shift(1)), abs(low - close.shift(1))))
    atr = tr.rolling(window=period).mean()
    hl2 = (high + low) / 2
    upperband, lowerband = hl2 + (multiplier * atr), hl2 - (multiplier * atr)
    supertrend, direction = np.zeros(len(df)), np.zeros(len(df))
    
    for i in range(1, len(df)):
        if close.iloc[i] > upperband.iloc[i-1]: direction[i] = 1
        elif close.iloc[i] < lowerband.iloc[i-1]: direction[i] = -1
        else: direction[i] = direction[i-1]
            
        if direction[i] == 1:
            lowerband.iloc[i] = max(lowerband.iloc[i], lowerband.iloc[i-1])
            supertrend[i] = lowerband.iloc[i]
        else:
            upperband.iloc[i] = min(upperband.iloc[i], upperband.iloc[i-1])
            supertrend[i] = upperband.iloc[i]
    df['Supertrend'], df['ST_Direction'] = supertrend, direction
    return df

def get_candlestick_pattern(df):
    if len(df) < 2: return "None"
    O1, C1 = df['Open'].iloc[-2], df['Close'].iloc[-2]
    O2, C2, H2, L2 = df['Open'].iloc[-1], df['Close'].iloc[-1], df['High'].iloc[-1], df['Low'].iloc[-1]
    body = abs(C2 - O2)
    rng = H2 - L2 if (H2 - L2) > 0 else 0.001
    if body <= (rng * 0.1): return "Doji"
    if C1 < O1 and C2 > O2 and O2 < C1 and C2 > O1: return "Bullish Engulfing"
    if C1 > O1 and C2 < O2 and O2 > C1 and C2 < O1: return "Bearish Engulfing"
    lower_shadow, upper_shadow = min(O2, C2) - L2, H2 - max(O2, C2)
    if lower_shadow > 2 * body and upper_shadow < 0.2 * body: return "Hammer"
    return "Normal"

def add_indicators(df, interval):
    if len(df) < 60: return df
    df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
    df["EMA50"] = df["Close"].ewm(span=50, adjust=False).mean()
    delta = df["Close"].diff()
    df["RSI"] = 100 - (100 / (1 + (delta.clip(lower=0).ewm(com=13, adjust=False).mean() / -delta.clip(upper=0).ewm(com=13, adjust=False).mean())))
    df["MACD_Line"] = df["Close"].ewm(span=12, adjust=False).mean() - df["Close"].ewm(span=26, adjust=False).mean()
    df["Signal_Line"] = df["MACD_Line"].ewm(span=9, adjust=False).mean()
    
    tp = (df['High'] + df['Low'] + df['Close']) / 3
    if 'd' not in interval and 'wk' not in interval and 'mo' not in interval:
        df['Date'] = df.index.date
        df['VWAP'] = (df['Volume'] * tp).groupby(df['Date']).cumsum() / df['Volume'].groupby(df['Date']).cumsum()
    else:
        df['VWAP'] = (df['Volume'] * tp).rolling(20).sum() / df['Volume'].rolling(20).sum()

    df = calculate_supertrend(df)
    df['Pivot'] = (df['High'].shift(1) + df['Low'].shift(1) + df['Close'].shift(1)) / 3
    df['Resistance_1'] = (2 * df['Pivot']) - df['Low'].shift(1)
    df['Support_1'] = (2 * df['Pivot']) - df['High'].shift(1)
    df["AVG_VOL"] = df["Volume"].rolling(20).mean()
    
    df['H-L'] = df['High'] - df['Low']
    df['H-PC'] = abs(df['High'] - df['Close'].shift(1))
    df['L-PC'] = abs(df['Low'] - df['Close'].shift(1))
    df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1)
    df['ATR'] = df['TR'].rolling(window=14).mean()
    return df

# ==========================================
# 4. MASTER PROCESSOR THREAD
# ==========================================
def process_stock_thread(symbol, interval, period, h52w, l52w, nifty_return, daily_close_series):
    df = get_data(symbol, interval, period)
    if df.empty or len(df) < 60: return None
    df = add_indicators(df, interval)
    close = float(df["Close"].iloc[-1])
    score = 0
    
    stock_return = ((close - df['Close'].iloc[0]) / df['Close'].iloc[0]) * 100
    rs_score = round(stock_return - nifty_return, 2) if nifty_return is not None else 0
    rs_status = "💪 Outperform" if rs_score > 0 else "📉 Underperform"

    # [V11 PRO FEATURE] - Smart Money Concepts (BOS/CHOCH)
    smc_structure, smc_alert = calculate_smc_structures(df)

    # [V11 PRO FEATURE] - XGBoost Predictive Intelligence Inference Vector
    xgb_prediction, xgb_confidence = train_xgboost_predictor(df)
    
    mtf_status = "Not Aligned"
    if daily_close_series is not None and len(daily_close_series) >= 50:
        d_ema20 = daily_close_series.ewm(span=20, adjust=False).mean().iloc[-1]
        d_ema50 = daily_close_series.ewm(span=50, adjust=False).mean().iloc[-1]
        if (d_ema20 > d_ema50) == (df["EMA20"].iloc[-1] > df["EMA50"].iloc[-1]):
            mtf_status = "ALIGNED 🟢" if (d_ema20 > d_ema50) else "ALIGNED 🔻"

    alerts = []
    vol_spike = "Normal"
    if float(df["Volume"].iloc[-1]) > float(df["AVG_VOL"].iloc[-1]) * 3:
        vol_spike = "🔥 SPIKE"
        alerts.append("🔥 Vol Spike")
        
    rsi_val = float(df["RSI"].iloc[-1])
    if rsi_val > 70: alerts.append("🚨 RSI Overbought")
    elif rsi_val < 30: alerts.append("⚠️ RSI Oversold")
    if smc_alert != "Normal": alerts.append(f"🏛️ {smc_structure}")
    
    breakout_high = df["High"].rolling(20).max().shift(1).iloc[-1]
    breakout_low = df["Low"].rolling(20).min().shift(1).iloc[-1]
    brk_sig = "NO"
    if close > breakout_high: brk_sig, _ = "BULLISH", alerts.append("📈 Breakout High")
    elif close < breakout_low: brk_sig, _ = "BEARISH", alerts.append("📉 Breakout Low")
        
    pattern = get_candlestick_pattern(df)
    if pattern in ["Bullish Engulfing", "Hammer"]: alerts.append(f"✨ {pattern}")
    alert_str = ", ".join(alerts) if alerts else "No Alerts"

    macd_val = "BULLISH" if df["MACD_Line"].iloc[-1] > df["Signal_Line"].iloc[-1] else "BEARISH"
    st_dir = "UP" if df["ST_Direction"].iloc[-1] == 1 else "DOWN"
    vwap_sig = "ABOVE" if close > float(df["VWAP"].iloc[-1]) else "BELOW"
    
    # Master Scoring Matrix
    if df["EMA20"].iloc[-1] > df["EMA50"].iloc[-1]: score += 1
    else: score -= 1
    if rsi_val > 60: score += 1
    elif rsi_val < 40: score -= 1
    if macd_val == "BULLISH": score += 1
    else: score -= 1
    if st_dir == "UP": score += 1
    else: score -= 1
    if vwap_sig == "ABOVE": score += 1
    else: score -= 1
    if brk_sig == "BULLISH": score += 1
    elif brk_sig == "BEARISH": score -= 1
    if smc_structure in ["BOS 📈", "CHOCH 🔄"]: score += 1

    signal = "STRONG BUY" if score >= 4 else "BUY" if score >= 2 else "STRONG SELL" if score <= -4 else "SELL" if score <= -2 else "WAIT"

    # AI ATR Target & SL Engine
    target, stoploss = "-", "-"
    try:
        atr_val = float(df["ATR"].iloc[-1])
        if pd.notna(atr_val) and atr_val > 0:
            if signal in ["STRONG BUY", "BUY"]:
                stoploss = round(close - (1.5 * atr_val), 2)
                target = round(close + (3.0 * atr_val), 2)
            elif signal in ["STRONG SELL", "SELL"]:
                stoploss = round(close + (1.5 * atr_val), 2)
                target = round(close - (3.0 * atr_val), 2)
    except: pass

    status_52w = "Mid Range"
    if h52w and l52w:
        if close >= h52w * 0.97: status_52w = "🟢 Near High"
        elif close <= l52w * 1.03: status_52w = "🔴 Near Low"

    return [
        symbol.replace('.NS', ''), round(close, 2), target, stoploss, smc_structure, xgb_prediction, f"{xgb_confidence}%", alert_str, mtf_status, ai_trend, f"{ai_conf}%", f"{rs_score}% ({rs_status})",
        round(float(df["Support_1"].iloc[-1]), 2), round(float(df["Resistance_1"].iloc[-1]), 2),
        round(h52w, 2) if h52w else "N/A", round(l52w, 2) if l52w else "N/A", status_52w,
        round(rsi_val, 2), brk_sig, macd_val, st_dir, vwap_sig, pattern, vol_spike, score, signal
    ]

def color_code(val):
    if isinstance(val, str):
        if any(x in val for x in ["STRONG BUY", "BULLISH", "UP", "ABOVE", "SPIKE", "Outperform", "🟢", "BOS 📈", "CHOCH 🔄"]): return 'color: green; font-weight: bold;'
        if any(x in val for x in ["STRONG SELL", "BEARISH", "DOWN", "BELOW", "Underperform", "🔻", "🚨", "BOS 📉"]): return 'color: red; font-weight: bold;'
    return ''

# ==========================================
# 5. UI TABS & RUN EXECUTION
# ==========================================
tab1, tab2 = st.tabs(["🚀 V11 PRO Master Dashboard", "🔍 Custom Stock Search"])

with tab1:
    if run_button or auto_refresh:
        selected_stocks = stocks if sector == "All NSE500" else sector_stocks[sector]
        nifty_df = get_data("^NSEI", interval, period)
        nifty_return = ((nifty_df['Close'].iloc[-1] - nifty_df['Close'].iloc[0]) / nifty_df['Close'].iloc[0]) * 100 if not nifty_df.empty else 0

        st.write("⚡ Executing XGBoost Predictive Logic and Smart Money Framework Matrix...")
        high_52w_dict, low_52w_dict, daily_series_dict = {}, {}, {}
        try:
            bulk_df = yf.download([f"{s}.NS" for s in selected_stocks], period="1y", interval="1d", progress=False, auto_adjust=True)
            for s in selected_stocks:
                t = f"{s}.NS"
                try:
                    if isinstance(bulk_df.columns, pd.MultiIndex):
                        high_52w_dict[s], low_52w_dict[s], daily_series_dict[s] = bulk_df['High'][t].max(), bulk_df['Low'][t].min(), bulk_df['Close'][t].dropna()
                    else:
                        high_52w_dict[s], low_52w_dict[s], daily_series_dict[s] = bulk_df['High'].max(), bulk_df['Low'].min(), bulk_df['Close'].dropna()
                except: pass
        except: pass

        progress = st.progress(0)
        results = []

        with ThreadPoolExecutor(max_workers=15) as executor:
            future_to_stock = {
                executor.submit(process_stock_thread, sym, interval, period, high_52w_dict.get(sym), low_52w_dict.get(sym), nifty_return, daily_series_dict.get(sym)): sym for sym in selected_stocks
            }
            for i, future in enumerate(as_completed(future_to_stock)):
                res = future.result()
                if res: results.append(res)
                progress.progress((i + 1) / len(selected_stocks))

        if results:
            df_res = pd.DataFrame(
                results, 
                columns=["Stock", "LTP", "Target", "Stoploss", "SMC Structure", "XGB Trend", "XGB Conf", "⚡ Alerts", "MTF Trend", "AI Trend", "Conf %", "RS vs NIFTY", "Support", "Resistance", "52W High", "52W Low", "52W Status", "RSI", "Breakout", "MACD", "Supertrend", "VWAP", "Pattern", "Volume", "Score", "Signal"]
            )
            df_res = df_res.sort_values(by="Score", ascending=False)
            st.session_state.v11_data = df_res
            
            buy_count = sum(1 for r in results if r[-1] == 'STRONG BUY')
            if buy_count > 0: st.toast(f"🔥 V11 PRO ACTION ALERT: {buy_count} STRONG BUY Signals!", icon='⚡')

    if not st.session_state.v11_data.empty:
        final_df = st.session_state.v11_data
        
        st.markdown("### 🏆 Top Institutional Breakouts (V11 PRO)")
        top_stocks = final_df[final_df['Signal'] == 'STRONG BUY'].sort_values(by='Score', ascending=False)
        
        if not top_stocks.empty:
            cols = st.columns(4)
            for i, (index, row) in enumerate(top_stocks.head(4).iterrows()):
                with cols[i]:
                    st.metric(label=f"🟢 {row['Stock']} ({row['SMC Structure']})", value=f"₹{row['LTP']}", delta=f"TGT: ₹{row['Target']}")
                    st.caption(f"**SL:** ₹{row['Stoploss']} | **XGB:** {row['XGB Trend']} ({row['XGB Conf']})")
        else:
            st.info("ప్రస్తుతం ఎటువంటి Institutional STRONG BUY సిగ్నల్స్ లేవు.")
            
        st.markdown("---")
        styled_df = final_df.style.map(color_code, subset=['Signal', 'SMC Structure', 'XGB Trend', '⚡ Alerts', 'MTF Trend', 'AI Trend', 'RS vs NIFTY', 'Breakout', 'MACD', 'Supertrend', 'VWAP', 'Volume'])
        st.dataframe(styled_df, use_container_width=True)
        
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            styled_df.to_excel(writer, index=False, sheet_name='V11_Live_Scanner')
        st.download_button("📥 Download V11 PRO Excel Report", data=buffer.getvalue(), file_name="V11_PRO_Master_Report.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    if auto_refresh:
        time.sleep(180)
        st.rerun()

# ---- TAB 2: CUSTOM STOCK SEARCH ----
with tab2:
    st.markdown("### 🔍 Search Any NSE Stock (V11 Machine Learning Engine)")
    search_query = st.text_input("Enter Stock Symbol (e.g., ITC, RELIANCE):").upper()
    
    if st.button("🔍 Run Deep AI Analytics"):
        if search_query:
            with st.spinner(f"Analyzing {search_query} vectors..."):
                res = process_stock_thread(search_query, interval, period, None, None, 0, None)
                if res:
                    st.success(f"V11.0 Analysis Complete for {search_query}")
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("LTP", f"₹{res[1]}")
                    c2.metric("SMC Structure", res[4])
                    c3.metric("XGBoost AI Forecast", res[5], delta=res[6])
                    c4.metric("Dynamic Target", f"₹{res[2]}")
                    
                    st.markdown("##### ⚙️ Technical Blueprint Details:")
                    st.write(f"- **Stoploss:** ₹{res[3]} | **Support (S1):** ₹{res[12]} | **Resistance (R1):** ₹{res[13]}")
                    st.write(f"- **AI Linear Trend:** {res[9]} ({res[10]}) | **Alerts:** {res[7]}")
                else:
                    st.error("Stock not found. Please verify spelling.")
