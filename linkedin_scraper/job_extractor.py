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
            
            # Simple JavaScript to extract job data using data-view-name and data-job-id attributes
            # This bypasses LinkedIn's HTML protection which returns scripts instead of raw HTML
            js_script = """
            (function() {
                // Find all divs (or any elements) with data-view-name="job-card"
                var cards = Array.from(document.querySelectorAll('[data-view-name="job-card"]'));
                var jobsData = {};
                
                // Extract job ID from each card
                for (var i = 0; i < cards.length; i++) {
                    var card = cards[i];
                    try {
                        // Get job ID directly from data-job-id attribute
                        var jobId = card.getAttribute('data-job-id');
                        
                        // If not found on card, try parent element
                        if (!jobId) {
                            var parent = card.closest('[data-job-id]');
                            if (parent) {
                                jobId = parent.getAttribute('data-job-id');
                            }
                        }
                        
                        // If we found a job ID, construct the job link
                        if (jobId) {
                            var jobLink = 'https://www.linkedin.com/jobs/view/' + jobId + '/';
                            jobsData[jobId] = jobLink;
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
    