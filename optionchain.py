def stock_analysis(symbol):
    try:
        import requests

        symbol = symbol.upper().strip()

        # auto fix NSE format
        if not symbol.endswith(".NS"):
            symbol = symbol + ".NS"

        url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbol}"

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json"
        }

        res = requests.get(url, headers=headers, timeout=5)

        # ❌ EMPTY CHECK FIX
        if not res or len(res.text) < 10:
            return None, None, "⚠ EMPTY RESPONSE (API BLOCKED)"

        # ❌ SAFE JSON PARSE
        try:
            data = res.json()
        except:
            return None, None, "⚠ API BLOCKED / INVALID RESPONSE"

        result = data.get("quoteResponse", {}).get("result", [])

        if not result:
            return None, None, "⚠ STOCK NOT FOUND (TRY RELIANCE.NS)"

        r = result[0]

        price = r.get("regularMarketPrice", None)
        change = r.get("regularMarketChangePercent", None)

        if price is None:
            return None, None, "⚠ NO LIVE DATA"

        # SIGNAL ENGINE
        if change is None:
            change = 0

        if change > 1:
            signal = "🟢 STRONG CALL SIDE"
        elif change < -1:
            signal = "🔴 STRONG PUT SIDE"
        else:
            signal = "🟡 SIDEWAYS"

        return price, change, signal

    except Exception as e:
        return None, None, f"⚠ ERROR: {str(e)}"
