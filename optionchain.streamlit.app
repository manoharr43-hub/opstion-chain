def option_chain():
    try:
        url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"

        session = requests.Session()

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.nseindia.com/",
            "Connection": "keep-alive"
        }

        # 🔥 IMPORTANT (cookie set)
        session.get("https://www.nseindia.com", headers=headers)

        response = session.get(url, headers=headers)

        if response.status_code != 200:
            return None, None, None

        data = response.json()

        records = data['records']['data']

        rows = []
        for item in records:
            rows.append({
                "Strike": item['strikePrice'],
                "Call OI": item.get('CE', {}).get('openInterest', 0),
                "Put OI": item.get('PE', {}).get('openInterest', 0)
            })

        df = pd.DataFrame(rows)

        if df.empty:
            return None, None, None

        support = df.loc[df['Put OI'].idxmax()]['Strike']
        resistance = df.loc[df['Call OI'].idxmax()]['Strike']

        return df, support, resistance

    except Exception as e:
        return None, None, None
