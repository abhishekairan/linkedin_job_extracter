"""
Job search module for LinkedIn.
Handles searching and loading job results using direct URL navigation.
Optimized to only login when required by LinkedIn.
"""
import logging
import time
import urllib.parse
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from .linkedin_auth import LinkedInAuth
from .security import SecurityManager

logger = logging.getLogger(__name__)


class JobSearch:
    """Handles LinkedIn job search operations using optimized direct URL navigation."""
    
    # Base jobs search URL
    JOBS_SEARCH_URL = "https://www.linkedin.com/jobs/search-results/"
    JOBS_GUEST_URL = "https://www.linkedin.com/jobs/search"
    
    # Time filter options (LinkedIn uses these for f_TPR parameter)
    TIME_FILTERS = {
        'any': None,  # No filter
        '1hour': 'r3600',  # Last 1 hour
        '2hours': 'r7200',  # Last 2 hours
        '3hours': 'r10800',  # Last 3 hours
        '4hours': 'r14400',  # Last 4 hours
        '6hours': 'r21600',  # Last 6 hours
        '8hours': 'r28800',  # Last 8 hours
        '12hours': 'r43200',  # Last 12 hours
        '1day': 'r86400',  # Last 1 day
        'week': 'r604800',  # Last week
        'month': 'r2592000',  # Last month
    }
    
    def __init__(self, driver):
        """
        Initialize JobSearch with WebDriver instance.
        
        Args:
            driver: Selenium WebDriver instance
        """
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
    
    def _build_search_url(self, keywords, location=None, time_filter=None, geo_id=None, distance=None):
        """
        Build LinkedIn job search URL with query parameters.
        
        Args:
            keywords (str): Job search keywords (required)
            location (str, optional): Job location filter (e.g., "United States", "New York")
            time_filter (str, optional): Time filter - 'any', '1hour', '24hours', 'week', 'month'
            geo_id (str, optional): LinkedIn geo ID for location (numeric string)
            distance (int, optional): Distance in miles/km (default: 120)
        
        Returns:
            str: Complete LinkedIn job search URL
        """
        # Start with base search URL
        params = {}
        
        # Add keywords (required)
        params['keywords'] = keywords
        
        # Add location if provided
        if location:
            params['location'] = location
        
        # Add geo ID if provided (more precise than location string)
        if geo_id:
            params['geoId'] = geo_id
        
        # Add distance (default 120 if not specified)
        if distance:
            params['distance'] = distance
        else:
            params['distance'] = 120
        
        # Add time filter (f_TPR parameter)
        if time_filter and time_filter in self.TIME_FILTERS:
            tpr_value = self.TIME_FILTERS[time_filter]
            if tpr_value:
                params['f_TPR'] = tpr_value
        
        # Build URL with query string
        query_string = urllib.parse.urlencode(params)
        url = f"{self.JOBS_SEARCH_URL}?{query_string}"
        
        logger.debug(f"Built search URL: {url}")
        return url
    
    def _is_login_required(self):
        """
        Check if LinkedIn requires login by examining current URL and page content.
        
        Returns:
            bool: True if login is required, False if guest access is allowed
        """
        try:
            current_url = self.driver.current_url.lower()
            
            # Check 1: If redirected to login page
            if "/uas/login" in current_url or "/login" in current_url:
                logger.info("Login required: Redirected to login page")
                return True
            
            # Check 2: Check for login-related elements on page
            try:
                # Look for "Sign in" button or login form
                sign_in_elements = self.driver.find_elements(By.XPATH, 
                    "//a[contains(@href, '/login')] | //button[contains(text(), 'Sign in')] | //input[@type='password']")
                if sign_in_elements:
                    logger.info("Login required: Found login elements on page")
                    return True
            except Exception:
                pass
            
            # Check 3: Check if page shows "Sign in to view more jobs" message
            try:
                page_text = self.driver.page_source.lower()
                if "sign in to view" in page_text or "sign in" in page_text:
                    # But check if we can actually see job cards (guest access might work)
                    job_cards = self.driver.execute_script("""
                        return Array.from(document.querySelectorAll('[data-job-id]')).length;
                    """)
                    if job_cards == 0:
                        logger.info("Login required: No job cards visible and sign-in prompt detected")
                        return True
            except Exception:
                pass
            
            # Check 4: Try to detect job cards - if we can see them, login not required
            try:
                job_cards = self.driver.execute_script("""
                    return Array.from(document.querySelectorAll('[data-job-id]')).length;
                """)
                if job_cards > 0:
                    logger.info(f"Login not required: Found {job_cards} job cards (guest access working)")
                    return False
            except Exception:
                pass
            
            # Default: Assume login required if we can't determine
            logger.warning("Could not determine login requirement, assuming login required")
            return True
            
        except Exception as e:
            logger.warning(f"Error checking login requirement: {str(e)}")
            # On error, assume login required for safety
            return True
    
    def search_jobs(self, keywords, location=None, num_results=25, time_filter=None, geo_id=None, distance=None):
        """
        Search for jobs on LinkedIn using optimized direct URL navigation.
        
        Process:
        1. Build search URL with parameters
        2. Navigate directly to search URL
        3. Check if login is required
        4. Login only if required
        5. Find and extract job IDs
        
        Args:
            keywords (str): Job search keywords (required)
            location (str, optional): Job location filter (e.g., "United States", "New York")
            num_results (int, optional): Number of results to load (default: 25, ignored - loads all)
            time_filter (str, optional): Time filter - 'any', '1hour', '24hours', 'week', 'month'
            geo_id (str, optional): LinkedIn geo ID for location (numeric string)
            distance (int, optional): Distance in miles/km (default: 120)
        
        Returns:
            list: List of job IDs found, or empty list if search failed
        """
        try:
            logger.info(f"Starting job search with keywords: '{keywords}'")
            if location:
                logger.info(f"Location filter: {location}")
            if time_filter:
                logger.info(f"Time filter: {time_filter}")
            
            # Step 1: Build search URL directly
            search_url = self._build_search_url(keywords, location, time_filter, geo_id, distance)
            logger.info(f"Navigating directly to search URL: {search_url}")
            
            # Navigate to search URL
            self.driver.get(search_url)
            
            # Add human-like delay for page to load
            SecurityManager.random_delay(2, 4)
            
            # Step 2: Check if login is required
            logger.info("Checking if login is required...")
            login_required = self._is_login_required()
            
            # Step 3: Login only if required
            if login_required:
                logger.info("Login required. Attempting to authenticate...")
                auth = LinkedInAuth(self.driver)
                
                # Check if already logged in (might have been logged in from previous session)
                if not auth.is_logged_in():
                    logger.info("Not authenticated. Performing login...")
                    login_success = auth.login(manual_verification=True)
                    if not login_success:
                        logger.error("Authentication failed. Cannot proceed with job search.")
                        logger.error("Tip: If CAPTCHA/verification is required, ensure HEADLESS_MODE=False in .env")
                        return []
                    logger.info("✓ Authentication successful")
                    
                    # After login, LinkedIn might redirect - navigate back to search URL
                    logger.info("Navigating back to search URL after login...")
                    self.driver.get(search_url)
                    SecurityManager.random_delay(2, 3)
                else:
                    logger.info("✓ Already authenticated (session persisted)")
            else:
                logger.info("✓ Login not required - using guest access")
            
            # Step 4: Find and extract job IDs
            logger.info("Waiting for job cards to load using JavaScript...")
            
            # Use JavaScript to detect job cards since LinkedIn blocks Selenium selectors
            max_attempts = 10
            attempt = 0
            job_ids = []
            
            while attempt < max_attempts:
                attempt += 1
                time.sleep(2)  # Wait for page to render
                
                # Use JavaScript to extract job IDs directly
                found_job_ids = self.driver.execute_script("""
                    // Extract job IDs from data-job-id attributes
                    var cards = Array.from(document.querySelectorAll('[data-job-id]'));
                    var jobIds = cards.map((c) => c.dataset.jobId).filter(Boolean);
                    return jobIds;
                """)
                
                if found_job_ids and len(found_job_ids) > 0:
                    job_ids = found_job_ids
                    logger.info(f"Found {len(job_ids)} job cards on initial load")
                    break
                else:
                    logger.debug(f"Waiting for job cards... (attempt {attempt}/{max_attempts})")
            
            if not job_ids:
                logger.warning("No job cards found after waiting. LinkedIn may be blocking or page structure changed.")
                # Try one more time after a longer wait
                time.sleep(5)
                job_ids = self.driver.execute_script("""
                    var cards = Array.from(document.querySelectorAll('[data-job-id]'));
                    return cards.map((c) => c.dataset.jobId).filter(Boolean);
                """)
                if job_ids:
                    logger.info(f"Found {len(job_ids)} job cards after extended wait")
                else:
                    logger.error("No job cards found. Search may have failed.")
                    return []
            
            # Additional wait to ensure cards are fully loaded
            SecurityManager.random_delay(1, 2)
            
            # Scroll to load all available results
            logger.info("Scrolling to load additional job results...")
            all_job_ids = self._scroll_to_load_more(num_results, job_ids)
            
            # Remove duplicates and return unique job IDs
            unique_job_ids = list(dict.fromkeys(all_job_ids))  # Preserves order while removing duplicates
            
            logger.info(f"Job search completed successfully. Found {len(unique_job_ids)} unique jobs")
            return unique_job_ids
        
        except TimeoutException as e:
            logger.error(f"Timeout waiting for job cards: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Job search failed: {str(e)}", exc_info=True)
            return []
    
    def extract_jobs(self, jobs_ids):
        """
        Convert job IDs to dictionary mapping job_id to job_link.
        
        Args:
            jobs_ids (list): List of job IDs to convert
        
        Returns:
            dict: Dictionary mapping job_id to job_link
                  Format: {job_id: job_link}
        """
        jobs_data = {}
        try:
            if not jobs_ids:
                logger.warning("No job IDs provided for extraction")
                return jobs_data
            
            logger.info(f"Converting {len(jobs_ids)} job IDs to job links...")
            for job_id in jobs_ids:
                if job_id:  # Skip None or empty IDs
                    job_link = f"https://www.linkedin.com/jobs/view/{job_id}/"
                    jobs_data[job_id] = job_link
            
            logger.info(f"Successfully converted {len(jobs_data)} job IDs to links")
            return jobs_data
        except Exception as e:
            logger.error(f"Job extraction failed: {str(e)}")
            return jobs_data
    def _scroll_to_load_more(self, target_count, initial_job_ids):
        """
        Scroll page to load more job results dynamically.
        This is a PRIVATE method.
        Continues scrolling until no more jobs are loaded.
        
        Args:
            target_count (int): Target number of job cards to load (ignored - loads all available)
            initial_job_ids (list): List of job IDs already found before scrolling
        
        Returns:
            list: List of all job IDs found (including initial ones)
        """
        try:
            all_job_ids = list(initial_job_ids) if initial_job_ids else []
            previous_count = len(all_job_ids)
            no_change_count = 0  # Track consecutive scrolls with no new jobs
            max_no_change = 3  # Stop after 3 consecutive scrolls with no new jobs
            
            logger.info(f"Starting scroll with {previous_count} initial jobs. Loading more...")
            
            while True:
                # Scroll to bottom of page with random intervals
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                
                # Human-like scroll delay
                SecurityManager.human_like_scroll_delay()
                
                # Get current job IDs using JavaScript (bypasses LinkedIn blocking)
                current_job_ids = self.driver.execute_script("""
                    // Extract all job IDs from data-job-id attributes
                    var cards = Array.from(document.querySelectorAll('[data-job-id]'));
                    return cards.map((c) => c.dataset.jobId).filter(Boolean);
                """)
                
                # Update all_job_ids with new unique IDs
                if current_job_ids:
                    for job_id in current_job_ids:
                        if job_id not in all_job_ids:
                            all_job_ids.append(job_id)
                
                current_count = len(all_job_ids)
                logger.info(f"Loaded {current_count} total jobs (found {current_count - previous_count} new)")
                
                # Check if no new jobs were loaded
                if current_count == previous_count:
                    no_change_count += 1
                    if no_change_count >= max_no_change:
                        logger.info(f"No more jobs loading. Stopped at {current_count} total jobs")
                        break
                else:
                    no_change_count = 0  # Reset counter if new jobs were found
                
                previous_count = current_count
            
            return all_job_ids
        
        except Exception as e:
            logger.warning(f"Error during scrolling: {str(e)}")
            # Return whatever we have so far
            return all_job_ids if 'all_job_ids' in locals() else initial_job_ids


# Example search URLs:
# https://www.linkedin.com/jobs/search-results/?keywords=Full%20Stack&distance=120
# https://www.linkedin.com/jobs/search-results/?keywords=Full%20Stack&distance=120&f_TPR=r3600&geoId=106728703
# 
# Usage examples:
# - search_jobs("Python Developer", location="United States", time_filter="1hour")
# - search_jobs("Data Scientist", location="New York", geo_id="106728703", distance=50)