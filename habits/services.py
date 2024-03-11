import requests
from requests import Response

from config.settings import TELEGRAM_BOT_TOKEN


def tg_send_message(message: str, chat_id: str | int) -> Response | None:
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    data = {
        'chat_id': chat_id,
        'text': message
    }
    response = requests.post(url, data=data)
    return response
