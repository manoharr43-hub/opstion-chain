# 🚀 NSE AI PRO MAX V10 FINAL CLEAN CODE
import streamlit as st, yfinance as yf, pandas as pd, numpy as np
import requests, hashlib, json, time, pytz
import plotly.graph_objects as go
from datetime import datetime

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(page_title="NSE AI PRO MAX V10", page_icon="🚀", layout="wide")

# =========================================================
# SHOONYA API CLASS
# =========================================================
class ShoonyaAPI:
    BASE_URL = "https://api.shoonya.com/NorenWClientTP"
    def __init__(self):
        self.session_token = None
        self.user_id = None
        self.headers = {"Content-Type": "application/x-www-form-urlencoded"}
        self.token_cache = {}

    def login(self, user_id, password, totp, vendor_code, api_secret):
        pwd_hash = hashlib.sha256(password.encode()).hexdigest()
        app_key = f"{user_id}|{api_secret}"
        app_key_hash = hashlib.sha256(app_key.encode()).hexdigest()
        payload = f"jData={{\"uid\":\"{user_id}\",\"pwd\":\"{pwd_hash}\",\"factor2\":\"{totp}\",\"vc\":\"{vendor_code}\",\"appkey\":\"{app_key_hash}\",\"source\":\"API\"}}"
        response = requests.post(f"{self.BASE_URL}/QuickAuth", data=payload, headers=self.headers)
        data = response.json()
        if data.get("stat") == "Ok":
            self.session_token = data.get("susertoken")
            self.user_id = user_id
            return True
        return False

    def _post(self, endpoint, jdata):
        payload = f"jData={json.dumps(jdata)}&jKey={self.session_token}"
        response = requests.post(f"{self.BASE_URL}/{endpoint}", data=payload, headers=self.headers)
        return response.json()

    def get_quote(self, exchange, symbol):
        token_data = self._post("SearchScrip", {"uid": self.user_id, "stext": symbol, "exch": exchange})
        token = token_data["values"][0]["token"]
        return self._post("GetQuotes", {"uid": self.user_id, "exch": exchange, "token": token})

# =========================================================
# INDICATORS
# =========================================================
def calculate_indicators(df):
    df["EMA20"] = df["Close"].ewm(span=20).mean()
    df["EMA50"] = df["Close"].ewm(span=50).mean()
    delta = df["Close"].diff()
    gain, loss = delta.clip(lower=0), -delta.clip(upper=0)
    rs = gain.rolling(14).mean() / (loss.rolling(14).mean() + 1e-10)
    df["RSI"] = 100 - (100 / (1 + rs))
    ema12, ema26 = df["Close"].ewm(span=12).mean(), df["Close"].ewm(span=26).mean()
    df["MACD"], df["MACD_SIGNAL"] = ema12 - ema26, (ema12 - ema26).ewm(span=9).mean()
    df["VWAP"] = (df["Close"] * df["Volume"]).cumsum() / (df["Volume"].cumsum() + 1e-10)
    return df

def generate_signal(latest):
    score = 0
    score += 25 if latest["EMA20"] > latest["EMA50"] else -25
    score += 20 if 55 <= latest["RSI"] <= 70 else -15
    score += 25 if latest["MACD"] > latest["MACD_SIGNAL"] else -25
    score += 20 if latest["Close"] > latest["VWAP"] else -20
    signal = "🚀 STRONG BUY" if score >= 70 else "✅ BUY" if score >= 30 else "🔻 SELL" if score <= -30 else "⚠️ SIDEWAYS"
    return signal, score
