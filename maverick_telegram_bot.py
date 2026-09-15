import os
import socket
import sqlite3
import logging
import asyncio
import html
import re
import fitz # PyMuPDF
import io
import base64
import httpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.request import HTTPXRequest
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, Application
from groq import AsyncGroq
from dotenv import load_dotenv
import sys

from src.utils.ai_provider import get_first_configured_api_key

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
DNS_PRIORITY_HOSTS = ["api.groq.com", "google.com", "huggingface.co", "api.telegram.org", "openrouter.ai"]

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
                    try:
                        numeric_port = int(port)
                    except (ValueError, TypeError):
                        numeric_port = 443 if 'https' in str(port).lower() else (80 if 'http' in str(port).lower() else 0)
                    for ip in ips:
                        try:
                            results.extend(_original_getaddrinfo(ip, port, family, type, proto, flags))
                        except:
                            # pyrefly: ignore [bad-argument-type]
                            results.append((socket.AF_INET, type or socket.SOCK_STREAM, proto or 6, '', (ip, numeric_port)))
                    return results
            except Exception as pe:
                print(f">>> [DNS PATCH] Fallback resolution failed: {pe}", flush=True)
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
GROQ_API_KEY = get_first_configured_api_key(["GROQ_API_KEY"])
OPENROUTER_API_KEY = get_first_configured_api_key([
    "OPENROUTER_API_KEY",
    "OPENCLAW_API_KEY",
    "FREEMODEL_API_KEY",
    "FREE_MODEL_API_KEY",
    "OPENAI_API_KEY",
])
MODEL_NAME = "openai/gpt-oss-120b"
VISION_MODEL = "meta-llama/llama-3.2-11b-vision-instruct:free" 
DB_FILE = "/tmp/conversation_history.db" if os.path.exists("/tmp") else "local_memory.db"

# API Endpoints
OPENROUTER_API_BASE = (
    os.getenv("OPENROUTER_API_BASE")
    or os.getenv("FREEMODEL_API_BASE")
    or os.getenv("FREE_MODEL_API_BASE")
    or "https://openrouter.ai/api/v1"
)

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
        c.execute('''CREATE TABLE IF NOT EXISTS memories
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      user_id INTEGER NOT NULL,
                      content TEXT NOT NULL,
                      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                      updated_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        c.execute("CREATE INDEX IF NOT EXISTS idx_memories_user_id ON memories (user_id)")
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
        c.execute("DELETE FROM memories WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def add_memory(user_id: int, content: str):
    content = " ".join(content.split()).strip()
    if not content or len(content) > 500:
        return False
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute(
            "SELECT id FROM memories WHERE user_id = ? AND lower(content) = lower(?)",
            (user_id, content),
        )
        if c.fetchone():
            conn.close()
            return False
        c.execute(
            "INSERT INTO memories (user_id, content) VALUES (?, ?)",
            (user_id, content),
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Add memory error: {e}")
        return False

def get_memories(user_id: int, limit=20):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute(
            "SELECT id, content FROM memories WHERE user_id = ? "
            "ORDER BY updated_at DESC, id DESC LIMIT ?",
            (user_id, limit),
        )
        rows = c.fetchall()
        conn.close()
        return [{"id": memory_id, "content": content} for memory_id, content in rows]
    except Exception as e:
        logger.error(f"Get memories error: {e}")
        return []

def delete_memory(user_id: int, memory_id: int):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("DELETE FROM memories WHERE user_id = ? AND id = ?", (user_id, memory_id))
        deleted = c.rowcount > 0
        conn.commit()
        conn.close()
        return deleted
    except Exception as e:
        logger.error(f"Delete memory error: {e}")
        return False

def extract_explicit_memory(text: str):
    """Capture only unambiguous user facts, never arbitrary conversation text."""
    patterns = [
        r"^(?:please\s+)?remember(?:\s+that)?\s+(.+)$",
        r"^my\s+name\s+is\s+(.+)$",
        r"^i\s+(?:am|work\s+at|study\s+at|prefer|like)\s+(.+)$",
    ]
    for pattern in patterns:
        match = re.match(pattern, text.strip(), flags=re.IGNORECASE)
        if match:
            value = match.group(1).strip().rstrip(".!?")
            if value and len(value) <= 450:
                if pattern.startswith("^my"):
                    return f"The user's name is {value}."
                return value[0].upper() + value[1:] + "."
    return None

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
    """Enhanced sanitizer that converts Markdown symbols and complex HTML to Telegram-safe HTML."""
    if not text:
        return ""
    
    import re
    import html

    # 1. Protect existing code blocks (often generated by AI with ``` or <code>)
    # We want to preserve their content and escape it properly later
    code_blocks = []
    def placeholder_code(match):
        code_blocks.append(match.group(0))
        return f"__CODE_BLOCK_{len(code_blocks)-1}__"
    
    # Capture code blocks with or without language markers
    text = re.sub(r'```(?:\w+)?\n?.*?```', placeholder_code, text, flags=re.DOTALL)
    text = re.sub(r'<code>.*?</code>', placeholder_code, text, flags=re.DOTALL)

    # 2. Escape illegal HTML characters in the REMAINING text
    # This ensures a stray '<' doesn't crash the Telegram API
    text = html.escape(text)

    # 3. Handle Markdown Bold (** or __)
    text = re.sub(r'(\*\*|__)(.*?)\1', r'<b>\2</b>', text)
    
    # 4. Handle Markdown Italic (* or _ inside spaces)
    text = re.sub(r'(?<!\w)([\*_])(?!\s)(.*?)(?<!\s)\1(?!\w)', r'<i>\2</i>', text)

    # 5. Handle Markdown Headers (###, ##, #)
    text = re.sub(r'^(#{1,6})\s*(.*?)$', r'<b>\2</b>', text, flags=re.MULTILINE)

    # 6. Handle Markdown Bullet Points (*, -, +)
    text = re.sub(r'^\s*[\*\-\+]\s+', '• ', text, flags=re.MULTILINE)

    # 7. Convert escaped HTML tags back to real tags ONLY IF they are supported
    supported_tags = ['b', 'strong', 'i', 'em', 'u', 'ins', 's', 'strike', 'del', 'code', 'pre', 'a']
    for tag in supported_tags:
        text = text.replace(f'&lt;{tag}&gt;', f'<{tag}>')
        text = text.replace(f'&lt;/{tag}&gt;', f'</{tag}>')
        # Handle tags with attributes (like <a href="...">)
        text = re.sub(fr'&lt;{tag}\s+(.*?)&gt;', fr'<{tag} \1>', text, flags=re.IGNORECASE)

    # 8. Restore and Clean Code Blocks
    for i, block in enumerate(code_blocks):
        # Strip the ``` or <code> symbols
        content = re.sub(r'^```(?:\w+)?\n?|```$', '', block).strip()
        content = re.sub(r'^<code>|</code>$', '', content).strip()
        # Escape the inner content of the code block
        content = html.escape(content)
        # Use <pre> for code blocks in Telegram
        text = text.replace(f"__CODE_BLOCK_{i}__", f"<pre>{content}</pre>")

    # 9. Clean up whitespace and special entities
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.replace('&nbsp;', ' ')
    
    # Final check: Unescape certain HTML entities that AI might have produced but we escaped
    text = text.replace('&amp;quot;', '"').replace('&amp;apos;', "'")
    
    return text.strip()

async def get_vision_completion(prompt: str, image_base64: str, user_id: int):
    """Get completion from a vision model via OpenRouter."""
    if not OPENROUTER_API_KEY:
        raise Exception("OPENROUTER_API_KEY is not configured.")

    async with httpx.AsyncClient(timeout=45.0) as client:
        try:
            logger.info(f"Querying vision model '{VISION_MODEL}' for user {user_id}")
            response = await client.post(
                f"{OPENROUTER_API_BASE}/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": VISION_MODEL,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
                                },
                            ],
                        }
                    ],
                    "max_tokens": 1500,
                    "temperature": 0.2,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data['choices'][0]['message']['content']

        except httpx.HTTPStatusError as e:
            logger.error(f"OpenRouter vision API error: {e.response.status_code} {e.response.text}")
            raise Exception(f"Vision API request failed: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Vision completion error: {e}")
            raise

async def get_resilient_completion(messages: list, user_id: int):
    """Try multiple Groq models with fallback chain."""
    if not ai_client:
        raise Exception("Groq client not initialized. Check GROQ_API_KEY environment variable.")

    models_to_try = [
        MODEL_NAME,                    # Primary: openai/gpt-oss-120b
        "openai/gpt-oss-20b",          # Fallback 1: Fast 20B
        "qwen/qwen3.8-27b",            # Fallback 2: Qwen 27B
        "groq/compound-mini",          # Fallback 3: Compound Mini
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
            msg = completion.choices[0].message
            answer = msg.content or getattr(msg, "reasoning", "") or ""
            
            # Guard against HTML gateway error pages
            if answer and ("<!DOCTYPE" in answer[:20] or "<html>" in answer.lower()[:20]):
                logger.warning(f"Model {model} returned HTML. Trying next model...")
                continue
                
            if answer and len(answer.strip()) > 5:
                return answer.strip()
            
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
        f"/code &lt;task&gt; - AI Coding Assistant\n"
        f"/help - Show all commands\n"
        f"/history - View recent conversations\n"
        f"/remember &lt;fact&gt; - Save a fact for future chats\n"
        f"/memories - View saved facts\n"
        f"/forget &lt;number&gt; - Delete a saved fact\n"
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
        "• /code &lt;task&gt; - AI Coding Assistant\n"
        "• /history - Recall your last 5 interactions\n"
        "• /remember &lt;fact&gt; - Save a fact for future chats\n"
        "• /memories - View saved facts\n"
        "• /forget &lt;number&gt; - Delete a saved fact\n"
        "• /clear - Reset conversation memory\n"
        "• /about - Learn about the Maverick AI engine\n"
        "• /test - Launch the full Research Desk"
    )
    await update.message.reply_html(help_text)

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    about_text = (
        "💠 <b>About Maverick AI</b>\n\n"
        "Maverick is a high-performance biomedical synthesis engine powered by "
        "<b>gpt-oss:120b (Claude Code) via Groq</b>. "
        "Optimized for clinical research, oncology, and pharmacology data extraction."
    )
    await update.message.reply_html(about_text)

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if clear_history(user_id):
        await update.message.reply_text("🧹 Memory cleared successfully.")
    else:
        await update.message.reply_text("❌ Failed to clear memory.")

async def remember_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_html("Usage: <code>/remember I work at Example University</code>")
        return
    content = " ".join(context.args)
    if add_memory(update.effective_user.id, content):
        await update.message.reply_text("🧠 Saved. I will remember this for future conversations.")
    else:
        await update.message.reply_text("This fact is already saved, empty, or too long.")

async def memories_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    memories = get_memories(update.effective_user.id)
    if not memories:
        await update.message.reply_text("I do not have any saved memories for you yet.")
        return
    text = "🧠 <b>Your saved memories:</b>\n\n"
    for index, memory in enumerate(memories, start=1):
        text += f"<b>{index}.</b> {html.escape(memory['content'])}\n"
    await update.message.reply_html(text)

async def forget_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_html("Usage: <code>/forget 1</code> (use /memories to see numbers)")
        return
    index = int(context.args[0])
    memories = get_memories(update.effective_user.id)
    if index < 1 or index > len(memories):
        await update.message.reply_text("That memory number was not found.")
        return
    if delete_memory(update.effective_user.id, memories[index - 1]["id"]):
        await update.message.reply_text("🧹 Memory deleted.")
    else:
        await update.message.reply_text("I could not delete that memory.")

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
    """Answer code, analysis, and research tasks using Groq AI (Claude-style agent)."""
    if not context.args:
        if update.effective_message:
            await update.effective_message.reply_html(
                "<b>🛠️ Maverick Code Agent</b>\n\n"
                "Ask me to analyze code, explain concepts, or help with research tasks.\n"
                "Example: <code>/claude analyze the search module architecture</code>\n"
                "Example: <code>/claude write a unit test for the API endpoint</code>\n"
                "Example: <code>/claude explain how BioBERT embeddings work</code>"
            )
        return

    task = " ".join(context.args)
    user_id = update.effective_user.id
    processing_msg = await update.effective_message.reply_html("👨‍💻 <i>Maverick Code Agent thinking...</i>")

    try:
        system_prompt = (
            "You are Maverick Code Agent — an expert AI assistant specialized in biomedical software, "
            "Python, FastAPI, machine learning, and research architecture. "
            "You help developers analyze code, write tests, debug issues, and explain complex systems. "
            "Be precise, concise, and technically accurate. "
            "Use plain text with minimal formatting (no markdown symbols like **, ##). "
            "Use <b>bold</b> for key terms and <code>code</code> for snippets (Telegram HTML mode)."
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": task}
        ]

        answer = await get_resilient_completion(messages, user_id)

        # Sanitize for Telegram
        answer = sanitize_for_telegram(answer)
        if len(answer) > 3900:
            answer = answer[:3900] + "\n\n<i>...(response truncated)</i>"

        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=processing_msg.message_id,
            text=f"🛠️ <b>Maverick Code Agent:</b>\n\n{answer}",
            parse_mode='HTML'
        )

    except Exception as e:
        logger.error(f"Claude Code Command Error: {e}")
        safe_error = html.escape(str(e)[:200])
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=processing_msg.message_id,
            text=f"❌ <b>Agent Error</b>: {safe_error}",
            parse_mode='HTML'
        )

async def code_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Answer coding, programming, and software engineering tasks."""
    if not context.args:
        if update.effective_message:
            await update.effective_message.reply_html(
                "<b>💻 Maverick Coding Skill</b>\n\n"
                "Ask me to write code, debug scripts, or explain algorithms.\n"
                "Example: <code>/code write a Python script to fetch NCBI data</code>\n"
                "Example: <code>/code explain React hooks</code>"
            )
        return

    task = " ".join(context.args)
    user_id = update.effective_user.id
    processing_msg = await update.effective_message.reply_html("👨‍💻 <i>Maverick Code Agent thinking...</i>")

    try:
        system_prompt = (
            "You are Maverick Code Agent — an expert AI assistant specialized in software engineering, "
            "web development, ML, and computational biology. "
            "You help developers write code, debug issues, and explain programming concepts. "
            "Be precise and technically accurate. "
            "For formatting in Telegram: Use <b>bold</b> and for code blocks use <code>your code here</code>."
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": task}
        ]

        answer = await get_resilient_completion(messages, user_id)
        answer = sanitize_for_telegram(answer)

        if len(answer) > 3900:
            answer = answer[:3900] + "\n\n<i>...(response truncated)</i>"

        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=processing_msg.message_id,
            text=f"💻 <b>Maverick Code:</b>\n\n{answer}",
            parse_mode='HTML'
        )

    except Exception as e:
        logger.error(f"Code Command Error: {e}")
        safe_error = html.escape(str(e)[:200])
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=processing_msg.message_id,
            text=f"❌ <b>Code Error</b>: {safe_error}",
            parse_mode='HTML'
        )

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle PDF uploads."""
    user_id = update.effective_user.id
    doc = update.message.document
    
    if not doc.file_name.lower().endswith(".pdf") and "pdf" not in doc.mime_type.lower():
        await update.message.reply_html("💠 <i>Maverick currently only supports PDF analysis. Try uploading a research paper.</i>")
        return

    thinking = await update.message.reply_html(f"📑 <i>Analyzing PDF: {html.escape(doc.file_name)}...</i>")
    
    try:
        new_file = await context.bot.get_file(doc.file_id)
        # Download to memory
        file_bytes = await new_file.download_as_bytearray()
        
        # Extract text
        with fitz.open(stream=file_bytes, filetype="pdf") as pdf:
            pdf_text = ""
            for page in pdf:
                pdf_text += page.get_text()
        
        extracted_context = pdf_text[:4000] # Limit to avoid prompt overflow
        
        # Forward to handle_message with extra context
        caption = update.message.caption or f"What are the key findings in {doc.file_name}?"
        rich_query = f"{caption}\n\n[CONTEXT FROM ATTACHED PDF: {doc.file_name}]\n{extracted_context}"
        
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=thinking.message_id)
        await handle_message(update, context, override_msg=rich_query, original_caption=caption)
        
    except Exception as e:
        logger.error(f"PDF Analysis Error: {e}")
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=thinking.message_id,
            text=f"❌ <b>PDF Extraction Error</b>: {html.escape(str(e)[:200])}",
            parse_mode='HTML'
        )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle image uploads and analyze them with a vision model."""
    user_id = update.effective_user.id
    caption = update.message.caption or "Analyze this biomedical image and provide a detailed description."

    # Notify the user that the image is being processed
    thinking_msg = await update.message.reply_html("🔬 <i>Analyzing image with Maverick Vision...</i>")

    try:
        # Get the largest photo size
        photo = update.message.photo[-1]
        photo_file = await context.bot.get_file(photo.file_id)
        
        # Download the photo into memory
        file_bytes_io = io.BytesIO()
        await photo_file.download_to_memory(file_bytes_io)
        file_bytes_io.seek(0)
        
        # Encode the image in base64
        image_base64 = base64.b64encode(file_bytes_io.read()).decode('utf-8')
        
        # Get the analysis from the vision model
        analysis = await get_vision_completion(caption, image_base64, user_id)
        
        # Save messages to history
        save_message(user_id, "user", f"[Image] {caption}")
        save_message(user_id, "assistant", analysis)
        
        # Sanitize the response and send it
        sanitized_analysis = sanitize_for_telegram(analysis)
        if len(sanitized_analysis) > 4000:
            sanitized_analysis = sanitized_analysis[:3990] + "..."

        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=thinking_msg.message_id,
            text=f"👁️‍🗨️ <b>Maverick Vision Analysis:</b>\n\n{sanitized_analysis}",
            parse_mode='HTML'
        )

    except Exception as e:
        logger.error(f"Photo analysis error: {e}")
        safe_error = html.escape(str(e))[:200]
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=thinking_msg.message_id,
            text=f"❌ <b>Vision Error</b>: {safe_error}",
            parse_mode='HTML'
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE, override_msg=None, force_search=False, original_caption=None):
    user_id = update.effective_user.id
    incoming_text = override_msg if override_msg else update.message.text
    display_text = original_caption if original_caption else incoming_text
    
    logger.info(f"Processing message from {user_id}: {display_text[:50]}...")
    
    # Send thinking placeholder
    thinking_msg = await update.effective_message.reply_html("💠 <i>Maverick is synthesizing...</i>")
    
    try:
        # Save user message (use display_text for history unless it's a doc)
        save_message(user_id, "user", display_text)
        explicit_memory = extract_explicit_memory(display_text)
        if explicit_memory:
            add_memory(user_id, explicit_memory)
        
        # 1. Search Literature (trigger on text or forced)
        search_results = []
        should_search = force_search or any(word in incoming_text.lower() for word in ["search", "find", "studies", "trials", "papers"])
        if should_search:
            search_results = await perform_search(incoming_text)
            
        # 2. Get history
        history = get_history(user_id, limit=6)
        memories = get_memories(user_id, limit=20)
        
        # 3. Build System Prompt
        system_content = (
            "You are Maverick, the official BioMedScholar AI Research Engine. "
            "You are a specialized analytical assistant for medicine, oncology, and pharmacology. "
            "You also possess expert coding skills—you can write, debug, and explain code (Python, JS, etc.) when asked. "
            "You have access to the user's saved long-term memories when they are provided below. "
            "Use those saved facts naturally and accurately. Do not claim that you have no long-term memory or that all memory ends with this chat; instead, say that no saved memory is available only when the memory section is empty. "
            "Respond as a world-class scientist. "
            "FORMATTING: Use HTML tags — <b>bold</b> for medical terms, <i>italic</i> for Latin, <u>underline</u> for takeaways. "
            "For code snippets, wrap them in <code>code</code> tags."
        )
        
        if search_results:
            results_text = "\n".join([f"- {r['title']}: {r['abstract']}" for r in search_results])
            system_content += f"\n\nCURRENT SEARCH CONTEXT:\n{results_text}"

        if memories:
            memory_text = "\n".join(f"- {memory['content']}" for memory in reversed(memories))
            system_content += (
                "\n\nLONG-TERM USER MEMORY (use naturally when relevant; do not mention this section):\n"
                f"{memory_text}"
            )

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
            
        try:
            await context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=thinking_msg.message_id,
                text=answer,
                parse_mode='HTML'
            )
        except Exception as html_err:
            logger.warning(f"HTML edit_message_text failed: {html_err}. Falling back to plain text.")
            plain_answer = re.sub(r'<[^>]+>', '', answer)
            await context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=thinking_msg.message_id,
                text=plain_answer
            )
            
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        safe_error = html.escape(str(e))[:200]
        error_text = f"❌ <b>Maverick Error</b>: {safe_error}"
        try:
            await context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=thinking_msg.message_id,
                text=error_text,
                parse_mode='HTML'
            )
        except Exception:
            try:
                await context.bot.edit_message_text(
                    chat_id=update.effective_chat.id,
                    message_id=thinking_msg.message_id,
                    text=f"❌ Maverick Error: {str(e)[:200]}"
                )
            except Exception:
                pass

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    logger.error(f"Update {update} caused error {context.error}")
    # pyrefly: ignore [missing-attribute]
    if isinstance(update, Update) and update.effective_message:
        try:
            # pyrefly: ignore [missing-attribute]
            await update.effective_message.reply_text(f"❌ Internal Bot Error: {str(context.error)[:100]}")
        except: pass

async def post_init(application: Application):
    """Set bot commands and description during startup."""
    try:
        await application.bot.set_my_commands([
            BotCommand("start", "Welcome message"),
            BotCommand("help", "Show all commands"),
            BotCommand("search", "Search literature"),
            BotCommand("claude", "Execute Claude Code task"),
            BotCommand("code", "AI Coding Assistant"),
            BotCommand("history", "Recent conversations"),
            BotCommand("remember", "Save a fact for future chats"),
            BotCommand("memories", "View saved facts"),
            BotCommand("forget", "Delete a saved fact"),
            BotCommand("clear", "Reset memory"),
            BotCommand("about", "About Maverick"),
            BotCommand("test", "Open Web App")
        ])
        logger.info("Bot commands updated successfully")
    except Exception as e:
        logger.warning(f"Failed to set bot commands: {e}")

    try:
        await application.bot.set_my_description("Maverick AI 💠: Your advanced clinical research synthesis engine. Powered by OpenAI GPT OSS 120B via Groq with biomedical search.")
        await application.bot.set_my_short_description("Maverick AI — Powered by OpenAI GPT OSS 120B via Groq")
        logger.info("Bot description updated successfully")
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
        t_request = HTTPXRequest(
            connect_timeout=30.0,
            read_timeout=30.0,
            write_timeout=30.0,
            pool_timeout=30.0
        )
        app = ApplicationBuilder().token(TELEGRAM_TOKEN).request(t_request).post_init(post_init).build()
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
    app.add_handler(CommandHandler("remember", remember_command))
    app.add_handler(CommandHandler("memories", memories_command))
    app.add_handler(CommandHandler("forget", forget_command))
    app.add_handler(CommandHandler("search", search_command))
    app.add_handler(CommandHandler("claude", claude_code_command))
    app.add_handler(CommandHandler("code", code_command))
    app.add_handler(CommandHandler("test", test_command))
    
    # Regular text messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.Document.PDF, handle_document))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("-" * 30)
    print("MAVERICK TELEGRAM BOT ONLINE")
    print(f"User DB: {DB_FILE}")
    print("-" * 30)
    
    app.run_polling(bootstrap_retries=-1, timeout=30)

if __name__ == "__main__":
    main()
