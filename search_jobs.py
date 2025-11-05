"""
Standalone job search service that connects to the browser service.
This script performs job searches using the persistent browser maintained by browser_service.py.

Usage:
    python search_jobs.py "keywords" [location] [output_file]
    python search_jobs.py --keywords "keyword1,keyword2" --locations "location1,location2" [output_file]
    
Example:
    python search_jobs.py "Python Developer" "United States"
    python search_jobs.py "Data Scientist" "New York" output.json
    python search_jobs.py --keywords "Python Developer,Data Scientist" --locations "United States,New York"
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


def get_browser_instance():
    """
    Get or create browser instance. This should be called once at the start.
    
    Returns:
        tuple: (browser_manager, driver) or (None, None) if failed
    """
    try:
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
            return None, None
        
        logger.info("✓ Connected to browser service and ready for job search")
        return browser_manager, driver
    
    except Exception as e:
        logger.error(f"Error getting browser instance: {str(e)}", exc_info=True)
        return None, None


def search_jobs_single(keywords, location, driver, job_search, num_results=None):
    """
    Perform a single job search with given keywords and location.
    
    Args:
        keywords (str): Job search keywords
        location (str): Job location filter
        driver: Selenium WebDriver instance
        job_search: JobSearch instance
        num_results (int, optional): Number of results (ignored - loads all available)
    
    Returns:
        dict: Dictionary mapping job_id to job_link
    """
    try:
        logger.info(f"Searching for jobs: '{keywords}' in {location}")
        
        # Rate limit to prevent account flagging
        security_manager.rate_limit_search()
        
        # Perform job search and extract jobs
        # Using optimized direct URL navigation - login handled automatically by job_search if required
        # This minimizes login attempts by only logging in when LinkedIn requires it
        jobs_ids = job_search.search_jobs(keywords, location, num_results or 0, time_filter='3hours')
        if not jobs_ids:
            logger.warning(f"No jobs found for '{keywords}' in {location}")
            return {}
        
        # Extract job data using the same JobSearch instance
        # This ensures extraction uses the same detection methods as search
        jobs_data = job_search.extract_jobs(jobs_ids)
        
        logger.info(f"✓ Found {len(jobs_data)} jobs for '{keywords}' in {location}")
        return jobs_data
    
    except Exception as e:
        logger.error(f"Error during job search for '{keywords}' in {location}: {str(e)}", exc_info=True)
        return {}


def search_jobs_standalone(keywords, locations=None, num_results=None):
    """
    Search for jobs using the shared browser instance.
    Supports both single and multiple keywords/locations.
    
    Args:
        keywords (str or list): Job search keywords (single string or list of strings)
        locations (str or list, optional): Job location filter (single string or list of strings)
        num_results (int, optional): Number of results (ignored - loads all available)
    
    Returns:
        dict: Dictionary mapping job_id to job_link (combined results from all searches)
    """
    try:
        # Normalize inputs to lists
        if isinstance(keywords, str):
            keywords_list = [keywords]
        else:
            keywords_list = keywords
        
        if locations is None:
            locations_list = [None]
        elif isinstance(locations, str):
            locations_list = [locations]
        else:
            locations_list = locations
        
        # Get browser instance once (reused for all searches)
        browser_manager, driver = get_browser_instance()
        if not driver:
            logger.error("Failed to get browser instance")
            return {}
        
        # Create JobSearch instance once (reused for all searches)
        job_search = JobSearch(driver)
        
        # Accumulate all results
        all_jobs = {}
        total_searches = len(keywords_list) * len(locations_list)
        search_count = 0
        
        logger.info(f"Starting job search: {len(keywords_list)} keyword(s) × {len(locations_list)} location(s) = {total_searches} search(es)")
        
        # Iterate through each location, then each keyword
        for location in locations_list:
            for keyword in keywords_list:
                search_count += 1
                logger.info(f"[{search_count}/{total_searches}] Processing: keyword='{keyword}', location='{location or 'None'}'")
                
                # Perform single search
                jobs_data = search_jobs_single(keyword, location, driver, job_search, num_results)
                
                # Merge results (all_jobs dict will automatically deduplicate by job_id)
                all_jobs.update(jobs_data)
        
        logger.info(f"✓ Completed all searches. Total unique jobs found: {len(all_jobs)}")
        return all_jobs
    
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
  python search_jobs.py --keywords "Python Developer,Data Scientist" --locations "United States,New York"
  python search_jobs.py --keywords "Python,Java" --locations "New York,San Francisco" output.json
        """
    )
    
    # Support both positional and named arguments for backward compatibility
    parser.add_argument('keywords', nargs='?', help='Job search keywords (single or comma-separated)')
    parser.add_argument('location', nargs='?', default=None, help='Job location filter (single or comma-separated, optional)')
    parser.add_argument('output', nargs='?', default='jobs_output.json', 
                       help='Output JSON file (default: jobs_output.json)')
    
    # Named arguments for multiple keywords/locations
    parser.add_argument('--keywords', dest='keywords_list', help='Comma-separated list of job search keywords')
    parser.add_argument('--locations', dest='locations_list', help='Comma-separated list of job locations')
    
    args = parser.parse_args()
    
    logger.info("="*60)
    logger.info("LinkedIn Job Search Service")
    logger.info("="*60)
    
    # Parse keywords
    if args.keywords_list:
        # Use --keywords if provided
        keywords = [k.strip() for k in args.keywords_list.split(',')]
    elif args.keywords:
        # Use positional keyword
        if ',' in args.keywords:
            keywords = [k.strip() for k in args.keywords.split(',')]
        else:
            keywords = [args.keywords]
    else:
        logger.error("Keywords are required")
        parser.print_help()
        sys.exit(1)
    
    # Parse locations
    if args.locations_list:
        # Use --locations if provided
        locations = [l.strip() for l in args.locations_list.split(',')]
    elif args.location:
        # Use positional location
        if ',' in args.location:
            locations = [l.strip() for l in args.location.split(',')]
        else:
            locations = [args.location]
    else:
        locations = [None]
    
    logger.info(f"Keywords: {keywords}")
    logger.info(f"Locations: {locations}")
    
    # Perform search
    results = search_jobs_standalone(keywords, locations)
    
    if results:
        # Save results to file
        output_file = Path(args.output)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✓ Results saved to: {output_file}")
        
        # Print summary
        print("\n" + "="*60)
        print(f"Found {len(results)} unique jobs")
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

