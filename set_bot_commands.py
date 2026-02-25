import os
import requests
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("TELEGRAM_BOT_TOKEN")

if not token:
    print("❌ No TELEGRAM_BOT_TOKEN found in .env")
    exit(1)

commands = [
    {"command": "start",   "description": "Welcome message & quick start"},
    {"command": "help",    "description": "Show all commands"},
    {"command": "search",  "description": "Search biomedical literature"},
    {"command": "clear",   "description": "Clear conversation memory"},
    {"command": "history", "description": "View recent conversation"},
    {"command": "about",   "description": "About Maverick AI"},
]

url = f"https://api.telegram.org/bot{token}/setMyCommands"
response = requests.post(url, json={"commands": commands})
data = response.json()

if data.get("ok"):
    print("SUCCESS: Bot commands set!")
    print("Commands registered:")
    for cmd in commands:
        print(f"  /{cmd['command']} - {cmd['description']}")
else:
    print(f"FAILED: {data}")
