df_hist = t.history(start=bt_date, end=bt_date + timedelta(days=1), interval="15m")

# 🔥 TIME FILTER (NEW)
df_hist = df_hist.between_time("09:15", "15:30")

if not df_hist.empty:
    for i in range(20, len(df_hist)):
        sub_df = df_hist.iloc[:i+1]
        res = analyze_data(sub_df)

        if res and res[1] != "WAIT":
            bt_results.append({
                "Time": sub_df.index[-1].strftime('%H:%M'),
                "Stock": s,
                "Signal": res[1],
                "Big Player": res[2],
                "Entry": res[3],
                "SL": res[4],
                "Target": res[5]
            })
