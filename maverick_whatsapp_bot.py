import os
import sqlite3
import logging
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = "meta-llama/llama-4-maverick-17b-128e-instruct"
DB_FILE = "whatsapp_memory.db"

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

init_db()

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
        
        # Prepare messages for Llama 3.3
        messages = [
            {
                "role": "system", 
                "content": (
                    "You are the Maverick Suite (💠), a premium analytical biomedical research engine. "
                    "Your identity is sharp, precise, and authoritative. "
                    "You are powered by Llama 3.3 Maverick architecture. "
                    "You are communicating with the user via WhatsApp. "
                    "You maintain active knowledge memory to ensure research continuity. "
                    "Provide clear, evidence-based insights, and keep your tone professional yet engaging."
                )
            }
        ]
        
        last_role = "system"
        for h in history:
            if h['role'] == last_role:
                messages[-1]['content'] += "\n" + h['content']
            else:
                messages.append(h)
                last_role = h['role']
        
        # Generate completion
        completion = groq_client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.3,
            max_tokens=2048
        )
        
        answer = completion.choices[0].message.content
        
        # Save AI response
        save_message(sender_number, "assistant", answer)
        
        # Twilio WhatsApp limit is 1600 characters per message
        if len(answer) > 1500:
            # For simplicity, we send the first 1500 chars. 
            # In a real app, you'd send multiple messages or use a media URL.
            msg.body(answer[:1500] + "...")
        else:
            msg.body(answer)
            
    except Exception as e:
        logger.error(f"Error processing WhatsApp message: {e}")
        msg.body(f"❌ *Error*: {str(e)}")
        
    return str(resp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("-" * 30)
    print("MAVERICK WHATSAPP BOT IS ONLINE")
    print(f"Model: {MODEL_NAME}")
    print(f"Endpoint: /whatsapp")
    print("-" * 30)
    app.run(host='0.0.0.0', port=port)
