import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = "openai/gpt-oss-120b"

client = Groq(api_key=GROQ_API_KEY)

try:
    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": "Hello"}],
        max_tokens=10
    )
    print("Success!")
    print(completion.choices[0].message.content)
except Exception as e:
    print(f"Error: {e}")
