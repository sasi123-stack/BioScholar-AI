import time
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def test_modals(url):
    print(f"Starting test for: {url}")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    wait = WebDriverWait(driver, 15)

    report = []

    try:
        driver.get(url)
        time.sleep(5)  # Wait for initial load

        # 1. Test Shortcuts Modal from Header
        print("Testing Shortcuts Modal from Header...")
        menu_trigger = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".menu-trigger")))
        menu_trigger.click()
        time.sleep(1)

        shortcuts_item = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Shortcuts']/..")))
        shortcuts_item.click()
        time.sleep(2)

        modal = driver.find_element(By.ID, "shortcuts-modal")
        if "open" in modal.get_attribute("class") or "active" in modal.get_attribute("class"):
            report.append(f"SUCCESS: Shortcuts modal opened from header.")
        else:
            report.append(f"FAILURE: Shortcuts modal did not open from header.")

        # Close Modal
        close_btn = modal.find_element(By.CSS_SELECTOR, ".modal-close")
        close_btn.click()
        time.sleep(1)

        # 2. Test Scheduled Actions Modal from Header
        print("Testing Scheduled Actions Modal from Header...")
        menu_trigger.click()
        time.sleep(1)
        scheduler_item = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Scheduled Actions']/..")))
        scheduler_item.click()
        time.sleep(2)

        modal = driver.find_element(By.ID, "scheduler-modal")
        if "open" in modal.get_attribute("class") or "active" in modal.get_attribute("class"):
            report.append(f"SUCCESS: Scheduled Actions modal opened from header.")
        else:
            report.append(f"FAILURE: Scheduled Actions modal did not open from header.")

        # Close Modal
        close_btn = modal.find_element(By.CSS_SELECTOR, ".modal-close")
        close_btn.click()
        time.sleep(1)

        # 3. Test Help Guide Modal from Header
        print("Testing Help Guide Modal from Header...")
        menu_trigger.click()
        time.sleep(1)
        help_item = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Help Guide']/..")))
        help_item.click()
        time.sleep(2)

        modal = driver.find_element(By.ID, "help-modal")
        if "open" in modal.get_attribute("class") or "active" in modal.get_attribute("class"):
            report.append(f"SUCCESS: Help Guide modal opened from header.")
        else:
            report.append(f"FAILURE: Help Guide modal did not open from header.")

        # Close Modal
        close_btn = modal.find_element(By.CSS_SELECTOR, ".modal-close")
        close_btn.click()
        time.sleep(1)

        # 4. Test Quick Access Taskbar (Shortcuts)
        print("Testing Shortcuts from Taskbar...")
        taskbar_shortcuts = driver.find_element(By.CSS_SELECTOR, ".quick-taskbar button[title='Keyboard Shortcuts']")
        taskbar_shortcuts.click()
        time.sleep(2)
        modal = driver.find_element(By.ID, "shortcuts-modal")
        if "open" in modal.get_attribute("class"):
            report.append(f"SUCCESS: Shortcuts modal opened from taskbar.")
        else:
            report.append(f"FAILURE: Shortcuts modal did not open from taskbar.")
        
        close_btn = modal.find_element(By.CSS_SELECTOR, ".modal-close")
        close_btn.click()
        time.sleep(1)

    except Exception as e:
        report.append(f"ERROR during testing: {str(e)}")
    finally:
        driver.quit()

    return report

if __name__ == "__main__":
    firebase_url = "https://biomed-scholar.web.app"
    results = test_modals(firebase_url)
    print("\n--- TEST REPORT ---")
    for res in results:
        print(res)
