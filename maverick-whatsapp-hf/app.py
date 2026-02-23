import os
import sqlite3
import logging
import threading
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from groq import Groq

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = "meta-llama/llama-4-maverick-17b-128e-instruct"
DB_FILE = "/tmp/whatsapp_memory.db" # Use /tmp for HF Spaces ephemeral write access

# Initialize Groq Client
try:
    groq_client = Groq(api_key=GROQ_API_KEY)
except Exception as e:
    logger.error(f"Failed to initialize Groq client: {e}")
    groq_client = None

# Initialize Database
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS history
                 (user_id TEXT, role TEXT, content TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

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

init_db()

app = Flask(__name__)

@app.route("/")
def health():
    return "Maverick WhatsApp Bot (Llama 4) is running."

@app.route("/whatsapp", methods=['POST'])
def whatsapp_reply():
    """Handle incoming WhatsApp messages from Twilio."""
    incoming_msg = request.values.get('Body', '')
    sender_number = request.values.get('From')
    
    logger.info(f"Received message from {sender_number}: {incoming_msg[:50]}...")
    
    resp = MessagingResponse()
    msg = resp.message()
    
    if not groq_client:
        msg.body("❌ *Error*: Groq API key is not configured.")
        return str(resp)

    try:
        # Save user message
        save_message(sender_number, "user", incoming_msg)
        
        # Get history
        history = get_history(sender_number)
        
        # Prepare messages for Llama 4 Maverick
        messages = [
            {
                "role": "system", 
                "content": (
                    "You are the Maverick Suite (💠), a premium analytical biomedical research engine. "
                    "Your identity is sharp, precise, and authoritative. "
                    "You are powered by Llama 4 Maverick architecture. "
                    "You are communicating with the user via WhatsApp. "
                    "You maintain active knowledge memory to ensure research continuity."
                )
            }
        ]
        messages.extend(history)
        
        # Generate completion
        completion = groq_client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.3,
            max_tokens=1024
        )
        
        answer = completion.choices[0].message.content
        
        # Save AI response
        save_message(sender_number, "assistant", answer)
        
        # Twilio WhatsApp limit is 1600 characters per message
        if len(answer) > 1500:
            msg.body(answer[:1500] + "...")
        else:
            msg.body(answer)
            
    except Exception as e:
        logger.error(f"Error processing WhatsApp message: {e}")
        msg.body(f"❌ *Error*: {str(e)}")
        
    return str(resp)

if __name__ == "__main__":
    # HF Spaces uses port 7860
    app.run(host='0.0.0.0', port=7860)
