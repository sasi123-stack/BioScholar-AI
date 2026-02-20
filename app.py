import os
import logging
import asyncio
import sqlite3
import threading
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler
from groq import Groq
from flask import Flask

# Configuration
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = "meta-llama/llama-4-maverick-17b-128e-instruct"
DB_FILE = "conversation_history.db"

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

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

def get_history(user_id, limit=10):
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

# Initialize Groq Client
try:
    groq_client = Groq(api_key=GROQ_API_KEY)
except Exception as e:
    logger.error(f"Failed to initialize Groq client: {e}")
    groq_client = None

# Dummy Flask app for Hugging Face health check
app = Flask(__name__)

@app.route('/')
def health():
    return "Maverick AI with Long Term Memory is online."

def run_flask():
    app.run(host='0.0.0.0', port=7860)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚡ *Maverick AI (Llama 4) with Long-Term Memory Connected*\n\n"
        "I remember our previous conversations! Ask me anything about "
        "medical literature or scientific papers. \n\n"
        "Use /clear to reset my memory.",
        parse_mode='Markdown'
    )

async def clear_memory_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    clear_history(user_id)
    await update.message.reply_text("Memory cleared! Starting fresh. 🧹")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    user_id = update.effective_user.id
    
    if not user_text:
        return

    try:
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        # Save user message
        save_message(user_id, "user", user_text)
        
        # Get history
        history = get_history(user_id)
        
        # Prepare messages for LLM
        messages = [
            {
                "role": "system", 
                "content": (
                    "You are Maverick, a sharp, precise, and analytical biomedical research assistant. "
                    "vibe: Sharp, precise, analytical, and highly efficient. emoji: 🦞. "
                    "You are powered by Llama 4 Maverick. Use professional but accessible language. "
                    "You have long-term memory and should refer to previous parts of the conversation when relevant."
                )
            }
        ]
        messages.extend(history)
        
        response = groq_client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.3,
            max_tokens=2048
        )
        
        answer = response.choices[0].message.content
        
        # Save AI response
        save_message(user_id, "assistant", answer)
        
        if len(answer) > 4000:
            for i in range(0, len(answer), 4000):
                await update.message.reply_text(answer[i:i+4000])
        else:
            await update.message.reply_text(answer)
            
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        await update.message.reply_text(f"❌ *Error*: {str(e)}", parse_mode='Markdown')

if __name__ == '__main__':
    if not TELEGRAM_TOKEN or not GROQ_API_KEY:
        logger.error("Error: API Keys not set")
        exit(1)

    # Start Flask in a background thread
    threading.Thread(target=run_flask, daemon=True).start()

    # Build the Telegram Application
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    # Add Handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('clear', clear_memory_command))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("🚀 MAVERICK AI WITH MEMORY IS ONLINE")
    application.run_polling()
