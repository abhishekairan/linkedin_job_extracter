"""
Security utilities to prevent account flagging and bot detection.
Implements human-like behavior patterns and rate limiting.
"""
import logging
import random
import time

logger = logging.getLogger(__name__)


class SecurityManager:
    """Manages security measures to prevent account flagging."""
    
    # Rate limiting constants
    MIN_SEARCH_INTERVAL = 5  # Minimum seconds between searches
    MAX_SEARCH_INTERVAL = 20  # Maximum seconds between searches
    MIN_ACTION_DELAY = 1  # Minimum delay for actions (seconds)
    MAX_ACTION_DELAY = 3  # Maximum delay for actions (seconds)
    
    # Scroll behavior constants
    MIN_SCROLL_DELAY = 0.5  # Minimum delay between scrolls
    MAX_SCROLL_DELAY = 2.0  # Maximum delay between scrolls
    
    def __init__(self):
        """Initialize SecurityManager."""
        self.last_search_time = 0
        self.search_count = 0
    
    @staticmethod
    def random_delay(min_seconds=None, max_seconds=None):
        """
        Add random delay to simulate human behavior.
        
        Args:
            min_seconds (float): Minimum delay (default: MIN_ACTION_DELAY)
            max_seconds (float): Maximum delay (default: MAX_ACTION_DELAY)
        """
        min_delay = min_seconds or SecurityManager.MIN_ACTION_DELAY
        max_delay = max_seconds or SecurityManager.MAX_ACTION_DELAY
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    @staticmethod
    def human_like_scroll_delay():
        """Add random delay between scrolls to simulate human scrolling."""
        delay = random.uniform(
            SecurityManager.MIN_SCROLL_DELAY,
            SecurityManager.MAX_SCROLL_DELAY
        )
        time.sleep(delay)
    
    def rate_limit_search(self):
        """
        Enforce rate limiting between searches.
        Waits if search is attempted too soon after last search.
        """
        current_time = time.time()
        time_since_last = current_time - self.last_search_time
        
        # Calculate required wait time
        required_interval = random.uniform(
            self.MIN_SEARCH_INTERVAL,
            self.MAX_SEARCH_INTERVAL
        )
        
        if time_since_last < required_interval:
            wait_time = required_interval - time_since_last
            logger.info(f"Rate limiting: Waiting {wait_time:.1f}s before next search")
            time.sleep(wait_time)
        
        self.last_search_time = time.time()
        self.search_count += 1
    
    @staticmethod
    def random_mouse_movement(driver):
        """
        Simulate random mouse movement to appear more human-like.
        Only works when browser is visible (not headless).
        
        Args:
            driver: Selenium WebDriver instance
        """
        try:
            # Generate random coordinates within viewport
            width = driver.execute_script("return window.innerWidth;")
            height = driver.execute_script("return window.innerHeight;")
            
            x = random.randint(0, width)
            y = random.randint(0, height)
            
            # Move mouse using JavaScript
            driver.execute_script(f"document.elementFromPoint({x}, {y});")
            time.sleep(random.uniform(0.1, 0.3))
        except Exception as e:
            logger.debug(f"Mouse movement simulation failed: {str(e)}")
    
    @staticmethod
    def get_chrome_stealth_options():
        """
        Get Chrome options optimized for stealth and preventing bot detection.
        
        Returns:
            list: List of Chrome arguments for stealth mode
        """
        return [
            # Hide automation flags
            '--disable-blink-features=AutomationControlled',
            
            # Disable automation indicators
            '--disable-dev-shm-usage',
            '--no-sandbox',
            
            # Realistic viewport
            '--start-maximized',
            
            # Disable automation detection
            '--disable-web-security',
            '--disable-features=IsolateOrigins,site-per-process',
            
            # Prevent detection
            '--disable-background-networking',
            '--disable-background-timer-throttling',
            '--disable-client-side-phishing-detection',
            '--disable-default-apps',
            '--disable-extensions',
            '--disable-hang-monitor',
            '--disable-popup-blocking',
            '--disable-prompt-on-repost',
            '--disable-sync',
            '--disable-translate',
            '--metrics-recording-only',
            '--no-first-run',
            '--safebrowsing-disable-auto-update',
            '--enable-automation',
            '--password-store=basic',
            '--use-mock-keychain',
        ]
    
    @staticmethod
    def inject_stealth_scripts(driver):
        """
        Inject JavaScript to mask automation indicators.
        
        Args:
            driver: Selenium WebDriver instance
        """
        try:
            # Remove webdriver property
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                '''
            })
            
            # Override navigator.plugins
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5]
                    });
                '''
            })
            
            # Override navigator.languages
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['en-US', 'en']
                    });
                '''
            })
            
            # Override chrome property
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    window.chrome = {
                        runtime: {}
                    };
                '''
            })
            
            # Override permissions
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    const originalQuery = window.navigator.permissions.query;
                    window.navigator.permissions.query = (parameters) => (
                        parameters.name === 'notifications' ?
                            Promise.resolve({ state: Notification.permission }) :
                            originalQuery(parameters)
                    );
                '''
            })
            
            logger.debug("Stealth scripts injected successfully")
        except Exception as e:
            logger.warning(f"Failed to inject some stealth scripts: {str(e)}")
    
    @staticmethod
    def get_random_user_agent():
        """
        Get a random realistic user agent string.
        
        Returns:
            str: Random user agent string
        """
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        ]
        return random.choice(user_agents)

