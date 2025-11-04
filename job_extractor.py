"""
Job description extractor with stealth mode support.
Extracts job description and job ID from LinkedIn job pages.
Handles job not found errors gracefully.
Uses BrowserManager to reuse existing browser instance configured via .env
"""
import logging
import time
import re
from pathlib import Path
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException, WebDriverException
from linkedin_scraper.config import Config
from linkedin_scraper.browser_manager import BrowserManager
from linkedin_scraper.security import SecurityManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class JobExtractor:
    """Extracts job descriptions and job IDs from LinkedIn job pages."""
    
    def __init__(self, driver=None, try_remote_connection=True):
        """
        Initialize JobExtractor with WebDriver instance.
        
        Args:
            driver: Optional Selenium WebDriver instance. If None, uses BrowserManager to get/create browser.
            try_remote_connection (bool): If True, tries to connect to existing browser service (default: True)
        """
        self.driver = driver
        self.try_remote_connection = try_remote_connection
        self.browser_manager = None
        # browser_created is False if using BrowserManager (shared instance)
        # True only if we manually create and manage a browser (not used anymore)
        self.browser_created = False
    
    def _get_browser_instance(self):
        """
        Get browser instance using BrowserManager (respects .env configuration).
        Tries to connect to existing browser service, or creates new one if needed.
        
        Returns:
            webdriver.Chrome: Configured Chrome WebDriver instance from BrowserManager
        """
        try:
            logger.info("Getting browser instance from BrowserManager...")
            
            # Validate configuration
            Config.validate()
            
            # Create browser manager instance
            self.browser_manager = BrowserManager()
            
            # Get or create browser instance
            # This will use existing browser from browser_service if available,
            # or create new one with .env configuration (stealth mode, paths, etc.)
            driver = self.browser_manager.get_or_create_browser(
                try_remote_connection=self.try_remote_connection
            )
            
            # Verify browser is accessible
            if not self.browser_manager.is_browser_alive():
                logger.error("Browser instance is not accessible")
                raise RuntimeError("Browser instance is not accessible")
            
            logger.info("✓ Browser instance obtained from BrowserManager")
            logger.info(f"Using Chrome binary: {Config.CHROME_BINARY_PATH or 'System default'}")
            logger.info(f"Using ChromeDriver: {Config.CHROMEDRIVER_PATH}")
            logger.info(f"Headless mode: {Config.HEADLESS_MODE}")
            
            return driver
            
        except Exception as e:
            logger.error(f"Failed to get browser instance: {str(e)}")
            raise
    
    def _extract_job_id(self, url=None):
        """
        Extract job ID from URL or page.
        
        Args:
            url (str, optional): Job URL. If None, uses current page URL.
        
        Returns:
            str: Job ID if found, None otherwise
        """
        try:
            # Method 1: Extract from URL
            if url:
                match = re.search(r'/jobs/view/(\d+)', url)
                if match:
                    job_id = match.group(1)
                    logger.debug(f"Extracted job ID from URL: {job_id}")
                    return job_id
            
            # Method 2: Extract from current page URL
            current_url = self.driver.current_url
            match = re.search(r'/jobs/view/(\d+)', current_url)
            if match:
                job_id = match.group(1)
                logger.debug(f"Extracted job ID from current URL: {job_id}")
                return job_id
            
            # Method 3: Extract from page data attributes using JavaScript
            try:
                job_id = self.driver.execute_script("""
                    // Try to find job ID in data attributes
                    var jobId = null;
                    
                    // Check for data-job-id attribute
                    var jobElement = document.querySelector('[data-job-id]');
                    if (jobElement) {
                        jobId = jobElement.getAttribute('data-job-id');
                    }
                    
                    // Check for job ID in meta tags
                    if (!jobId) {
                        var metaTag = document.querySelector('meta[property="og:url"]');
                        if (metaTag) {
                            var url = metaTag.getAttribute('content');
                            var match = url.match(/\\/jobs\\/view\\/(\\d+)/);
                            if (match) {
                                jobId = match[1];
                            }
                        }
                    }
                    
                    return jobId;
                """)
                
                if job_id:
                    logger.debug(f"Extracted job ID from page: {job_id}")
                    return job_id
            except Exception as e:
                logger.debug(f"JavaScript extraction failed: {str(e)}")
            
            logger.warning("Could not extract job ID from URL or page")
            return None
            
        except Exception as e:
            logger.error(f"Error extracting job ID: {str(e)}")
            return None
    
    def _is_job_not_found(self):
        """
        Check if the job page indicates job not found or no longer exists.
        
        Returns:
            bool: True if job not found, False otherwise
        """
        try:
            current_url = self.driver.current_url.lower()
            
            # Check 1: URL indicates error page
            if "404" in current_url or "not-found" in current_url or "error" in current_url:
                logger.warning("Job not found: URL indicates error page")
                return True
            
            # Check 2: Page title indicates job not found
            page_title = self.driver.title.lower()
            if "not found" in page_title or "404" in page_title or "error" in page_title:
                logger.warning("Job not found: Page title indicates error")
                return True
            
            # Check 3: Check for common "not found" messages in page source
            page_source = self.driver.page_source.lower()
            not_found_indicators = [
                "this job is no longer accepting applications",
                "this job posting is no longer available",
                "job not found",
                "this job is no longer available",
                "the job you're looking for doesn't exist",
                "page not found"
            ]
            
            for indicator in not_found_indicators:
                if indicator in page_source:
                    logger.warning(f"Job not found: Found indicator '{indicator}'")
                    return True
            
            # Check 4: Check if job description container exists
            # If job description doesn't exist, job might not be found
            try:
                has_description = self.driver.execute_script("""
                    return document.querySelector('section.show-more-less-html') !== null ||
                           document.querySelector('.jobs-description__container') !== null ||
                           document.querySelector('[data-job-id]') !== null;
                """)
                
                if not has_description:
                    # Additional check: might be loading or might not exist
                    time.sleep(2)  # Wait a bit more
                    has_description = self.driver.execute_script("""
                        return document.querySelector('section.show-more-less-html') !== null ||
                               document.querySelector('.jobs-description__container') !== null;
                    """)
                    
                    if not has_description:
                        logger.warning("Job not found: Job description container not found")
                        return True
            except Exception as e:
                logger.debug(f"Error checking job description: {str(e)}")
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking if job not found: {str(e)}")
            # On error, assume job might exist (don't fail prematurely)
            return False
    
    def extract_job_details(self, url):
        """
        Extract job description and job ID from LinkedIn job page.
        
        Args:
            url (str): LinkedIn job URL (e.g., 'https://www.linkedin.com/jobs/view/4236473183')
        
        Returns:
            dict: Dictionary containing:
                - 'job_id' (str): Job ID if found
                - 'job_description' (str): HTML of job description if found
                - 'success' (bool): True if extraction successful
                - 'error' (str): Error message if failed
        """
        result = {
            'job_id': None,
            'job_description': None,
            'success': False,
            'error': None
        }
        
        try:
            # Get browser instance if not provided
            # Uses BrowserManager which respects .env configuration
            if not self.driver:
                self.driver = self._get_browser_instance()
            
            logger.info(f"Extracting job details from: {url}")
            
            # Navigate to job page
            self.driver.get(url)
            
            # Add human-like delay
            SecurityManager.random_delay(2, 4)
            
            # Check if job not found
            if self._is_job_not_found():
                result['error'] = "Job not found or no longer exists"
                result['success'] = False
                logger.error(f"Job not found: {url}")
                return result
            
            # Extract job ID
            job_id = self._extract_job_id(url)
            result['job_id'] = job_id
            
            if job_id:
                logger.info(f"✓ Extracted job ID: {job_id}")
            else:
                logger.warning("Could not extract job ID")
            
            # Wait for dynamic content to load
            time.sleep(2)
            
            # Get page source
            html = self.driver.page_source
            
            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find job description container
            # Try multiple selectors as LinkedIn may use different structures
            job_description = None
            
            # Method 1: section with class 'show-more-less-html'
            job_description = soup.find('section', class_='show-more-less-html')
            
            # Method 2: article with class 'jobs-description__container'
            if not job_description:
                job_description = soup.find('article', class_='jobs-description__container')
            
            # Method 3: div with job description content
            if not job_description:
                job_description = soup.find('div', {'class': re.compile(r'.*description.*', re.I)})
            
            if job_description:
                result['job_description'] = str(job_description)
                result['success'] = True
                logger.info("✓ Job description extracted successfully")
            else:
                result['error'] = "Job description container not found on page"
                result['success'] = False
                logger.warning("Job description container not found")
            
            return result
            
        except TimeoutException as e:
            result['error'] = f"Timeout waiting for page to load: {str(e)}"
            result['success'] = False
            logger.error(f"Timeout error: {str(e)}")
            return result
        except WebDriverException as e:
            result['error'] = f"Browser error: {str(e)}"
            result['success'] = False
            logger.error(f"Browser error: {str(e)}")
            return result
        except Exception as e:
            result['error'] = f"Unexpected error: {str(e)}"
            result['success'] = False
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return result
    
    def save_job_description(self, url, output_file='job_description.html'):
        """
        Save job description to HTML file.
        
        Args:
            url (str): LinkedIn job URL
            output_file (str): Output file path (default: 'job_description.html')
        
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            result = self.extract_job_details(url)
            
            if not result['success']:
                logger.error(f"Failed to extract job details: {result.get('error', 'Unknown error')}")
                return False
            
            if not result['job_description']:
                logger.error("No job description found to save")
                return False
            
            # Save to file
            output_path = Path(output_file)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result['job_description'])
            
            logger.info(f"✓ Job description saved to: {output_path}")
            
            if result['job_id']:
                logger.info(f"✓ Job ID: {result['job_id']}")
            
            print(f'Job description saved to {output_path}')
            if result['job_id']:
                print(f'Job ID: {result["job_id"]}')
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving job description: {str(e)}")
            return False
    
    def close(self):
        """
        Close browser instance if it was provided externally.
        Note: If browser was obtained from BrowserManager (shared instance),
        it will NOT be closed to maintain persistence for other services.
        """
        # Only close if driver was provided externally (not from BrowserManager)
        # BrowserManager maintains shared instances, so we don't close those
        if self.driver and not self.browser_manager:
            # Driver was provided externally, but we shouldn't close it
            # as it might be managed by another component
            logger.debug("Driver was provided externally - not closing (may be managed elsewhere)")
        elif self.browser_manager:
            # Browser is managed by BrowserManager - don't close it
            logger.debug("Browser is managed by BrowserManager - not closing (maintains persistence)")
        # If no driver, nothing to close
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - closes browser."""
        self.close()


def main():
    """Main function for command-line usage."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python job_extractor.py <job_url> [output_file]")
        print("Example: python job_extractor.py 'https://www.linkedin.com/jobs/view/4236473183'")
        sys.exit(1)
    
    url = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'job_description.html'
    
    # Use context manager for automatic cleanup
    with JobExtractor() as extractor:
        success = extractor.save_job_description(url, output_file)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
