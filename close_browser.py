"""
Utility script to close the persistent browser instance.
Use this if you need to manually close the browser.
"""
import logging
import sys
from pathlib import Path
from linkedin_scraper.config import Config
from linkedin_scraper.browser_manager import BrowserManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

def main():
    """Close the persistent browser instance."""
    try:
        logger.info("Checking for persistent browser instance...")
        Config.validate()
        
        browser_manager = BrowserManager()
        status = browser_manager.get_browser_status()
        
        if status['has_browser']:
            logger.info(f"Found browser instance (Active instances: {status['instance_count']})")
            logger.info("Closing browser...")
            
            # Force close regardless of instance count
            if browser_manager.close_browser(force=True):
                logger.info("✓ Browser closed successfully")
            else:
                logger.warning("Failed to close browser")
        else:
            logger.info("No active browser instance found")
    
    except Exception as e:
        logger.error(f"Error closing browser: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()

