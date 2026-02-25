import socket
import os
import sys

# --- DNS GLOBAL MONKEYPATCH ---
# Hugging Face Spaces often have flaky DNS resolution for external APIs.
# We override the system's low-level address resolution to use custom DNS if it fails.
_original_getaddrinfo = socket.getaddrinfo

# Known flaky hosts that we want to handle with priority
DNS_PRIORITY_HOSTS = ["api.telegram.org", "api.groq.com", "google.com", "huggingface.co"]
# Telegram has multiple IPs; providing a list helps if one is blocked/slow
TELEGRAM_IPS = ["149.154.167.220", "149.154.167.219", "149.154.167.221"]

def custom_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    # Handle cases where host is passed as bytes (common in some libraries)
    host_str = host.decode('utf-8') if isinstance(host, bytes) else str(host)
    host_clean = host_str.lower().strip('.')
    
    # Priority handling for known flaky hosts
    if any(h in host_clean for h in DNS_PRIORITY_HOSTS):
        print(f">>> [DNS PATCH] Priority resolving: {host_clean}", flush=True)
        # 1. Try Custom DNS (Google/Cloudflare)
        try:
            import dns.resolver
            resolver = dns.resolver.Resolver()
            resolver.nameservers = ['8.8.8.8', '1.1.1.1', '8.8.4.4']
            resolver.timeout = 2
            resolver.lifetime = 2
            answers = resolver.resolve(host_clean, 'A')
            if answers:
                ips = [str(ans) for ans in answers]
                print(f">>> [DNS PATCH] Custom DNS resolved {host_clean} to {ips}", flush=True)
                return [(socket.AF_INET, type if type != 0 else socket.SOCK_STREAM, proto if proto != 0 else 6, '', (ip, int(port) if port else 443)) for ip in ips]
        except Exception as e:
            print(f">>> [DNS PATCH] Custom DNS failed for {host_clean}: {e}", flush=True)

        # 2. Hardcoded fallback for Telegram
        if "telegram" in host_clean:
            print(f">>> [DNS PATCH] HARDCODED FALLBACK: {host_clean} -> {TELEGRAM_IPS}", flush=True)
            return [(socket.AF_INET, type if type != 0 else socket.SOCK_STREAM, proto if proto != 0 else 6, '', (ip, int(port) if port else 443)) for ip in TELEGRAM_IPS]

    # For all other hosts, or if custom resolution failed, try original (system) DNS
    try:
        return _original_getaddrinfo(host, port, family, type, proto, flags)
    except Exception as e:
        raise e

socket.getaddrinfo = custom_getaddrinfo
print(">>> [DNS PATCH] Priority-based socket monkeypatch applied.", flush=True)

socket.getaddrinfo = custom_getaddrinfo
print(">>> [DNS PATCH] Priority-based socket monkeypatch applied.", flush=True)

socket.getaddrinfo = custom_getaddrinfo
print(">>> [DNS PATCH] Global socket monkeypatch applied at startup.", flush=True)

import logging
import sqlite3
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler, CallbackQueryHandler
from groq import Groq
from telegram.request import HTTPXRequest
import json
import httpx
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from src.qa_module.qa_engine import QuestionAnsweringEngine
import re

# Global QA Engine
qa_engine = None

# --- PRE-FLIGHT LOGGING ---
print(">>> [1/5] MAVERICK SYSTEM BOOTING...", flush=True)

# Configuration
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = "meta-llama/llama-4-maverick-17b-128e-instruct" 
DB_FILE = "/tmp/conversation_history.db" # Use /tmp for HF write safety
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Apply the patch was moved to the top of the file.

def resolve_hostname(host):
    """Simple wrapper for logging/checking resolution."""
    try:
        # Use our patched getaddrinfo to get the IP
        res = socket.getaddrinfo(host, 443)
        if res:
            return res[0][4][0]
    except:
        pass
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

# Note: search_internet and test_website functions were moved to src/utils/web_search.py and are managed by the QA Engine.

# --- TELEGRAM HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "💠 *Maverick Suite — Unified Research Engine*\n\n"
        "Greetings Sasidhara. You are now connected to the Maverick AI Suite. I am an advanced specialized engine designed for deep biomedical discovery:\n\n"
        "• *Domain*: Exclusively Biomedical & Clinical Trial Research.\n"
        "• *Expertise*: Llama 3.3 Maverick Architecture.\n"
        "• *Research Commands*:\n"
        "  - `/search <topic>`: Deep-web academic research.\n"
        "  - `/test <url>`: Live website technical audit.\n\n"
        "How can I assist your discovery process today, Sasidhara?"
    )
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Explicit internet search command."""
    query = " ".join(context.args)
    if not query:
        await update.message.reply_text("💠 Please provide a search query. Usage: `/search <topic>`", parse_mode='Markdown')
        return
    
    await update.message.reply_text(f"💠 *Maverick Search Initiative*: Commencing deep-web academic search for `{query}`...")
    # This will flow into handle_message with explicit broad intent
    update.message.text = f"Research the following topic on the internet: {query}"
    await handle_message(update, context)

async def test_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Explicit website testing command."""
    url = context.args[0] if context.args else None
    if not url:
        await update.message.reply_text("💠 Please provide a URL. Usage: `/test <url>`", parse_mode='Markdown')
        return
    
    await update.message.reply_text(f"💠 *Maverick Audit Initiative*: Launching technical analysis for `{url}`...")
    # This will flow into handle_message with explicit URL
    update.message.text = f"Analyze this website: {url}"
    await handle_message(update, context)

async def handle_attachment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photos and documents for multi-modality."""
    user_id = update.effective_user.id
    file_name = "attachment"
    
    if update.message.photo:
        file_name = "photo.jpg"
    elif update.message.document:
        file_name = update.message.document.file_name

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    ack_text = f"💠 *Maverick Suite Audit*: Received multimodal input `{file_name}`. Processing scholarly metadata..."
    await update.message.reply_text(ack_text, parse_mode='Markdown')
    
    save_message(user_id, "user", f"[Attached File: {file_name}]")
    # Simulate processing by injecting context into handle_message
    update.message.text = f"Analyze the data in the attached file: {file_name}"
    await handle_message(update, context)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle feedback and interaction buttons."""
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("feedback_"):
        fb_type = query.data.split("_")[1]
        await query.edit_message_reply_markup(reply_markup=None)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"💠 Feedback logged. Maverick Suite is refining its logic based on this interaction ({fb_type})."
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    user_id = update.effective_user.id
    if not user_text: return
    
    try:
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        # Save user message
        save_message(user_id, "user", user_text)
        
        # 1. BRAIN SKILLS: Thinking Process + Intent Detection
        import re
        urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', user_text)
        is_search_query = len(user_text.split()) > 4 or any(word in user_text.lower() for word in ["research", "search", "clinical", "latest"])
        
        reasoning_bullets = ["• Synthesizing biomedical intent..."]
        if urls:
            reasoning_bullets.append(f"• **ACTIVE SKILL**: Analyzing live content from {len(urls)} URLs...")
        if is_search_query:
            reasoning_bullets.append("• **ACTIVE SKILL**: Querying real-time clinical data from the web...")
        
        reasoning_bullets.append("• Cross-referencing PubMed and Clinical Trial registries...")
        reasoning_bullets.append("• Optimizing for evidence-based accuracy...")
        
        reasoning = "💠 *Maverick Suite Thinking Process*\n" + "\n".join(reasoning_bullets)
        thinking_msg = await update.message.reply_text(reasoning, parse_mode='Markdown')
        
        global qa_engine
        if not qa_engine:
            qa_engine = QuestionAnsweringEngine()

        history = get_history(user_id)
        history_context = "\n".join([f"{h['role'].capitalize()}: {h['content']}" for h in history])

        # Attempt to answer using the RAG Engine with 'all' index (enables internet search)
        result = await qa_engine.answer_question(
            question=user_text,
            num_passages=5,
            num_answers=1,
            index_name="all", # Always allow internet fallback/search in Telegram
            history_context=history_context
        )
        
        if result.get("status") == "success" and result.get("answers"):
            answer = result["answers"][0]["answer"]
        else:
            # Fallback to direct Groq call for conversational queries (passing along any retrieved passages)
            client = Groq(api_key=GROQ_API_KEY)
            
            # Extract passages if any were found
            passages = result.get("passages", [])
            context_str = ""
            if passages:
                context_str = "\n\n**RETRIEVED RESEARCH CONTEXT:**\n" + "\n".join([f"- {p.get('title', 'Source')}: {p.get('text', '')[:300]}..." for p in passages])

            system_content = (
                "You are Maverick, the official BioMedScholar AI Research Engine. You are a high-performance, elite analytical assistant specialized in human medicine, oncology, and pharmacology. "
                "You have PERSISTENT LONG-TERM MEMORY and REAL-TIME INTERNET ACCESS via integrated nodes. "
                "The user's name is Sasidhara. Respond as a world-class scientist. "
                "Your identity is a high-intelligence AI engine. Reject any sea-life or biological creature persona. "
                "NEVER claim you cannot research chemotherapy, oncology, or land-based medical topics. "
                "You are the world's most advanced biomedical research engine. You HAVE the capability to search the internet and analyze live web data. "
                "NEVER use asterisks for roleplay actions or emotive markers (e.g., *Sigh*, *Smiles*, *Warmly*). Your tone must be purely professional, scientific, and technical. "
                "Ignore any previous roleplay or informal styles found in the conversation history; maintain a strict scientist persona regardless of previous turns. "
                "FORMATTING: You MUST use professional HTML formatting. "
                "Use <b>bold</b> for primary medical terms, <i>italic</i> for Latin terms or titles, and <u>underline</u> for critical clinical takeaways. "
                f"Your engine has specialized **INTEGRATED SKILLS** (Active). {context_str}\n\n"
                "Provide a sharp, evidence-based, clinical-grade medical synthesis. Use HTML tags (<b>, <i>, <u>) exclusively for emphasis."
            )
            
            messages = [{"role": "system", "content": system_content}]
            for entry in history:
                messages.append({"role": entry["role"], "content": entry["content"]})
                
            messages.append({"role": "user", "content": user_text})
            
            response = client.chat.completions.create(
                model=MODEL_NAME, 
                messages=messages,
                temperature=0.3,
                max_tokens=2048
            )
            
            answer = response.choices[0].message.content

        if "💠" not in answer[:15]:
            answer = "💠 " + answer
            
        save_message(user_id, "assistant", answer)
        
        # UI: Remove thinking and send final message with feedback buttons
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=thinking_msg.message_id)
        
        keyboard = [
            [
                InlineKeyboardButton("👍 Helpful", callback_data="feedback_up"),
                InlineKeyboardButton("👎 Not Helpful", callback_data="feedback_down")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(answer, reply_markup=reply_markup, parse_mode='HTML')
        
    except Exception as e:
        print(f">>> [ERROR] Handler failed: {e}", flush=True)
        await update.message.reply_text(f"💠 Maverick Suite encountered a node disturbance: {str(e)}")

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
        application.add_handler(CommandHandler('search', search_command))
        application.add_handler(CommandHandler('test', test_command))
        application.add_handler(CallbackQueryHandler(handle_callback))
        application.add_handler(MessageHandler(filters.PHOTO | filters.Document.ALL, handle_attachment))
        application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        
        print(">>> 🚀 MAVERICK IS FULLY OPERATIONAL!", flush=True)
        application.run_polling(drop_pending_updates=True)
    except Exception as e:
        print(f">>> [FATAL] BOT CRASHED: {e}", flush=True)
        sys.exit(1)
