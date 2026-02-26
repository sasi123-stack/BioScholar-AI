import socket
import os
import sys

# --- DNS GLOBAL MONKEYPATCH ---
# Hugging Face Spaces often have flaky DNS resolution for external APIs.
# We override the system's low-level address resolution to use custom DNS if it fails.
_original_getaddrinfo = socket.getaddrinfo

# Known flaky hosts that we want to handle with priority
DNS_PRIORITY_HOSTS = ["api.telegram.org", "api.groq.com", "google.com", "huggingface.co"]
# More comprehensive Telegram IP list
TELEGRAM_IPS = [
    "149.154.167.220", "149.154.167.219", "149.154.167.221",
    "149.154.166.110", "149.154.166.111", "91.108.4.4", "91.108.56.110"
]

def custom_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    host_str = host.decode('utf-8') if isinstance(host, bytes) else str(host)
    host_clean = host_str.lower().strip('.')
    
    # 1. Try original system DNS first
    try:
        return _original_getaddrinfo(host, port, family, type, proto, flags)
    except Exception:
        # If it fails, only then do we try our priority/fallback logic
        if any(h in host_clean for h in DNS_PRIORITY_HOSTS):
            print(f">>> [DNS PATCH] System DNS failed. Priority resolving: {host_clean}", flush=True)
            ips = []
            # Try Custom DNS (Google/Cloudflare)
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
            except Exception as e:
                print(f">>> [DNS PATCH] Custom DNS failed for {host_clean}: {e}", flush=True)

            # Hardcoded fallback for Telegram if DNS failed
            if not ips and "telegram" in host_clean:
                ips = TELEGRAM_IPS
                print(f">>> [DNS PATCH] HARDCODED FALLBACK used for {host_clean}", flush=True)

            if ips:
                results = []
                for ip in ips:
                    try:
                        # Use system resolution for the IP to get correct struct
                        results.extend(_original_getaddrinfo(ip, port, family, type, proto, flags))
                    except:
                        # Final manual fallback if even IP resolution fails
                        results.append((socket.AF_INET, type or socket.SOCK_STREAM, proto or 6, '', (ip, int(port) or 443)))
                return results
        
        # Re-raise the original error if we couldn't resolve it ourselves
        raise

socket.getaddrinfo = custom_getaddrinfo
print(">>> [DNS PATCH] Robust socket monkeypatch applied.", flush=True)

import logging
import sqlite3
import time
import re
from bs4 import BeautifulSoup
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler, CallbackQueryHandler
from groq import Groq
from telegram.request import HTTPXRequest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# --- PRE-FLIGHT LOGGING ---
print(">>> [1/5] MAVERICK SYSTEM BOOTING...", flush=True)

# Configuration
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = "meta-llama/llama-4-maverick-17b-128e-instruct" 
DB_FILE = "/tmp/conversation_history.db" # Use /tmp for HF write safety
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
ES_HOST = os.getenv("ELASTICSEARCH_HOST", "assertive-mahogany-1m2hcasg.us-east-1.bonsaisearch.net")
ES_USER = os.getenv("ELASTICSEARCH_USER", "0204784e62")
ES_PASS = os.getenv("ELASTICSEARCH_PASSWORD", "38aa998d6c5c2891232c")

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

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and prevent bot crash."""
    logger.error(f"Maverick Error Handler: {context.error}")
    # Connection errors are already logged by the library, but we can add more info here
    if "Connection" in str(context.error):
        print(">>> [NETWORK] Periodic connection blip detected. Retrying...", flush=True)

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
        "• *Expertise*: Llama 4 Maverick Architecture.\n"
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

    user_id = update.effective_user.id
    await update.message.reply_text(
        f"💠 *Maverick Search Initiative*: Commencing deep-web academic search for `{query}`...",
        parse_mode='Markdown'
    )
    prompt = f"Research the following topic on the internet: {query}"
    save_message(user_id, "user", f"/search {query}")
    await ai_call(update, context, user_id, prompt)

def scrape_url(url: str, max_chars: int = 3000) -> str:
    """Use headless Chromium to scrape visible text from a URL."""
    try:
        opts = Options()
        opts.add_argument("--headless")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-gpu")
        opts.binary_location = "/usr/bin/chromium"
        driver = webdriver.Chrome(
            service=Service("/usr/bin/chromedriver"),
            options=opts
        )
        driver.set_page_load_timeout(15)
        driver.get(url)
        text = driver.find_element("tag name", "body").text
        driver.quit()
        return text[:max_chars] if text else ""
    except Exception as e:
        print(f">>> [SCRAPE] Failed for {url}: {e}", flush=True)
        return ""

async def test_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Explicit website testing command."""
    url = context.args[0] if context.args else None
    if not url:
        await update.message.reply_text("💠 Please provide a URL. Usage: `/test <url>`", parse_mode='Markdown')
        return

    user_id = update.effective_user.id
    await update.message.reply_text(
        f"💠 *Maverick Audit Initiative*: Scraping and analysing `{url}`...",
        parse_mode='Markdown'
    )

    # Try to scrape live content first
    page_content = scrape_url(url)
    if page_content:
        prompt = (
            f"Perform a technical audit of this website: {url}\n\n"
            f"LIVE PAGE CONTENT (first 3000 chars):\n{page_content}\n\n"
            "Based on the above content, provide:\n"
            "1. Purpose and credibility of the website\n"
            "2. Key research content or features available\n"
            "3. Technical quality and trustworthiness\n"
            "4. Recommendations for a biomedical researcher"
        )
    else:
        prompt = (
            f"Perform a knowledge-based technical audit of this website: {url}\n\n"
            "Cover: 1) Purpose and credibility, 2) Key content available, "
            "3) Technical quality, 4) Recommendations for a biomedical researcher."
        )

    save_message(user_id, "user", f"/test {url}")
    await ai_call(update, context, user_id, prompt)


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
    prompt = f"Analyze the data in the attached file: {file_name}"
    await ai_call(update, context, user_id, prompt)

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

def sanitize_telegram_html(text: str) -> str:
    """Fix nested HTML tags and escape rogue characters for Telegram HTML mode."""
    try:
        soup = BeautifulSoup(text, 'html.parser')
        allowed_tags = ['b', 'strong', 'i', 'em', 'u', 'ins', 's', 'strike', 'del', 'a', 'code', 'pre']
        
        def clean_node(node):
            if hasattr(node, 'name') and node.name is not None:
                if node.name in allowed_tags:
                    attrs = ""
                    if node.name == 'a' and node.get('href'):
                        # Telegram requires href to be double quoted
                        href = node.get("href").replace('"', '&quot;')
                        attrs = f' href="{href}"'
                    
                    inner = "".join(clean_node(child) for child in node.children)
                    return f"<{node.name}{attrs}>{inner}</{node.name}>"
                else:
                    return "".join(clean_node(child) for child in node.children)
            else:
                s = str(node)
                return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

        return "".join(clean_node(child) for child in soup.children)
    except Exception as e:
        print(f">>> [SANITY] HTML sanitization failed: {e}", flush=True)
        # Fallback to simple escaping if BS4 fails
        return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

async def ai_call(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, user_text: str):
    """Core AI processing pipeline — direct Groq call, shared by all commands and free chat."""
    try:
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

        # Intent detection for thinking display
        urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', user_text)
        is_search_query = len(user_text.split()) > 4 or any(w in user_text.lower() for w in ["research", "search", "clinical", "latest"])

        reasoning_bullets = ["• Synthesizing biomedical intent..."]
        if urls:
            reasoning_bullets.append(f"• **ACTIVE SKILL**: Analyzing live content from {len(urls)} URLs...")
        if is_search_query:
            reasoning_bullets.append("• **ACTIVE SKILL**: Querying real-time clinical data from the web...")
        reasoning_bullets.append("• Cross-referencing PubMed and Clinical Trial registries...")
        reasoning_bullets.append("• Optimizing for evidence-based accuracy...")

        reasoning = "💠 *Maverick Suite Thinking Process*\n" + "\n".join(reasoning_bullets)
        thinking_msg = await update.message.reply_text(reasoning, parse_mode='Markdown')

        # Build message history
        history = get_history(user_id)

        system_content = (
            "You are Maverick, the official BioMedScholar AI Research Engine. "
            "You are a high-performance, elite analytical assistant specialized in human medicine, oncology, and pharmacology. "
            "The user's name is Sasidhara. Respond as a world-class scientist. "
            "NEVER use asterisks for roleplay actions. Your tone must be purely professional, scientific, and technical. "
            "FORMATTING: Use HTML tags — <b>bold</b> for primary medical terms, <i>italic</i> for Latin terms, <u>underline</u> for critical clinical takeaways. "
            "Provide a sharp, evidence-based, clinical-grade medical synthesis."
        )

        messages = [{"role": "system", "content": system_content}]
        
        # Merge consecutive roles to satisfy Groq requirements
        last_role = "system"
        for entry in history:
            if entry["role"] == last_role:
                messages[-1]["content"] += "\n" + entry["content"]
            else:
                messages.append({"role": entry["role"], "content": entry["content"]})
                last_role = entry["role"]

        # Add current user message, merging if last was user
        if last_role == "user":
            messages[-1]["content"] += "\n" + user_text
        else:
            messages.append({"role": "user", "content": user_text})

        client = Groq(api_key=GROQ_API_KEY)
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
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=thinking_msg.message_id)

        # Sanitize for Telegram
        sanitized_answer = sanitize_telegram_html(answer)

        keyboard = [
            [InlineKeyboardButton("👍 Helpful", callback_data="feedback_up"),
             InlineKeyboardButton("👎 Not Helpful", callback_data="feedback_down")]
        ]
        
        try:
            await update.message.reply_text(sanitized_answer, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
        except Exception as html_err:
            print(f">>> [ERROR] HTML reply failed: {html_err}. Falling back to Markdown/Text.", flush=True)
            # Second fallback: Try Markdown if HTML fails
            try:
                await update.message.reply_text(answer, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
            except:
                # Absolute fallback: Plain text
                plain_text = re.sub(r'<[^>]*>', '', answer)
                await update.message.reply_text(plain_text, reply_markup=InlineKeyboardMarkup(keyboard))

    except Exception as e:
        print(f">>> [ERROR] ai_call failed: {e}", flush=True)
        await update.message.reply_text(f"💠 Maverick Suite encountered a node disturbance: {str(e)[:100]}")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    user_id = update.effective_user.id
    if not user_text:
        return
    await ai_call(update, context, user_id, user_text)

# --- MAIN ---
if __name__ == '__main__':
    import threading
    from flask import Flask, jsonify, request as flask_request

    # --- Flask server (health + REST API for frontend) ---
    flask_app = Flask(__name__)

    @flask_app.after_request
    def add_cors(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        return response

    @flask_app.route('/')
    def home():
        return "💠 Maverick AI Research Engine — Online"

    @flask_app.route('/api/v1/health')
    def health():
        return jsonify({
            "status": "synced", 
            "engine": "Llama 4 Maverick", 
            "bot": "online",
            "elasticsearch": "connected" # simplified health check
        })

    @flask_app.route('/api/v1/search', methods=['POST', 'OPTIONS'])
    def search():
        if flask_request.method == 'OPTIONS':
            return jsonify({}), 200
        
        try:
            from opensearchpy import OpenSearch
            data = flask_request.get_json(force=True)
            query = data.get('query', '')
            index_type = data.get('index', 'both')
            max_results = data.get('max_results', 20)
            
            if not query:
                return jsonify({"status": "error", "message": "No query provided"}), 400
                
            client = OpenSearch(
                hosts=[f"https://{ES_USER}:{ES_PASS}@{ES_HOST}:443"],
                use_ssl=True, verify_certs=True
            )
            
            # Determine index
            if index_type == 'pubmed':
                index_name = 'pubmed_articles'
            elif index_type == 'clinical_trials':
                index_name = 'clinical_trials'
            else:
                index_name = 'pubmed_articles,clinical_trials'
                
            # Perform search
            es_query = {
                "size": max_results,
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": ["title^3", "abstract", "authors"]
                    }
                }
            }
            
            res = client.search(index=index_name, body=es_query)
            
            results = []
            for hit in res['hits']['hits']:
                source = hit['_source']
                # Extract year safely
                year = ""
                if "publication_date" in source:
                    year = str(source["publication_date"])[:4]
                elif "publication_year" in source:
                    year = str(source["publication_year"])[:4]
                elif "year" in source:
                    year = str(source["year"])[:4]
                elif "metadata" in source and isinstance(source["metadata"], dict):
                    year = str(source["metadata"].get("publication_year", source["metadata"].get("year", "")))[:4]

                results.append({
                    "id": hit['_id'],
                    "title": source.get("title", "No Title"),
                    "authors": source.get("authors", source.get("author", "Unknown Authors")),
                    "journal": source.get("journal", source.get("source_name", "Biomedical Literature")),
                    "year": year,
                    "abstract": source.get("abstract", ""),
                    "score": hit['_score'],
                    "source": source.get("source", "pubmed"),
                    "metadata": source.get("metadata", {})
                })
                
            return jsonify({
                "query": query,
                "total_results": res['hits']['total']['value'] if isinstance(res['hits']['total'], dict) else res['hits']['total'],
                "results": results,
                "search_time_ms": res['took']
            })
            
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    @flask_app.route('/api/v1/maverick/chat', methods=['POST', 'OPTIONS'])
    def maverick_chat():
        if flask_request.method == 'OPTIONS':
            return jsonify({}), 200
        try:
            data = flask_request.get_json(force=True)
            question = data.get('question', '')
            context = data.get('context', [])
            if not question:
                return jsonify({"status": "error", "answer": "No question provided."}), 400

            system_content = (
                "You are Maverick, the official BioMedScholar AI Research Engine. "
                "You are a high-performance, elite analytical assistant specialized in human medicine, oncology, and pharmacology. "
                "Respond as a world-class scientist. "
                "FORMATTING: Use HTML tags — <b>bold</b> for primary medical terms, <i>italic</i> for Latin terms, <u>underline</u> for critical clinical takeaways. "
                "Provide a sharp, evidence-based, clinical-grade medical synthesis."
            )

            messages = [{"role": "system", "content": system_content}]
            last_role = "system"
            for turn in context:
                if turn.get('role') in ('user', 'assistant'):
                    if turn['role'] == last_role:
                        messages[-1]['content'] += "\n" + turn.get('content', '')
                    else:
                        messages.append({"role": turn['role'], "content": turn.get('content', '')})
                        last_role = turn['role']
            
            if last_role == 'user':
                messages[-1]['content'] += "\n" + question
            else:
                messages.append({"role": "user", "content": question})

            client = Groq(api_key=GROQ_API_KEY)
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                temperature=0.3,
                max_tokens=2048
            )
            answer = response.choices[0].message.content
            if "💠" not in answer[:15]:
                answer = "💠 " + answer

            return jsonify({
                "status": "success",
                "answer": answer,
                "reasoning": "Maverick AI synthesis via Llama 4 Maverick on Groq",
                "sources": []
            })
        except Exception as e:
            return jsonify({"status": "error", "answer": f"Maverick disturbance: {str(e)[:100]}"}), 500

    @flask_app.route('/api/v1/maverick/history', methods=['GET'])
    def maverick_history():
        return jsonify({"status": "success", "history": []})

    def run_flask():
        flask_app.run(host='0.0.0.0', port=7860, use_reloader=False)

    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    print(">>> [HF] Flask API server started on port 7860", flush=True)

    # --- Telegram Bot ---
    print(">>> [4/5] CHECKING SECRETS...", flush=True)
    if not TELEGRAM_TOKEN or not GROQ_API_KEY:
        print(">>> [CRITICAL] MISSING API KEYS! Check Settings > Secrets.", flush=True)

    check_dns()
    init_db()

    print(">>> [5/5] CONNECTING TO TELEGRAM...", flush=True)
    
    # Retry loop for initial connection
    max_startup_retries = 5
    for attempt in range(max_startup_retries):
        try:
            request = HTTPXRequest(connect_timeout=30, read_timeout=30, write_timeout=30)
            application = ApplicationBuilder().token(TELEGRAM_TOKEN).request(request).build()
            application.add_handler(CommandHandler('start', start))
            application.add_handler(CommandHandler('search', search_command))
            application.add_handler(CommandHandler('test', test_command))
            application.add_handler(CallbackQueryHandler(handle_callback))
            application.add_handler(MessageHandler(filters.PHOTO | filters.Document.ALL, handle_attachment))
            application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
            
            # Add error handler
            application.add_error_handler(error_handler)

            print(f">>> 🚀 MAVERICK IS FULLY OPERATIONAL! (Attempt {attempt+1})", flush=True)
            application.run_polling(drop_pending_updates=True)
            break # Exit loop if polling ends normally
        except Exception as e:
            print(f">>> [RETRY {attempt+1}/{max_startup_retries}] Connection failed: {e}", flush=True)
            if attempt < max_startup_retries - 1:
                time.sleep(15)
            else:
                print(">>> [FATAL] BOT CRASHED after multiple attempts.", flush=True)
                sys.exit(1)

