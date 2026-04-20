import requests
import hashlib
import json

class NorenApi:
    def __init__(self, host, websocket):
        self.host = host
        self.ses = requests.Session()
        self.uid = None

    def login(self, userid, password, twoFA, vendor_code, api_secret, imei):

        # 🔐 Password hashing (IMPORTANT)
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

        res = self.ses.post(url, data=payload)

        try:
            data = res.json()
            if data.get("stat") == "Ok":
                self.uid = userid
            return data
        except:
            return None

    def search_scrip(self, exchange, searchtext):
        url = self.host + "SearchScrip"
        payload = {
            "uid": self.uid,
            "exch": exchange,
            "stext": searchtext
        }
        res = self.ses.post(url, data=payload)
        try:
            return res.json()
        except:
            return None

    def get_quotes(self, exch, token):
        url = self.host + "GetQuotes"
        payload = {
            "uid": self.uid,
            "exch": exch,
            "token": token
        }
        res = self.ses.post(url, data=payload)
        try:
            return res.json()
        except:
            return None
