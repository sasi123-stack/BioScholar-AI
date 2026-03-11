import os
import asyncio
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def check_commands():
    if not TOKEN:
        print("Error: No token found!", flush=True)
        return
        
    bot = Bot(token=TOKEN)
    try:
        commands = await bot.get_my_commands()
        print(f"Registered Commands:", flush=True)
        for cmd in commands:
            print(f"- /{cmd.command}: {cmd.description}", flush=True)
            
    except Exception as e:
        print(f"Failed to fetch commands: {e}", flush=True)

if __name__ == "__main__":
    asyncio.run(check_commands())
