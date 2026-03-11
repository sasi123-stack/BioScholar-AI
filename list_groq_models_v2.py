import os
import sys
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

print(f"Connecting to Groq with key: {GROQ_API_KEY[:10]}...", flush=True)

try:
    print("Listing models...", flush=True)
    models = client.models.list()
    for model in models.data:
        print(model.id, flush=True)
except Exception as e:
    print(f"Error: {e}", flush=True)
