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
        Simple check: If browser redirects to /feed, user is logged in.
        LinkedIn redirects to login if not authenticated.
        
        Returns:
            bool: True if logged in, False otherwise
        """
        try:
            logger.info("Checking login status...")
            
            # Get current URL first
            current_url = self.driver.current_url.lower()
            
            # If already on feed page, user is logged in
            if "/feed/" in current_url:
                logger.info("Already logged into LinkedIn (on feed page)")
                return True
            
            # Navigate to feed URL - LinkedIn redirects to login if not authenticated
            self.driver.get(self.LINKEDIN_HOME_URL)
            time.sleep(2)  # Wait for redirect/page load
            
            # Check final URL - if redirected to /feed, logged in
            final_url = self.driver.current_url.lower()
            
            if "/feed/" in final_url:
                logger.info("Already logged into LinkedIn (redirected to feed)")
                return True
            
            # If redirected to login or checkpoint, not logged in
            if "login" in final_url or "/checkpoint/" in final_url:
                logger.info("Not logged in - redirected to login/checkpoint page")
                return False
            
            # Default: not logged in if we're not on feed
            logger.info("Not logged in - not on feed page")
            return False
        
        except Exception as e:
            logger.warning(f"Error checking login status: {str(e)}")
            return False
    
    def login(self, manual_verification=True):
        """
        Perform LinkedIn login using credentials from Config.
        Only triggers manual verification if login doesn't redirect to /feed.
        
        Args:
            manual_verification (bool): If True, allows manual verification when needed.
                                       Browser will wait for user to complete CAPTCHA/2FA.
        
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
            
            # Wait for login to process and redirect
            time.sleep(5)  # Wait for redirect after login
            
            # Check current URL - if redirected to /feed, login was successful
            current_url = self.driver.current_url.lower()
            
            if "/feed/" in current_url:
                logger.info("Login successful! Redirected to feed page.")
                return True
            
            # If not redirected to /feed, manual verification might be needed
            if manual_verification:
                logger.warning("Login did not redirect to /feed. Manual verification may be required.")
                logger.warning(f"Current URL: {self.driver.current_url}")
                return self._wait_for_manual_verification()
            else:
                logger.error("Login did not redirect to /feed. Manual verification may be required.")
                logger.error(f"Current URL: {self.driver.current_url}")
                logger.error("Set manual_verification=True to enable manual login.")
                return False
        
        except TimeoutException:
            if manual_verification:
                logger.warning("Login timeout, attempting manual verification...")
                return self._wait_for_manual_verification()
            else:
                logger.error("Login timeout - may need manual verification or CAPTCHA")
                return False
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            if manual_verification:
                logger.warning("Attempting manual verification...")
                return self._wait_for_manual_verification()
            return False
    
    def _wait_for_manual_verification(self, timeout=300):
        """
        Wait for user to manually complete verification (CAPTCHA, 2FA, etc.).
        
        Args:
            timeout (int): Maximum time to wait in seconds (default: 5 minutes)
        
        Returns:
            bool: True if login successful after manual verification, False otherwise
        """
        logger.info("="*60)
        logger.info("MANUAL VERIFICATION REQUIRED")
        logger.info("="*60)
        logger.info("Please complete the following in the browser:")
        logger.info("1. Solve any CAPTCHA if present")
        logger.info("2. Complete 2FA if required")
        logger.info("3. Navigate to LinkedIn feed (https://www.linkedin.com/feed/)")
        logger.info("4. The script will automatically detect when you're logged in")
        logger.info("="*60)
        logger.info(f"Waiting up to {timeout} seconds for manual verification...")
        logger.info(f"Current URL: {self.driver.current_url}")
        
        start_time = time.time()
        check_interval = 120  # Check every 5 seconds
        
        while time.time() - start_time < timeout:
            time.sleep(check_interval)
            
            # Check if user navigated away or completed login
            current_url = self.driver.current_url
            
            # Check if logged in
            if self.is_logged_in():
                logger.info("✓ Manual verification completed! Login successful.")
                return True
            
            # Check if still on login/verification page
            if "login" not in current_url.lower() and "challenge" not in current_url.lower():
                # User might be navigating, wait a bit more
                time.sleep(2)
                if self.is_logged_in():
                    logger.info("✓ Manual verification completed! Login successful.")
                    return True
            
            elapsed = int(time.time() - start_time)
            remaining = timeout - elapsed
            if elapsed % 30 == 0:  # Log every 30 seconds
                logger.info(f"Still waiting... ({elapsed}s elapsed, {remaining}s remaining)")
        
        logger.error(f"Timeout after {timeout} seconds. Manual verification not completed.")
        return False

