"""
Main entry point for LinkedIn Job Scraper.
Orchestrates all modules to search and extract job listings.
"""
import logging
import sys
import json
from pathlib import Path
from linkedin_scraper.config import Config
from linkedin_scraper.browser_manager import BrowserManager
from linkedin_scraper.linkedin_auth import LinkedInAuth
from linkedin_scraper.job_search import JobSearch
from linkedin_scraper.job_extractor import JobExtractor

# Setup logging
log_dir = Path(__file__).parent / 'logs'
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'linkedin_scraper.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Add project to Python path
sys.path.insert(0, str(Path(__file__).parent))


def scrape_linkedin_jobs(keywords, location=None, num_results=25):
    """
    Main function to scrape LinkedIn jobs.
    
    Args:
        keywords (str): Job search keywords
        location (str, optional): Job location filter
        num_results (int, optional): Number of results to extract (default: 25)
    
    Returns:
        dict: Dictionary mapping job_id to job_link
              Format: {job_id: job_link}
    """
    try:
        # Validate configuration
        logger.info("Validating configuration...")
        Config.validate()
        
        # Create browser manager
        browser_manager = BrowserManager()
        
        # Get or create browser instance (maintains persistence)
        driver = browser_manager.get_or_create_browser()
        
        # Authenticate
        auth = LinkedInAuth(driver)
        
        # Check if already logged in
        if not auth.is_logged_in():
            logger.info("Not logged in, attempting login...")
            # Attempt login with manual verification enabled
            # Set manual_verification=False to disable manual verification prompt
            login_success = auth.login(manual_verification=True)
            if not login_success:
                logger.error("Login failed. Exiting.")
                logger.info("Tip: If CAPTCHA/verification was required, check if HEADLESS_MODE=False in .env")
                return {}
        else:
            logger.info("Already authenticated")
        
        # Search for jobs
        job_search = JobSearch(driver)
        if not job_search.search_jobs(keywords, location, num_results):
            logger.error("Job search failed. Exiting.")
            return {}
        
        # Extract job data
        job_extractor = JobExtractor(driver)
        jobs_data = job_extractor.extract_jobs()
        
        logger.info(f"Successfully extracted {len(jobs_data)} jobs")
        return jobs_data
    
    except Exception as e:
        logger.error(f"Error during job scraping: {str(e)}", exc_info=True)
        return {}


def main():
    """Main function to run the scraper with example parameters."""
    logger.info("Starting LinkedIn Job Scraper")
    
    # Example search parameters
    keywords = "Python Developer"
    location = "United States"
    num_results = 25
    
    # Scrape jobs
    results = scrape_linkedin_jobs(keywords, location, num_results)
    
    if results:
        # Print results
        print("\n" + "="*60)
        print(f"Found {len(results)} jobs:")
        print("="*60)
        for job_id, job_link in results.items():
            print(f"Job ID: {job_id}")
            print(f"Link: {job_link}")
            print("-" * 60)
        
        # Save to JSON file
        output_file = Path(__file__).parent / 'jobs_output.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Results saved to {output_file}")
        print(f"\nResults saved to: {output_file}")
    else:
        print("No jobs found or error occurred")
        logger.warning("No jobs extracted")
    
    logger.info("Job scraping completed")
    logger.info("Note: Browser instance remains open to maintain session")
    logger.info("Next script run will reuse the existing browser instance")
    logger.info("To close browser manually, use: browser_manager.close_browser(force=True)")


if __name__ == "__main__":
    main()

