# =============================
# BIG PLAYER DETECTION
# =============================
df["Signal"] = ""

for i in range(len(df)):

    call_change = df.loc[i, "Call_Change"]
    put_change = df.loc[i, "Put_Change"]

    # Strong Buy
    if put_change > 3000 and call_change < 0:
        df.loc[i, "Signal"] = "🟢 BIG BUY"

    # Strong Sell
    elif call_change > 3000 and put_change < 0:
        df.loc[i, "Signal"] = "🔴 BIG SELL"

    else:
        df.loc[i, "Signal"] = "—"
