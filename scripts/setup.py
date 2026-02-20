"""Setup script to initialize the project."""

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent


def run_command(cmd: str, description: str):
    """Run a shell command and print status."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"{'='*60}")
    
    result = subprocess.run(cmd, shell=True, cwd=PROJECT_ROOT)
    
    if result.returncode != 0:
        print(f"❌ Failed: {description}")
        sys.exit(1)
    else:
        print(f"✅ Success: {description}")


def main():
    """Run setup steps."""
    print("🚀 Setting up Biomedical Search Engine Project")
    
    # Create .env file if it doesn't exist
    env_file = PROJECT_ROOT / ".env"
    env_example = PROJECT_ROOT / ".env.example"
    
    if not env_file.exists() and env_example.exists():
        print("\n📝 Creating .env file from .env.example...")
        env_file.write_text(env_example.read_text())
        print("✅ .env file created. Please update with your credentials.")
    
    # Create necessary directories
    dirs = ["data/raw", "data/processed", "models", "logs"]
    for dir_path in dirs:
        (PROJECT_ROOT / dir_path).mkdir(parents=True, exist_ok=True)
    print(f"✅ Created directories: {', '.join(dirs)}")
    
    # Download spaCy model
    print("\n📦 Downloading spaCy language model...")
    try:
        run_command(
            "python -m spacy download en_core_web_sm",
            "Download spaCy English model"
        )
    except:
        print("⚠️ Could not download spaCy model. You may need to install it manually.")
    
    print("\n" + "="*60)
    print("✨ Setup complete!")
    print("="*60)
    print("\nNext steps:")
    print("1. Update .env file with your API keys and credentials")
    print("2. Start Docker services: cd docker && docker-compose up -d")
    print("3. Run data pipeline to ingest data")
    print("4. Start the API: python -m uvicorn src.api.main:app --reload")


if __name__ == "__main__":
    main()
