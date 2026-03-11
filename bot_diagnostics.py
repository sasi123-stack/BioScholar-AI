import os
import asyncio
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def check_bot():
    print(f"Using Token: {TOKEN[:10]}...", flush=True)
    if not TOKEN:
        print("Error: No token found!", flush=True)
        return
        
    bot = Bot(token=TOKEN)
    try:
        me = await bot.get_me()
        print(f"Bot info retrieved successfully!", flush=True)
        print(f"Name: {me.first_name}", flush=True)
        print(f"Username: @{me.username}", flush=True)
        
        # Try to update description to see if we have full control
        description = "Maverick AI 🦞: Advanced research intelligence. Powered by GPT OSS 120B."
        await bot.set_my_description(description)
        print("Updated bot description to GPT OSS 120B!", flush=True)
        
    except Exception as e:
        print(f"Failed to connect to Telegram: {e}", flush=True)

if __name__ == "__main__":
    asyncio.run(check_bot())
