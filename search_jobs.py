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
from geo_id import get_geo_id, get_geo_ids

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


def search_jobs_single(keywords, geo_id, driver, job_search, num_results=None, filters=None, location_name=None):
    """
    Perform a single job search with given keywords and geo-id.
    
    Args:
        keywords (str): Job search keywords
        geo_id (str): LinkedIn geo-id for location (numeric string)
        driver: Selenium WebDriver instance
        job_search: JobSearch instance
        num_results (int, optional): Number of results (ignored - loads all available)
        filters (dict, optional): Dictionary of filter parameters to pass to search_jobs()
        location_name (str, optional): Location name for logging purposes
    
    Returns:
        dict: Dictionary mapping job_id to job_link
    """
    try:
        # Prepare location display for logging
        if location_name:
            location_display = location_name
            geo_id_display = f" (geo-id: {geo_id})" if geo_id else ""
        elif geo_id:
            location_display = f"geo-id:{geo_id}"
            geo_id_display = ""
        else:
            location_display = "No location"
            geo_id_display = ""
        
        logger.info(f"Searching for jobs: '{keywords}' in {location_display}{geo_id_display}")
        
        # Rate limit to prevent account flagging
        security_manager.rate_limit_search()
        
        # Prepare filter parameters (default to empty dict if not provided)
        filter_params = filters.copy() if filters else {}
        
        # Ensure geo_id is in filters (prioritize geo_id over location)
        # Only add geo_id if it's not None
        if geo_id is not None:
            filter_params['geo_id'] = geo_id
        # Remove location parameter if present, as we're using geo_id instead
        if 'location' in filter_params:
            del filter_params['location']
        
        # Perform job search and extract jobs
        # Using optimized direct URL navigation - login handled automatically by job_search if required
        # This minimizes login attempts by only logging in when LinkedIn requires it
        # Pass location=None to ensure we only use geo_id in URL
        jobs_ids = job_search.search_jobs(
            keywords, 
            location=None,  # Don't use location parameter, use geo_id in filters instead
            num_results=num_results or 0,
            **filter_params
        )
        if not jobs_ids:
            logger.warning(f"No jobs found for '{keywords}' in {location_display}{geo_id_display}")
            return {}
        
        # Extract job data using the same JobSearch instance
        # This ensures extraction uses the same detection methods as search
        jobs_data = job_search.extract_jobs(jobs_ids)
        
        logger.info(f"✓ Found {len(jobs_data)} jobs for '{keywords}' in {location_display}{geo_id_display}")
        return jobs_data
    
    except Exception as e:
        location_display = location_name or (f"geo-id:{geo_id}" if geo_id else "No location")
        logger.error(f"Error during job search for '{keywords}' in {location_display}: {str(e)}", exc_info=True)
        return {}


def search_jobs_standalone(keywords, locations=None, num_results=None, filters=None):
    """
    Search for jobs using the shared browser instance.
    Supports both single and multiple keywords/locations.
    Locations are converted to geo-ids and applied through URL parameters.
    
    Args:
        keywords (str or list): Job search keywords (single string or list of strings)
        locations (str or list, optional): Job location filter (single string or list of strings, or geo-ids)
        num_results (int, optional): Number of results (ignored - loads all available)
        filters (dict, optional): Dictionary of filter parameters to pass to search_jobs()
    
    Returns:
        dict: Dictionary mapping job_id to job_link (combined results from all searches)
    """
    try:
        # Normalize inputs to lists
        if isinstance(keywords, str):
            keywords_list = [keywords]
        else:
            keywords_list = keywords
        
        # Convert locations to geo-ids
        if locations is None:
            geo_ids_list = [None]
            location_names_map = {None: "No location"}
        else:
            # Get geo-ids from locations (handles both location names and numeric geo-ids)
            if isinstance(locations, str):
                locations_list = [locations]
            else:
                locations_list = locations
            
            # Convert locations to geo-ids and create mapping
            geo_ids_list = []
            location_names_map = {}
            
            for loc in locations_list:
                if not loc:
                    continue
                    
                loc = loc.strip()
                
                # Check if it's already a numeric geo-id
                if loc.isdigit():
                    geo_id = loc
                    geo_ids_list.append(geo_id)
                    location_names_map[geo_id] = f"geo-id:{geo_id}"
                else:
                    # Try to get geo-id from location name
                    geo_id = get_geo_id(loc)
                    if geo_id:
                        if geo_id not in geo_ids_list:
                            geo_ids_list.append(geo_id)
                        location_names_map[geo_id] = loc
                    else:
                        # Location not found, log warning but skip it
                        logger.warning(f"Location '{loc}' not found in geo-id map and is not a numeric geo-id. Skipping.")
        
        # If no geo-ids found, use None (search without location filter)
        if not geo_ids_list:
            geo_ids_list = [None]
            location_names_map = {None: "No location"}
        
        # Get browser instance once (reused for all searches)
        browser_manager, driver = get_browser_instance()
        if not driver:
            logger.error("Failed to get browser instance")
            return {}
        
        # Create JobSearch instance once (reused for all searches)
        job_search = JobSearch(driver)
        
        # Accumulate all results
        all_jobs = {}
        total_searches = len(keywords_list) * len(geo_ids_list)
        search_count = 0
        
        logger.info(f"Starting job search: {len(keywords_list)} keyword(s) × {len(geo_ids_list)} location(s) = {total_searches} search(es)")
        
        # Iterate through each geo-id (location), then each keyword
        # This ensures for every location, each job title is searched
        for geo_id in geo_ids_list:
            location_name = location_names_map.get(geo_id)
            
            for keyword in keywords_list:
                search_count += 1
                # Perform single search with geo_id in filters
                jobs_data = search_jobs_single(keyword, geo_id, driver, job_search, num_results, filters, location_name)
                
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
  # Basic search
  python search_jobs.py "Python Developer"
  python search_jobs.py "Data Scientist" "New York"
  
  # With filters
  python search_jobs.py "Software Engineer" --location "United States" --jobtype F --worktype 2,3 --experience 4,5
  python search_jobs.py "Developer" --location "New York" --time-filter week --easy-apply --sort-by DD
  
  # Multiple keywords/locations
  python search_jobs.py --keywords "Python Developer,Data Scientist" --locations "United States,New York"
  python search_jobs.py --keywords "Python,Java" --locations "New York,San Francisco" output.json
  
  # Advanced filters
  python search_jobs.py "Manager" --location "United States" --jobtype F --experience 5,6 --job-function mgmt --industry 96,4
        """
    )
    
    # Support both positional and named arguments for backward compatibility
    parser.add_argument('keywords', nargs='?', help='Job search keywords (single or comma-separated)')
    parser.add_argument('location', nargs='?', default=None, help='Job location filter (single or comma-separated, optional)')
    parser.add_argument('output', nargs='?', default='jobs_output.json', 
                       help='Output JSON file (default: jobs_output.json)')
    
    # Named arguments for multiple keywords/locations
    parser.add_argument('--keywords', dest='keywords_list', help='Comma-separated list of job search keywords')
    parser.add_argument('--locations', dest='locations_list', help='Comma-separated list of job locations (will be converted to geo-ids automatically, or can be geo-ids directly)')
    parser.add_argument('--location', dest='location_named', help='Job location filter (alternative to positional, will be converted to geo-id automatically)')
    
    # Core search parameters
    parser.add_argument('--geo-id', dest='geo_id', help='LinkedIn geo ID for location (numeric string, can be comma-separated for multiple locations). Takes precedence over --location/--locations. Locations are applied through URL parameters.')
    parser.add_argument('--distance', type=int, help='Search radius in miles/km from location (default: 120)')
    parser.add_argument('--time-filter', dest='time_filter', 
                       choices=['any', '1hour', '2hours', '3hours', '4hours', '6hours', '8hours', '12hours', '1day', 'week', 'month'],
                       help='Time filter for job posting date')
    
    # Job type filters (f_JT)
    parser.add_argument('--jobtype', '--job-type', dest='job_types',
                       help='Job type filters: F (Full-time), P (Part-time), C (Contract), T (Temporary), I (Internship), V (Volunteer). Can be comma-separated like "F,C"')
    
    # Experience level filters (f_E)
    parser.add_argument('--experience', '--experience-level', dest='experience_levels',
                       help='Experience level filters: 1 (Internship), 2 (Entry), 3 (Associate), 4 (Mid-Senior), 5 (Director), 6 (Executive). Can be comma-separated like "4,5"')
    
    # Work type filters (f_WT)
    parser.add_argument('--worktype', '--work-type', dest='work_types',
                       help='Work type filters: 1 (On-site), 2 (Hybrid), 3 (Remote). Can be comma-separated like "2,3"')
    
    # Specialized filters
    parser.add_argument('--easy-apply', dest='easy_apply', action='store_true',
                       help='Filter for Easy Apply jobs only')
    parser.add_argument('--no-easy-apply', dest='easy_apply', action='store_false',
                       help='Include all jobs (not just Easy Apply)')
    parser.add_argument('--actively-hiring', dest='actively_hiring', action='store_true',
                       help='Filter for companies actively hiring')
    parser.add_argument('--no-actively-hiring', dest='actively_hiring', action='store_false',
                       help='Include all companies (not just actively hiring)')
    parser.add_argument('--verified-jobs', dest='verified_jobs', action='store_true',
                       help='Filter for verified job postings only')
    parser.add_argument('--no-verified-jobs', dest='verified_jobs', action='store_false',
                       help='Include all job postings (not just verified)')
    parser.add_argument('--jobs-at-connections', dest='jobs_at_connections', action='store_true',
                       help='Filter for jobs at companies where you have connections')
    parser.add_argument('--no-jobs-at-connections', dest='jobs_at_connections', action='store_false',
                       help='Include all jobs (not just at connections)')
    
    # Job function and industry filters
    parser.add_argument('--job-function', dest='job_function',
                       help='Job function filters: sale, mgmt, acct, it, mktg, hr. Can be comma-separated like "it,mktg"')
    parser.add_argument('--industry', 
                       help='Industry filter codes (numeric strings). Can be comma-separated like "96,4". See LinkedIn documentation for codes.')
    
    # Sorting
    parser.add_argument('--sort-by', dest='sort_by', choices=['DD', 'R'],
                       help='Sort option: DD (Date Descending/newest first), R (Relevance/default)')
    
    # Advanced filters
    parser.add_argument('--city-id', dest='city_id',
                       help='Filter by specific city ID (numeric string)')
    parser.add_argument('--company-id', dest='company_id',
                       help='Filter by specific company ID (numeric string)')
    
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
    
    # Parse locations (support both positional and --location)
    # Note: Locations are converted to geo-ids automatically
    # If --geo-id is provided, it takes precedence and locations are ignored
    location_value = args.location_named or args.location
    if args.geo_id:
        # If --geo-id is provided directly, use it and ignore location arguments
        # Support comma-separated geo-ids
        if ',' in args.geo_id:
            locations = [gid.strip() for gid in args.geo_id.split(',')]
        else:
            locations = [args.geo_id.strip()]
        logger.info(f"Using geo-ids directly: {locations}")
    elif args.locations_list:
        # Use --locations if provided (will be converted to geo-ids)
        locations = [l.strip() for l in args.locations_list.split(',')]
    elif location_value:
        # Use positional or --location (will be converted to geo-ids)
        if ',' in location_value:
            locations = [l.strip() for l in location_value.split(',')]
        else:
            locations = [location_value]
    else:
        locations = [None]
    
    logger.info(f"Keywords: {keywords}")
    logger.info(f"Locations/Geo-ids: {locations}")
    
    # Build filters dictionary (exclude geo_id from filters as it's handled separately)
    filters = {}
    if args.distance:
        filters['distance'] = args.distance
    if args.time_filter:
        filters['time_filter'] = args.time_filter
    if args.job_types:
        filters['job_types'] = args.job_types
    if args.experience_levels:
        filters['experience_levels'] = args.experience_levels
    if args.work_types:
        filters['work_types'] = args.work_types
    if args.easy_apply is not None:
        filters['easy_apply'] = args.easy_apply
    if args.actively_hiring is not None:
        filters['actively_hiring'] = args.actively_hiring
    if args.verified_jobs is not None:
        filters['verified_jobs'] = args.verified_jobs
    if args.jobs_at_connections is not None:
        filters['jobs_at_connections'] = args.jobs_at_connections
    if args.job_function:
        filters['job_function'] = args.job_function
    if args.industry:
        filters['industry'] = args.industry
    if args.sort_by:
        filters['sort_by'] = args.sort_by
    if args.city_id:
        filters['city_id'] = args.city_id
    if args.company_id:
        filters['company_id'] = args.company_id
    
    if filters:
        logger.info(f"Applied filters: {filters}")
    
    # Perform search
    results = search_jobs_standalone(keywords, locations, filters=filters)
    
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

