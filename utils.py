import requests

def telegram_alert(message):

    bot_token = "YOUR_BOT_TOKEN"

    chat_id = "YOUR_CHAT_ID"

    url = (
        f"https://api.telegram.org/bot"
        f"{bot_token}/sendMessage"
    )

    payload = {
        "chat_id": chat_id,
        "text": message
    }

    requests.post(
        url,
        data=payload
    )
