
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

def run_headed_test():
    print("STARTING: Headed Filter Test on Live Site...")
    
    # Configure Chrome options - HEADED MODE
    chrome_options = Options()
    # chrome_options.add_argument("--headless") # Commented out for headed mode
    chrome_options.add_argument("--window-size=1280,800")
    chrome_options.add_experimental_option("detach", True) # Keep browser open after script

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        wait = WebDriverWait(driver, 20)
    except Exception as e:
        print(f"ERROR: Failed to initialize WebDriver: {e}")
        return

    try:
        # 1. Load the Application
        url = "https://biomed-scholar.web.app"
        print(f"URL: {url}")
        driver.get(url)
        time.sleep(4) # Internal waiting time
        
        # 2. Search
        print("SEARCHING: 'diabetes'...")
        search_input = wait.until(EC.presence_of_element_located((By.ID, "header-search-input")))
        search_input.clear()
        search_input.send_keys("diabetes")
        search_input.send_keys(Keys.RETURN)
        
        print("WAITING: loading results...")
        time.sleep(5) # Internal waiting time
        
        # 3. Test Year Filter
        print("CLICKING: '2025' filter...")
        year_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".quick-filter-chip[data-value='2025']")))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", year_btn)
        time.sleep(1)
        year_btn.click()
        
        print("WAITING: year filter update...")
        time.sleep(5) # Internal waiting time
        
        # 4. Test Source Filter
        print("CLICKING: 'PubMed' filter...")
        pubmed_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".quick-filter-chip[data-value='pubmed']")))
        pubmed_btn.click()
        
        print("WAITING: source filter update...")
        time.sleep(5) # Internal waiting time

        # 5. Test Time Horizon
        print("CLICKING: 'Last 3Y' filter...")
        horizon_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".quick-filter-chip[data-value='3y']")))
        horizon_btn.click()
        
        print("WAITING: final verification wait...")
        time.sleep(5) # Internal waiting time
        
        print("SUCCESS: Headed test sequence complete!")
        
    except Exception as e:
        print(f"FAILED: {e}")
    finally:
        print("FINISHED: Test finished. Browser remains open via detach option.")

if __name__ == "__main__":
    run_headed_test()
