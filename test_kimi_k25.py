"""
Test script for Kimi K2.5 integration with OpenClaw
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from qa_module.openclaw_generator import OpenClawGenerator
from utils.logger import get_logger

logger = get_logger(__name__)

def test_kimi_k25_integration():
    """Test Kimi K2.5 integration"""
    
    print("=" * 80)
    print("🚀 Testing Kimi K2.5 Integration with OpenClaw")
    print("=" * 80)
    print()
    
    # Check environment variables
    api_key = os.getenv("OPENCLAW_API_KEY")
    api_base = os.getenv("OPENCLAW_API_BASE")
    
    print(f"✅ API Base: {api_base}")
    print(f"✅ API Key: {api_key[:20]}..." if api_key else "❌ API Key not set")
    print()
    
    if not api_key or api_key == "sk-or-v1-YOUR_OPENROUTER_API_KEY_HERE":
        print("⚠️  WARNING: Please set your OpenRouter API key in .env file")
        print("   Get your key from: https://openrouter.ai/keys")
        print()
        print("   Update .env with:")
        print("   OPENCLAW_API_KEY=sk-or-v1-YOUR_ACTUAL_KEY")
        print()
        return False
    
    # Initialize generator
    print("🔧 Initializing Kimi K2.5 Generator...")
    try:
        generator = OpenClawGenerator()
        print("✅ Generator initialized successfully")
        print()
    except Exception as e:
        print(f"❌ Failed to initialize generator: {e}")
        return False
    
    # Test with sample biomedical question
    print("📝 Testing with sample biomedical question...")
    print()
    
    test_question = "What are the main mechanisms of action for mRNA vaccines?"
    
    test_passages = [
        {
            "title": "mRNA Vaccine Technology",
            "text": "mRNA vaccines work by delivering genetic instructions to cells, which then produce a harmless piece of the virus's spike protein. This triggers an immune response without causing disease.",
            "source_type": "pubmed",
            "doc_id": "test_001"
        },
        {
            "title": "Immune Response to mRNA Vaccines",
            "text": "The immune system recognizes the spike protein as foreign and produces antibodies and T-cells. This creates immunological memory for future protection.",
            "source_type": "pubmed",
            "doc_id": "test_002"
        }
    ]
    
    print(f"Question: {test_question}")
    print()
    print("Context passages:")
    for i, p in enumerate(test_passages, 1):
        print(f"  [{i}] {p['title']}")
    print()
    
    print("🤖 Generating answer with Kimi K2.5...")
    print("   (This may take 5-15 seconds for deep reasoning)")
    print()
    
    try:
        result = generator.generate_answer(test_question, test_passages)
        
        print("=" * 80)
        print("📊 RESULT")
        print("=" * 80)
        print()
        print(f"Answer: {result['answer']}")
        print()
        print(f"Confidence: {result['confidence']:.2f} ({result['confidence_level']})")
        print(f"Source: {result.get('title', 'N/A')}")
        print()
        
        if result.get('status') == 'error':
            print("❌ Error occurred during generation")
            return False
        else:
            print("✅ Kimi K2.5 integration working successfully!")
            return True
            
    except Exception as e:
        print(f"❌ Error during answer generation: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    success = test_kimi_k25_integration()
    
    print()
    print("=" * 80)
    if success:
        print("🎉 All tests passed! Kimi K2.5 is ready to use.")
        print()
        print("Next steps:")
        print("  1. Start your backend: uvicorn src.api.app:app --reload")
        print("  2. Test Q&A endpoint: POST to /api/v1/qa")
        print("  3. Deploy to Hugging Face (see KIMI_K2.5_SETUP.md)")
    else:
        print("❌ Tests failed. Please check the errors above.")
        print()
        print("Troubleshooting:")
        print("  1. Verify your OpenRouter API key in .env")
        print("  2. Check you have credits in your OpenRouter account")
        print("  3. See KIMI_K2.5_SETUP.md for detailed setup instructions")
    print("=" * 80)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
