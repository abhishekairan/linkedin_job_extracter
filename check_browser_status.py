"""
Utility script to check the status of the persistent browser instance.
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
    """Check and display browser status."""
    try:
        Config.validate()
        browser_manager = BrowserManager()
        status = browser_manager.get_browser_status()
        
        print("\n" + "="*60)
        print("Browser Instance Status")
        print("="*60)
        print(f"Browser exists: {status['has_browser']}")
        print(f"Browser is alive: {status['is_alive']}")
        print(f"Active instances: {status['instance_count']}")
        print("="*60)
        
        if status['has_browser'] and status['is_alive']:
            print("✓ Browser is running and ready to use")
            print("\nYou can run your scraping scripts and they will reuse this browser.")
        elif status['has_browser'] and not status['is_alive']:
            print("⚠ Browser instance exists but is not responding")
            print("It may have crashed. A new browser will be created on next run.")
        else:
            print("No browser instance found")
            print("A new browser will be created on next script run.")
        
        print()
    
    except Exception as e:
        logger.error(f"Error checking browser status: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()

