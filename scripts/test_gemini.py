
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.qa_module.gemini_generator import GeminiGenerator

def test_gemini():
    gen = GeminiGenerator()
    print(f"API Key found: {bool(gen.api_key)}")
    if gen.api_key:
        print(f"API Key prefix: {gen.api_key[:5]}...")
    
    question = "What is the capital of France?"
    passages = [{"text": "Paris is the capital of France.", "title": "Geography", "source_type": "test"}]
    
    print("Testing generation...")
    try:
        result = gen.generate_answer(question, passages)
        print("\nResult:")
        print(result)
    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    test_gemini()
