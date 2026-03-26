import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def run_test():
    url = "https://biomed-scholar.web.app"
    print(f"--- STARTING SELENIUM TEST FOR {url} ---")
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        wait = WebDriverWait(driver, 20)
        
        driver.get(url)
        time.sleep(8) # Robust wait for initial assets
        
        results = []
        
        def check_modal(trigger_selector, modal_id, name):
            try:
                print(f"Testing {name}...")
                # Ensure header menu is open if needed
                if "menu-item" in trigger_selector:
                    trigger = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".menu-trigger")))
                    driver.execute_script("arguments[0].click();", trigger)
                    time.sleep(1)
                
                # Use JS click to bypass any overlays
                btn = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, trigger_selector)))
                driver.execute_script("arguments[0].click();", btn)
                
                time.sleep(3) # Wait for animation
                
                modal = driver.find_element(By.ID, modal_id)
                is_open = "open" in modal.get_attribute("class") or "active" in modal.get_attribute("class")
                
                if is_open:
                    print(f"  [PASS] {name} modal is visible.")
                    results.append(f"PASS: {name} modal opened.")
                    # Close it
                    close_btn = modal.find_element(By.CSS_SELECTOR, ".modal-close")
                    driver.execute_script("arguments[0].click();", close_btn)
                    time.sleep(1)
                else:
                    print(f"  [FAIL] {name} modal class list: {modal.get_attribute('class')}")
                    results.append(f"FAIL: {name} modal did not display 'open' class.")
            except Exception as e:
                print(f"  [ERROR] {name}: {str(e)}")
                results.append(f"ERROR: {name} - {str(e)[:100]}")

        # Test Cases
        check_modal("button.menu-item[onclick*='showKeyboardShortcuts']", "shortcuts-modal", "Header Shortcuts")
        check_modal("button.menu-item[onclick*='openScheduledActionsModal']", "scheduler-modal", "Header Scheduler")
        check_modal("button.menu-item[onclick*='showHelpModal']", "help-modal", "Header Help Guide")
        
        # Taskbar Test
        check_modal(".quick-taskbar button[title='Keyboard Shortcuts']", "shortcuts-modal", "Taskbar Shortcuts")
        check_modal(".quick-taskbar button[title='Scheduled Actions']", "scheduler-modal", "Taskbar Scheduler")
        check_modal(".quick-taskbar button[title='Help Guide']", "help-modal", "Taskbar Help Guide")
        
        print("\n--- FINAL TEST RESULTS ---")
        for r in results:
            print(r)
            
        driver.quit()
        
    except Exception as top_e:
        print(f"CRITICAL ERROR: {str(top_e)}")

if __name__ == "__main__":
    run_test()
