import socket
from groq import AsyncGroq
from dotenv import load_dotenv

# --- DNS GLOBAL MONKEYPATCH ---
# Hugging Face Spaces often have flaky DNS resolution for external APIs.
_original_getaddrinfo = socket.getaddrinfo
DNS_PRIORITY_HOSTS = ["api.groq.com", "google.com", "huggingface.co", "api.telegram.org"]

def custom_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    host_str = host.decode('utf-8') if isinstance(host, bytes) else str(host)
    host_clean = host_str.lower().strip('.')
    try:
        return _original_getaddrinfo(host, port, family, type, proto, flags)
    except Exception:
        if any(h in host_clean for h in DNS_PRIORITY_HOSTS):
            print(f">>> [DNS PATCH] System DNS failed. Priority resolving: {host_clean}", flush=True)
            try:
                import dns.resolver
                resolver = dns.resolver.Resolver()
                resolver.nameservers = ['8.8.8.8', '1.1.1.1', '8.8.4.4']
                resolver.timeout = 2
                resolver.lifetime = 2
                answers = resolver.resolve(host_clean, 'A')
                if answers:
                    ips = [str(ans) for ans in answers]
                    results = []
                    for ip in ips:
                        try:
                            results.extend(_original_getaddrinfo(ip, port, family, type, proto, flags))
                        except:
                            results.append((socket.AF_INET, type or socket.SOCK_STREAM, proto or 6, '', (ip, int(port) or 443)))
                    return results
            except: pass
        raise

socket.getaddrinfo = custom_getaddrinfo
print(">>> [DNS PATCH] Applied to Telegram Bot", flush=True)

load_dotenv()

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

import os
import sqlite3
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, Application

# Configuration
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = "openai/gpt-oss-120b"
DB_FILE = "/tmp/conversation_history.db" if os.path.exists("/tmp") else "local_memory.db"

# Search Config (Bonsai/OpenSearch)
ES_HOST = os.getenv("ELASTICSEARCH_HOST", "assertive-mahogany-1m2hcasg.us-east-1.bonsaisearch.net")
ES_USER = os.getenv("ELASTICSEARCH_USER", "0204784e62")
ES_PASS = os.getenv("ELASTICSEARCH_PASSWORD", "38aa998d6c5c2891232c")

# Initialize Groq Client
try:
    groq_client = AsyncGroq(api_key=GROQ_API_KEY)
    logger.info("AsyncGroq client initialized")
except Exception as e:
    logger.error(f"Failed to initialize Groq client: {e}")
    groq_client = None

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
        logger.error(f"Database initialization error: {e}")

def save_message(user_id: int, role: str, content: str):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO history (user_id, role, content) VALUES (?, ?, ?)", (user_id, role, content))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Save message error: {e}")

def get_history(user_id: int, limit=10):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT role, content FROM history WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?", (user_id, limit))
        rows = c.fetchall()
        conn.close()
        return [{"role": r, "content": c} for r, c in reversed(rows)]
    except:
        return []

def clear_history(user_id: int):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("DELETE FROM history WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
        return True
    except:
        return False

# Search Logic
async def perform_search(query: str, max_results=3):
    try:
        from opensearchpy import OpenSearch
        client = OpenSearch(
            hosts=[f"https://{ES_USER}:{ES_PASS}@{ES_HOST}:443"],
            use_ssl=True, verify_certs=True
        )
        
        es_query = {
            "size": max_results,
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["title^3", "abstract"]
                }
            }
        }
        
        res = client.search(index="pubmed_articles,clinical_trials", body=es_query)
        results = []
        for hit in res['hits']['hits']:
            source = hit['_source']
            results.append({
                "title": source.get("title", "No Title"),
                "abstract": source.get("abstract", "No abstract available.")[:300] + "...",
                "source": "PubMed" if "pubmed" in hit['_index'] else "ClinicalTrials"
            })
        return results
    except Exception as e:
        logger.error(f"Search failed: {e}")
        return []

# Command Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_text = (
        f"<b>💠 Welcome to Maverick AI 💠</b>\n\n"
        f"Hello {user.first_name}! I am the BioMedScholar Research Engine Bot.\n"
        f"I can help you navigate 35M+ biomedical articles and clinical trials.\n\n"
        f"🚀 <b>Available Commands:</b>\n"
        f"/search &lt;topic&gt; - AI biomedical literature search\n"
        f"/help - Show all commands\n"
        f"/history - View recent conversations\n"
        f"/clear - Wipe memory\n"
        f"/about - About Maverick Engine\n"
        f"/test - Open Web App"
    )
    
    keyboard = [
        [InlineKeyboardButton("🌐 Open BioMedScholar AI", url="https://biomed-scholar.web.app")],
        [InlineKeyboardButton("🔬 Interactive Maverick Desk", url="https://biomed-scholar.web.app/maverick")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_html(welcome_text, reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🤖 <b>Maverick Bot Commands</b>\n\n"
        "• /start - Welcome message\n"
        "• /search &lt;topic&gt; - AI literature search & synthesis\n"
        "• /history - Recall your last 5 interactions\n"
        "• /clear - Reset conversation memory\n"
        "• /about - Learn about the GPT OSS 120B engine\n"
        "• /test - Launch the full Research Desk"
    )
    await update.message.reply_html(help_text)

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    about_text = (
        "💠 <b>About Maverick AI</b>\n\n"
        "Maverick is a high-performance biomedical synthesis engine powered by Groq's low-latency "
        "<b>GPT OSS 120B</b> platform. Optimized for clinical research, oncology, and pharmacology "
        "data extraction."
    )
    await update.message.reply_html(about_text)

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if clear_history(user_id):
        await update.message.reply_text("🧹 Memory cleared successfully.")
    else:
        await update.message.reply_text("❌ Failed to clear memory.")

async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    history = get_history(user_id, limit=5)
    if not history:
        await update.message.reply_text("No recent history found.")
        return
    
    text = "📝 <b>Recent History:</b>\n\n"
    for msg in history:
        role = "👤 You" if msg['role'] == 'user' else "🤖 Maverick"
        content = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
        text += f"<b>{role}:</b> {content}\n\n"
    
    await update.message.reply_html(text)

async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_html("Please provide a search topic. Example: <code>/search immunotherapy for GBM</code>")
        return
    
    query = " ".join(context.args)
    await handle_message(update, context, override_msg=query, force_search=True)

async def test_app(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🚀 Launch BioMedScholar", url="https://biomed-scholar.web.app")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Click below to open the full Research Intelligence Platform:", reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE, override_msg=None, force_search=False):
    user_id = update.effective_user.id
    incoming_text = override_msg if override_msg else update.message.text
    
    logger.info(f"Processing message from {user_id}: {incoming_text[:50]}...")
    
    # Send thinking placeholder
    thinking_msg = await update.message.reply_html("💠 <i>Maverick is synthesizing...</i>")
    
    try:
        # Save user message
        save_message(user_id, "user", incoming_text)
        
        # 1. Search Literature
        search_results = []
        if force_search or any(word in incoming_text.lower() for word in ["search", "find", "studies", "trials", "papers"]):
            search_results = await perform_search(incoming_text)
            
        # 2. Get history
        history = get_history(user_id, limit=6)
        
        # 3. Build System Prompt
        system_content = (
            "You are Maverick, the official BioMedScholar AI Research Engine. "
            "You are a specialized analytical assistant for medicine, oncology, and pharmacology. "
            "Respond as a world-class scientist. "
            "FORMATTING: Use HTML tags — <b>bold</b> for medical terms, <i>italic</i> for Latin, <u>underline</u> for takeaways."
        )
        
        if search_results:
            results_text = "\n".join([f"- {r['title']}: {r['abstract']}" for r in search_results])
            system_content += f"\n\nCURRENT SEARCH CONTEXT:\n{results_text}"

        # 4. Prepare messages
        messages = [{"role": "system", "content": system_content}]
        for h in history:
            messages.append(h)
        
        # Add current message if not in history
        if not history or history[-1]['content'] != incoming_text:
            messages.append({"role": "user", "content": incoming_text})
            
        # 5. Generate completion
        logger.info(f"Requesting completion for user {user_id}")
        try:
            completion = await groq_client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                temperature=0.3,
                max_tokens=2048
            )
        except Exception as model_err:
            logger.warning(f"Primary model {MODEL_NAME} failed: {model_err}. Trying fallback...")
            completion = await groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=0.3,
                max_tokens=2048
            )
        
        logger.info(f"Completion received for user {user_id}")
        answer = completion.choices[0].message.content
        if "💠" not in answer[:15]:
            answer = "💠 " + answer
            
        # Save AI response
        save_message(user_id, "assistant", answer)
        
        # Edit/Split message if too long
        if len(answer) > 4000:
            answer = answer[:3990] + "..."
            
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=thinking_msg.message_id,
            text=answer,
            parse_mode='HTML'
        )
            
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        error_text = f"❌ <b>Maverick Error</b>: {str(e)[:100]}"
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=thinking_msg.message_id,
            text=error_text,
            parse_mode='HTML'
        )

async def post_init(application: Application):
    """Set bot commands during startup."""
    await application.bot.set_my_commands([
        BotCommand("start", "Welcome message"),
        BotCommand("help", "Show all commands"),
        BotCommand("search", "Search literature"),
        BotCommand("history", "Recent conversations"),
        BotCommand("clear", "Reset memory"),
        BotCommand("about", "About Maverick"),
        BotCommand("test", "Open Web App")
    ])

def main():
    print(">>> [BOT] Starting initialization...", flush=True)
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is missing!")
        print(">>> [BOT ERROR] TELEGRAM_BOT_TOKEN is missing!", flush=True)
        return

    init_db()
    
    try:
        app = ApplicationBuilder().token(TELEGRAM_TOKEN).post_init(post_init).build()
        print(">>> [BOT] Application built successfully", flush=True)
    except Exception as e:
        print(f">>> [BOT ERROR] Failed to build application: {e}", flush=True)
        return

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(CommandHandler("history", history_command))
    app.add_handler(CommandHandler("search", search_command))
    app.add_handler(CommandHandler("test", test_app))
    
    # Regular text messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("-" * 30)
    print("💠 MAVERICK TELEGRAM BOT ONLINE")
    print(f"User DB: {DB_FILE}")
    print("-" * 30)
    
    app.run_polling()

if __name__ == "__main__":
    main()
