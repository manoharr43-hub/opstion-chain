# =============================
# 🔥 V7 PRO ADD-ON (NO CHANGE TO OLD CODE)
# =============================

import requests

# TELEGRAM SETTINGS (OPTIONAL)
TELEGRAM_TOKEN = ""
CHAT_ID = ""

def send_telegram(msg):
    if TELEGRAM_TOKEN == "" or CHAT_ID == "":
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except:
        pass


# BACKTEST FUNCTION
def backtest_accuracy(df):
    correct = 0
    total = 0

    for i in range(50, len(df)-1):
        try:
            if df['Close'][i] > df['EMA50'][i]:
                if df['Close'][i+1] > df['Close'][i]:
                    correct += 1
                total += 1
        except:
            continue

    if total == 0:
        return 0

    return round((correct/total)*100,2)


# =============================
# 🎯 ENHANCED DISPLAY TABLE
# =============================
if 'df_result' in locals() and not df_result.empty:

    enhanced_results = []

    for stock in stocks_to_scan:
        try:
            df = data[stock].dropna()
            df = calculate_indicators(df)

            latest = df.iloc[-1]
            price = latest['Close']

            # OPTION SIGNAL
            signal = df_result[df_result['Stock'] == stock]['Signal'].values[0]

            if "BUY" in signal:
                option = "🟢 CE"
            elif "SELL" in signal:
                option = "🔴 PE"
            else:
                option = "⚖️ WAIT"

            # TARGET / SL
            target = price * 1.02
            stoploss = price * 0.98

            # CONFIDENCE
            score = df_result[df_result['Stock'] == stock]['Score'].values[0]
            confidence = min(100, score * 15)

            # ACCURACY
            accuracy = backtest_accuracy(df)

            enhanced_results.append({
                "Stock": stock,
                "Price": round(price,2),
                "Signal": signal,
                "Option": option,
                "Confidence %": confidence,
                "Accuracy %": accuracy,
                "Target": round(target,2),
                "Stoploss": round(stoploss,2)
            })

            # TELEGRAM ALERT (STRONG BUY ONLY)
            if "STRONG BUY" in signal:
                msg = f"""
🔥 STRONG BUY ALERT

📊 {stock}
💰 Price: {round(price,2)}
🎯 Target: {round(target,2)}
🛑 SL: {round(stoploss,2)}
📈 Confidence: {confidence}%
                """
                send_telegram(msg)

        except:
            continue

    df_enhanced = pd.DataFrame(enhanced_results)

    st.markdown("## 🚀 PRO AI TRADE PANEL")
    st.dataframe(df_enhanced.sort_values(by="Confidence %", ascending=False), use_container_width=True)
