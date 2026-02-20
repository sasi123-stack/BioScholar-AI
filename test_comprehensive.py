import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def run_comprehensive_tests():
    print("Starting Comprehensive BioMed Scholar Selenium Tests...")
    
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    wait = WebDriverWait(driver, 20)

    try:
        # 1. Load Application
        print("1. Loading application...")
        driver.get("https://biomed-scholar.web.app")
        wait.until(EC.title_contains("BioMed Scholar"))
        print("[SUCCESS] Application loaded")

        # 2. Test Navigation Tabs
        print("2. Testing navigation tabs...")
        tabs = {
            "articles": driver.find_element(By.CSS_SELECTOR, ".nav-tab[data-tab='articles']"),
            "qa": driver.find_element(By.CSS_SELECTOR, ".nav-tab[data-tab='qa']"),
            "trends": driver.find_element(By.CSS_SELECTOR, ".nav-tab[data-tab='trends']")
        }

        # Check QA Tab
        tabs["qa"].click()
        wait.until(EC.visibility_of_element_located((By.ID, "qa-tab")))
        print("[SUCCESS] Switched to AI Chat tab")

        # Check Trends Tab
        tabs["trends"].click()
        wait.until(EC.visibility_of_element_located((By.ID, "trends-tab")))
        print("[SUCCESS] Switched to Trends tab")

        # Back to Articles
        tabs["articles"].click()
        wait.until(EC.visibility_of_element_located((By.ID, "articles-tab")))
        print("[SUCCESS] Switched back to Articles tab")

        # 3. Test Search & Filters
        print("3. Testing search and sidebar filters...")
        search_input = driver.find_element(By.ID, "header-search-input")
        search_input.send_keys("diabetes")
        search_input.send_keys(Keys.RETURN)
        
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "result-card")))
        print("[SUCCESS] Search results displayed")

        # Test Sidebar Source Filter (PubMed)
        pubmed_chip = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".filter-chip[data-filter='pubmed']")))
        driver.execute_script("arguments[0].click();", pubmed_chip)
        time.sleep(1) # Allow for re-render
        print("[SUCCESS] Applied PubMed source filter")

        # 4. Test Modals
        print("4. Testing ancillary modals...")
        
        # Help Modal
        help_btn = driver.find_element(By.CLASS_NAME, "help-btn")
        driver.execute_script("arguments[0].click();", help_btn)
        wait.until(EC.visibility_of_element_located((By.ID, "help-modal")))
        print("[SUCCESS] Help modal opened")
        close_help = driver.find_element(By.CSS_SELECTOR, "#help-modal .modal-close")
        driver.execute_script("arguments[0].click();", close_help)
        wait.until(EC.invisibility_of_element_located((By.ID, "help-modal")))

        # Advanced Search Modal
        adv_btn = driver.find_element(By.CSS_SELECTOR, "[onclick='openAdvancedSearch()']")
        driver.execute_script("arguments[0].click();", adv_btn)
        wait.until(EC.visibility_of_element_located((By.ID, "advanced-search-modal")))
        print("[SUCCESS] Advanced search modal opened")
        close_adv = driver.find_element(By.CSS_SELECTOR, "#advanced-search-modal .modal-close")
        driver.execute_script("arguments[0].click();", close_adv)
        wait.until(EC.invisibility_of_element_located((By.ID, "advanced-search-modal")))

        # 5. Test Reading List & Save All
        print("5. Testing Reading List and Save All...")
        
        # Click Save All (using JS click to avoid header interception)
        save_all_btn = driver.find_element(By.CSS_SELECTOR, ".results-actions-header button.results-save-all")
        driver.execute_script("arguments[0].click();", save_all_btn)
        time.sleep(1)
        
        # Open Reading List Panel
        driver.find_element(By.CLASS_NAME, "reading-list-btn").click()
        wait.until(EC.visibility_of_element_located((By.ID, "reading-list-panel")))
        
        saved_items = driver.find_elements(By.CLASS_NAME, "reading-list-item")
        print(f"[SUCCESS] Reading list contains {len(saved_items)} items")
        assert len(saved_items) > 0

        # Close Reading List
        driver.find_element(By.CLASS_NAME, "close-panel-btn").click()
        
        # 6. Test Article Detail Deep Interaction
        print("6. Testing article detail modal and tabs...")
        first_title = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "result-title")))
        driver.execute_script("arguments[0].click();", first_title)
        wait.until(EC.visibility_of_element_located((By.ID, "article-detail-modal")))
        
        # Test tab switching inside modal
        fulltext_tab = driver.find_element(By.CSS_SELECTOR, "[onclick=\"switchModalTab('fulltext')\"]")
        driver.execute_script("arguments[0].click();", fulltext_tab)
        wait.until(EC.visibility_of_element_located((By.ID, "modal-tab-fulltext")))
        print("[SUCCESS] Switched to Full Text tab in modal")

        close_modal = driver.find_element(By.CLASS_NAME, "article-modal-close")
        driver.execute_script("arguments[0].click();", close_modal)

        # 7. Test AI Chat Message
        print("7. Testing AI Chat message submission...")
        tabs["qa"].click()
        chat_input = wait.until(EC.presence_of_element_located((By.ID, "chat-input")))
        chat_input.send_keys("What is insulin resistance?")
        driver.find_element(By.ID, "chat-send-btn").click()
        
        # Wait for a response (any message after the user message)
        time.sleep(3)
        messages = driver.find_elements(By.CLASS_NAME, "chat-message")
        print(f"[SUCCESS] Chat messages present: {len(messages)}")

        print("\n[COMPLETE] All comprehensive tests passed successfully!")

    except Exception as e:
        print(f"\n[FAILURE] Test failed: {e}")
        driver.save_screenshot("comprehensive_test_failure.png")
    finally:
        print("Closing browser...")
        driver.quit()

if __name__ == "__main__":
    run_comprehensive_tests()
