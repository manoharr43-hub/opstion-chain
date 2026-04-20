import requests
import websocket
import json
import threading

class NorenApi:
    def __init__(self, host, websocket):
        self.host = host
        self.ws_url = websocket
        self.ses = requests.Session()
        self.uid = None

    # =============================
    # LOGIN
    # =============================
    def login(self, userid, password, twoFA, vendor_code, api_secret, imei):
        url = self.host + "QuickAuth"
        data = {
            "uid": userid,
            "pwd": password,
            "factor2": twoFA,
            "vc": vendor_code,
            "appkey": api_secret,
            "imei": imei
        }

        res = self.ses.post(url, data=data)
        try:
            js = res.json()
            if js.get("stat") == "Ok":
                self.uid = userid
            return js
        except:
            return None

    # =============================
    # SEARCH SCRIP
    # =============================
    def search_scrip(self, exchange, searchtext):
        url = self.host + "SearchScrip"
        data = {
            "uid": self.uid,
            "exch": exchange,
            "stext": searchtext
        }

        res = self.ses.post(url, data=data)
        try:
            return res.json()
        except:
            return None

    # =============================
    # GET QUOTES
    # =============================
    def get_quotes(self, exch, token):
        url = self.host + "GetQuotes"
        data = {
            "uid": self.uid,
            "exch": exch,
            "token": token
        }

        res = self.ses.post(url, data=data)
        try:
            return res.json()
        except:
            return None
