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
        Uses data-view-name='job-card' and data-job-id attributes for reliable extraction.
        This method bypasses LinkedIn's HTML protection by using JavaScript injection.
        
        Returns:
            dict: Dictionary mapping job_id to job_link
                  Format: {job_id: job_link}
        """
        try:
            logger.info("Injecting JavaScript to extract job cards...")
            
            # JavaScript to extract job data using the same multi-method approach as job_search.py
            # This bypasses LinkedIn's HTML protection which returns scripts instead of raw HTML
            # Uses the same card detection methods that successfully find cards during search
            js_script = """
            (function() {
                // Use the same multi-method approach as job_search.py to find cards
                var cards = [];
                
                // Method 1: data-view-name attribute
                cards = Array.from(document.querySelectorAll('[data-view-name="job-card"]'));
                
                // Method 2: base-card class
                if (cards.length === 0) {
                    cards = Array.from(document.querySelectorAll('.base-card'));
                }
                
                // Method 3: jobs-list-item class
                if (cards.length === 0) {
                    cards = Array.from(document.querySelectorAll('.jobs-search-results__list-item'));
                }
                
                // Method 4: Any element with job link (most reliable fallback)
                if (cards.length === 0) {
                    var links = Array.from(document.querySelectorAll('a[href*="/jobs/view/"]'));
                    // Get unique parent containers for each link
                    var uniqueCards = new Set();
                    links.forEach(function(link) {
                        var card = link.closest('li') || 
                                  link.closest('.base-card') || 
                                  link.closest('.jobs-search-results__list-item') ||
                                  link.parentElement;
                        if (card) {
                            uniqueCards.add(card);
                        }
                    });
                    cards = Array.from(uniqueCards);
                }
                
                var jobsData = {};
                
                // Extract job data from found cards
                for (var i = 0; i < cards.length; i++) {
                    var card = cards[i];
                    try {
                        var jobId = null;
                        var href = '';
                        
                        // Method 1: Get job ID directly from data-job-id attribute
                        jobId = card.getAttribute('data-job-id');
                        
                        // Method 2: Try to get from parent element
                        if (!jobId) {
                            var parent = card.closest('[data-job-id]');
                            if (parent) {
                                jobId = parent.getAttribute('data-job-id');
                            }
                        }
                        
                        // Method 3: Extract from link (most reliable)
                        var linkElement = card.querySelector('.base-card__full-link') || 
                                         card.querySelector('a[href*="/jobs/view/"]') ||
                                         card.querySelector('a[data-tracking-control-name*="job"]') ||
                                         (card.tagName === 'A' && card.href ? card : null);
                        
                        if (linkElement) {
                            // Get href from link element
                            if (linkElement.href) {
                                href = linkElement.href;
                            } else if (linkElement.getAttribute('href')) {
                                href = linkElement.getAttribute('href');
                            }
                            
                            // Extract job ID from URL if not already found
                            if (!jobId && href) {
                                var match = href.match(/\\/jobs\\/view\\/(\\d+)\\/?/);
                                if (match && match[1]) {
                                    jobId = match[1];
                                }
                            }
                        }
                        
                        // Method 4: Try to find link anywhere in card if not found yet
                        if (!href || !jobId) {
                            var allLinks = card.querySelectorAll('a[href*="/jobs/view/"]');
                            if (allLinks.length > 0) {
                                var firstLink = allLinks[0];
                                if (firstLink.href) {
                                    href = firstLink.href;
                                } else if (firstLink.getAttribute('href')) {
                                    href = firstLink.getAttribute('href');
                                }
                                
                                if (!jobId && href) {
                                    var match = href.match(/\\/jobs\\/view\\/(\\d+)\\/?/);
                                    if (match && match[1]) {
                                        jobId = match[1];
                                    }
                                }
                            }
                        }
                        
                        // Build full URL if relative
                        if (href && href.startsWith('/')) {
                            href = 'https://www.linkedin.com' + href;
                        } else if (!href && jobId) {
                            // Construct URL from job ID if link not found
                            href = 'https://www.linkedin.com/jobs/view/' + jobId + '/';
                        }
                        
                        // Store job data if we have either job ID or valid link
                        if (jobId) {
                            // Use job ID as key
                            jobsData[jobId] = href || ('https://www.linkedin.com/jobs/view/' + jobId + '/');
                        } else if (href && href.includes('/jobs/view/')) {
                            // Extract job ID from href if we have link but no ID
                            var match = href.match(/\\/jobs\\/view\\/(\\d+)\\/?/);
                            if (match && match[1]) {
                                jobId = match[1];
                                jobsData[jobId] = href;
                            }
                        }
                    } catch (e) {
                        // Skip this card if there's an error
                        console.warn('Error extracting job card:', e);
                        continue;
                    }
                }
                
                return jobsData;
            })();
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
            
            # JavaScript to extract job data with details using the same multi-method approach
            js_script = """
            // Use the same multi-method approach as job_search.py to find cards
            var cards = [];
            
            // Method 1: data-view-name attribute
            cards = Array.from(document.querySelectorAll('[data-view-name="job-card"]'));
            
            // Method 2: base-card class
            if (cards.length === 0) {
                cards = Array.from(document.querySelectorAll('.base-card'));
            }
            
            // Method 3: jobs-list-item class
            if (cards.length === 0) {
                cards = Array.from(document.querySelectorAll('.jobs-search-results__list-item'));
            }
            
            // Method 4: Any element with job link (most reliable fallback)
            if (cards.length === 0) {
                var links = Array.from(document.querySelectorAll('a[href*="/jobs/view/"]'));
                var uniqueCards = new Set();
                links.forEach(function(link) {
                    var card = link.closest('li') || 
                              link.closest('.base-card') || 
                              link.closest('.jobs-search-results__list-item') ||
                              link.parentElement;
                    if (card) {
                        uniqueCards.add(card);
                    }
                });
                cards = Array.from(uniqueCards);
            }
            
            var jobsData = {};
            
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

