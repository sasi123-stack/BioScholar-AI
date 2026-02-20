"""
Test script to verify OpenClaw AI Agent on Hugging Face is responding
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time

# Configuration
AGENT_URL = "https://sasidhara123-biosense-ai-agent.hf.space/?token=admin-token-123"
TEST_MESSAGE = "hello"
WAIT_TIMEOUT = 30  # seconds

def test_openclaw_agent():
    """Test if the OpenClaw agent responds to a simple message"""
    
    print(f"🚀 Testing OpenClaw Agent at: {AGENT_URL}")
    print(f"📝 Test message: '{TEST_MESSAGE}'")
    print("-" * 60)
    
    # Setup Chrome driver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in background
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=options)
    
    try:
        # Navigate to the agent
        print("1️⃣  Navigating to agent URL...")
        driver.get(AGENT_URL)
        time.sleep(5)  # Wait for page to load
        
        # Take screenshot of initial page
        driver.save_screenshot("openclaw_initial.png")
        print("   ✅ Page loaded (screenshot: openclaw_initial.png)")
        
        # Check for common error messages
        page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
        
        if "connection refused" in page_text:
            print("   ❌ ERROR: Connection refused - agent may not be running")
            return False
        
        if "pairing required" in page_text:
            print("   ⚠️  WARNING: Pairing required message detected")
        
        if "unauthorized" in page_text:
            print("   ⚠️  WARNING: Unauthorized message detected")
        
        # Look for chat input (common selectors)
        print("\n2️⃣  Looking for chat input...")
        input_selectors = [
            "textarea",
            "input[type='text']",
            "[contenteditable='true']",
            "#chat-input",
            ".chat-input",
            "[placeholder*='message' i]",
            "[placeholder*='type' i]",
        ]
        
        chat_input = None
        for selector in input_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    chat_input = elements[0]
                    print(f"   ✅ Found input using selector: {selector}")
                    break
            except:
                continue
        
        if not chat_input:
            print("   ❌ ERROR: Could not find chat input field")
            print("   Available elements:")
            print(f"   - Textareas: {len(driver.find_elements(By.TAG_NAME, 'textarea'))}")
            print(f"   - Text inputs: {len(driver.find_elements(By.CSS_SELECTOR, 'input[type=text]'))}")
            driver.save_screenshot("openclaw_no_input.png")
            return False
        
        # Send test message
        print(f"\n3️⃣  Sending message: '{TEST_MESSAGE}'")
        chat_input.clear()
        chat_input.send_keys(TEST_MESSAGE)
        time.sleep(1)
        
        # Try to find and click send button
        send_button = None
        send_selectors = [
            "button[type='submit']",
            "button:contains('Send')",
            ".send-button",
            "#send-button",
        ]
        
        for selector in send_selectors:
            try:
                buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                if buttons:
                    send_button = buttons[0]
                    break
            except:
                continue
        
        if send_button:
            send_button.click()
            print("   ✅ Clicked send button")
        else:
            # Try pressing Enter
            chat_input.send_keys(Keys.RETURN)
            print("   ✅ Pressed Enter to send")
        
        # Wait for response
        print(f"\n4️⃣  Waiting for AI response (up to {WAIT_TIMEOUT}s)...")
        time.sleep(10)  # Give it time to respond
        
        # Take screenshot after sending
        driver.save_screenshot("openclaw_after_send.png")
        print("   ✅ Screenshot saved (openclaw_after_send.png)")
        
        # Check if there's a response
        page_text_after = driver.find_element(By.TAG_NAME, "body").text
        
        # Look for signs of a response
        if len(page_text_after) > len(page_text) + 10:
            print("\n✅ SUCCESS: Page content changed - AI likely responded!")
            print(f"   Page text length before: {len(page_text)}")
            print(f"   Page text length after: {len(page_text_after)}")
            
            # Try to extract the response
            print("\n📝 Recent page content:")
            print("-" * 60)
            print(page_text_after[-500:])  # Last 500 characters
            print("-" * 60)
            return True
        else:
            print("\n⚠️  WARNING: No significant change in page content")
            print("   This could mean:")
            print("   - The AI hasn't responded yet (try waiting longer)")
            print("   - The API key is missing")
            print("   - There's an error in the agent")
            return False
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        driver.save_screenshot("openclaw_error.png")
        return False
    
    finally:
        driver.quit()
        print("\n🏁 Test completed")

if __name__ == "__main__":
    success = test_openclaw_agent()
    exit(0 if success else 1)
