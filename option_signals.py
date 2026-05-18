def generate_signal(latest):

    buy = (
        latest['EMA20'] > latest['EMA50']
        and latest['Close'] > latest['VWAP']
        and latest['RSI'] > 55
    )

    sell = (
        latest['EMA20'] < latest['EMA50']
        and latest['Close'] < latest['VWAP']
        and latest['RSI'] < 45
    )

    if buy:
        return "🚀 BUY"

    elif sell:
        return "🔻 SELL"

    else:
        return "⏳ WAIT"
