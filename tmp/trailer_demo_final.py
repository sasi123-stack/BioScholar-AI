from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Update with your ChromeDriver path
CHROME_DRIVER_PATH = r"C:\Users\sasid\Downloads\chromedriver-win64\chromedriver.exe"
URL = "https://biomed-scholar.web.app/"

def run_trailer_demo():
    print("--- STARTING TRAILER RECORDING RUN ---")
    service = Service(CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()
    
    try:
        driver.get(URL)
        wait = WebDriverWait(driver, 15)
        
        # 1. Search for a core topic
        print("ACTION: Searching for mRNA immunotherapy...")
        search_input = wait.until(EC.presence_of_element_located((By.ID, "search-input")))
        for char in "mRNA immunotherapy": 
            search_input.send_keys(char)
            time.sleep(0.05)
        
        driver.find_element(By.CSS_SELECTOR, ".search-btn").click()
        time.sleep(4) 
        
        # 2. Show the Maverick Insight box
        print("ACTION: Highlighting Maverick Insight Synthesis...")
        wait.until(EC.presence_of_element_located((By.ID, "maverick-insight-box")))
        time.sleep(5) 
        
        # 3. Switch to Chat Bot
        print("ACTION: Demonstrating Maverick AI Chat capabilities...")
        driver.find_element(By.CSS_SELECTOR, '[data-tab="chat"]').click()
        time.sleep(2)
        
        chat_input = driver.find_element(By.ID, "chat-input")
        chat_input.send_keys("What are the Phase III results for mRNA-4157?")
        driver.find_element(By.ID, "send-btn").click()
        time.sleep(8) 
        
        print("\n--- DEMO COMPLETE. STOP YOUR RECORDING NOW ---")
        time.sleep(5)
        
    finally:
        driver.quit()

if __name__ == "__main__":
    run_trailer_demo()
