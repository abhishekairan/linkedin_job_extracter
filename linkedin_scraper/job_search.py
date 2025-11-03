"""
Job search module for LinkedIn.
Handles searching and loading job results.
"""
import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

logger = logging.getLogger(__name__)


class JobSearch:
    """Handles LinkedIn job search operations."""
    
    # Base jobs URL
    JOBS_URL = "https://www.linkedin.com/jobs/search/"
    
    def __init__(self, driver):
        """
        Initialize JobSearch with WebDriver instance.
        
        Args:
            driver: Selenium WebDriver instance
        """
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
    
    def search_jobs(self, keywords, location=None, num_results=25):
        """
        Search for jobs on LinkedIn.
        
        Args:
            keywords (str): Job search keywords (required)
            location (str, optional): Job location filter
            num_results (int, optional): Number of results to load (default: 25)
        
        Returns:
            bool: True if search successful, False otherwise
        """
        try:
            logger.info(f"Searching for jobs with keywords: '{keywords}'")
            
            # Build search URL
            url = f"{self.JOBS_URL}?keywords={keywords}"
            if location:
                url += f"&location={location}"
            
            logger.info(f"Navigating to: {url}")
            self.driver.get(url)
            time.sleep(3)  # Wait for page load
            
            # Wait for job cards to appear using data-view-name attribute (more reliable)
            logger.info("Waiting for job cards to load...")
            try:
                # Try the more reliable data-view-name selector first
                self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-view-name='job-card']"))
                )
            except TimeoutException:
                # Fallback to class selector if data-view-name doesn't work
                logger.warning("data-view-name selector not found, trying class selector...")
                self.wait.until(
                    EC.presence_of_element_located((By.CLASS_NAME, "base-card"))
                )
            
            # Scroll to load more results
            self._scroll_to_load_more(num_results)
            
            logger.info("Job search completed successfully")
            return True
        
        except TimeoutException as e:
            logger.error(f"Timeout waiting for job cards: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Job search failed: {str(e)}")
            return False
    
    def _scroll_to_load_more(self, target_count):
        """
        Scroll page to load more job results dynamically.
        This is a PRIVATE method.
        
        Args:
            target_count (int): Target number of job cards to load
        
        Returns:
            bool: True if scrolling completed
        """
        try:
            loaded_count = 0
            scroll_pause_time = 1
            max_scrolls = 50  # Prevent infinite scrolling
            scroll_count = 0
            
            logger.info(f"Scrolling to load {target_count} job results...")
            
            while loaded_count < target_count and scroll_count < max_scrolls:
                # Scroll to bottom of page
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(scroll_pause_time)
                
                # Get current count of loaded job cards using data-view-name selector
                jobs = self.driver.find_elements(By.CSS_SELECTOR, "[data-view-name='job-card']")
                if not jobs:
                    # Fallback to class selector
                    jobs = self.driver.find_elements(By.CLASS_NAME, "base-card")
                loaded_count = len(jobs)
                
                logger.info(f"Loaded {loaded_count} out of {target_count} jobs")
                
                # Check if we've reached target
                if loaded_count >= target_count:
                    break
                
                scroll_count += 1
            
            if scroll_count >= max_scrolls:
                logger.warning(f"Reached max scrolls. Loaded {loaded_count} jobs instead of {target_count}")
            
            return True
        
        except Exception as e:
            logger.warning(f"Error during scrolling: {str(e)}")
            return False

