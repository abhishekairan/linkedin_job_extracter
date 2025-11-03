# LinkedIn Job Scraper - Cursor AI Coding Instructions

## Project Goal

Build a Python automation script that runs on Linux servers to maintain a persistent Chrome browser instance, authenticate to LinkedIn, search for jobs, extract job card information via JavaScript injection, and return results as a dictionary of job IDs mapped to job links.

---

## Core Requirements

1. **Persistent Browser Instance**: Maintain a single Chrome process that stays open to avoid repeated logins
2. **Security**: Store credentials (email/password) in `.env` file, never hardcode
3. **Cross-Platform Support**: Primary focus on Linux, secondary support for Windows
4. **Account Protection**: Minimize login attempts to avoid account flagging
5. **Data Extraction**: Use JavaScript injection to extract job cards and return `{job_id: job_link}` dictionary

---

## File Structure to Create

```
linkedin-job-scraper/
├── .env                              # GITIGNORE - Credentials
├── .env.example                      # Template for .env
├── .gitignore                        # Git ignore file
├── requirements.txt                  # Python dependencies
├── main.py                           # Entry point script
├── linkedin_scraper/
│   ├── __init__.py                   # Package initialization
│   ├── config.py                     # Configuration management
│   ├── browser_manager.py            # Browser instance management
│   ├── linkedin_auth.py              # Authentication logic
│   ├── job_search.py                 # Job search operations
│   └── job_extractor.py              # JavaScript injection & extraction
├── logs/                             # Directory for log files
└── README.md                         # Project documentation
```

---

## Step-by-Step Implementation Instructions

### STEP 1: Project Initialization

#### 1.1 Create directory structure
- Create root directory: `linkedin-job-scraper`
- Create subdirectory: `linkedin_scraper`
- Create subdirectory: `logs`
- Create file: `linkedin_scraper/__init__.py` (can be empty)

#### 1.2 Create requirements.txt
Add these dependencies:
```
selenium==4.15.2
python-dotenv==1.0.0
```

#### 1.3 Create .gitignore file
Add these patterns:
```
.env
*.log
logs/
__pycache__/
*.pyc
.vscode/
.idea/
venv/
*.db
jobs_output.json
```

#### 1.4 Create .env.example template
```
LINKEDIN_EMAIL=your-email@example.com
LINKEDIN_PASSWORD=your-password
CHROMEDRIVER_PATH=/path/to/chromedriver
CHROME_BINARY_PATH=/usr/bin/chromium-browser
HEADLESS_MODE=False
WAIT_TIME=10
```

---

### STEP 2: Create Configuration Module (`linkedin_scraper/config.py`)

**Purpose**: Centralize all configuration and environment variables

**Implementation Details**:

1. Import required modules:
   - `os` for environment variables
   - `Path` from `pathlib` for file paths
   - `load_dotenv` from `dotenv`

2. Load .env file from project root directory

3. Create a `Config` class with class variables for:
   - `LINKEDIN_EMAIL` - from env var `LINKEDIN_EMAIL`
   - `LINKEDIN_PASSWORD` - from env var `LINKEDIN_PASSWORD`
   - `CHROMEDRIVER_PATH` - from env var, default `/usr/bin/chromedriver`
   - `CHROME_BINARY_PATH` - from env var, default `/usr/bin/chromium-browser`
   - `HEADLESS_MODE` - from env var (convert string "true"/"false" to boolean)
   - `IMPLICIT_WAIT` - from env var `WAIT_TIME`, default 10 seconds
   - `PLATFORM` - detect OS using `platform.system()` to return 'Linux', 'Windows', or 'Darwin'

4. Add validation class method:
   - Check if `LINKEDIN_EMAIL` and `LINKEDIN_PASSWORD` exist
   - Verify `CHROMEDRIVER_PATH` file exists
   - Raise `ValueError` if credentials missing
   - Raise `FileNotFoundError` if ChromeDriver not found
   - Return `True` if all valid

**Expected Output**: A centralized Config class that can be imported and used across all modules

---

### STEP 3: Create Browser Manager Module (`linkedin_scraper/browser_manager.py`)

**Purpose**: Manage persistent Chrome browser instance with health checks

**Implementation Details**:

1. Import required modules:
   - Selenium WebDriver and related imports
   - `Chrome`, `Options`, `Service` classes
   - `WebDriverException` for error handling

2. Create `BrowserManager` class:

   a. **`__init__` method**:
      - Initialize `self.driver = None`
      - Initialize `self.config = Config`

   b. **`_get_chrome_options()` method**:
      - Create Chrome `Options` instance
      - Set binary location to `config.CHROME_BINARY_PATH`
      - Add arguments:
        - `--no-sandbox` (required for Linux servers)
        - `--disable-dev-shm-usage` (prevent memory issues)
        - `--disable-blink-features=AutomationControlled` (hide automation)
        - `--start-maximized` (open maximized)
      - Set user agent to a standard Mozilla/5.0 string
      - If `HEADLESS_MODE` is True, add `--headless` argument
      - Return options object

   c. **`_create_service()` method**:
      - Create and return a Chrome `Service` with `CHROMEDRIVER_PATH`

   d. **`launch_browser()` method**:
      - Create Chrome options via `_get_chrome_options()`
      - Create service via `_create_service()`
      - Create WebDriver: `webdriver.Chrome(service=service, options=options)`
      - Set implicit wait to `config.IMPLICIT_WAIT`
      - Log successful launch
      - Return the driver
      - On exception: log error and raise

   e. **`is_browser_alive()` method**:
      - Return False if driver is None
      - Try to execute simple JavaScript: `self.driver.execute_script("return 1;")`
      - Return True if successful
      - Return False if any exception occurs
      - Log warning if not alive

   f. **`get_or_create_browser()` method** (KEY METHOD):
      - Check if driver exists AND is alive
      - If yes: log "Using existing browser instance" and return driver
      - If no: log "Creating new browser instance"
      - Try to quit existing driver if it exists (catch exceptions)
      - Call `launch_browser()` and return result

   g. **`close_browser()` method**:
      - If driver exists:
        - Try to call `driver.quit()`
        - Catch and log any exceptions
        - Set `self.driver = None`

   h. **Context manager methods** (for `with` statements):
      - `__enter__`: Return `self.get_or_create_browser()`
      - `__exit__`: Pass (don't close to keep persistent)

**Expected Output**: A robust browser manager that reuses browser instances and checks health

---

### STEP 4: Create LinkedIn Authentication Module (`linkedin_scraper/linkedin_auth.py`)

**Purpose**: Handle LinkedIn login and session verification

**Implementation Details**:

1. Import required modules:
   - Selenium WebDriver locators and waits
   - `By`, `WebDriverWait`, `EC` (expected conditions)
   - Exception handling imports

2. Create `LinkedInAuth` class:

   a. **Class variables**:
      - `LINKEDIN_LOGIN_URL = "https://www.linkedin.com/login"`
      - `LINKEDIN_HOME_URL = "https://www.linkedin.com/feed/"`

   b. **`__init__` method**:
      - Accept driver parameter
      - Store `self.driver = driver`
      - Create WebDriverWait: `self.wait = WebDriverWait(driver, Config.IMPLICIT_WAIT)`

   c. **`is_logged_in()` method** (CRITICAL):
      - Navigate to `LINKEDIN_HOME_URL`
      - Wait 2 seconds for page load
      - Check if "login" is in current URL:
        - If yes: return False (not logged in)
      - Try to wait for presence of element with class name `scaffold-finite-scroll__content`
      - If timeout: log warning and return False
      - If successful: log "Already logged into LinkedIn" and return True
      - On any exception: log warning and return False

   d. **`login()` method**:
      - Log "Attempting LinkedIn login..."
      - Navigate to `LINKEDIN_LOGIN_URL`
      - Wait 2 seconds
      - Find element with ID "username":
        - Clear it
        - Send keys with `Config.LINKEDIN_EMAIL`
        - Log "Email entered"
      - Find element with ID "password":
        - Clear it
        - Send keys with `Config.LINKEDIN_PASSWORD`
        - Log "Password entered"
      - Find button with XPath `//button[@type='submit']`:
        - Click it
        - Log "Login button clicked"
      - Wait 3 seconds
      - Call `is_logged_in()` to verify
      - If verified: log "Login successful!" and return True
      - If not verified: log error and return False
      - On TimeoutException: log error about verification needed and return False
      - On any exception: log error and return False

**Expected Output**: Authentication module that checks login status and performs login

---

### STEP 5: Create Job Search Module (`linkedin_scraper/job_search.py`)

**Purpose**: Search for jobs and load results

**Implementation Details**:

1. Import required modules:
   - Selenium WebDriver locators and waits
   - `By`, `WebDriverWait`, `EC`
   - Time module for delays

2. Create `JobSearch` class:

   a. **Class variable**:
      - `JOBS_URL = "https://www.linkedin.com/jobs/search/"`

   b. **`__init__` method**:
      - Accept driver parameter
      - Store `self.driver = driver`
      - Create WebDriverWait

   c. **`search_jobs()` method**:
      - Parameters: `keywords` (required), `location` (optional), `num_results=25` (default)
      - Log search keywords
      - Build URL: `{JOBS_URL}?keywords={keywords}`
      - If location provided: append `&location={location}`
      - Navigate to search URL
      - Wait 3 seconds for page load
      - Wait for presence of elements with class `base-card` (job cards)
      - Call `_scroll_to_load_more(num_results)` to load results
      - Return True if successful
      - On TimeoutException: log error and return False
      - On any exception: log error and return False

   d. **`_scroll_to_load_more()` method** (PRIVATE):
      - Parameters: `target_count`
      - Initialize `loaded_count = 0` and `scroll_pause_time = 1`
      - Loop while `loaded_count < target_count`:
        - Execute JavaScript: `window.scrollTo(0, document.body.scrollHeight);`
        - Wait 1 second
        - Get all elements with class `base-card`: `self.driver.find_elements(By.CLASS_NAME, "base-card")`
        - Update `loaded_count = len(jobs)`
        - Log current count
        - If loaded_count >= target_count: break loop
      - Return True
      - On exception: log warning and return False

**Expected Output**: Job search module that searches LinkedIn and loads job listings

---

### STEP 6: Create Job Extractor Module (`linkedin_scraper/job_extractor.py`)

**Purpose**: Extract job data using JavaScript injection

**Implementation Details**:

1. Import required modules:
   - Selenium WebDriver for executing scripts
   - JSON for potential data formatting

2. Create `JobExtractor` class:

   a. **`__init__` method**:
      - Accept driver parameter
      - Store `self.driver = driver`

   b. **`extract_jobs()` method** (PRIMARY):
      - Log "Injecting JavaScript to extract job cards..."
      - Create JavaScript string that:
        - Creates empty object `jobsData = {}`
        - Gets all elements: `document.querySelectorAll('.base-card')`
        - For each card:
          - Try to find element with class `base-card__full-link`
          - Extract `href` attribute
          - Use regex to match job ID from URL pattern: `/jobs/view/(\d+)/`
          - If match found:
            - Extract job ID (number from regex group 1)
            - Store in object: `jobsData[jobId] = href`
        - Return `jobsData`
      - Execute JavaScript: `self.driver.execute_script(js_script)`
      - Log count of extracted jobs
      - Return results
      - On exception: log error and return empty dict

   c. **`extract_jobs_with_details()` method** (OPTIONAL ADVANCED):
      - Similar to `extract_jobs()` but also extract:
        - Job title from element with class `base-search-card__title`
        - Company name from element with class `base-search-card__subtitle`
      - Return format: `{job_id: {link, title, company}}`
      - Implement same error handling as basic extraction

**Expected Output**: Extracted job data in dictionary format

---

### STEP 7: Create Main Script (`main.py`)

**Purpose**: Orchestrate all modules and provide entry point

**Implementation Details**:

1. **Setup Logging**:
   - Configure logging with basicConfig
   - Format: `'%(asctime)s - %(name)s - %(levelname)s - %(message)s'`
   - Add two handlers:
     - FileHandler pointing to `logs/linkedin_scraper.log`
     - StreamHandler (console output)
   - Set level to INFO

2. **Add project to Python path**:
   - Use `sys.path.insert(0, str(Path(__file__).parent))`

3. **Import all modules**:
   - Import Config, BrowserManager, LinkedInAuth, JobSearch, JobExtractor

4. **Create `scrape_linkedin_jobs()` function**:
   - Parameters: `keywords`, `location=None`, `num_results=25`
   - Steps:
     a. Call `Config.validate()` to verify configuration
     b. Create BrowserManager instance
     c. Call `get_or_create_browser()` to get or create driver
     d. Create LinkedInAuth instance with driver
     e. Check if logged in: `auth.is_logged_in()`
        - If not logged in: call `auth.login()`
        - If login fails: log error and return empty dict
     f. Create JobSearch instance
     g. Call `search_jobs(keywords, location, num_results)`
        - If fails: log error and return empty dict
     h. Create JobExtractor instance
     i. Call `extract_jobs()` to get job data
     j. Log success message with count
     k. Return jobs_data
   - Wrap in try-except to catch all errors
   - Return empty dict on any exception

5. **Create `main()` function**:
   - Log "Starting LinkedIn Job Scraper"
   - Set example keywords: `"Python Developer"`
   - Set example location: `"United States"`
   - Call `scrape_linkedin_jobs()` with examples
   - If results:
     - Print formatted output showing job IDs and links
     - Save to JSON file `jobs_output.json` with indentation
     - Log success message
   - Else:
     - Print "No jobs found or error occurred"
   - Log "Job scraping completed"

6. **Entry point**:
   - Add `if __name__ == "__main__": main()`

**Expected Output**: Fully functional main script that orchestrates the entire workflow

---

## Step 8: Create Supporting Files

### 8.1 Create `linkedin_scraper/__init__.py`

Add imports for easy access:
```python
from .browser_manager import BrowserManager
from .linkedin_auth import LinkedInAuth
from .job_search import JobSearch
from .job_extractor import JobExtractor

__all__ = ['BrowserManager', 'LinkedInAuth', 'JobSearch', 'JobExtractor']
```

### 8.2 Create `README.md`

Include:
- Project title and description
- Installation instructions
- Usage examples
- Configuration setup
- Troubleshooting section
- Security notes

---

## Implementation Checklist

Use this checklist to verify all components are complete:

- [ ] **Project Initialization**
  - [ ] Directory structure created
  - [ ] requirements.txt created with dependencies
  - [ ] .gitignore configured
  - [ ] .env.example template created

- [ ] **config.py**
  - [ ] Environment variables loaded from .env
  - [ ] All Config class variables defined
  - [ ] validate() method implements checks
  - [ ] Platform detection working

- [ ] **browser_manager.py**
  - [ ] Chrome options configured for Linux
  - [ ] Browser launch functionality working
  - [ ] Health check implemented
  - [ ] get_or_create_browser() returns persistent instance
  - [ ] Context manager methods present

- [ ] **linkedin_auth.py**
  - [ ] is_logged_in() checks session status
  - [ ] login() performs authentication
  - [ ] Error handling for failed login
  - [ ] Proper waiting for page elements

- [ ] **job_search.py**
  - [ ] search_jobs() constructs and navigates URLs
  - [ ] Dynamic scrolling loads more results
  - [ ] Job cards are properly detected

- [ ] **job_extractor.py**
  - [ ] JavaScript injection correctly extracts job IDs
  - [ ] Regex pattern matches job URLs correctly
  - [ ] Returns dictionary format {job_id: link}
  - [ ] Error handling for extraction failures

- [ ] **main.py**
  - [ ] Logging configured properly
  - [ ] scrape_linkedin_jobs() orchestrates workflow
  - [ ] main() provides CLI usage
  - [ ] Results saved to JSON

- [ ] **Supporting files**
  - [ ] __init__.py created with imports
  - [ ] README.md contains instructions

---

## Testing Instructions for Cursor

After implementing all files, test in this order:

1. **Configuration Test**:
   ```python
   from linkedin_scraper.config import Config
   Config.validate()  # Should not raise exceptions
   print(Config.PLATFORM)  # Should print OS name
   ```

2. **Browser Manager Test**:
   ```python
   from linkedin_scraper.browser_manager import BrowserManager
   bm = BrowserManager()
   driver = bm.get_or_create_browser()
   print(bm.is_browser_alive())  # Should print True
   ```

3. **Authentication Test**:
   ```python
   from linkedin_scraper.linkedin_auth import LinkedInAuth
   auth = LinkedInAuth(driver)
   logged_in = auth.is_logged_in()  # Check session
   if not logged_in:
       auth.login()  # Try login
   ```

4. **Full Integration Test**:
   ```python
   python main.py  # Should search, extract, and save jobs
   # Check logs/linkedin_scraper.log for details
   # Check jobs_output.json for results
   ```

---

## Critical Success Factors

1. **Persistent Browser**: Verify same driver instance is reused across multiple runs
2. **Security**: Ensure credentials never appear in code or logs
3. **Error Recovery**: Browser should restart if it crashes
4. **Data Format**: Results must be dictionary with format `{job_id: job_link}`
5. **Logging**: All significant actions logged for debugging
6. **Cross-Platform**: Code should work on Linux (primary) and Windows (secondary)

---

## Additional Notes for Cursor

- Use proper type hints in function signatures
- Add docstrings to all functions and classes
- Use meaningful variable names
- Add inline comments for complex logic
- Handle all exceptions with proper logging
- Test on Linux before considering Windows compatibility
- Verify ChromeDriver and Chrome versions match
- Use absolute paths with pathlib where possible
- Keep constants at module or class level
- Do not hardcode sensitive information anywhere
