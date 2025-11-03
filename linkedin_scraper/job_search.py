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
from .linkedin_auth import LinkedInAuth
from .security import SecurityManager

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
        Checks authentication first and authenticates if needed.
        
        Args:
            keywords (str): Job search keywords (required)
            location (str, optional): Job location filter
            num_results (int, optional): Number of results to load (default: 25)
        
        Returns:
            bool: True if search successful, False otherwise
        """
        try:
            # Check authentication before searching
            auth = LinkedInAuth(self.driver)
            if not auth.is_logged_in():
                logger.warning("Not authenticated. Attempting to authenticate before job search...")
                login_success = auth.login(manual_verification=True)
                if not login_success:
                    logger.error("Authentication failed. Cannot proceed with job search.")
                    logger.error("Tip: If CAPTCHA/verification is required, ensure HEADLESS_MODE=False in .env")
                    return False
                logger.info("✓ Authentication successful")
            else:
                logger.debug("Already authenticated")
            
            logger.info(f"Searching for jobs with keywords: '{keywords}'")
            
            # Build search URL
            url = f"{self.JOBS_URL}?keywords={keywords}"
            if location:
                url += f"&location={location}"
            
            logger.info(f"Navigating to: {url}")
            self.driver.get(url)
            
            # Add human-like delay before interacting with page
            SecurityManager.random_delay(2, 4)
            
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
            
            # Scroll to load all available results (ignores num_results limit)
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
        Continues scrolling until no more jobs are loaded.
        
        Args:
            target_count (int): Target number of job cards to load (ignored - loads all available)
        
        Returns:
            bool: True if scrolling completed
        """
        try:
            loaded_count = 0
            previous_count = 0
            scroll_pause_time = 1
            no_change_count = 0  # Track consecutive scrolls with no new jobs
            max_no_change = 3  # Stop after 3 consecutive scrolls with no new jobs
            
            logger.info("Scrolling to load all available job results...")
            
            while True:
                # Scroll to bottom of page with random intervals
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                
                # Human-like scroll delay
                SecurityManager.human_like_scroll_delay()
                
                # Get current count of loaded job cards using data-view-name selector
                jobs = self.driver.find_elements(By.CSS_SELECTOR, "[data-view-name='job-card']")
                if not jobs:
                    # Fallback to class selector
                    jobs = self.driver.find_elements(By.CLASS_NAME, "base-card")
                loaded_count = len(jobs)
                
                logger.info(f"Loaded {loaded_count} jobs")
                
                # Check if no new jobs were loaded
                if loaded_count == previous_count:
                    no_change_count += 1
                    if no_change_count >= max_no_change:
                        logger.info(f"No more jobs loading. Stopped at {loaded_count} jobs")
                        break
                else:
                    no_change_count = 0  # Reset counter if new jobs were found
                
                previous_count = loaded_count
            
            return True
        
        except Exception as e:
            logger.warning(f"Error during scrolling: {str(e)}")
            return False

