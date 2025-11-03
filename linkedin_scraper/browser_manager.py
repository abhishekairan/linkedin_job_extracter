"""
Browser instance management module.
Handles persistent Chrome browser instances with health checks.
"""
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from .config import Config

logger = logging.getLogger(__name__)


class BrowserManager:
    """Manages persistent Chrome browser instance with health checks."""
    
    def __init__(self):
        """Initialize BrowserManager with no active driver."""
        self.driver = None
        self.config = Config
    
    def _get_chrome_options(self):
        """
        Create and configure Chrome options.
        
        Returns:
            Options: Configured Chrome options object
        """
        options = Options()
        
        # Set binary location
        if self.config.CHROME_BINARY_PATH:
            options.binary_location = self.config.CHROME_BINARY_PATH
        
        # Add required arguments for Linux servers
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--start-maximized')
        
        # Set user agent
        options.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Headless mode if configured
        if self.config.HEADLESS_MODE:
            options.add_argument('--headless')
        
        return options
    
    def _create_service(self):
        """
        Create Chrome service with driver path.
        
        Returns:
            Service: Configured Chrome service object
        """
        return Service(self.config.CHROMEDRIVER_PATH)
    
    def launch_browser(self):
        """
        Launch a new Chrome browser instance.
        
        Returns:
            webdriver.Chrome: Chrome WebDriver instance
        
        Raises:
            WebDriverException: If browser launch fails
        """
        try:
            options = self._get_chrome_options()
            service = self._create_service()
            
            logger.info(f"Launching Chrome browser on {self.config.PLATFORM}...")
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.implicitly_wait(self.config.IMPLICIT_WAIT)
            
            logger.info("Browser launched successfully")
            return self.driver
        
        except Exception as e:
            logger.error(f"Failed to launch browser: {str(e)}")
            raise WebDriverException(f"Browser launch failed: {str(e)}")
    
    def is_browser_alive(self):
        """
        Check if the browser instance is still alive and responsive.
        
        Returns:
            bool: True if browser is alive, False otherwise
        """
        if self.driver is None:
            return False
        
        try:
            # Try to execute simple JavaScript to verify browser is responsive
            self.driver.execute_script("return 1;")
            return True
        except Exception as e:
            logger.warning(f"Browser health check failed: {str(e)}")
            return False
    
    def get_or_create_browser(self):
        """
        Get existing browser instance or create a new one.
        This is the KEY METHOD for maintaining persistence.
        
        Returns:
            webdriver.Chrome: Active Chrome WebDriver instance
        """
        # Check if driver exists and is alive
        if self.driver is not None and self.is_browser_alive():
            logger.info("Using existing browser instance")
            return self.driver
        
        # Driver doesn't exist or is not alive - create new one
        logger.info("Creating new browser instance")
        
        # Try to quit existing driver if it exists (cleanup)
        if self.driver is not None:
            try:
                self.driver.quit()
            except Exception:
                pass  # Ignore errors during cleanup
        
        # Launch new browser
        return self.launch_browser()
    
    def close_browser(self):
        """Close the browser instance and clean up."""
        if self.driver is not None:
            try:
                self.driver.quit()
                logger.info("Browser closed successfully")
            except Exception as e:
                logger.warning(f"Error closing browser: {str(e)}")
            finally:
                self.driver = None
    
    def __enter__(self):
        """Context manager entry - return browser instance without closing."""
        return self.get_or_create_browser()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit - do NOT close browser to maintain persistence.
        Pass to keep browser open for reuse.
        """
        pass

