
import requests
import websocket
import json

class NorenApi:
    def __init__(self, host, websocket):
        self.host = host
        self.websocket_url = websocket
        self.session = requests.Session()
        self.susertoken = None

    # =========================
    # LOGIN
    # =========================
    def login(self, userid, password, twoFA, vendor_code, api_secret, imei):
        url = self.host + "QuickAuth"

        payload = {
            "uid": userid,
            "pwd": password,
            "factor2": twoFA,
            "vc": vendor_code,
            "appkey": api_secret,
            "imei": imei
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0"
        }

        res = self.session.post(url, data=payload, headers=headers)

        try:
            data = res.json()
        except:
            return {"stat": "Not_Ok", "emsg": res.text}

        if data.get("stat") == "Ok":
            self.susertoken = data.get("susertoken")

        return data

    # =========================
    # GET QUOTES
    # =========================
    def get_quotes(self, exch, token):
        url = self.host + "GetQuotes"

        payload = {
            "uid": "",
            "exch": exch,
            "token": token,
            "susertoken": self.susertoken
        }

        res = self.session.post(url, data=payload)

        try:
            return res.json()
        except:
            return {"stat": "Not_Ok", "emsg": res.text}

    # =========================
    # OPTION CHAIN (BASIC)
    # =========================
    def get_option_chain(self, exch, symbol, strike, count):
        url = self.host + "GetOptionChain"

        payload = {
            "uid": "",
            "exch": exch,
            "tsym": symbol,
            "strprc": strike,
            "cnt": count,
            "susertoken": self.susertoken
        }

        res = self.session.post(url, data=payload)

        try:
            return res.json()
        except:
            return {"stat": "Not_Ok", "emsg": res.text}
