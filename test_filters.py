
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

def run_filter_tests():
    print("Starting BioMed Scholar Filter Button Tests (Local)...")
    
    # Configure Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")

    # Initialize WebDriver
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        wait = WebDriverWait(driver, 20)
    except Exception as e:
        print(f"[FATAL] Failed to initialize WebDriver: {e}")
        return

    try:
        # 1. Load the Application
        print("1. Loading application (localhost:8081)...")
        driver.get("http://localhost:8081")
        # Allow time for initial load
        time.sleep(3)
        print(f"[INFO] Page loaded: {driver.title}")

        # 2. Perform Search to enable filters
        print("2. Performing search to enable filters...")
        try:
            # Wait for either input
            search_inputs = driver.find_elements(By.ID, "header-search-input")
            if not search_inputs or not search_inputs[0].is_displayed():
                 search_inputs = driver.find_elements(By.ID, "hero-search-input")
            
            if not search_inputs:
                raise Exception("No search input found")
                
            search_input = search_inputs[0]
            search_input.clear()
            search_input.send_keys("cancer") # Use a broad term likely to have 2025 results
            search_input.send_keys(Keys.RETURN)
        except Exception as e:
            print(f"[ERROR] Could not perform search: {e}")
            driver.save_screenshot("search_fail.png")
            raise

        # Wait for results
        print("Waiting for initial search results...")
        try:
            wait.until(EC.invisibility_of_element_located((By.ID, "skeleton-loader")))
            wait.until(EC.presence_of_element_located((By.ID, "search-results")))
            # Check we have results
            results = driver.find_elements(By.CLASS_NAME, "result-card")
            print(f"[SUCCESS] Initial search returned {len(results)} results.")
        except:
             print("[WARN] Search results not found immediately.")
        
        # Define buttons to test
        test_groups = {
            "PUBLICATION YEAR": ["2025"], # Focus on 2025 first as known working/problematic
            "TIME HORIZON": ["Last 3Y"],
            "EVIDENCE LEVEL": ["Meta-Analysis"]
        }

        # Verify buttons exist and are clickable
        for group_name, buttons in test_groups.items():
            print(f"\nTesting Group: {group_name}")
            for btn_text in buttons:
                print(f"  - Testing button: '{btn_text}' ...", end="", flush=True)
                try:
                    # Find button
                    # Simple text match for buttons
                    xpath = f"//button[contains(text(), '{btn_text}')]"
                    btn = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                    
                    # Scroll into view
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                    time.sleep(0.5) 
                    
                    # Click
                    driver.execute_script("arguments[0].click();", btn)
                    print(" [CLICKED] ", end="")
                    
                    # Wait for Skeleton Loader to appear (indicating search started)
                    # Note: It might be too fast to catch, so we wait for results to stabilize
                    
                    # Wait for results to reload
                    time.sleep(2) # Give time for fetch
                    
                    # Verify results are present
                    results = driver.find_elements(By.CLASS_NAME, "result-card")
                    print(f" - Results: {len(results)}")
                    
                    # Specific checks
                    if btn_text == "2025" and len(results) > 0:
                        # Check dates
                        texts = [r.text for r in results[:3]]
                        if any("2025" in t for t in texts):
                            print("    [PASS] Found 2025 in top results.")
                        else:
                            print(f"    [WARN] 2025 not found in top results: {texts}")

                except Exception as e:
                    print(f" [FAILED] - {e}")
                    driver.save_screenshot(f"fail_{btn_text}.png")

        print("\n[COMPLETE] Filter button testing finished.")

    except Exception as e:
        print(f"\n[FAILURE] Test suite failed: {e}")
        driver.save_screenshot("suite_failure.png")
    finally:
        print("Closing browser...")
        driver.quit()

if __name__ == "__main__":
    run_filter_tests()
