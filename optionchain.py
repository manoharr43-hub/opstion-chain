@st.cache_data(ttl=60)
def get_option_chain_data():
    try:
        session = requests.Session()

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive"
        }

        # Step 1: Get cookies properly
        session.get("https://www.nseindia.com", headers=headers, timeout=10)
        time.sleep(2)

        # Step 2: API call
        url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
        response = session.get(url, headers=headers, timeout=15)

        if response.status_code != 200:
            st.error(f"Blocked (Status {response.status_code})")
            return None

        data = response.json()

        # 🔥 IMPORTANT FIX
        if "records" not in data or "data" not in data["records"]:
            st.error("⚠ NSE blocked or empty response")
            return None

        rows = []
        for item in data["records"]["data"]:

            strike = item.get("strikePrice", 0)

            call_oi = item.get("CE", {}).get("openInterest", 0)
