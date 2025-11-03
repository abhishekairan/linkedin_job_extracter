# LinkedIn Job Scraper - Project Overview

## Project Purpose

This project provides a scalable, secure LinkedIn job scraping solution that maintains a single persistent browser instance to prevent account flagging and supports remote access for monitoring and manual interventions.

## Architecture

The project is organized into **two standalone services**:

### 1. Browser & Login Service (`browser_service.py`)
- **Purpose**: Maintains a persistent Chrome browser instance and LinkedIn authentication
- **Responsibilities**:
  - Launch and maintain single browser instance
  - Handle LinkedIn login and session management
  - Monitor browser health and re-authenticate if needed
  - Provide browser access via remote debugging port (9222)
  - Prevent multiple browser instances to avoid account flagging

### 2. Job Search & Extract Service (`search_jobs.py`)
- **Purpose**: Performs job searches and extracts job data
- **Responsibilities**:
  - Connect to browser service via remote debugging
  - Perform job searches with keywords and location filters
  - Extract job IDs and URLs using JavaScript injection
  - Return job dictionary format: `{job_id: job_url}`
  - Implement rate limiting and human-like behavior

## Core Components

### Linkedin Scraper Package (`linkedin_scraper/`)

1. **`config.py`**: Configuration management (credentials, paths, settings)
2. **`browser_manager.py`**: Browser instance management with remote debugging support
3. **`linkedin_auth.py`**: LinkedIn authentication and session verification
4. **`job_search.py`**: Job search operations with authentication checks
5. **`job_extractor.py`**: JavaScript injection for job data extraction
6. **`security.py`**: Security measures to prevent account flagging

## Key Features

### Security & Account Protection

- **Single Browser Instance**: Maintains only one browser to prevent multiple logins
- **Stealth Mode**: Browser fingerprint masking and automation detection bypass
- **Rate Limiting**: Enforces delays between searches (30-120 seconds)
- **Human-like Behavior**: Random delays, scroll patterns, and mouse movements
- **JavaScript Injection**: Bypasses LinkedIn's HTML protection (returns scripts instead of HTML)
- **Attribute-based Extraction**: Uses `data-view-name="job-card"` and `data-job-id` attributes

### Scalability

- **Remote Browser Access**: Multiple services can connect to single browser
- **Job ID-based Operations**: Dictionary format `{job_id: job_url}` enables batch operations
- **Modular Architecture**: Services can be extended independently
- **Remote Debugging**: Enables cross-process browser sharing

## Project Structure

```
linkedin_job_extracter/
├── browser_service.py          # Standalone browser/login service
├── search_jobs.py              # Standalone job search/extract service
├── linkedin_scraper/           # Core package
│   ├── __init__.py
│   ├── config.py
│   ├── browser_manager.py
│   ├── linkedin_auth.py
│   ├── job_search.py
│   ├── job_extractor.py
│   └── security.py
├── logs/                        # Log files
├── .env                        # Configuration (not in git)
├── requirements.txt            # Python dependencies
├── PROJECT.md                  # This file
├── BROWSER_SERVICE.md          # Browser service documentation
├── JOB_SEARCH_SERVICE.md       # Job search service documentation
├── REMOTE_ACCESS.md            # Remote access setup guide
├── CHANGELOG.md                # Version history
└── README.md                   # Quick start guide
```

## Data Flow

```
1. Start browser_service.py
   └─> Launches Chrome with remote debugging (port 9222)
   └─> Authenticates to LinkedIn
   └─> Maintains session and health checks

2. Run search_jobs.py
   └─> Checks browser service status
   └─> Connects via remote debugging
   └─> Verifies/authenticates if needed
   └─> Performs job search
   └─> Extracts jobs using JavaScript
   └─> Returns {job_id: job_url} dictionary
```

## Job Extraction Method

### Why JavaScript Injection?

LinkedIn protects their HTML by returning JavaScript instead of raw HTML when accessed programmatically. Traditional parsers (BeautifulSoup, lxml) cannot extract data from these dynamic scripts.

### Solution

1. **JavaScript Injection**: Execute JavaScript directly in the browser's DOM
2. **Attribute-based Selection**: Use LinkedIn's data attributes:
   - `data-view-name="job-card"` to find job cards
   - `data-job-id` to extract job IDs directly
3. **Fallback Methods**: Extract from URLs if attributes unavailable

### Extraction Process

```javascript
// Pseudocode
1. Find all elements with data-view-name="job-card"
2. For each card:
   a. Extract data-job-id attribute (primary method)
   b. If not found, try parent element with data-job-id
   c. If still not found, extract from URL pattern /jobs/view/{id}/
3. Build full job URL
4. Return {job_id: job_url} dictionary
```

## Configuration

All configuration is managed through `.env` file:

```env
# Required
LINKEDIN_EMAIL=your_email@example.com
LINKEDIN_PASSWORD=your_password

# Optional (defaults provided)
CHROMEDRIVER_PATH=/usr/bin/chromedriver
CHROME_BINARY_PATH=/usr/bin/chromium-browser
HEADLESS_MODE=False
WAIT_TIME=10
```

## Usage Patterns

### Pattern 1: Service-based (Recommended)

```bash
# Terminal 1: Start browser service
python browser_service.py

# Terminal 2: Run searches
python search_jobs.py "Python Developer" "United States"
```

### Pattern 2: Single Script (Legacy)

```bash
python main.py  # Creates own browser instance
```

## Security Measures Implemented

1. **Browser Fingerprint Masking**
   - Removes `navigator.webdriver` property
   - Overrides automation indicators
   - Random realistic user agents

2. **Rate Limiting**
   - Minimum 30 seconds between searches
   - Random intervals (30-120 seconds)
   - Search counter tracking

3. **Human-like Behavior**
   - Random delays (1-3 seconds for actions)
   - Human-like scroll delays (0.5-2 seconds)
   - Random mouse movements (when visible)

4. **Stealth Scripts**
   - CDP commands to mask automation
   - Navigator property overrides
   - Permission API masking

## Future Scalability

The project is designed for future extensions:

1. **Batch Job Operations**: Dictionary format enables processing multiple jobs
2. **API Integration**: Services can be wrapped in REST API
3. **Multiple Accounts**: Can extend to support account rotation
4. **Job Details Extraction**: Can add methods to extract full job details
5. **Application Automation**: Can add job application automation
6. **Scheduling**: Can integrate with cron/Task Scheduler

## Technology Stack

- **Python 3.7+**: Core language
- **Selenium**: Browser automation
- **Chrome/ChromeDriver**: Browser and driver
- **JavaScript Injection**: Data extraction
- **Remote Debugging Protocol**: Cross-process communication

## Development Notes

### Key Design Decisions

1. **Single Browser Instance**: Prevents account flagging from multiple logins
2. **Service Separation**: Allows independent scaling and updates
3. **JavaScript Injection**: Only reliable method for LinkedIn's protected HTML
4. **Remote Debugging**: Enables service-to-service communication
5. **Rate Limiting**: Built-in protection against aggressive scraping

### Maintenance Considerations

- Browser service must run continuously
- Remote debugging port (9222) must be accessible
- Logs are stored in `logs/` directory
- Status files created in project root (JSON format)
- Browser session persists across script runs

## Related Documentation

- **BROWSER_SERVICE.md**: Detailed browser service guide
- **JOB_SEARCH_SERVICE.md**: Job search service guide
- **REMOTE_ACCESS.md**: Remote access setup (RealVNC, etc.)
- **CHANGELOG.md**: Version history and changes
- **README.md**: Quick start guide

