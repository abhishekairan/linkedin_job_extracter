"""
Job description extractor with stealth mode support.
Extracts job description and job ID from LinkedIn job pages.
Handles job not found errors gracefully.
"""
import logging
import time
import re
from pathlib import Path
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException
from linkedin_scraper.config import Config
from linkedin_scraper.security import SecurityManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class JobExtractor:
    """Extracts job descriptions and job IDs from LinkedIn job pages."""
    
    def __init__(self, driver=None):
        """
        Initialize JobExtractor with WebDriver instance.
        
        Args:
            driver: Optional Selenium WebDriver instance. If None, creates new stealth browser.
        """
        self.driver = driver
        self.browser_created = driver is None
    
    def _create_stealth_browser(self):
        """
        Create a Chrome browser instance with stealth options.
        
        Returns:
            webdriver.Chrome: Configured Chrome WebDriver instance
        """
        try:
            logger.info("Creating stealth browser instance...")
            
            # Load configuration
            Config.validate()
            
            # Create Chrome options with stealth settings
            options = Options()
            
            # Set binary location if configured
            if Config.CHROME_BINARY_PATH:
                options.binary_location = Config.CHROME_BINARY_PATH
            
            # Required arguments for stability
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu-sandbox')
            options.add_argument('--disable-setuid-sandbox')
            
            # Stealth and anti-detection options
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--start-maximized')
            options.add_argument('--disable-default-apps')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-sync')
            options.add_argument('--disable-translate')
            options.add_argument('--no-first-run')
            options.add_argument('--password-store=basic')
            
            # Set random realistic user agent
            user_agent = SecurityManager.get_random_user_agent()
            options.add_argument(f'user-agent={user_agent}')
            
            # Headless mode if configured
            if Config.HEADLESS_MODE:
                options.add_argument('--headless')
                options.add_argument('--headless=new')
                options.add_argument('--disable-gpu')
            
            # Create service
            service = Service(Config.CHROMEDRIVER_PATH)
            
            # Create WebDriver
            driver = webdriver.Chrome(service=service, options=options)
            driver.implicitly_wait(Config.IMPLICIT_WAIT)
            
            # Inject stealth scripts
            try:
                SecurityManager.inject_stealth_scripts(driver)
                logger.info("✓ Stealth scripts injected successfully")
            except Exception as e:
                logger.warning(f"Failed to inject some stealth scripts: {str(e)}")
            
            logger.info("✓ Stealth browser created successfully")
            return driver
            
        except Exception as e:
            logger.error(f"Failed to create stealth browser: {str(e)}")
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
            # Create browser if not provided
            if not self.driver:
                self.driver = self._create_stealth_browser()
            
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
        """Close browser instance if it was created by this extractor."""
        if self.browser_created and self.driver:
            try:
                self.driver.quit()
                logger.info("Browser closed")
            except Exception as e:
                logger.warning(f"Error closing browser: {str(e)}")
    
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
