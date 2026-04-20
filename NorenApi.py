import requests
import hashlib
import json

class NorenApi:
    def __init__(self, host, websocket=None):
        self.host = host
        self.session = requests.Session()
        self.uid = None

        # ✅ IMPORTANT HEADERS (without this login fails)
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded"
        })

    # =============================
    # LOGIN
    # =============================
    def login(self, userid, password, twoFA, vendor_code, api_secret, imei):

        pwd = hashlib.sha256(password.encode()).hexdigest()
        appkey = hashlib.sha256((userid + "|" + api_secret).encode()).hexdigest()

        url = self.host + "QuickAuth"

        payload = {
            "uid": userid,
            "pwd": pwd,
            "factor2": twoFA,
            "vc": vendor_code,
            "appkey": appkey,
            "imei": imei
        }

        res = self.session.post(url, data=payload)

        print("RAW RESPONSE:", res.text)  # 🔥 DEBUG

        try:
            data = res.json()
            if data.get("stat") == "Ok":
                self.uid = userid
            return data
        except:
            return None

    # =============================
    # SEARCH
    # =============================
    def search_scrip(self, exch, text):
        url = self.host + "SearchScrip"
        payload = {
            "uid": self.uid,
            "exch": exch,
            "stext": text
        }
        return self.session.post(url, data=payload).json()

    # =============================
    # QUOTES
    # =============================
    def get_quotes(self, exch, token):
        url = self.host + "GetQuotes"
        payload = {
            "uid": self.uid,
            "exch": exch,
            "token": token
        }
        return self.session.post(url, data=payload).json()
