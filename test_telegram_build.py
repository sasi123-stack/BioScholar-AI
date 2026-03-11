import os
import asyncio
from telegram.ext import ApplicationBuilder
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def main():
    print(f"Token: {TOKEN[:10]}...", flush=True)
    try:
        app = ApplicationBuilder().token(TOKEN).build()
        print("Application built!", flush=True)
        # We don't start polling, just check if it builds
    except Exception as e:
        print(f"Error: {e}", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
