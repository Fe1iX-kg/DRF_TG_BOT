import requests
from django.conf import settings


def send_telegram_message(message):
    bot_token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    response = requests.post(url, data=payload)
    if not response.ok:
        print(f"Telegram error: {response.text}, status: {response.status_code}, message: {message}")
    return response