# 📊 Shoonya Pro Option Chain (NIFTY & BANKNIFTY)

Shoonya (Finvasia) API ఆధారంగా రూపొందించబడిన రియల్-టైమ్ ఆప్షన్ చైన్ అనలిటిక్స్ టూల్. ఇది నేరుగా బ్రోకర్ API నుండి డేటాను తీసుకుంటుంది, కాబట్టి NSE క్లౌడ్ రిస్ట్రిక్షన్స్ (Cloud Restrictions) లేకుండా వేగంగా పనిచేస్తుంది.

## ✨ ఫీచర్లు (Features)
- **Live Spot Price:** నిఫ్టీ మరియు బ్యాంక్ నిఫ్టీ యొక్క ఖచ్చితమైన లైవ్ ధర.
- **Official API Data:** Shoonya API వాడటం వల్ల ఎటువంటి డేటా బ్లాకింగ్ ఉండదు.
- **Side-by-Side View:** కాల్స్ (CE) మరియు పుట్స్ (PE) ఒకే స్ట్రైక్ ప్రైస్ వద్ద చూడవచ్చు.
- **Auto Refresh:** ప్రతి 15 సెకన్లకు (లేదా మీకు నచ్చిన సమయంలో) డేటా ఆటోమేటిక్‌గా అప్‌డేట్ అవుతుంది.
- **TOTP Automation:** `pyotp` ఉపయోగించి ఆటోమేటిక్ లాగిన్ సదుపాయం.

## 🛠️ ఇన్‌స్టాలేషన్ (Setup Instructions)

### 1. లైబ్రరీలను ఇన్‌స్టాల్ చేయండి:
```bash
pip install NorenRestApiPy pyotp pandas streamlit
git add app.py requirements.txt .streamlit/secrets.toml
git commit -m "Add app.py, requirements.txt, secrets.toml"
git push origin main

