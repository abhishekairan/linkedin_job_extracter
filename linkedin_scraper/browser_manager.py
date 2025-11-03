"""
Browser instance management module.
Handles persistent Chrome browser instances with health checks.
Supports remote debugging for cross-process browser sharing.
"""
import logging
import json
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from .config import Config

logger = logging.getLogger(__name__)

# Remote debugging port file
DEBUG_PORT_FILE = Path(__file__).parent.parent / 'browser_debug_port.json'
DEFAULT_DEBUG_PORT = 9222


class BrowserManager:
    """Manages persistent Chrome browser instance with health checks."""
    
    # Class-level driver storage for persistence across instances
    _shared_driver = None
    _instance_count = 0
    
    def __init__(self):
        """Initialize BrowserManager - uses shared driver instance."""
        self.config = Config
        BrowserManager._instance_count += 1
    
    def _get_chrome_options(self, use_remote_debugging=False, debug_port=None):
        """
        Create and configure Chrome options.
        
        Args:
            use_remote_debugging (bool): If True, enable remote debugging port
            debug_port (int, optional): Remote debugging port number
        
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
        
        # Stealth and anti-detection options
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--start-maximized')
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-features=IsolateOrigins,site-per-process')
        options.add_argument('--disable-background-networking')
        options.add_argument('--disable-background-timer-throttling')
        options.add_argument('--disable-default-apps')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-sync')
        options.add_argument('--disable-translate')
        options.add_argument('--metrics-recording-only')
        options.add_argument('--no-first-run')
        options.add_argument('--password-store=basic')
        
        # Set random realistic user agent
        from .security import SecurityManager
        user_agent = SecurityManager.get_random_user_agent()
        options.add_argument(f'user-agent={user_agent}')
        
        # Remote debugging for cross-process access
        if use_remote_debugging:
            port = debug_port or DEFAULT_DEBUG_PORT
            options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
            logger.info(f"Using remote debugging on port {port}")
        else:
            # Enable remote debugging port when creating new browser
            port = debug_port or DEFAULT_DEBUG_PORT
            options.add_argument(f'--remote-debugging-port={port}')
            logger.info(f"Remote debugging enabled on port {port}")
        
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
    
    def launch_browser(self, use_remote_debugging=False):
        """
        Launch a new Chrome browser instance or connect to existing one via remote debugging.
        Stores it as a class variable to persist across instances.
        
        Args:
            use_remote_debugging (bool): If True, connect to existing browser via remote debugging
        
        Returns:
            webdriver.Chrome: Chrome WebDriver instance
        
        Raises:
            WebDriverException: If browser launch fails
        """
        try:
            # Check if we should connect to existing browser
            if use_remote_debugging:
                debug_port = self._get_debug_port()
                if debug_port:
                    logger.info(f"Connecting to existing browser on remote debugging port {debug_port}...")
                    options = self._get_chrome_options(use_remote_debugging=True, debug_port=debug_port)
                    # No service needed when connecting to existing browser
                    BrowserManager._shared_driver = webdriver.Chrome(options=options)
                    BrowserManager._shared_driver.implicitly_wait(self.config.IMPLICIT_WAIT)
                    logger.info("Successfully connected to existing browser instance")
                    return BrowserManager._shared_driver
            
            # Launch new browser with remote debugging enabled
            debug_port = DEFAULT_DEBUG_PORT
            options = self._get_chrome_options(use_remote_debugging=False, debug_port=debug_port)
            service = self._create_service()
            
            logger.info(f"Launching Chrome browser on {self.config.PLATFORM}...")
            BrowserManager._shared_driver = webdriver.Chrome(service=service, options=options)
            BrowserManager._shared_driver.implicitly_wait(self.config.IMPLICIT_WAIT)
            
            # Inject stealth scripts to prevent detection
            try:
                from .security import SecurityManager
                SecurityManager.inject_stealth_scripts(BrowserManager._shared_driver)
            except Exception as e:
                logger.warning(f"Failed to inject stealth scripts: {str(e)}")
            
            # Save debug port info
            self._save_debug_port(debug_port)
            
            logger.info("Browser launched successfully and stored as persistent instance")
            logger.info("Browser will remain open until explicitly closed or machine shutdown")
            return BrowserManager._shared_driver
        
        except Exception as e:
            logger.error(f"Failed to launch browser: {str(e)}")
            raise WebDriverException(f"Browser launch failed: {str(e)}")
    
    def _save_debug_port(self, port):
        """Save remote debugging port to file."""
        try:
            data = {'port': port, 'timestamp': str(Path(__file__).stat().st_mtime)}
            with open(DEBUG_PORT_FILE, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            logger.warning(f"Failed to save debug port: {str(e)}")
    
    def _get_debug_port(self):
        """Get remote debugging port from file."""
        try:
            if DEBUG_PORT_FILE.exists():
                with open(DEBUG_PORT_FILE, 'r') as f:
                    data = json.load(f)
                    return data.get('port', DEFAULT_DEBUG_PORT)
        except Exception as e:
            logger.warning(f"Failed to read debug port: {str(e)}")
        return DEFAULT_DEBUG_PORT
    
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
    
    def get_or_create_browser(self, try_remote_connection=True):
        """
        Get existing browser instance or create a new one.
        This is the KEY METHOD for maintaining persistence.
        Uses class-level storage to persist across script runs.
        Can connect to browser from another process via remote debugging.
        
        Args:
            try_remote_connection (bool): If True, try to connect to browser from another process
        
        Returns:
            webdriver.Chrome: Active Chrome WebDriver instance
        """
        # Check if shared driver exists and is alive
        if BrowserManager._shared_driver is not None and self.is_browser_alive():
            logger.info("Reusing existing persistent browser instance")
            logger.info(f"(Active instances: {BrowserManager._instance_count})")
            return BrowserManager._shared_driver
        
        # Try to connect to browser from another process via remote debugging
        if try_remote_connection:
            try:
                debug_port = self._get_debug_port()
                if DEBUG_PORT_FILE.exists():
                    logger.info("Attempting to connect to browser service via remote debugging...")
                    driver = self.launch_browser(use_remote_debugging=True)
                    # Verify connection works
                    if self.is_browser_alive():
                        logger.info("✓ Connected to browser service successfully")
                        BrowserManager._shared_driver = driver
                        return driver
                    else:
                        logger.warning("Failed to connect to remote browser")
                        try:
                            driver.quit()
                        except:
                            pass
            except Exception as e:
                logger.debug(f"Could not connect to remote browser: {str(e)}")
                logger.info("Will create new browser instance")
        
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

