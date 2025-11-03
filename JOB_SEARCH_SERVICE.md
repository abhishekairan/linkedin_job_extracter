# Job Search & Extract Service Documentation

## Overview

The **Job Search Service** (`search_jobs.py`) is a standalone script that connects to the browser service, performs LinkedIn job searches, and extracts job data using JavaScript injection. It returns a dictionary mapping job IDs to job URLs.

## Purpose

- Connect to browser service via remote debugging
- Perform job searches with keywords and location filters
- Extract job IDs and URLs from search results
- Return job dictionary: `{job_id: job_url}`
- Implement rate limiting and security measures

## Features

### 1. Browser Service Integration

- Checks if browser service is running
- Connects via remote debugging protocol
- Verifies authentication before searching
- Re-authenticates if needed

### 2. Job Search

- Searches with keywords and location filters
- Loads all available job listings (no limit)
- Scrolls automatically to load more results
- Human-like scrolling behavior

### 3. Job Extraction

- Uses JavaScript injection to bypass LinkedIn's HTML protection
- Extracts job IDs from `data-job-id` attribute
- Uses `data-view-name="job-card"` to find job cards
- Builds complete job URLs

### 4. Security & Rate Limiting

- Rate limits searches (30-120 seconds between searches)
- Random delays to simulate human behavior
- Prevents account flagging

## Installation & Setup

### Prerequisites

1. Browser service must be running (`python browser_service.py`)
2. Python 3.7+ installed
3. All dependencies from `requirements.txt`

### Configuration

No separate configuration needed - uses same `.env` as browser service.

## Usage

### Basic Usage

```bash
python search_jobs.py "Python Developer"
```

### With Location

```bash
python search_jobs.py "Data Scientist" "New York"
```

### With Custom Output File

```bash
python search_jobs.py "Software Engineer" "United States" my_jobs.json
```

### Command Syntax

```bash
python search_jobs.py <keywords> [location] [output_file]
```

- **keywords** (required): Job search keywords
- **location** (optional): Location filter
- **output_file** (optional): Output JSON file (default: `jobs_output.json`)

## Job Extraction Process

### Why JavaScript Injection?

LinkedIn protects their HTML by returning JavaScript code instead of raw HTML when accessed programmatically. Traditional parsers (BeautifulSoup, lxml) cannot extract data from these scripts.

### Extraction Method

The service uses JavaScript injection with these steps:

1. **Find Job Cards**: 
   ```javascript
   document.querySelectorAll('[data-view-name="job-card"]')
   ```

2. **Extract Job ID**:
   ```javascript
   card.getAttribute('data-job-id')
   // Or from parent: card.closest('[data-job-id]')
   // Or from URL: /jobs/view/{id}/
   ```

3. **Build Job URL**:
   ```javascript
   'https://www.linkedin.com/jobs/view/' + jobId + '/'
   ```

4. **Return Dictionary**:
   ```javascript
   {job_id: job_url}
   ```

### JavaScript Code Flow

```javascript
(function() {
    // 1. Find all job cards
    var cards = Array.from(document.querySelectorAll('[data-view-name="job-card"]'));
    var jobsData = {};
    
    // 2. Process each card
    for (var i = 0; i < cards.length; i++) {
        var card = cards[i];
        
        // 3. Extract job ID (primary: data-job-id attribute)
        var jobId = card.getAttribute('data-job-id');
        
        // 4. Fallback methods if needed
        if (!jobId) {
            // Try parent element
            var parent = card.closest('[data-job-id]');
            if (parent) jobId = parent.getAttribute('data-job-id');
            
            // Or extract from URL
            if (!jobId) {
                var href = card.querySelector('a[href*="/jobs/view/"]').href;
                var match = href.match(/\/jobs\/view\/(\d+)\//);
                if (match) jobId = match[1];
            }
        }
        
        // 5. Build full URL
        var url = 'https://www.linkedin.com/jobs/view/' + jobId + '/';
        
        // 6. Store in dictionary
        jobsData[jobId] = url;
    }
    
    return jobsData;
})();
```

## Output Format

### Dictionary Structure

```python
{
    "123456789": "https://www.linkedin.com/jobs/view/123456789/",
    "987654321": "https://www.linkedin.com/jobs/view/987654321/",
    "456789123": "https://www.linkedin.com/jobs/view/456789123/"
}
```

- **Key**: Job ID (string, numeric)
- **Value**: Full LinkedIn job URL (string)

### JSON File Format

Results are saved to JSON file:

```json
{
  "123456789": "https://www.linkedin.com/jobs/view/123456789/",
  "987654321": "https://www.linkedin.com/jobs/view/987654321/",
  "456789123": "https://www.linkedin.com/jobs/view/456789123/"
}
```

### Using the Output

```python
import json

# Load job dictionary
with open('jobs_output.json', 'r') as f:
    jobs = json.load(f)

# Iterate through jobs
for job_id, job_url in jobs.items():
    print(f"Job ID: {job_id}")
    print(f"URL: {job_url}")

# Access specific job
job_id = "123456789"
if job_id in jobs:
    print(f"Job URL: {jobs[job_id]}")
```

## Security Features

### Rate Limiting

The service enforces rate limiting between searches:

- **Minimum Interval**: 30 seconds
- **Maximum Interval**: 120 seconds
- **Random**: Interval chosen randomly within range

```python
# Rate limiting is automatic
security_manager.rate_limit_search()  # Waits if needed
```

### Human-like Behavior

1. **Random Delays**: 1-3 seconds for actions
2. **Scroll Delays**: 0.5-2 seconds between scrolls
3. **Page Load Delays**: 2-4 seconds after navigation

### Authentication Checks

Before each search:
1. Verifies browser service is running
2. Connects to browser
3. Checks authentication status
4. Re-authenticates if needed

## Service Flow

```
1. Start search_jobs.py
   │
   ├─> Rate limit check (wait if too soon)
   │
   ├─> Check browser service status
   │   └─> Error if service not running
   │
   ├─> Connect to browser via remote debugging
   │   └─> Uses browser_debug_port.json
   │
   ├─> Verify authentication
   │   ├─> If not authenticated → authenticate
   │   └─> If authenticated → continue
   │
   ├─> Perform job search
   │   ├─> Navigate to search URL
   │   ├─> Wait for job cards
   │   └─> Scroll to load all jobs
   │
   ├─> Extract job data
   │   ├─> Inject JavaScript
   │   ├─> Extract job IDs and URLs
   │   └─> Return dictionary
   │
   └─> Save to JSON file
       └─> Print summary
```

## Examples

### Example 1: Basic Search

```bash
$ python search_jobs.py "Python Developer"
============================================================
LinkedIn Job Search Service
============================================================
Checking if browser service is running...
✓ Browser service is running and ready
✓ Already authenticated
✓ Connected to browser service and ready for job search
Searching for jobs: 'Python Developer'
Scrolling to load all available job results...
Loaded 25 jobs
Loaded 50 jobs
Loaded 100 jobs
No more jobs loading. Stopped at 125 jobs
✓ Successfully extracted 125 jobs
✓ Results saved to: jobs_output.json

============================================================
Found 125 jobs
============================================================
Results saved to: jobs_output.json
============================================================
```

### Example 2: With Location

```bash
$ python search_jobs.py "Data Scientist" "San Francisco" sf_data_jobs.json
```

### Example 3: Programmatic Usage

```python
from search_jobs import search_jobs_standalone

# Search for jobs
jobs = search_jobs_standalone(
    keywords="Software Engineer",
    location="New York"
)

# Process results
print(f"Found {len(jobs)} jobs")
for job_id, job_url in jobs.items():
    # Do something with each job
    process_job(job_id, job_url)
```

## Troubleshooting

### "Browser service is not running"

**Solution**: Start browser service first:
```bash
python browser_service.py
```

### "Rate limiting: Waiting X seconds"

**Solution**: This is normal behavior to prevent account flagging. Wait for the delay to complete.

### "No jobs found"

**Possible Causes**:
- Search keywords too specific
- Location filter too restrictive
- LinkedIn search returned no results

**Solutions**:
- Try broader keywords
- Remove location filter
- Check if jobs exist manually on LinkedIn

### "Authentication failed"

**Solutions**:
1. Check browser service logs
2. Verify credentials in `.env`
3. Check if CAPTCHA/2FA required
4. Restart browser service

### "Connection to browser failed"

**Solutions**:
1. Verify browser service is running
2. Check remote debugging port (9222)
3. Review browser service logs
4. Restart browser service

## Best Practices

1. **Wait Between Searches**: Let rate limiting work
2. **Monitor Output**: Check job count makes sense
3. **Use Specific Keywords**: Better search results
4. **Save Output Files**: Keep job dictionaries for later use
5. **Check Logs**: Review `logs/job_search.log` for issues

## Integration

### With Browser Service

The service automatically connects to browser service:
- No manual connection needed
- Uses remote debugging protocol
- Shares browser instance

### With Your Applications

```python
import json
from search_jobs import search_jobs_standalone

# Search
jobs = search_jobs_standalone("Developer", "Remote")

# Process jobs
for job_id, url in jobs.items():
    # Your application logic
    save_to_database(job_id, url)
    send_notification(job_id, url)
    # etc.
```

## Logging

Logs are written to: `logs/job_search.log`

Log entries include:
- Search initiation
- Rate limiting waits
- Browser connection status
- Authentication checks
- Job extraction progress
- Errors and warnings

## Next Steps

- See **BROWSER_SERVICE.md** for browser service details
- See **REMOTE_ACCESS.md** for monitoring setup
- See **PROJECT.md** for architecture overview

