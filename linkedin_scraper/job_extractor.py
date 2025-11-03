"""
Job extraction module using JavaScript injection.
Extracts job data from LinkedIn job cards.
"""
import logging
import json
import re

logger = logging.getLogger(__name__)


class JobExtractor:
    """Extracts job information using JavaScript injection."""
    
    def __init__(self, driver):
        """
        Initialize JobExtractor with WebDriver instance.
        
        Args:
            driver: Selenium WebDriver instance
        """
        self.driver = driver
    
    def extract_jobs(self):
        """
        Extract job IDs and links using JavaScript injection.
        Uses data-view-name='job-card' selector for more reliable extraction.
        Based on v2 implementation approach.
        This is the PRIMARY extraction method.
        
        Returns:
            dict: Dictionary mapping job_id to job_link
                  Format: {job_id: job_link}
        """
        try:
            logger.info("Injecting JavaScript to extract job cards...")
            
            # JavaScript to extract job data using data-view-name attribute
            # This approach is more stable as it targets LinkedIn's data attributes
            js_script = """
            // Helper function to get elements by attribute value (from v2)
            function getElementsByAttributeValue(attribute, value) {
                return Array.from(document.querySelectorAll(`[${attribute}='${value}']`));
            }
            
            var jobsData = {};
            var cards = getElementsByAttributeValue('data-view-name', 'job-card');
            console.log(cards.length);
            for (var i = 0; i < cards.length; i++) {
                var card = cards[i];
                try {
                    // Try multiple selectors for link element
                    var linkElement = card.querySelector('.base-card__full-link') || 
                                     card.querySelector('a[href*="/jobs/view/"]') ||
                                     card.querySelector('a[data-tracking-control-name*="job"]');
                    
                    if (linkElement) {
                        var href = linkElement.getAttribute('href');
                        if (href) {
                            // Extract job ID from URL pattern: /jobs/view/123456/
                            var match = href.match(/\\/jobs\\/view\\/(\\d+)\\/?/);
                            if (match && match[1]) {
                                var jobId = match[1];
                                // Ensure full URL
                                if (href.startsWith('/')) {
                                    href = 'https://www.linkedin.com' + href;
                                }
                                jobsData[jobId] = href;
                            }
                        }
                    }
                } catch (e) {
                    // Skip this card if there's an error
                    continue;
                }
            }
            
            return jobsData;
            """
            
            # Execute JavaScript and get results
            jobs_data = self.driver.execute_script(js_script)
            
            if not jobs_data:
                jobs_data = {}
            
            logger.info(f"Extracted {len(jobs_data)} jobs")
            return jobs_data
        
        except Exception as e:
            logger.error(f"Job extraction failed: {str(e)}")
            return {}
    
    def extract_jobs_with_details(self):
        """
        Extract jobs with additional details (title, company).
        Uses data-view-name='job-card' selector for more reliable extraction.
        This is an OPTIONAL ADVANCED method.
        
        Returns:
            dict: Dictionary mapping job_id to job details
                  Format: {job_id: {'link': link, 'title': title, 'company': company}}
        """
        try:
            logger.info("Extracting jobs with detailed information...")
            
            # JavaScript to extract job data with details using data-view-name attribute
            js_script = """
            // Helper function to get elements by attribute value (from v2)
            function getElementsByAttributeValue(attribute, value) {
                return Array.from(document.querySelectorAll(`[${attribute}='${value}']`));
            }
            
            var jobsData = {};
            var cards = getElementsByAttributeValue('data-view-name', 'job-card');
            
            for (var i = 0; i < cards.length; i++) {
                var card = cards[i];
                try {
                    // Try multiple selectors for link element
                    var linkElement = card.querySelector('.base-card__full-link') || 
                                     card.querySelector('a[href*="/jobs/view/"]') ||
                                     card.querySelector('a[data-tracking-control-name*="job"]');
                    
                    if (linkElement) {
                        var href = linkElement.getAttribute('href');
                        if (href) {
                            var match = href.match(/\\/jobs\\/view\\/(\\d+)\\/?/);
                            if (match && match[1]) {
                                var jobId = match[1];
                                
                                // Ensure full URL
                                if (href.startsWith('/')) {
                                    href = 'https://www.linkedin.com' + href;
                                }
                                
                                // Extract title - try multiple selectors
                                var titleElement = card.querySelector('.base-search-card__title') ||
                                                  card.querySelector('h3') ||
                                                  card.querySelector('.job-card-list__title');
                                var title = titleElement ? titleElement.textContent.trim() : '';
                                
                                // Extract company name - try multiple selectors
                                var companyElement = card.querySelector('.base-search-card__subtitle') ||
                                                     card.querySelector('h4') ||
                                                     card.querySelector('.job-card-container__company-name');
                                var company = companyElement ? companyElement.textContent.trim() : '';
                                
                                jobsData[jobId] = {
                                    'link': href,
                                    'title': title,
                                    'company': company
                                };
                            }
                        }
                    }
                } catch (e) {
                    continue;
                }
            }
            
            return jobsData;
            """
            
            # Execute JavaScript and get results
            jobs_data = self.driver.execute_script(js_script)
            
            if not jobs_data:
                jobs_data = {}
            
            logger.info(f"Extracted {len(jobs_data)} jobs with details")
            return jobs_data
        
        except Exception as e:
            logger.error(f"Detailed job extraction failed: {str(e)}")
            return {}

