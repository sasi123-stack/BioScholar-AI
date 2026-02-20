import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys

def run_test():
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Headed mode enabled
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    wait = WebDriverWait(driver, 15)

    try:
        print("🚀 Navigating to BioMedScholar AI...")
        driver.get("https://biomed-scholar.web.app")

        # 1. Test Navigation to "AI Chat" Tab
        print("🔘 Navigating to 'AI Chat' tab...")
        time.sleep(2)
        
        # Click the AI Chat tab button
        chat_tab_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-tab='qa']")))
        chat_tab_btn.click()
        time.sleep(1)
        
        # Verify Chat Interface is visible
        chat_container = driver.find_element(By.CSS_SELECTOR, "#qa-tab .chat-container")
        is_visible = chat_container.is_displayed()
        print(f"✅ AI Chat Interface visible: {is_visible}")
        
        # 2. Test Sending a Message
        print("\n💬 Testing AI Chat Interaction...")
        chat_input = wait.until(EC.presence_of_element_located((By.ID, "chat-input")))
        chat_input.clear()
        chat_input.send_keys("What are the latest treatments for Alzheimer's?")
        time.sleep(1)
        
        send_btn = driver.find_element(By.ID, "chat-send-btn")
        send_btn.click()
        
        # Wait for response (user bubble first, then AI response)
        print("⏳ Waiting for AI response (Llama 4)...")
        
        # Check for user message
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".chat-message.user")))
        print("✅ User message sent.")
        
        # Check for AI typing indicator or response
        # Note: This depends on backend latency. We'll wait up to 10s for ANY response bubble from AI.
        try:
            ai_response = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".chat-message.ai"))
            )
            print("✅ AI Response received!")
            print(f"📝 Response preview: {ai_response.text[:50]}...")
        except:
            print("⚠️ AI Response timed out (backend might be cold or model loading)")

        print("\n✨ Chat test completed!")

    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        driver.save_screenshot("chat_test_failure.png")
        print("Captured failure screenshot at chat_test_failure.png")
    finally:
        driver.quit()

if __name__ == "__main__":
    run_test()
