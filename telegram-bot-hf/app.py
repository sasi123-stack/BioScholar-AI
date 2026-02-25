import socket
import os
import sys
import logging
import sqlite3
import threading
import re
from flask import Flask, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler, CallbackQueryHandler
from groq import Groq
from telegram.request import HTTPXRequest

# --- DNS GLOBAL MONKEYPATCH (For stability on Hugging Face) ---
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

# Configuration
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = "meta-llama/llama-4-maverick-17b-128e-instruct"
DB_FILE = "/tmp/conversation_history.db"  # Use /tmp for HF Spaces

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize Database
def init_db():
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS history
                     (user_id INTEGER, role TEXT, content TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Database init failed: {e}")

def save_message(user_id, role, content):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO history (user_id, role, content) VALUES (?, ?, ?)", (user_id, role, content))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Save message failed: {e}")

def get_history(user_id, limit=10):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT role, content FROM history WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?", (user_id, limit))
        rows = c.fetchall()
        conn.close()
        return [{"role": r, "content": c} for r, c in reversed(rows)]
    except Exception as e:
        logger.error(f"Get history failed: {e}")
        return []

def clear_history(user_id):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("DELETE FROM history WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Clear history failed: {e}")

init_db()

# Initialize Groq Client
try:
    groq_client = Groq(api_key=GROQ_API_KEY)
except Exception as e:
    logger.error(f"Failed to initialize Groq client: {e}")
    groq_client = None

# System Prompt
SYSTEM_PROMPT = """You are Maverick, the official BioMedScholar AI Research Engine. 
You are a sharp, precise, and analytical biomedical research assistant.
vibe: Sharp, precise, analytical, and highly efficient. emoji: 💠.
You are powered by Llama 4 Maverick architecture via Groq.
You have PERSISTENT LONG-TERM MEMORY and specialized research discovery skills.

Always be precise, cite evidence levels where possible, and use medical terminology appropriately.
Ignore any previous roleplay styles; maintain a strict scientist persona.
Format responses clearly with bullet points or numbered lists when appropriate."""

# Flask app for health checks
flask_app = Flask(__name__)

@flask_app.route('/')
def health():
    return "Maverick AI Research Engine is online."

@flask_app.route('/api/v1/health')
def health_v1():
    return jsonify({"status": "synced", "message": "Maverick AI is operational", "engine": "Llama 4 Maverick"})

def run_flask():
    flask_app.run(host='0.0.0.0', port=7860)

# Helper for safe Markdown rendering
def safe_markdown(text):
    """Strip characters that break Telegram Markdown parser."""
    # Escape underscores that are not part of a pair
    text = re.sub(r'(?<!\s)_(?!\s)', r'\_', text)
    return text

# Command Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name or "Researcher"
    msg = (
        f"💠 *Welcome to Maverick Suite, {user_name}!*\n\n"
        "Unified Research Engine with active knowledge memory. I am specifically "
        "optimized for medical literature, clinical trials, and deep scientific audits.\n\n"
        "*AUTHORIZED SKILLS:*\n"
        "• `/search <topic>`: Deep-web academic research.\n"
        "• `/help`: Show all available commands.\n"
        "• `/clear`: Reset research memory.\n"
        "• `/history`: View recent conversation.\n"
        "• `/test`: Launch technical audit.\n\n"
        "Or just type any research question to begin."
    )
    await update.message.reply_text(msg, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "💠 *Maverick Command Reference*\n\n"
        "*/start* - Welcome message and quick start\n"
        "*/help* - Show this help menu\n"
        "*/search* <query> - Deep biomedical literature search\n"
        "*/clear* - Clear your conversation history\n"
        "*/history* - Show your last messages\n"
        "*/about* - About Maverick AI Research Engine\n"
        "*/test* - Analyze website or open platform\n\n"
        "Web App: [biomed-scholar.web.app](https://biomed-scholar.web.app)"
    )
    await update.message.reply_text(msg, parse_mode='Markdown')

async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    clear_history(user_id)
    await update.message.reply_text("💠 *Memory cleared!* Starting fresh. 🧹", parse_mode='Markdown')

async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    hist = get_history(user_id, limit=6)
    if not hist:
        await update.message.reply_text("No conversation history yet. Start researching!")
        return
    
    lines = ["💠 *Recent Research Activity:*\n"]
    for msg in hist[-4:]:
        role = "User" if msg['role'] == 'user' else "Maverick"
        content = msg['content'][:150] + "..." if len(msg['content']) > 150 else msg['content']
        lines.append(f"• *{role}*: {content}")
    
    await update.message.reply_text('\n\n'.join(lines), parse_mode='Markdown')

async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = ' '.join(context.args)
    if not query:
        await update.message.reply_text("💠 Usage: `/search <topic>`", parse_mode='Markdown')
        return

    user_id = update.effective_user.id
    await update.message.reply_text(
        f"💠 *Maverick Search Initiative*: Synthesizing biomedical literature for `{query}`...",
        parse_mode='Markdown'
    )
    prompt = (
        f'Conduct a comprehensive biomedical literature synthesis for: "{query}".\n\n'
        "Please provide:\n"
        "1. Overview of this research topic (2-3 sentences)\n"
        "2. Key findings from recent literature (bullet points)\n"
        "3. Important clinical considerations\n"
        "4. Evidence quality and study design insights\n\n"
        "Be precise and evidence-based."
    )
    save_message(user_id, "user", f"/search {query}")
    await ai_reply(update, user_id, prompt, save_user_msg=False)

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "💠 *About Maverick AI*\n\n"
        "Maverick is the premium AI research engine powering BioMedScholar AI. "
        "Built for evidence-based biomedical discovery.\n\n"
        "*Architecture:* Llama 4 Maverick (17B Optimized)\n"
        "*Provider:* Groq Intelligence\n"
        "*Capabilities:* RAG-enhanced synthesis, Clinical trial auditing, Real-time literature discovery.\n\n"
        "Official Web Platform: https://biomed-scholar.web.app"
    )
    await update.message.reply_text(msg, parse_mode='Markdown')

async def test_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    url = context.args[0] if context.args else None

    if url:
        # Perform AI analysis of the given URL
        await update.message.reply_text(
            f"💠 *Maverick Audit Initiative*: Launching technical analysis for `{url}`...",
            parse_mode='Markdown'
        )
        prompt = (
            f"Perform a technical audit and content analysis of this website: {url}\n\n"
            "Please cover:\n"
            "1. Purpose and credibility of the website\n"
            "2. Key content or research available\n"
            "3. Technical quality and trustworthiness\n"
            "4. Recommendations for a biomedical researcher"
        )
        save_message(user_id, "user", f"/test {url}")
        await ai_reply(update, user_id, prompt, save_user_msg=False)
    else:
        # No URL given — show platform links
        keyboard = [
            [InlineKeyboardButton("Open BioMedScholar AI", url="https://biomed-scholar.web.app")],
            [InlineKeyboardButton("PubMed Search", url="https://biomed-scholar.web.app/#articles")],
            [InlineKeyboardButton("Maverick AI Chat", url="https://biomed-scholar.web.app/#chat")],
        ]
        await update.message.reply_text(
            "💠 *BioMedScholar AI — Web Platform*\n\n"
            "Access the full research suite with 35M+ PubMed articles, clinical trials, and Maverick AI chat.\n\n"
            "Tip: Use `/test <url>` to analyze any website.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )

async def ai_reply(update: Update, user_id: int, prompt: str, save_user_msg: bool = True):
    """Core AI call — sends a prompt to Groq and replies. Reusable by all commands."""
    try:
        await context_send_typing(update)
        if save_user_msg:
            save_message(user_id, "user", prompt)

        history = get_history(user_id)
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history
        # If history already has the user turn, avoid duplicating it
        if not history or history[-1].get("content") != prompt:
            messages.append({"role": "user", "content": prompt})

        response = groq_client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.3,
            max_tokens=2048
        )

        answer = response.choices[0].message.content
        if "💠" not in answer[:15]:
            answer = "💠 " + answer

        save_message(user_id, "assistant", answer)

        # Split into 4000-char chunks (Telegram limit is 4096)
        chunks = [answer[i:i+4000] for i in range(0, len(answer), 4000)]
        for chunk in chunks:
            try:
                await update.message.reply_text(safe_markdown(chunk), parse_mode='Markdown')
            except Exception:
                await update.message.reply_text(chunk)

    except Exception as e:
        logger.error(f"ai_reply error: {e}")
        await update.message.reply_text(f"💠 Maverick Alert: A node disturbance occurred. ({str(e)[:80]})")


async def context_send_typing(update: Update):
    """Send typing action safely."""
    try:
        await update.get_bot().send_chat_action(
            chat_id=update.effective_chat.id, action="typing"
        )
    except Exception:
        pass


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    user_id = update.effective_user.id
    if not user_text:
        return
    await ai_reply(update, user_id, user_text, save_user_msg=True)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await context.bot.send_message(chat_id=update.effective_chat.id, text="💠 Feedback logged.")

if __name__ == '__main__':
    if not TELEGRAM_TOKEN or not GROQ_API_KEY:
        logger.error("Error: API Keys not set")
        sys.exit(1)

    # Start Flask in background
    threading.Thread(target=run_flask, daemon=True).start()

    # Build Application with timeouts
    request = HTTPXRequest(connect_timeout=30, read_timeout=30)
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).request(request).build()
    
    # Add Handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('clear', clear_command))
    application.add_handler(CommandHandler('history', history_command))
    application.add_handler(CommandHandler('search', search_command))
    application.add_handler(CommandHandler('about', about_command))
    application.add_handler(CommandHandler('test', test_command))
    application.add_handler(CallbackQueryHandler(handle_callback))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("🚀 MAVERICK AI RESEARCH ENGINE IS ONLINE")
    application.run_polling(drop_pending_updates=True)
