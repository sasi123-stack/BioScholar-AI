import os
import sys
import logging
import sqlite3
import socket
import time
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler
from groq import Groq
from telegram.request import HTTPXRequest

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

# --- DNS CUSTOM RESOLVER ---
def resolve_hostname(host):
    """
    Attempts to resolve hostname using system first, then falls back to custom DNS
    if dnspython is available.
    """
    try:
        addr = socket.gethostbyname(host)
        return addr
    except Exception as e:
        print(f">>> [SYSTEM DNS FAILED] {host}: {e}. Trying custom DNS...", flush=True)
        try:
            import dns.resolver
            resolver = dns.resolver.Resolver()
            resolver.nameservers = ['8.8.8.8', '1.1.1.1'] # Google and Cloudflare
            answers = resolver.resolve(host, 'A')
            if answers:
                addr = str(answers[0])
                print(f">>> [CUSTOM DNS SUCCESS] {host} resolved to {addr}", flush=True)
                return addr
        except Exception as e2:
            print(f">>> [CUSTOM DNS FAILED] {host}: {e2}", flush=True)
    return None

def check_dns(retries=5):
    print(">>> [2/5] CHECKING NETWORK CONNECTIVITY...", flush=True)
    hosts = ["api.telegram.org", "google.com", "api.groq.com"]
    for host in hosts:
        success = False
        for i in range(retries):
            addr = resolve_hostname(host)
            if addr:
                print(f">>> [OK] {host} resolved to {addr}", flush=True)
                success = True
                break
            else:
                if i < retries - 1:
                    print(f">>> [RETRY {i+1}] {host} failed. Waiting 10s...", flush=True)
                    time.sleep(10)
                else:
                    print(f">>> [ERROR] Final failure resolving {host}", flush=True)
        if not success and host == "api.telegram.org":
            print(">>> [WARNING] Telegram API unreachable. Space may have restricted egress.", flush=True)

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
    
    check_dns()
    init_db()
    
    print(">>> [5/5] CONNECTING TO TELEGRAM...", flush=True)
    try:
        # Robust request settings for potentially restricted/slow networks
        # We increase the connection pool size and timeouts
        request = HTTPXRequest(connect_timeout=30, read_timeout=30, write_timeout=30)
        
        application = ApplicationBuilder().token(TELEGRAM_TOKEN).request(request).build()
        application.add_handler(CommandHandler('start', start))
        application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        
        print(">>> 🚀 MAVERICK IS FULLY OPERATIONAL!", flush=True)
        application.run_polling(drop_pending_updates=True)
    except Exception as e:
        print(f">>> [FATAL] BOT CRASHED: {e}", flush=True)
        sys.exit(1)
