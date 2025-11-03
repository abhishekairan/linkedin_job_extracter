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
    
    # Class-level driver storage for persistence across instances
    _shared_driver = None
    _instance_count = 0
    
    def __init__(self):
        """Initialize BrowserManager - uses shared driver instance."""
        self.config = Config
        BrowserManager._instance_count += 1
    
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
        Stores it as a class variable to persist across instances.
        
        Returns:
            webdriver.Chrome: Chrome WebDriver instance
        
        Raises:
            WebDriverException: If browser launch fails
        """
        try:
            options = self._get_chrome_options()
            service = self._create_service()
            
            logger.info(f"Launching Chrome browser on {self.config.PLATFORM}...")
            BrowserManager._shared_driver = webdriver.Chrome(service=service, options=options)
            BrowserManager._shared_driver.implicitly_wait(self.config.IMPLICIT_WAIT)
            
            logger.info("Browser launched successfully and stored as persistent instance")
            logger.info("Browser will remain open until explicitly closed or machine shutdown")
            return BrowserManager._shared_driver
        
        except Exception as e:
            logger.error(f"Failed to launch browser: {str(e)}")
            raise WebDriverException(f"Browser launch failed: {str(e)}")
    
    def is_browser_alive(self):
        """
        Check if the browser instance is still alive and responsive.
        Uses the shared class-level driver instance.
        
        Returns:
            bool: True if browser is alive, False otherwise
        """
        if BrowserManager._shared_driver is None:
            return False
        
        try:
            # Try to execute simple JavaScript to verify browser is responsive
            BrowserManager._shared_driver.execute_script("return 1;")
            return True
        except Exception as e:
            logger.warning(f"Browser health check failed: {str(e)}")
            # If browser is dead, clear the reference
            BrowserManager._shared_driver = None
            return False
    
    def get_or_create_browser(self):
        """
        Get existing browser instance or create a new one.
        This is the KEY METHOD for maintaining persistence.
        Uses class-level storage to persist across script runs.
        
        Returns:
            webdriver.Chrome: Active Chrome WebDriver instance
        """
        # Check if shared driver exists and is alive
        if BrowserManager._shared_driver is not None and self.is_browser_alive():
            logger.info("Reusing existing persistent browser instance")
            logger.info(f"(Active instances: {BrowserManager._instance_count})")
            return BrowserManager._shared_driver
        
        # Driver doesn't exist or is not alive - create new one
        logger.info("Creating new persistent browser instance")
        logger.info("This browser will stay open until explicitly closed or machine shutdown")
        
        # Try to cleanup dead driver reference if it exists
        if BrowserManager._shared_driver is not None:
            try:
                BrowserManager._shared_driver.quit()
            except Exception:
                pass  # Ignore errors during cleanup
            finally:
                BrowserManager._shared_driver = None
        
        # Launch new browser
        return self.launch_browser()
    
    def close_browser(self, force=False):
        """
        Close the browser instance and clean up.
        
        Args:
            force (bool): If True, closes browser even if multiple instances exist.
                        If False (default), only closes if this is the last instance.
        
        Returns:
            bool: True if browser was closed, False otherwise
        """
        if BrowserManager._shared_driver is None:
            logger.info("No browser instance to close")
            return False
        
        if not force and BrowserManager._instance_count > 1:
            logger.info(f"Not closing browser - {BrowserManager._instance_count} active instances")
            logger.info("Use close_browser(force=True) to force close")
            return False
        
        try:
            BrowserManager._shared_driver.quit()
            logger.info("Browser closed successfully")
            return True
        except Exception as e:
            logger.warning(f"Error closing browser: {str(e)}")
            return False
        finally:
            BrowserManager._shared_driver = None
            BrowserManager._instance_count = 0
    
    @classmethod
    def get_browser_status(cls):
        """
        Get status of the shared browser instance.
        
        Returns:
            dict: Status information about the browser
        """
        has_browser = cls._shared_driver is not None
        is_alive = False
        
        if has_browser:
            try:
                cls._shared_driver.execute_script("return 1;")
                is_alive = True
            except Exception:
                is_alive = False
        
        return {
            'has_browser': has_browser,
            'is_alive': is_alive,
            'instance_count': cls._instance_count
        }
    
    def __enter__(self):
        """Context manager entry - return browser instance without closing."""
        return self.get_or_create_browser()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit - do NOT close browser to maintain persistence.
        Pass to keep browser open for reuse.
        """
        pass

