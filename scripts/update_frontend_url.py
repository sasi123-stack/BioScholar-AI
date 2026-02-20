"""Helper script to create a production-ready frontend configuration."""

import sys
from pathlib import Path

def create_config_file(api_url: str):
    """Create a config file for the frontend."""
    
    # Read current app.js
    frontend_dir = Path(__file__).parent.parent / "frontend"
    app_js = frontend_dir / "app.js"
    
    # Create backup
    backup = frontend_dir / "app.js.backup"
    if not backup.exists():
        with open(app_js, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(backup, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Backup created: {backup}")
    
    # Read current content
    with open(app_js, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace API_BASE_URL
    if "const API_BASE_URL = 'http://localhost:8000/api/v1';" in content:
        new_content = content.replace(
            "const API_BASE_URL = 'http://localhost:8000/api/v1';",
            f"const API_BASE_URL = '{api_url}/api/v1';"
        )
        
        with open(app_js, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ Updated API_BASE_URL to: {api_url}/api/v1")
        print(f"\n📝 To revert: copy {backup} back to app.js")
    else:
        print("⚠️  Could not find API_BASE_URL line. Update manually.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python update_frontend_url.py <ngrok-api-url>")
        print("Example: python update_frontend_url.py https://abc123.ngrok.io")
        sys.exit(1)
    
    api_url = sys.argv[1].rstrip('/')
    create_config_file(api_url)
    print("\n🚀 Frontend ready! Share the ngrok frontend URL with your friends.")
