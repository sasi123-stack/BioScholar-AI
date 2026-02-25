import socket
import os
import sys

# --- DNS GLOBAL MONKEYPATCH ---
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
import sqlite3
import threading
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler
from groq import Groq
from flask import Flask
from telegram.request import HTTPXRequest

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
        return [{"role": r, "content": ct} for r, ct in reversed(rows)]
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
            body { margin:0; font-family:'Inter',sans-serif; background:#0f172a; color:#f8fafc;
                   display:flex; flex-direction:column; align-items:center; justify-content:center;
                   min-height:100vh; text-align:center; }
            h1 { font-size:3rem; font-weight:800; margin:0 0 16px;
                 background:linear-gradient(135deg,#fff,#94a3b8); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
            p { color:#94a3b8; max-width:480px; line-height:1.6; margin:0 0 32px; }
            a.btn { display:inline-flex; align-items:center; gap:10px; padding:14px 28px;
                    background:#0088cc; color:white; text-decoration:none; font-weight:700;
                    border-radius:50px; box-shadow:0 8px 24px rgba(0,136,204,0.4);
                    transition:all 0.3s; }
            a.btn:hover { transform:translateY(-2px); box-shadow:0 12px 32px rgba(0,136,204,0.6); }
        </style>
    </head>
    <body>
        <div style="font-size:72px;margin-bottom:16px;">💠</div>
        <h1>Maverick AI Bot</h1>
        <p>Premium Biomedical Intelligence. Powered by Llama 4 Maverick via Groq.</p>
        <a href="https://t.me/Meverick_AI_bot" class="btn">Open in Telegram</a>
        <p style="margin-top:24px;font-size:0.85rem;color:#475569;">
            Web App: <a href="https://biomed-scholar.web.app" style="color:#38bdf8;">biomed-scholar.web.app</a>
        </p>
    </body>
    </html>
    """

@app.route('/logs')
def get_logs():
    try:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r") as f:
                return f.read(), 200, {'Content-Type': 'text/plain'}
        return "Log file not found", 404
    except Exception as e:
        return str(e), 500

def run_flask():
    print(">>> [3/5] STARTING HEALTH CHECK PORT 7860...", flush=True)
    app.run(host='0.0.0.0', port=7860)

# --- SYSTEM PROMPT ---
SYSTEM_PROMPT = """You are Maverick (a biomedical research AI assistant built into BioMedScholar AI.
You specialize in:
- PubMed literature analysis and synthesis
- Clinical trial interpretation and eligibility criteria
- Drug mechanisms, pharmacology, and interactions
- Medical terminology explanations
- Evidence-based medicine and study design critique
- Biostatistics and research methodology

Always be precise, cite evidence levels where possible, and use medical terminology appropriately.
If asked about something outside biomedical research, politely redirect to your specialty.
Format responses clearly with bullet points or numbered lists when appropriate."""

# --- COMMAND HANDLERS (all use plain Markdown, NOT MarkdownV2) ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name or "Researcher"
    msg = (
        f"*Welcome to Maverick, {user_name}!*\n\n"
        "I'm your AI-powered biomedical research assistant. I can help you with:\n"
        "🔬 PubMed literature analysis\n"
        "🧪 Clinical trial interpretation\n"
        "💊 Drug mechanisms & pharmacology\n"
        "📊 Research methodology & stats\n\n"
        "*Available Commands:*\n"
        "/help - Show all commands\n"
        "/search <query> - Biomedical literature search\n"
        "/clear - Clear conversation memory\n"
        "/history - View recent conversation\n"
        "/about - About Maverick AI\n"
        "/test - Open BioMedScholar AI website\n\n"
        "Or just type your research question to get started!"
    )
    await update.message.reply_text(msg, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "*Maverick Command Reference*\n\n"
        "*/start* - Welcome message and quick start\n"
        "*/help* - Show this help menu\n"
        "*/search* <query> - Quick biomedical search\n"
        "*/clear* - Clear your conversation history\n"
        "*/history* - Show your last 5 messages\n"
        "*/about* - About Maverick AI\n"
        "*/test* - Open BioMedScholar AI website\n\n"
        "*Tips:*\n"
        "- Just type any question for AI analysis\n"
        "- Ask about drugs, trials, studies, diseases\n"
        "- Request literature summaries or comparisons\n"
        "- Ask for simple explanations of complex topics\n\n"
        "Web App: https://biomed-scholar.web.app"
    )
    await update.message.reply_text(msg, parse_mode='Markdown')

async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    clear_history(user_id)
    await update.message.reply_text("*Conversation cleared!*\nMemory wiped. Starting fresh.", parse_mode='Markdown')

async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    query = ' '.join(context.args)
    if not query:
        await update.message.reply_text(
            "Please provide a search query.\n*Usage:* /search diabetes treatment 2024",
            parse_mode='Markdown'
        )
        return
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    try:
        client = Groq(api_key=GROQ_API_KEY)
        search_prompt = (
            f'The user wants to search biomedical literature for: "{query}"\n\n'
            "Please provide:\n"
            "1. A brief overview of this research topic (2-3 sentences)\n"
            "2. Key findings from recent literature (bullet points)\n"
            "3. Important clinical considerations\n"
            "4. Suggested search terms to refine further\n\n"
            "Be concise and evidence-based."
        )
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": search_prompt}
            ]
        )
        answer = response.choices[0].message.content
        save_message(user_id, "user", f"/search {query}")
        save_message(user_id, "assistant", answer)
        await update.message.reply_text(f"*Search: {query}*\n\n{answer}", parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Search error: {e}")
        await update.message.reply_text(f"Search failed. Please try again.\nError: {str(e)[:100]}")

async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    hist = get_history(user_id, limit=10)
    if not hist:
        await update.message.reply_text("No conversation history yet. Start chatting!")
        return
    lines = ["*Recent Conversation:*\n"]
    for msg in hist[-5:]:
        icon = "You" if msg['role'] == 'user' else "Maverick"
        content = msg['content'][:120] + "..." if len(msg['content']) > 120 else msg['content']
        lines.append(f"*{icon}:* {content}")
    await update.message.reply_text('\n\n'.join(lines), parse_mode='Markdown')

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "*About Maverick AI*\n\n"
        "Maverick is the AI research engine powering BioMedScholar AI, "
        "a platform for evidence-based biomedical research.\n\n"
        "*Powered by:* Llama 4 Maverick via Groq\n"
        "*Specialties:* PubMed, Clinical Trials, Drug Research\n"
        "*Memory:* Per-user conversation history\n"
        "*Web App:* https://biomed-scholar.web.app\n\n"
        "Built for the biomedical research community."
    )
    await update.message.reply_text(msg, parse_mode='Markdown')

async def test_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Open BioMedScholar AI", url="https://biomed-scholar.web.app")],
        [InlineKeyboardButton("PubMed Search", url="https://biomed-scholar.web.app/#articles")],
        [InlineKeyboardButton("Maverick AI Chat", url="https://biomed-scholar.web.app/#chat")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    msg = (
        "*BioMedScholar AI - Web Platform*\n\n"
        "Access the full research platform with:\n"
        "🔬 35M+ PubMed articles\n"
        "🧪 Clinical trial database\n"
        "🤖 Maverick AI chat\n"
        "📊 Research trends & analytics\n\n"
        "Click below to open:"
    )
    await update.message.reply_text(msg, parse_mode='Markdown', reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    user_id = update.effective_user.id
    if not user_text:
        return
    try:
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        save_message(user_id, "user", user_text)
        client = Groq(api_key=GROQ_API_KEY)
        history = get_history(user_id, limit=10)
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history
        response = client.chat.completions.create(model=MODEL_NAME, messages=messages, max_tokens=1024)
        answer = response.choices[0].message.content
        if "💠" not in answer[:15]:
            answer = "💠 " + answer
        save_message(user_id, "assistant", answer)
        # Split long messages (Telegram 4096 char limit)
        if len(answer) > 4000:
            for i in range(0, len(answer), 4000):
                await update.message.reply_text(answer[i:i+4000])
        else:
            await update.message.reply_text(answer)
    except Exception as e:
        logger.error(f"Message handler error: {e}")
        await update.message.reply_text(f"Error processing your request. Please try again.\n{str(e)[:100]}")

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

        application.add_handler(CommandHandler('start',   start))
        application.add_handler(CommandHandler('help',    help_command))
        application.add_handler(CommandHandler('clear',   clear_command))
        application.add_handler(CommandHandler('search',  search_command))
        application.add_handler(CommandHandler('history', history_command))
        application.add_handler(CommandHandler('about',   about_command))
        application.add_handler(CommandHandler('test',    test_command))
        application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

        print(">>> MAVERICK IS FULLY OPERATIONAL!", flush=True)
        logger.info("Bot started: /start /help /clear /search /history /about /test")
        application.run_polling(drop_pending_updates=True)
    except Exception as e:
        print(f">>> [FATAL] BOT CRASHED: {e}", flush=True)
        logger.critical(f"Bot crashed: {e}")
