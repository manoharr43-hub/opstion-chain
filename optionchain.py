def stock_analysis(symbol):
    try:
        import requests

        symbol = symbol.upper().strip()

        # auto NSE format fix
        if not symbol.endswith(".NS"):
            symbol = symbol + ".NS"

        url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbol}"

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json,text/plain,*/*"
        }

        res = requests.get(url, headers=headers, timeout=5)

        # ❌ EMPTY CHECK
        if res is None or res.text.strip() == "":
            return None, None, "⚠ EMPTY RESPONSE (API BLOCKED)"

        # ❌ SAFE JSON PARSE
        try:
            data = res.json()
        except:
            return None, None, "⚠ DATA NOT JSON (BLOCKED)"

        result = data.get("quoteResponse", {}).get("result", [])

        if not result:
            return None, None, "⚠ STOCK NOT FOUND"

        result = result[0]

        price = result.get("regularMarketPrice", 0)
        change = result.get("regularMarketChangePercent", 0)

        if price == 0:
            return None, None, "⚠ NO LIVE DATA"

        # SIGNAL ENGINE
        if change >= 1:
            signal = "🟢 CALL SIDE STRONG"
        elif change <= -1:
            signal = "🔴 PUT SIDE STRONG"
        else:
            signal = "🟡 SIDEWAYS"

        return price, change, signal

    except Exception as e:
        return None, None, f"⚠ ERROR: {str(e)}"
