"""
LinkedIn authentication module.
Handles login and session verification.
"""
import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from .config import Config

logger = logging.getLogger(__name__)


class LinkedInAuth:
    """Handles LinkedIn authentication and session management."""
    
    # LinkedIn URLs
    LINKEDIN_LOGIN_URL = "https://www.linkedin.com/login"
    LINKEDIN_HOME_URL = "https://www.linkedin.com/feed/"
    
    def __init__(self, driver):
        """
        Initialize LinkedInAuth with WebDriver instance.
        
        Args:
            driver: Selenium WebDriver instance
        """
        self.driver = driver
        self.wait = WebDriverWait(driver, Config.IMPLICIT_WAIT)
    
    def is_logged_in(self):
        """
        Check if user is currently logged into LinkedIn.
        This is a CRITICAL method for avoiding unnecessary logins.
        
        Returns:
            bool: True if logged in, False otherwise
        """
        try:
            logger.info("Checking login status...")
            self.driver.get(self.LINKEDIN_HOME_URL)
            time.sleep(2)  # Wait for page load
            
            # Check if redirected to login page
            if "login" in self.driver.current_url.lower():
                logger.info("Not logged in - redirected to login page")
                return False
            
            # Try to find feed content (indicates successful login)
            try:
                self.wait.until(
                    EC.presence_of_element_located((By.CLASS_NAME, "scaffold-finite-scroll__content"))
                )
                logger.info("Already logged into LinkedIn")
                return True
            except TimeoutException:
                logger.warning("Could not find feed content - assuming not logged in")
                return False
        
        except Exception as e:
            logger.warning(f"Error checking login status: {str(e)}")
            return False
    
    def login(self):
        """
        Perform LinkedIn login using credentials from Config.
        
        Returns:
            bool: True if login successful, False otherwise
        """
        try:
            logger.info("Attempting LinkedIn login...")
            
            # Navigate to login page
            self.driver.get(self.LINKEDIN_LOGIN_URL)
            time.sleep(2)  # Wait for page load
            
            # Find and fill email field
            email_field = self.driver.find_element(By.ID, "username")
            email_field.clear()
            email_field.send_keys(Config.LINKEDIN_EMAIL)
            logger.info("Email entered")
            
            # Find and fill password field
            password_field = self.driver.find_element(By.ID, "password")
            password_field.clear()
            password_field.send_keys(Config.LINKEDIN_PASSWORD)
            logger.info("Password entered")
            
            # Find and click submit button
            submit_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            submit_button.click()
            logger.info("Login button clicked")
            
            # Wait for login to process
            time.sleep(3)
            
            # Verify login was successful
            if self.is_logged_in():
                logger.info("Login successful!")
                return True
            else:
                logger.error("Login verification failed - may need manual verification")
                return False
        
        except TimeoutException:
            logger.error("Login timeout - may need manual verification or CAPTCHA")
            return False
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return False

