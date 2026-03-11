import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

try:
    models = client.models.list()
    for model in models.data:
        print(model.id)
except Exception as e:
    print(f"Error: {e}")
