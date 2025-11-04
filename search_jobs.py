"""
Standalone job search service that connects to the browser service.
This script performs job searches using the persistent browser maintained by browser_service.py.

Usage:
    python search_jobs.py "keywords" [location] [output_file]
    
Example:
    python search_jobs.py "Python Developer" "United States"
    python search_jobs.py "Data Scientist" "New York" output.json
"""
import logging
import sys
import json
import time
import argparse
from pathlib import Path
from linkedin_scraper.config import Config
from linkedin_scraper.browser_manager import BrowserManager
from linkedin_scraper.job_search import JobSearch
from linkedin_scraper.security import SecurityManager

# Setup logging
log_dir = Path(__file__).parent / 'logs'
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'job_search.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Service files
SERVICE_DIR = Path(__file__).parent
STATUS_FILE = SERVICE_DIR / 'browser_service_status.json'

# Security manager for rate limiting
security_manager = SecurityManager()


def is_browser_service_running():
    """Check if browser service is running by reading status file."""
    try:
        if not STATUS_FILE.exists():
            return False
        
        with open(STATUS_FILE, 'r') as f:
            status = json.load(f)
        
        return status.get('running', False) and status.get('browser_alive', False)
    
    except Exception as e:
        logger.warning(f"Failed to check service status: {str(e)}")
        return False


def wait_for_service(max_wait=5):
    """Wait for browser service to be ready."""
    logger.info("Checking if browser service is running...")
    
    for i in range(max_wait):
        if is_browser_service_running():
            logger.info("✓ Browser service is running and ready")
            return True
        
        if i < max_wait - 1:
            time.sleep(1)
            logger.info(f"Waiting for browser service... ({i+1}/{max_wait})")
    
    return False


def search_jobs_standalone(keywords, location=None, num_results=None):
    """
    Search for jobs using the shared browser instance.
    
    Args:
        keywords (str): Job search keywords
        location (str, optional): Job location filter
        num_results (int, optional): Number of results (ignored - loads all available)
    
    Returns:
        dict: Dictionary mapping job_id to job_link
    """
    try:
        logger.info(f"Searching for jobs: '{keywords}'" + (f" in {location}" if location else ""))
        
        # Rate limit to prevent account flagging
        security_manager.rate_limit_search()
        
        # Check if browser service is running
        service_running = wait_for_service()
        if not service_running:
            logger.warning("Browser service status file indicates it's not running.")
            logger.warning("This might be OK if browser service was suspended (Ctrl+Z)")
            logger.warning("Will attempt to connect to existing browser anyway...")
        
        # Validate configuration
        Config.validate()
        
        # Get browser instance from browser manager
        # This will reuse the existing browser from the service, or create new one if needed
        # try_remote_connection=True allows connecting to browser service
        browser_manager = BrowserManager()
        driver = browser_manager.get_or_create_browser(try_remote_connection=True)
        
        # Verify we can access the browser
        if not browser_manager.is_browser_alive():
            logger.error("Browser instance is not accessible")
            return {}
        
        logger.info("✓ Connected to browser service and ready for job search")
        
        # Perform job search and extract jobs
        # Using optimized direct URL navigation - login handled automatically by job_search if required
        # This minimizes login attempts by only logging in when LinkedIn requires it
        job_search = JobSearch(driver)
        jobs_ids = job_search.search_jobs(keywords, location, num_results or 0)
        if not jobs_ids:
            logger.error("Job search failed - no jobs found")
            return {}
        
        # Extract job data using the same JobSearch instance
        # This ensures extraction uses the same detection methods as search
        jobs_data = job_search.extract_jobs(jobs_ids)
        
        logger.info(f"✓ Successfully extracted {len(jobs_data)} jobs: {jobs_data}")
        return jobs_data
    
    except Exception as e:
        logger.error(f"Error during job search: {str(e)}", exc_info=True)
        return {}


def main():
    """Main function with command-line interface."""
    parser = argparse.ArgumentParser(
        description='Search LinkedIn jobs using the browser service',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python search_jobs.py "Python Developer"
  python search_jobs.py "Data Scientist" "New York"
  python search_jobs.py "Software Engineer" "United States" output.json
        """
    )
    
    parser.add_argument('keywords', help='Job search keywords')
    parser.add_argument('location', nargs='?', default=None, help='Job location filter (optional)')
    parser.add_argument('output', nargs='?', default='jobs_output.json', 
                       help='Output JSON file (default: jobs_output.json)')
    
    args = parser.parse_args()
    
    logger.info("="*60)
    logger.info("LinkedIn Job Search Service")
    logger.info("="*60)
    
    # Perform search
    results = search_jobs_standalone(args.keywords, args.location)
    
    if results:
        # Save results to file
        output_file = Path(args.output)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✓ Results saved to: {output_file}")
        
        # Print summary
        print("\n" + "="*60)
        print(f"Found {len(results)} jobs")
        print("="*60)
        print(f"Results saved to: {output_file}")
        print("="*60)
    else:
        logger.warning("No jobs found or search failed")
        print("No jobs found or search failed")
        sys.exit(1)
    return results


if __name__ == "__main__":
    main()

