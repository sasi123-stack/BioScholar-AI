import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Configuration
BASE_URL = "https://biomed-scholar.web.app"
EXPECTED_WA_LINK = "https://wa.me/918500419303"

@pytest.fixture(scope="module")
def driver():
    """Pytest fixture for Selenium WebDriver."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Headless mode for CI
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    yield driver
    driver.quit()

@pytest.fixture
def wait(driver):
    """Pytest fixture for WebDriverWait."""
    return WebDriverWait(driver, 20)

def test_whatsapp_feedback_link(driver, wait):
    """Verify the WhatsApp feedback button exists and has the correct link."""
    driver.get(BASE_URL)
    
    # Wait for footer to be visible
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "footer-feedback-btn")))
    
    feedback_btn = driver.find_element(By.CLASS_NAME, "footer-feedback-btn")
    
    # Verify the href attribute
    href = feedback_btn.get_attribute("href")
    assert href == EXPECTED_WA_LINK, f"Expected WhatsApp link {EXPECTED_WA_LINK}, but got {href}"
    
    # Verify target="_blank" to ensure it opens in a new tab
    target = feedback_btn.get_attribute("target")
    assert target == "_blank", "Feedback link should open in a new tab"

def test_whatsapp_feedback_click(driver, wait):
    """Verify that clicking the WhatsApp feedback button opens a new window/tab."""
    driver.get(BASE_URL)
    
    # Get current window handle
    original_window = driver.current_window_handle
    
    # Find and click the feedback button
    feedback_btn = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "footer-feedback-btn")))
    feedback_btn.click()
    
    # Wait for the new window/tab
    wait.until(EC.number_of_windows_to_be(2))
    
    # Switch to the new window
    for window_handle in driver.window_handles:
        if window_handle != original_window:
            driver.switch_to.window(window_handle)
            break
            
    # Check the URL of the new tab
    current_url = driver.current_url
    assert "wa.me" in current_url or "whatsapp.com" in current_url
    
    # Close new tab and switch back
    driver.close()
    driver.switch_to.window(original_window)
