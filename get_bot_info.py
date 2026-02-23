import os
import requests
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("TELEGRAM_BOT_TOKEN")
if token:
    url = f"https://api.telegram.org/bot{token}/getMe"
    response = requests.get(url)
    print(response.json())
else:
    print("No token found")
