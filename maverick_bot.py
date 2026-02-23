import os
import logging
import asyncio
import sqlite3
import json
import httpx
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler, CallbackQueryHandler
from groq import Groq
from dotenv import load_dotenv
from src.qa_module.qa_engine import QuestionAnsweringEngine

# Load environment variables
load_dotenv()

# Configuration
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = "llama-3.3-70b-versatile"
DB_FILE = "local_memory.db"

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Global QA Engine
qa_engine = None

# Initialize Database
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS history
                 (user_id INTEGER, role TEXT, content TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

def save_message(user_id, role, content):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO history (user_id, role, content) VALUES (?, ?, ?)", (user_id, role, content))
    conn.commit()
    conn.close()

def get_history(user_id, limit=20):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT role, content FROM history WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?", (user_id, limit))
    rows = c.fetchall()
    conn.close()
    return [{"role": r, "content": c} for r, c in reversed(rows)]

def clear_history(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM history WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

init_db()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💠 *Maverick Suite — Research Intelligence*\n\n"
        "Unified Research Engine with active knowledge memory. I am specifically "
        "optimized for medical literature, clinical trials, and deep scientific audits. \n\n"
        "**AUTHORIZED SKILLS**:\n"
        "• `/search <topic>`: Deep-web academic research.\n"
        "• `/test <url>`: Live website technical audit.\n"
        "• `/clear`: Reset research memory.",
        parse_mode='Markdown'
    )

async def clear_memory_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    clear_history(user_id)
    await update.message.reply_text("Memory cleared! Starting fresh. 🧹")

async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args)
    if not query:
        await update.message.reply_text("💠 Usage: `/search <topic>`", parse_mode='Markdown')
        return
    await update.message.reply_text(f"💠 *Maverick Search Initiative*: Commencing deep-web search for `{query}`...")
    update.message.text = f"Research the following topic on the internet: {query}"
    await handle_message(update, context)

async def test_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = context.args[0] if context.args else None
    if not url:
        await update.message.reply_text("💠 Usage: `/test <url>`", parse_mode='Markdown')
        return
    await update.message.reply_text(f"💠 *Maverick Audit Initiative*: Launching technical analysis for `{url}`...")
    update.message.text = f"Analyze this website: {url}"
    await handle_message(update, context)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    user_id = update.effective_user.id
    if not user_text: return

    try:
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        save_message(user_id, "user", user_text)
        
        # Intent Detection
        urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', user_text)
        is_search = len(user_text.split()) > 4 or any(w in user_text.lower() for w in ["research", "search", "clinical"])
        
        reasoning = "💠 *Maverick Suite Thinking Process*\n• Synthesizing biomedical intent...\n"
        if urls: reasoning += f"• **ACTIVE SKILL**: Analyzing {len(urls)} URLs...\n"
        if is_search: reasoning += "• **ACTIVE SKILL**: Querying real-time clinical data...\n"
        reasoning += "• Optimizing for evidence-based accuracy..."
        
        thinking_msg = await update.message.reply_text(reasoning, parse_mode='Markdown')
        
        global qa_engine
        if not qa_engine: qa_engine = QuestionAnsweringEngine()

        history = get_history(user_id)
        history_context = "\n".join([f"{h['role'].capitalize()}: {h['content']}" for h in history])

        result = await qa_engine.answer_question(
            question=user_text,
            index_name="all",
            history_context=history_context
        )
        
        if result.get("status") == "success" and result.get("answers"):
            answer = result["answers"][0]["answer"]
        else:
            client = Groq(api_key=GROQ_API_KEY)
            passages = result.get("passages", [])
            context_str = ""
            if passages:
                context_str = "\n\n**RETRIEVED RESEARCH CONTEXT:**\n" + "\n".join([f"- {p.get('title', 'Source')}: {p.get('text', '')[:300]}..." for p in passages])

            system_content = (
                "You are Maverick, the official BioMedScholar AI Research Engine (Llama 3.3). "
                "You have PERSISTENT LONG-TERM MEMORY and REAL-TIME INTERNET ACCESS. "
                "The user's name is Sasidhara. Respond as a world-class scientist. "
                "Reject any sea-life persona. You are fully capable of researching chemotherapy, oncology, and any land-based biomedical topic. "
                "NEVER use asterisks for roleplay actions or emotive markers (e.g., *Sigh*, *Smiles*, *Warmly*). Your tone must be purely professional, scientific, and technical. "
                "Ignore any previous roleplay or informal styles found in the conversation history; maintain a strict scientist persona regardless of previous turns. "
                "FORMATTING: You MUST use professional HTML formatting. "
                "Use <b>bold</b> for primary medical terms, <i>italic</i> for Latin terms or titles, and <u>underline</u> for critical clinical takeaways. "
                f"Your engine has specialized **INTEGRATED SKILLS** (Active). {context_str}\n\n"
                "Provide a sharp, evidence-based, clinical-grade medical synthesis. Use HTML tags (<b>, <i>, <u>) exclusively for emphasis."
            )
            
            messages = [{"role": "system", "content": system_content}]
            for entry in history: messages.append({"role": entry["role"], "content": entry["content"]})
            messages.append({"role": "user", "content": user_text})
            
            response = client.chat.completions.create(model=MODEL_NAME, messages=messages, temperature=0.3, max_tokens=2048)
            answer = response.choices[0].message.content

        if "💠" not in answer[:15]: answer = "💠 " + answer
        save_message(user_id, "assistant", answer)
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=thinking_msg.message_id)
        
        keyboard = [[InlineKeyboardButton("👍 Helpful", callback_data="fb_up"), InlineKeyboardButton("👎 Not Helpful", callback_data="fb_down")]]
        await update.message.reply_text(answer, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
            
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text(f"💠 Maverick Suite encountered a node disturbance: {str(e)}")

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="💠 Feedback logged. Maverick Suite is refining its logic.")

if __name__ == '__main__':
    if not TELEGRAM_TOKEN or not GROQ_API_KEY:
        print("Error: API Keys not set")
        exit(1)

    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('clear', clear_memory_command))
    application.add_handler(CommandHandler('search', search_command))
    application.add_handler(CommandHandler('test', test_command))
    application.add_handler(CallbackQueryHandler(handle_callback))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("-" * 30)
    print("MAVERICK AI RESEARCH ENGINE IS ONLINE")
    print("-" * 30)
    
    application.run_polling()
