import os
import sys
import logging
import asyncio
import sqlite3
import socket
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler
from groq import Groq

# --- PRE-FLIGHT LOGGING ---
print(">>> [1/5] MAVERICK SYSTEM BOOTING...", flush=True)

# Configuration
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = "llama3-70b-8192" # Standard Groq Model
DB_FILE = "/tmp/conversation_history.db" # Use /tmp for HF write safety

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- DNS CHECK ---
def check_dns():
    print(">>> [2/5] CHECKING NETWORK CONNECTIVITY...", flush=True)
    for host in ["api.telegram.org", "google.com"]:
        try:
            addr = socket.gethostbyname(host)
            print(f">>> [OK] {host} resolved to {addr}", flush=True)
        except Exception as e:
            print(f">>> [ERROR] Could not resolve {host}: {e}", flush=True)

# --- DATABASE ---
def init_db():
    print(f">>> [3/5] INITIALIZING DATABASE AT {DB_FILE}...", flush=True)
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS history
                     (user_id INTEGER, role TEXT, content TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        conn.commit()
        conn.close()
        print(">>> [OK] DATABASE READY.", flush=True)
    except Exception as e:
        print(f">>> [ERROR] DATABASE FAILED: {e}", flush=True)

def save_message(user_id, role, content):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO history (user_id, role, content) VALUES (?, ?, ?)", (user_id, role, content))
        conn.commit()
        conn.close()
    except: pass

def get_history(user_id, limit=10):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT role, content FROM history WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?", (user_id, limit))
        rows = c.fetchall()
        conn.close()
        return [{"role": r, "content": c} for r, c in reversed(rows)]
    except: return []

def clear_history(user_id):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("DELETE FROM history WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
    except: pass

# --- TELEGRAM HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🦞 *Maverick (Hugging Face Edition) Ready.*\nMemory Active.", parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    user_id = update.effective_user.id
    if not user_text: return
    try:
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        save_message(user_id, "user", user_text)
        client = Groq(api_key=GROQ_API_KEY)
        history = get_history(user_id)
        messages = [{"role": "system", "content": "You are Maverick 🦞."}] + history
        response = client.chat.completions.create(model=MODEL_NAME, messages=messages)
        answer = response.choices[0].message.content
        save_message(user_id, "assistant", answer)
        await update.message.reply_text(answer)
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

# --- MAIN ---
if __name__ == '__main__':
    print(">>> [4/5] CHECKING SECRETS...", flush=True)
    if not TELEGRAM_TOKEN or not GROQ_API_KEY:
        print(">>> [CRITICAL] MISSING API KEYS! Check Settings > Secrets.", flush=True)
        # sys.exit(1) # Don't exit, let's see why it's missing if possible
    
    check_dns()
    init_db()
    
    print(">>> [5/5] CONNECTING TO TELEGRAM...", flush=True)
    try:
        application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        application.add_handler(CommandHandler('start', start))
        application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        print(">>> 🚀 MAVERICK IS FULLY OPERATIONAL!", flush=True)
        application.run_polling(drop_pending_updates=True)
    except Exception as e:
        print(f">>> [FATAL] BOT CRASHED: {e}", flush=True)
