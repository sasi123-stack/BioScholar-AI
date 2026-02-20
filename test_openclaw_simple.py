"""
Simple test for OpenClaw AI Agent - auto-installs Chrome driver
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time

# Configuration
AGENT_URL = "https://sasidhara123-biosense-ai-agent.hf.space/?token=admin-token-123"

print("🚀 Testing OpenClaw Agent")
print(f"📍 URL: {AGENT_URL}")
print("-" * 60)

# Setup Chrome with auto-install
print("\n1️⃣  Setting up Chrome WebDriver...")
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

try:
    # Navigate
    print("2️⃣  Navigating to agent...")
    driver.get(AGENT_URL)
    time.sleep(5)
    
    # Save screenshot
    driver.save_screenshot("openclaw_test.png")
    print("   ✅ Screenshot saved: openclaw_test.png")
    
    # Get page text
    page_text = driver.find_element(By.TAG_NAME, "body").text
    
    # Check status
    print("\n3️⃣  Checking page status...")
    if "connection refused" in page_text.lower():
        print("   ❌ Connection refused - agent not running")
    elif "pairing required" in page_text.lower():
        print("   ⚠️  Pairing required")
    elif "unauthorized" in page_text.lower():
        print("   ⚠️  Unauthorized")
    else:
        print("   ✅ Page loaded successfully")
    
    # Show page content
    print("\n📄 Page content (first 500 chars):")
    print("-" * 60)
    print(page_text[:500])
    print("-" * 60)
    
    # Try to find input
    print("\n4️⃣  Looking for chat input...")
    textareas = driver.find_elements(By.TAG_NAME, "textarea")
    text_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
    
    print(f"   Found {len(textareas)} textarea(s)")
    print(f"   Found {len(text_inputs)} text input(s)")
    
    if textareas or text_inputs:
        chat_input = textareas[0] if textareas else text_inputs[0]
        
        print("\n5️⃣  Sending 'hello' message...")
        chat_input.send_keys("hello")
        chat_input.send_keys(Keys.RETURN)
        
        print("   ⏳ Waiting 10 seconds for response...")
        time.sleep(10)
        
        # Check for response
        new_text = driver.find_element(By.TAG_NAME, "body").text
        driver.save_screenshot("openclaw_after_send.png")
        
        if len(new_text) > len(page_text) + 10:
            print("   ✅ SUCCESS - AI responded!")
            print(f"\n📝 Response (last 300 chars):")
            print("-" * 60)
            print(new_text[-300:])
            print("-" * 60)
        else:
            print("   ⚠️  No response detected")
            print("   💡 Check if OPENROUTER_API_KEY is set in HF Secrets")
    else:
        print("   ❌ No input field found")
        print("   💡 The chat interface may not have loaded yet")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    driver.save_screenshot("openclaw_error.png")

finally:
    driver.quit()
    print("\n🏁 Test completed")
