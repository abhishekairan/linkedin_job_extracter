"""
Standalone browser service that maintains persistent browser and LinkedIn login.
This service runs continuously, keeping the browser alive and authenticated.
Run this as a separate process that stays alive.

Usage:
    python browser_service.py

To stop:
    Create a file named 'stop_service' in the project root, or send SIGTERM
"""
import logging
import sys
import time
import signal
import json
from pathlib import Path
from linkedin_scraper.config import Config
from linkedin_scraper.browser_manager import BrowserManager
from linkedin_scraper.linkedin_auth import LinkedInAuth

# Setup logging
log_dir = Path(__file__).parent / 'logs'
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'browser_service.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Service control files
SERVICE_DIR = Path(__file__).parent
STATUS_FILE = SERVICE_DIR / 'browser_service_status.json'
STOP_FILE = SERVICE_DIR / 'stop_service'

# Global browser manager and driver
browser_manager = None
driver = None
auth = None
running = True


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    global running
    logger.info(f"Received signal {signum}, shutting down...")
    running = False


def update_status(status_info):
    """Update service status file."""
    try:
        status_data = {
            'running': True,
            'browser_alive': status_info.get('is_alive', False),
            'logged_in': status_info.get('logged_in', False),
            'timestamp': time.time()
        }
        with open(STATUS_FILE, 'w') as f:
            json.dump(status_data, f, indent=2)
    except Exception as e:
        logger.warning(f"Failed to update status file: {str(e)}")


def initialize_browser_and_auth():
    """Initialize browser and authenticate to LinkedIn."""
    global browser_manager, driver, auth
    
    try:
        logger.info("Initializing browser service...")
        Config.validate()
        
        # Create browser manager
        browser_manager = BrowserManager()
        driver = browser_manager.get_or_create_browser()
        
        # Initialize auth
        auth = LinkedInAuth(driver)
        
        # Check if already logged in
        if not auth.is_logged_in():
            logger.info("Not logged in, attempting login...")
            login_success = auth.login(manual_verification=True)
            if not login_success:
                logger.error("Login failed. Service will continue but authentication is required.")
                return False
        else:
            logger.info("Already authenticated to LinkedIn")
        
        logger.info("✓ Browser service initialized and authenticated")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize browser service: {str(e)}", exc_info=True)
        return False


def check_browser_health():
    """Check browser health and re-authenticate if needed."""
    global driver, auth
    
    if driver is None or auth is None:
        return False
    
    try:
        # Check if browser is alive
        browser_status = browser_manager.get_browser_status()
        if not browser_status['is_alive']:
            logger.warning("Browser is not alive, reinitializing...")
            initialize_browser_and_auth()
            return False
        
        # Check if still logged in
        is_logged_in = auth.is_logged_in()
        if not is_logged_in:
            logger.warning("Not logged in, attempting to re-login...")
            login_success = auth.login(manual_verification=True)
            if not login_success:
                logger.error("Re-login failed")
                is_logged_in = False
            else:
                is_logged_in = True
        
        # Update status
        status_info = {
            'is_alive': browser_status['is_alive'],
            'logged_in': is_logged_in
        }
        update_status(status_info)
        
        return True
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return False


def main():
    """Main service loop."""
    global running, driver, auth, browser_manager
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("="*60)
    logger.info("LinkedIn Browser Service")
    logger.info("="*60)
    logger.info("This service maintains a persistent browser and LinkedIn login.")
    logger.info("Press Ctrl+C or create 'stop_service' file to stop.")
    logger.info("="*60)
    
    # Initialize browser and authentication
    if not initialize_browser_and_auth():
        logger.error("Failed to initialize browser service. Exiting.")
        sys.exit(1)
    
    # Initial status update
    browser_status = browser_manager.get_browser_status()
    update_status({
        'is_alive': browser_status['is_alive'],
        'logged_in': True
    })
    
    # Main service loop
    health_check_interval = 60  # Check browser health every 60 seconds
    last_health_check = time.time()
    
    logger.info("Service running. Browser is ready for job searches.")
    logger.info(f"Status file: {STATUS_FILE}")
    
    try:
        while running:
            # Check for stop file
            if STOP_FILE.exists():
                logger.info("Stop file detected, shutting down...")
                running = False
                break
            
            # Periodic health check
            current_time = time.time()
            if current_time - last_health_check >= health_check_interval:
                check_browser_health()
                last_health_check = current_time
            
            # Sleep briefly to avoid high CPU usage
            time.sleep(5)
    
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.error(f"Service error: {str(e)}", exc_info=True)
    finally:
        # Cleanup
        logger.info("Shutting down browser service...")
        
        # Update status
        try:
            status_data = {
                'running': False,
                'browser_alive': False,
                'logged_in': False,
                'timestamp': time.time()
            }
            with open(STATUS_FILE, 'w') as f:
                json.dump(status_data, f, indent=2)
        except Exception:
            pass
        
        logger.info("Browser service stopped")
        # Note: Browser remains open to maintain session
        logger.info("Note: Browser instance remains open to preserve login session")


if __name__ == "__main__":
    main()

