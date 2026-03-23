import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def test_live_and_tabs():
    print("Initializing Maverick UI Selenium Test...")
    
    chrome_options = Options()
    chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    wait = WebDriverWait(driver, 30)

    try:
        # 1. Load Application
        print("1. Loading https://biomed-scholar.web.app ...")
        driver.get("https://biomed-scholar.web.app")
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "nav-tabs")))
        print(f"   [OK] Page title: {driver.title}")

        # DEBUG: List all tabs found
        print("DEBUG: Listing all nav tabs...")
        tabs = driver.find_elements(By.CLASS_NAME, "nav-tab")
        for i, tab in enumerate(tabs):
            print(f"   Tab {i}: Text='{tab.text}', Tag='{tab.tag_name}', DataTab='{tab.get_attribute('data-tab')}'")

        # 2. Test Tab Switching (Maverick AI Bot)
        print("2. Testing 'Maverick AI Bot' Tab...")
        # Search by data-tab attribute directly
        chat_tab_btn = driver.find_element(By.CSS_SELECTOR, "button[data-tab='chat']")
        driver.execute_script("arguments[0].click();", chat_tab_btn)
        
        wait.until(EC.visibility_of_element_located((By.ID, "chat-tab")))
        print("   [OK] Chat tab active.")

        # 3. Test Gemini Live
        print("3. Testing Gemini Live HUD...")
        live_btn = wait.until(EC.presence_of_element_located((By.ID, "gemini-live-toggle")))
        driver.execute_script("arguments[0].click();", live_btn)
        
        wait.until(EC.visibility_of_element_located((By.ID, "gemini-live-visualizer")))
        print("   [OK] HUD active.")

        # 4. End Session
        end_btn = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "live-end-btn")))
        driver.execute_script("arguments[0].click();", end_btn)
        wait.until(EC.invisibility_of_element_located((By.ID, "gemini-live-visualizer")))
        print("   [OK] Session ended.")

        print("\nSUCCESS: UI verified!")

    except Exception as e:
        print(f"\nFAILURE: {e}")
        driver.save_screenshot("selenium_error_v3.png")
    finally:
        driver.quit()
        print("Browser session closed.")

if __name__ == "__main__":
    test_live_and_tabs()
