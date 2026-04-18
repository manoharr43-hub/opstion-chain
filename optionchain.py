import requests
import hashlib

def shoonya_login(userid, password, totp, api_secret):
    url = "https://api.shoonya.com/NorenWClientTP/QuickAuth"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    try:
        pwd = hashlib.sha256(password.encode()).hexdigest()
        appkey = hashlib.sha256(api_secret.encode()).hexdigest()

        payload = {
            "uid": userid,
            "pwd": pwd,
            "factor2": totp,
            "vc": userid,   # ⚠️ VERY IMPORTANT FIX
            "appkey": appkey,
            "imei": "123456"
        }

        res = requests.post(url, data=payload, headers=headers, timeout=10)

        # 🔥 DEBUG PRINT
        print("Status:", res.status_code)
        print("Response:", res.text)

        if res.status_code != 200 or res.text.strip() == "":
            return None

        return res.json()

    except Exception as e:
        print("Login Error:", e)
        return None
