"""
Standalone browser service that maintains persistent browser instance.
This service runs continuously, keeping the browser alive for job searches.
Login is handled automatically by job_search when LinkedIn requires it.

Usage:
    python browser_service.py

To stop:
    Create a file named 'stop_service' in the project root, or send SIGTERM

Note:
    This service only maintains the browser instance. Authentication is handled
    on-demand by job_search.py when LinkedIn requires login, minimizing
    unnecessary login attempts.
"""
import logging
import sys
import time
import signal
import json
from pathlib import Path
from linkedin_scraper.config import Config
from linkedin_scraper.browser_manager import BrowserManager

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
    """Initialize browser instance (authentication handled by job_search when needed)."""
    global browser_manager, driver
    
    try:
        logger.info("Initializing browser service...")
        Config.validate()
        
        # Create browser manager and get browser instance
        # Login is NOT performed here - it will be handled by job_search when needed
        # This minimizes unnecessary login attempts
        browser_manager = BrowserManager()
        driver = browser_manager.get_or_create_browser()
        
        logger.info("✓ Browser service initialized")
        logger.info("Note: Login will be handled automatically by job_search when required")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize browser service: {str(e)}", exc_info=True)
        return False


def check_browser_health():
    """Check browser health (login handled by job_search when needed)."""
    global driver
    
    if driver is None:
        return False
    
    try:
        # Check if browser is alive
        browser_status = browser_manager.get_browser_status()
        if not browser_status['is_alive']:
            logger.warning("Browser is not alive, reinitializing...")
            initialize_browser_and_auth()
            return False
        
        # Update status (login status not tracked here - handled by job_search)
        status_info = {
            'is_alive': browser_status['is_alive'],
            'logged_in': False  # Not tracked here - login handled on-demand by job_search
        }
        update_status(status_info)
        
        return True
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return False


def main():
    """Main service loop."""
    global running, driver, browser_manager
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("="*60)
    logger.info("LinkedIn Browser Service")
    logger.info("="*60)
    logger.info("This service maintains a persistent browser instance.")
    logger.info("Login is handled automatically by job_search when required.")
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
        'logged_in': False  # Login handled on-demand by job_search
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

