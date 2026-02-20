import pytest
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Configuration
BASE_URL = "https://biomed-scholar.web.app"

@pytest.fixture(scope="module")
def driver():
    """Pytest fixture for Selenium WebDriver."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Headless mode for testing
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

class TestArticlesTab:
    """Test suite for the Articles tab UI."""

    def test_page_load(self, driver):
        """Verify the application loads and the Articles tab is active by default."""
        driver.get(BASE_URL)
        assert "BioMedScholar AI" in driver.title
        
        # Check if Articles tab is active
        articles_tab_btn = driver.find_element(By.CSS_SELECTOR, "button.nav-tab[data-tab='articles']")
        assert "active" in articles_tab_btn.get_attribute("class")
        
        articles_content = driver.find_element(By.ID, "articles-tab")
        assert "active" in articles_content.get_attribute("class")

    def test_search_and_results(self, driver, wait):
        """Verify that searching displays results in the Articles tab."""
        driver.get(BASE_URL)
        
        search_input = wait.until(EC.presence_of_element_located((By.ID, "header-search-input")))
        search_input.clear()
        search_input.send_keys("diabetes")
        search_input.send_keys(Keys.RETURN)
        
        # Wait for results to appear
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "result-card")))
        results = driver.find_elements(By.CLASS_NAME, "result-card")
        
        assert len(results) > 0, "No results found for search query"
        
        # Verify results are in the articles tab
        results_container = driver.find_element(By.ID, "search-results")
        assert results_container.is_displayed()

    def test_article_modal(self, driver, wait):
        """Verify that clicking an article opens the detail modal."""
        # Ensure we have results first
        search_input = wait.until(EC.presence_of_element_located((By.ID, "header-search-input")))
        search_input.clear()
        search_input.send_keys("cancer")
        search_input.send_keys(Keys.RETURN)
        
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "result-card")))
        
        # Click the first result title
        first_title = driver.find_element(By.CLASS_NAME, "result-title")
        first_title.click()
        
        # Wait for modal
        modal = wait.until(EC.presence_of_element_located((By.ID, "article-detail-modal")))
        # The modal might be visible by class "open" or just by CSS visibility
        assert "open" in modal.get_attribute("class") or modal.is_displayed()
        
        # Close modal
        close_btn = driver.find_element(By.CLASS_NAME, "article-modal-close")
        close_btn.click()
        wait.until(EC.invisibility_of_element_located((By.ID, "article-detail-modal")))

    def test_save_all_button(self, driver, wait):
        """Verify the 'Save All' button functionality."""
        driver.get(BASE_URL)
        
        # Perform search
        search_input = wait.until(EC.presence_of_element_located((By.ID, "header-search-input")))
        search_input.clear()
        search_input.send_keys("heart disease")
        search_input.send_keys(Keys.RETURN)
        
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "result-card")))
        
        # Click Save All
        save_all_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".results-actions-header button.results-save-all")))
        driver.execute_script("arguments[0].click();", save_all_btn)
        
        # Verify bookmarks are active
        time.sleep(2)  # Wait for state update
        active_bookmarks = driver.find_elements(By.CSS_SELECTOR, ".bookmark-btn.active")
        assert len(active_bookmarks) > 0, "No articles were bookmarked after 'Save All'"

    def test_tab_switching(self, driver, wait):
        """Verify switching between Articles and AI Chat tabs."""
        driver.get(BASE_URL)
        
        # Switch to AI Chat
        qa_tab_btn = driver.find_element(By.CSS_SELECTOR, "button.nav-tab[data-tab='qa']")
        qa_tab_btn.click()
        
        assert "active" in qa_tab_btn.get_attribute("class")
        qa_content = driver.find_element(By.ID, "qa-tab")
        assert "active" in qa_content.get_attribute("class")
        
        # Switch back to Articles
        articles_tab_btn = driver.find_element(By.CSS_SELECTOR, "button.nav-tab[data-tab='articles']")
        articles_tab_btn.click()
        
        assert "active" in articles_tab_btn.get_attribute("class")
        articles_content = driver.find_element(By.ID, "articles-tab")
        assert "active" in articles_content.get_attribute("class")
