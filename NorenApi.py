import requests
import hashlib

class NorenApi:
    def __init__(self, host, websocket=None):
        self.host = host
        self.session = requests.Session()
        self.uid = None

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

        try:
            data = res.json()
            if data.get("stat") == "Ok":
                self.uid = userid
            return data
        except:
            return None

    def search_scrip(self, exch, text):
        url = self.host + "SearchScrip"
        payload = {
            "uid": self.uid,
            "exch": exch,
            "stext": text
        }
        return self.session.post(url, data=payload).json()

    def get_quotes(self, exch, token):
        url = self.host + "GetQuotes"
        payload = {
            "uid": self.uid,
            "exch": exch,
            "token": token
        }
        return self.session.post(url, data=payload).json()
