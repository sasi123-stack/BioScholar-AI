
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

def test_telegram_web_link():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # User agent to avoid some simple bot detections
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    output_dir = "tests/screenshots"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    try:
        url = "https://web.telegram.org/a/#8513211167"
        print(f"\nAttemping to load: {url}")
        driver.get(url)
        
        # Wait for potential loading
        time.sleep(10)
        
        screenshot_path = os.path.join(output_dir, "telegram_web_check.png")
        driver.save_screenshot(screenshot_path)
        print(f"Screenshot saved to: {screenshot_path}")
        
        # Check title or some element to see if it loaded telegram
        title = driver.title
        print(f"Page Title: {title}")
        
        # In headless mode without login, we expect a login page or loading screen
        assert "Telegram" in title or "Loading" in title
        
    finally:
        driver.quit()

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
