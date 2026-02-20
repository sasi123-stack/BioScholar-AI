import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

print(f"Testing Groq Key: {GROQ_API_KEY[:10]}...")

try:
    client = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": "test"}],
        max_tokens=5
    )
    print("✅ Success! Key is valid.")
except Exception as e:
    print(f"❌ Failed: {e}")
