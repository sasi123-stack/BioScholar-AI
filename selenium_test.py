import time
import traceback
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys

def run_production_showcase():
    chrome_options = Options()
    # High resolution for video capture
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    wait = WebDriverWait(driver, 30)

    try:
        print("[STARTING] V1.6.5 PRODUCTION SHOWCASE...")
        driver.get("https://biomed-scholar.web.app")
        print(f"[STATUS] URL: {driver.current_url}")
        print(f"[STATUS] Title: {driver.title}")
        time.sleep(5) # Let initial animations settle

        # 1. DISMISS MODAL
        print("[STEP 1] Looking for Beta Modal Enter Button...")
        try:
            # Try to find by text first
            enter_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Got it! Explore v1.6.5')]")))
            print("[SUCCESS] Found Explore button by text.")
        except:
            print("[INFO] Could not find by text, trying CSS selector...")
            enter_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.modal-btn.primary")))
            print("[SUCCESS] Found Explore button by CSS.")

        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", enter_btn)
        time.sleep(1)
        enter_btn.click()
        print("[SUCCESS] Entered Platform.")
            
        time.sleep(3)

        # 2. TRENDS WALKTHROUGH
        print("[STEP 2] Navigating to Trends Tab...")
        trends_tab = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-tab='trends']")))
        trends_tab.click()
        time.sleep(2)

        # Click Refresh
        print("[STEP 3] Triggering Maverick AI Live Analysis...")
        refresh_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".refresh-trends-btn")))
        refresh_btn.click()
        time.sleep(6) 

        # 3. SEARCH JOURNEY
        print("[STEP 4] Executing Multi-Modal Search...")
        search_input = wait.until(EC.presence_of_element_located((By.ID, "header-search-input")))
        search_input.clear()
        search_input.send_keys("GLP-1 Weight Loss and Cardiometabolic Health")
        search_input.send_keys(Keys.RETURN)
        time.sleep(5)

        # 4. ARTICLE DETAIL
        print("[STEP 5] Opening Discovery Detail...")
        first_card = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".article-card")))
        first_card.click()
        time.sleep(3)
        
        # Scroll down in modal
        print("[STEP 6] Showcasing Gemini Nano: Local AI Summary...")
        try:
            modal_body = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".modal-body")))
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", modal_body)
        except:
            driver.execute_script("document.querySelector('.modal-body').scrollTop = 3000")
            
        time.sleep(8) # Hold for video
        
        # Close Article Modal
        print("[STEP 7] Closing modal...")
        close_btn = driver.find_element(By.CSS_SELECTOR, ".modal-close")
        close_btn.click()
        time.sleep(1)

        # 5. MAVERICK BOT
        print("[STEP 8] Engaging Maverick AI Intelligent Assistant...")
        chat_tab = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-tab='chat']")))
        chat_tab.click()
        time.sleep(2)

        chat_input = wait.until(EC.presence_of_element_located((By.ID, "chat-input")))
        chat_input.send_keys("What are the most promising alternatives to GLP-1 therapy for 2026?")
        chat_input.send_keys(Keys.RETURN)
        print("[STEP 9] Waiting for Intelligent Response...")
        time.sleep(12) # Hold for highlight

        # 6. FOOTER
        print("[STEP 10] Finalizing showcase...")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)

        print("[COMPLETE] SHOWCASE COMPLETE. v1.6.5 PREMIUM Production Build Verified.")

    except Exception as e:
        print("[FAILURE] Showcase interrupted!")
        print(f"Error: {str(e)}")
        # Save failure state
        screenshot_path = os.path.join(os.getcwd(), "showcase_failure.png")
        try:
            driver.save_screenshot(screenshot_path)
            print(f"[FAILURE] Captured screenshot at: {screenshot_path}")
        except:
            pass
        print(f"[FAILURE] Raw Details: {traceback.format_exc()}")
    finally:
        driver.quit()

if __name__ == "__main__":
    run_production_showcase()
