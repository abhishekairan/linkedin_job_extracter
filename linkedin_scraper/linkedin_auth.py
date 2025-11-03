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
    
    def login(self, manual_verification=True):
        """
        Perform LinkedIn login using credentials from Config.
        
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
            
            # Wait for login to process
            time.sleep(3)
            
            # Check if manual verification is needed
            if self._requires_manual_verification():
                if manual_verification:
                    logger.warning("Manual verification required (CAPTCHA or security challenge detected)")
                    return self._wait_for_manual_verification()
                else:
                    logger.error("Login requires manual verification. Set manual_verification=True to enable manual login.")
                    logger.info("Current URL: " + self.driver.current_url)
                    return False
            
            # Verify login was successful
            if self.is_logged_in():
                logger.info("Login successful!")
                return True
            else:
                if manual_verification:
                    logger.warning("Login verification failed, attempting manual verification...")
                    return self._wait_for_manual_verification()
                else:
                    logger.error("Login verification failed - may need manual verification")
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
            return False
    
    def _requires_manual_verification(self):
        """
        Check if the current page requires manual verification (CAPTCHA, 2FA, etc.).
        
        Returns:
            bool: True if manual verification is required
        """
        try:
            current_url = self.driver.current_url.lower()
            page_source = self.driver.page_source.lower()
            
            # Check for common verification indicators
            verification_indicators = [
                "challenge" in current_url,
                "captcha" in current_url,
                "verify" in current_url,
                "security" in current_url,
                "captcha" in page_source,
                "verify your identity" in page_source,
                "unusual activity" in page_source,
                "security challenge" in page_source
            ]
            
            return any(verification_indicators)
        except Exception:
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

