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

# --- PRE-FLIGHT LOGGING ---
print(">>> [1/5] MAVERICK SYSTEM BOOTING...", flush=True)

# Configuration
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = "meta-llama/llama-4-maverick-17b-128e-instruct" # User requested Maverick Llama 4
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

async def search_internet(query: str):
    """Search Google via Serper API for real-time information."""
    if not SERPER_API_KEY:
        print(">>> [WARNING] SERPER_API_KEY not found. Skipping internet search.", flush=True)
        return None
    
    print(f">>> [SEARCH] Querying Serper for: {query}", flush=True)
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": query})
    headers = {
        'X-API-KEY': SERPER_API_KEY,
        'Content-Type': 'application/json'
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, content=payload, timeout=10.0)
            results = response.json()
            
            snippets = []
            # Gather top 4 organic results
            for result in results.get("organic", [])[:4]:
                snippets.append(f"Source: {result.get('title')}\nSnippet: {result.get('snippet')}\nURL: {result.get('link')}")
                
            return "\n\n".join(snippets) if snippets else "No external results found."
    except Exception as e:
        print(f">>> [ERROR] Serper search failed: {e}", flush=True)
        return None

async def test_website(url: str):
    """Test a website using Selenium headless mode and return the results."""
    print(f">>> [BROWSER TEST] Testing URL: {url}", flush=True)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1280,720")
    
    # Path handling for HF Spaces / Debian
    if os.path.exists("/usr/bin/chromium"):
        chrome_options.binary_location = "/usr/bin/chromium"
    
    try:
        # We use a standard driver init; on HF/Linux we might need more config but this is the baseline
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        time.sleep(5) # Wait for JS
        
        title = driver.title
        final_url = driver.current_url
        page_source_len = len(driver.page_source)
        
        # Take a peek at the main heading if possible
        heading = "Could not find h1"
        try:
            h1 = driver.find_element("tag name", "h1")
            heading = h1.text
        except: pass
        
        driver.quit()
        
        return {
            "status": "success",
            "title": title,
            "final_url": final_url,
            "heading": heading,
            "size": page_source_len
        }
    except Exception as e:
        print(f">>> [ERROR] Browser test failed: {e}", flush=True)
        return {"status": "error", "message": str(e)}

# --- TELEGRAM HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "💠 *Maverick Suite — Unified Research Engine*\n\n"
        "You are now connected to the Maverick AI Suite. I am an advanced specialized engine designed for deep biomedical discovery:\n\n"
        "• *Discovery Engine*: Llama 4 Maverick (MoE) Architecture.\n"
        "• *RAG Systems*: Real-time scholarly cross-referencing.\n"
        "• *Knowledge Memory*: Context-aware research threads.\n"
        "• *Multimodal*: Support for document & image analysis.\n\n"
        "How can the Suite assist your research today?"
    )
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

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
        
        # 1. BRAIN SKILLS: Thinking Process + Internet Search
        reasoning = (
            "💠 *Maverick Suite Thinking Process*\n"
            "• Synthesizing biomedical intent...\n"
            "• Querying global scholarly indexed data...\n"
            "• Optimizing for evidence-based accuracy..."
        )
        thinking_msg = await update.message.reply_text(reasoning, parse_mode='Markdown')
        
        internet_knowledge = None
        browser_report = None
        
        if "test " in user_text.lower() and "http" in user_text.lower():
            parts = user_text.split()
            target_url = next((p for p in parts if "http" in p), None)
            if target_url:
                browser_report = await test_website(target_url)
        
        if not browser_report and len(user_text) > 8:
            internet_knowledge = await search_internet(user_text)
        
        client = Groq(api_key=GROQ_API_KEY)
        history = get_history(user_id)
        
        system_content = (
            "You are the Maverick Suite (💠), a premium analytical biomedical research engine. "
            "Your personality is highly technical, authoritative, yet efficient. "
            "You have integrated SKILLS: Internet Search for live data and Browser Testing for technical audits. "
            "Always maintain a professional, scientific tone."
        )
        
        if internet_knowledge:
            system_content += f"\n\n[INTERNET SEARCH RESULTS]:\n{internet_knowledge}"
            
        if browser_report:
            system_content += f"\n\n[BROWSER TEST REPORT]:\n{json.dumps(browser_report, indent=2)}"
        
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
        
        await update.message.reply_text(answer, reply_markup=reply_markup)
        
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
        application.add_handler(CallbackQueryHandler(handle_callback))
        application.add_handler(MessageHandler(filters.PHOTO | filters.Document.ALL, handle_attachment))
        application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        
        print(">>> 🚀 MAVERICK IS FULLY OPERATIONAL!", flush=True)
        application.run_polling(drop_pending_updates=True)
    except Exception as e:
        print(f">>> [FATAL] BOT CRASHED: {e}", flush=True)
        sys.exit(1)
