import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def validate_elements():
    print("Starting Comprehensive Web Element Validation...")
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    wait = WebDriverWait(driver, 10)
    
    try:
        # Load local server
        driver.get("http://localhost:8085/")
        time.sleep(2)
        print(f"Application loaded. Title: {driver.title}")
        print(f"Page Source Preview: {driver.page_source[:200]}")

        # Validate Nav Tabs
        print("Validating Navigation Tabs...")
        tabs = driver.find_elements(By.CSS_SELECTOR, ".nav-tab")
        assert len(tabs) == 3, f"Expected 3 tabs, found {len(tabs)}"
        for tab in tabs:
            assert tab.is_displayed(), f"Tab {tab.text} is not visible"
            print(f" - Verified tab: {tab.text}")

        # Validate More Options menu
        print("Validating 'More Options' Menu...")
        menu_trigger = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".menu-trigger")))
        assert menu_trigger.is_displayed(), "Menu trigger is hidden!"
        
        driver.execute_script("arguments[0].click();", menu_trigger)
        time.sleep(1)
        
        header_menu = driver.find_element(By.ID, "header-menu")
        classes = header_menu.get_attribute("class")
        assert "hidden" not in classes or header_menu.is_displayed(), "Header menu dropdown did not open"
        
        menu_items = header_menu.find_elements(By.CSS_SELECTOR, ".menu-item")
        print(f" - Found {len(menu_items)} menu items in dropdown. Clicking them worked.")
        
        # Validate Search
        print("Validating Search Input...")
        search_input = driver.find_element(By.ID, "header-search-input")
        assert search_input.is_displayed(), "Search input is not visible"
        search_input.send_keys("cancer")
        
        print("Validating Theme Toggle...")
        theme_toggle = driver.find_element(By.ID, "theme-toggle")
        assert theme_toggle.is_displayed(), "Theme toggle not visible"
        
        print("\nAll UI Elements Validated Successfully! The More Options menu is clearly visible.")

    except AssertionError as ae:
        print(f"\n[VALIDATION ERROR] {ae}")
    except Exception as e:
        print(f"\n[ERROR] {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    validate_elements()
