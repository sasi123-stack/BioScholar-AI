import os
import logging
import asyncio
import sqlite3
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = "meta-llama/llama-4-maverick-17b-128e-instruct"
DB_FILE = "local_memory.db"

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

# Initialize Groq Client
try:
    groq_client = Groq(api_key=GROQ_API_KEY)
except Exception as e:
    logger.error(f"Failed to initialize Groq client: {e}")
    groq_client = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚡ *Maverick AI (Llama 4) with Local Memory Connected*\n\n"
        "I now have long-term memory! Send me any question about "
        "medical literature, clinical trials, or scientific papers. \n\n"
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
        
        # Prepare messages
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
        print("Error: API Keys not set")
        exit(1)

    # Build the Telegram Application
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    # Add Handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('clear', clear_memory_command))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("-" * 30)
    print("MAVERICK AI WITH MEMORY IS ONLINE")
    print(f"Model: {MODEL_NAME}")
    print("Connecting to Telegram...")
    print("-" * 30)
    
    application.run_polling()
