import socket
import os
import sys

# --- DNS GLOBAL MONKEYPATCH ---
# Hugging Face Spaces often have flaky DNS resolution for external APIs.
_original_getaddrinfo = socket.getaddrinfo

DNS_PRIORITY_HOSTS = ["api.telegram.org", "api.groq.com", "google.com", "huggingface.co"]
TELEGRAM_IPS = ["149.154.167.220", "149.154.167.219", "149.154.167.221"]

def custom_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    host_str = host.decode('utf-8') if isinstance(host, bytes) else str(host)
    host_clean = host_str.lower().strip('.')
    if any(h in host_clean for h in DNS_PRIORITY_HOSTS):
        try:
            import dns.resolver
            resolver = dns.resolver.Resolver()
            resolver.nameservers = ['8.8.8.8', '1.1.1.1', '8.8.4.4']
            resolver.timeout = 2
            resolver.lifetime = 2
            answers = resolver.resolve(host_clean, 'A')
            if answers:
                ips = [str(ans) for ans in answers]
                return [(socket.AF_INET, type if type != 0 else socket.SOCK_STREAM, proto if proto != 0 else 6, '', (ip, int(port) if port else 443)) for ip in ips]
        except: pass
        if "telegram" in host_clean:
            return [(socket.AF_INET, type if type != 0 else socket.SOCK_STREAM, proto if proto != 0 else 6, '', (ip, int(port) if port else 443)) for ip in TELEGRAM_IPS]
    try:
        return _original_getaddrinfo(host, port, family, type, proto, flags)
    except Exception as e:
        raise e

socket.getaddrinfo = custom_getaddrinfo
print(">>> [DNS PATCH] Priority-based socket monkeypatch applied.", flush=True)

import logging
import asyncio
import sqlite3
import threading
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler
from groq import Groq
from flask import Flask
from telegram.request import HTTPXRequest

# --- PRE-FLIGHT LOGGING ---
print(">>> [1/5] MAVERICK SYSTEM BOOTING...", flush=True)

# Configuration
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = "meta-llama/llama-4-maverick-17b-128e-instruct" 
DB_FILE = "/tmp/conversation_history.db" 

LOG_FILE = "/tmp/maverick_bot.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# --- DATABASE ---
def init_db():
    print(f">>> [2/5] INITIALIZING DATABASE AT {DB_FILE}...", flush=True)
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

# --- FLASK ---
app = Flask(__name__)
@app.route('/')
def landing():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Maverick AI | BioMedScholar</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
        <style>
            :root {
                --primary: #0088cc;
                --bg: #0f172a;
                --text: #f8fafc;
                --accent: #38bdf8;
            }
            body {
                margin: 0;
                padding: 0;
                font-family: 'Inter', sans-serif;
                background-color: var(--bg);
                color: var(--text);
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                min-height: 100vh;
                text-align: center;
                overflow: hidden;
            }
            .background {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: radial-gradient(circle at 50% 50%, #1e293b 0%, #0f172a 100%);
                z-index: -1;
            }
            .lobster-icon {
                font-size: 80px;
                margin-bottom: 20px;
                filter: drop-shadow(0 0 20px rgba(0, 136, 204, 0.4));
                animation: float 3s ease-in-out infinite;
            }
            @keyframes float {
                0%, 100% { transform: translateY(0); }
                50% { transform: translateY(-10px); }
            }
            h1 {
                font-size: 3.5rem;
                font-weight: 800;
                margin: 0;
                letter-spacing: -1px;
                background: linear-gradient(135deg, #fff 0%, #94a3b8 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            p {
                font-size: 1.2rem;
                color: #94a3b8;
                max-width: 500px;
                margin: 20px 0 40px;
                line-height: 1.6;
            }
            .cta-button {
                display: inline-flex;
                align-items: center;
                gap: 12px;
                padding: 16px 32px;
                background-color: var(--primary);
                color: white;
                text-decoration: none;
                font-weight: 700;
                font-size: 1.1rem;
                border-radius: 50px;
                box-shadow: 0 10px 25px rgba(0, 136, 204, 0.4);
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            .cta-button:hover {
                transform: translateY(-3px) scale(1.02);
                box-shadow: 0 15px 35px rgba(0, 136, 204, 0.6);
                background-color: #0099e6;
            }
            .badge {
                padding: 6px 12px;
                background: rgba(56, 189, 248, 0.15);
                color: var(--accent);
                border-radius: 20px;
                font-size: 0.8rem;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-bottom: 30px;
                border: 1px solid rgba(56, 189, 248, 0.2);
            }
            .footer {
                position: absolute;
                bottom: 40px;
                color: #475569;
                font-size: 0.9rem;
            }
        </style>
    </head>
    <body>
        <div class="background"></div>
        <div class="badge">Experimental Research AI</div>
        <div class="lobster-icon">🦞</div>
        <h1>Maverick AI</h1>
        <p>Advanced Biomedical Intelligence powered by Llama 4. Persistent research memory on your favorite messaging platform.</p>
        
        <a href="https://web.telegram.org/a/#8513211167" target="_blank" class="cta-button">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
            </svg>
            Open in Telegram
        </a>

        <div class="footer">
            &copy; 2026 BioMedScholar AI • Maverick Standalone Instance
        </div>
    </body>
    </html>
    """


@app.route('/logs')
def get_logs():
    try:
        if os.path.exists("/tmp/maverick_bot.log"):
            with open("/tmp/maverick_bot.log", "r") as f:
                return f.read(), 200, {'Content-Type': 'text/plain'}
        return "Log file not found", 404
    except Exception as e:
        return str(e), 500

def run_flask():
    print(">>> [3/5] STARTING HEALTH CHECK PORT 7860...", flush=True)
    app.run(host='0.0.0.0', port=7860)

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
        sys.exit(1)
    
    init_db()
    threading.Thread(target=run_flask, daemon=True).start()
    
    print(">>> [5/5] CONNECTING TO TELEGRAM...", flush=True)
    try:
        request = HTTPXRequest(connect_timeout=30, read_timeout=30, write_timeout=30)
        application = ApplicationBuilder().token(TELEGRAM_TOKEN).request(request).build()
        application.add_handler(CommandHandler('start', start))
        application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        print(">>> 🚀 MAVERICK IS FULLY OPERATIONAL!", flush=True)
        application.run_polling(drop_pending_updates=True)
    except Exception as e:
        print(f">>> [FATAL] BOT CRASHED: {e}", flush=True)
