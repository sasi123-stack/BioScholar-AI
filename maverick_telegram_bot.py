import os
import socket
import html
import sqlite3
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, Application
from groq import AsyncGroq
from dotenv import load_dotenv
import sys

# Windows UTF-8 console support
if sys.platform == 'win32':
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except:
        pass

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

# Configuration
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = "llama-3.3-70b-versatile"   # Primary Groq model
DB_FILE = "/tmp/conversation_history.db" if os.path.exists("/tmp") else "local_memory.db"

# Search Config (Bonsai/OpenSearch)
ES_HOST = os.getenv("ELASTICSEARCH_HOST", "assertive-mahogany-1m2hcasg.us-east-1.bonsaisearch.net")
ES_USER = os.getenv("ELASTICSEARCH_USER", "0204784e62")
ES_PASS = os.getenv("ELASTICSEARCH_PASSWORD", "38aa998d6c5c2891232c")

# Initialize Groq AI Client
try:
    ai_client = AsyncGroq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
    logger.info("Groq AsyncGroq client initialized")
except Exception as e:
    logger.error(f"Failed to initialize Groq client: {e}")
    ai_client = None

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

def sanitize_for_telegram(text: str) -> str:
    """Sanitize and map unsupported HTML tags to Telegram-safe equivalents."""
    if not text:
        return ""
    
    import re
    # 1. Map Headers to Bold
    text = re.sub(r'<(h1|h2|h3|h4|h5|h6)[^>]*>', '<b>', text, flags=re.IGNORECASE)
    text = re.sub(r'</(h1|h2|h3|h4|h5|h6)>', '</b>\n\n', text, flags=re.IGNORECASE)
    
    # 2. Map Paragraphs and Divs to line breaks
    text = re.sub(r'<(p|div)[^>]*>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'</(p|div)>', '\n\n', text, flags=re.IGNORECASE)
    
    # 3. Handle line breaks and horizontal rules
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<hr\s*/?>', '\n〰️〰️〰️〰️〰️〰️〰️〰️\n', text, flags=re.IGNORECASE)

    # 4. Handle Lists (Convert to text bullets)
    text = re.sub(r'<li[^>]*>', '• ', text, flags=re.IGNORECASE)
    text = re.sub(r'</li>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<(ul|ol)[^>]*>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</(ul|ol)>', '\n', text, flags=re.IGNORECASE)

    # 5. Handle Tables (Convert to pipe-separated text)
    text = re.sub(r'<table[^>]*>', '\n📊 <b>Table Data:</b>\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</table>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<tr[^>]*>', '▪️ ', text, flags=re.IGNORECASE)
    text = re.sub(r'</tr>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<(td|th)[^>]*>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'</(td|th)>', ' | ', text, flags=re.IGNORECASE)
    text = re.sub(r' \|\s*\n', '\n', text) # strip trailing pipes

    # 6. Handle Superscripts and Subscripts
    text = re.sub(r'<sup[^>]*>', '^', text, flags=re.IGNORECASE)
    text = re.sub(r'</sup>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'<sub[^>]*>', '_', text, flags=re.IGNORECASE)
    text = re.sub(r'</sub>', '', text, flags=re.IGNORECASE)
    
    # 7. Remove unsupported tags entirely but keep inner content
    supported_tags = ['b', 'strong', 'i', 'em', 'u', 'ins', 's', 'strike', 'del', 'code', 'pre', 'a']
    all_tags = re.findall(r'<(/?)([a-z0-9]+)(\s*[^>]*)>', text, flags=re.IGNORECASE)
    
    for is_closing, tag_name, attrs in all_tags:
        if tag_name.lower() not in supported_tags:
            full_tag = f"<{is_closing}{tag_name}{attrs}>"
            text = text.replace(full_tag, "")
            
    # Clean up double line breaks and HTML entities
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.replace('&nbsp;', ' ')
    
    return text.strip()

async def get_resilient_completion(messages: list, user_id: int):
    """Try multiple Groq models with fallback chain."""
    if not ai_client:
        raise Exception("Groq client not initialized. Check GROQ_API_KEY environment variable.")

    models_to_try = [
        MODEL_NAME,                # Primary: llama-3.3-70b-versatile
        "llama-3.1-70b-versatile", # Fallback 1
        "llama-3.1-8b-instant",    # Fallback 2: Fast/light
        "gemma2-9b-it",            # Fallback 3: Google Gemma
    ]
    
    last_err = None
    for model in models_to_try:
        try:
            logger.info(f"Trying Groq model '{model}' for user {user_id}")
            completion = await ai_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.3,
                max_tokens=2048
            )
            answer = completion.choices[0].message.content
            
            # Guard against HTML gateway error pages
            if answer and ("<!DOCTYPE" in answer[:20] or "<html>" in answer.lower()[:20]):
                logger.warning(f"Model {model} returned HTML. Trying next model...")
                continue
                
            return answer
            
        except Exception as e:
            logger.warning(f"Groq model '{model}' failed: {e}")
            last_err = e
            continue
            
    raise Exception(f"All Groq models failed. Final error: {last_err}")

# Command Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_text = (
        f"<b>💠 Welcome to Maverick AI 💠</b>\n\n"
        f"Hello {user.first_name}! I am the BioMedScholar Research Engine Bot.\n"
        f"I can help you navigate 35M+ biomedical articles and clinical trials.\n\n"
        f"🚀 <b>Available Commands:</b>\n"
        f"/search &lt;topic&gt; - AI biomedical literature search\n"
        f"/claude &lt;task&gt; - Execute Claude Code command\n"
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
    
    if update.effective_message:
        await update.effective_message.reply_html(welcome_text, reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🤖 <b>Maverick Bot Commands</b>\n\n"
        "• /start - Welcome message\n"
        "• /search &lt;topic&gt; - AI literature search & synthesis\n"
        "• /claude &lt;task&gt; - Evaluate Claude Code in backend\n"
        "• /history - Recall your last 5 interactions\n"
        "• /clear - Reset conversation memory\n"
        "• /about - Learn about the Maverick AI engine\n"
        "• /test - Launch the full Research Desk"
    )
    await update.message.reply_html(help_text)

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    about_text = (
        "💠 <b>About Maverick AI</b>\n\n"
        "Maverick is a high-performance biomedical synthesis engine powered by "
        "<b>Groq's low-latency inference API</b> (llama-3.3-70b-versatile). "
        "Optimized for clinical research, oncology, and pharmacology data extraction."
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
        if update.effective_message:
            await update.effective_message.reply_html("Please provide a search topic. Example: <code>/search immunotherapy for GBM</code>")
        return
    
    query = " ".join(context.args)
    await handle_message(update, context, override_msg=query, force_search=True)

async def test_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🚀 Launch BioMedScholar", url="https://biomed-scholar.web.app")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.effective_message:
        await update.effective_message.reply_text("Click below to open the full Research Intelligence Platform:", reply_markup=reply_markup)

async def claude_code_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Execute a task via the Claude Code CLI tool."""
    if not context.args:
        if update.effective_message:
            await update.effective_message.reply_html(
                "<b>🛠️ Claude Code Executor</b>\n\n"
                "Please provide a task or question for Claude Code.\n"
                "Example: <code>/claude analyze the current project structure</code>\n"
                "Example: <code>/claude write a unit test for the search module</code>"
            )
        return
        
    task = " ".join(context.args)
    processing_msg = await update.effective_message.reply_html("👨‍💻 <i>Launching Claude Code Agent...</i>")
    
    try:
        # Check if claude is available
        import shutil
        claude_path = shutil.which("claude")
        if not claude_path:
            await context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=processing_msg.message_id,
                text="❌ <b>Claude Code Error</b>: The <code>claude</code> CLI is not installed or not in the system PATH.",
                parse_mode='HTML'
            )
            return

        # Prepare environment for Claude Code
        env = os.environ.copy()
        # Ensure we don't accidentally leak tokens if not intended, but provide necessary ones
        if "ANTHROPIC_API_KEY" not in env and os.getenv("GROQ_API_KEY"):
            # If no Anthropic key, we might be using a router or local setup
            env["ANTHROPIC_AUTH_TOKEN"] = "test" 
            env["ANTHROPIC_BASE_URL"] = "http://127.0.0.1:3456"
        
        env["NO_PROXY"] = "127.0.0.1"
        env["DISABLE_TELEMETRY"] = "true"
        
        # Execute claude command
        # -p (prompt mode) is used for one-off tasks
        proc = await asyncio.create_subprocess_exec(
            "claude", "-p", task,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env
        )
        
        # Wait for completion with timeout (30s for responsiveness, adjust if needed)
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=45)
            output = stdout.decode('utf-8', errors='replace')
            err_output = stderr.decode('utf-8', errors='replace')
            
            if not output.strip() and err_output:
                output = f"Error Output:\n{err_output}"
            elif not output.strip():
                output = "Command finished with no output."
                 
            # Format and sanitize response
            clean_out = html.escape(output)
            if len(clean_out) > 3800:
                 clean_out = clean_out[:3800] + "\n...(results truncated for Telegram overhead)"
                 
            await context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=processing_msg.message_id,
                text=f"<b>Claude Code Result:</b>\n<pre>{clean_out}</pre>",
                parse_mode='HTML'
            )
        except asyncio.TimeoutError:
            proc.kill()
            await context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=processing_msg.message_id,
                text="⏳ <b>Timeout</b>: Claude Code task is taking too long. Try a simpler request.",
                parse_mode='HTML'
            )

    except Exception as e:
        logger.error(f"Claude Code Execution Error: {e}")
        safe_error = html.escape(str(e))
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=processing_msg.message_id,
            text=f"❌ <b>Claude Code System Error</b>: {safe_error}",
            parse_mode='HTML'
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE, override_msg=None, force_search=False):
    user_id = update.effective_user.id
    incoming_text = override_msg if override_msg else update.message.text
    
    logger.info(f"Processing message from {user_id}: {incoming_text[:50]}...")
    
    # Send thinking placeholder
    thinking_msg = await update.effective_message.reply_html("💠 <i>Maverick is synthesizing...</i>")
    
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
            
        # 5. Generate completion (Resilient)
        try:
            answer = await get_resilient_completion(messages, user_id)
            if "💠" not in answer[:15]:
                answer = "💠 " + answer
        except Exception as e:
            logger.error(f"Critical failure in get_resilient_completion: {e}")
            answer = f"❌ <b>Maverick System Error</b>: {html.escape(str(e)[:200])}"
            
        # Save AI response
        save_message(user_id, "assistant", answer)
        
        # 6. Sanitize for Telegram Parsing
        answer = sanitize_for_telegram(answer)
        
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
        # Escape the error message to avoid Telegram parse errors (like <!doctype)
        safe_error = html.escape(str(e))[:200]
        error_text = f"❌ <b>Maverick Error</b>: {safe_error}"
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=thinking_msg.message_id,
            text=error_text,
            parse_mode='HTML'
        )

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    logger.error(f"Update {update} caused error {context.error}")
    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text(f"❌ Internal Bot Error: {str(context.error)[:100]}")
        except: pass

async def post_init(application: Application):
    """Set bot commands and description during startup."""
    await application.bot.set_my_commands([
        BotCommand("start", "Welcome message"),
        BotCommand("help", "Show all commands"),
        BotCommand("search", "Search literature"),
        BotCommand("claude", "Execute Claude Code task"),
        BotCommand("history", "Recent conversations"),
        BotCommand("clear", "Reset memory"),
        BotCommand("about", "About Maverick"),
        BotCommand("test", "Open Web App")
    ])
    try:
        await application.bot.set_my_description("Maverick AI 🦞: Your advanced clinical research synthesis engine. Powered by Groq (llama-3.3-70b-versatile) with biomedical search.")
        await application.bot.set_my_short_description("Maverick AI Research Bot — Powered by Groq")
        logger.info("Bot commands and description updated successfully")
    except Exception as e:
        logger.warning(f"Failed to set bot description: {e}")

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

    app.add_error_handler(error_handler)

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(CommandHandler("history", history_command))
    app.add_handler(CommandHandler("search", search_command))
    app.add_handler(CommandHandler("claude", claude_code_command))
    app.add_handler(CommandHandler("test", test_command))
    
    # Regular text messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("-" * 30)
    print("MAVERICK TELEGRAM BOT ONLINE")
    print(f"User DB: {DB_FILE}")
    print("-" * 30)
    
    app.run_polling()

if __name__ == "__main__":
    main()
