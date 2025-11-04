# Changelog

All notable changes to this project will be documented in this file.

## [3.2.0] - 2025-11-04

### Fixed
- **ROOT FIX: Browser session creation failure ("chrome not reachable")**
  - Removed problematic Chrome options that caused Chrome to hang or crash during startup:
    - Removed `--disable-web-security` (can cause Chrome to hang)
    - Removed `--disable-features=IsolateOrigins,site-per-process` (can cause crashes)
  - Added critical stability options to prevent Chrome from becoming unreachable:
    - Added `--disable-gpu-sandbox`, `--disable-setuid-sandbox` for better stability
    - Added `--disable-hang-monitor`, `--disable-crash-reporter` to prevent startup issues
    - Added `--remote-allow-origins=*` to ensure remote debugging accepts connections
  - Improved remote debugging configuration:
    - Explicitly bind to `127.0.0.1` to ensure Chrome listens on correct interface
    - Added proper connection verification after browser creation
  - Enhanced error messages with detailed troubleshooting steps for "chrome not reachable" errors
  - Simplified login check logic to only check for `/feed` redirect (removed unnecessary manual verification triggers)

### Changed
- **Consolidated job extraction into JobSearch module**
  - Removed `job_extractor.py` module (deleted)
  - Added `extract_jobs()` method to `JobSearch` class
  - Extraction now uses the **exact same multi-method detection** as job search for consistency
  - This fixes the issue where `job_search.py` could find jobs but `job_extractor.py` failed to extract them
  - Updated `search_jobs.py` and `main.py` to use `JobSearch.extract_jobs()` instead of `JobExtractor`
  - Removed `JobExtractor` from `linkedin_scraper/__init__.py` exports
- Simplified `LinkedInAuth.is_logged_in()` to use simple URL-based check (redirect to `/feed` = logged in)
- Simplified `LinkedInAuth.login()` to only trigger manual verification if login doesn't redirect to `/feed`
- Removed `_requires_manual_verification()` method (no longer needed)

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.1.4] - 2025-11-03

### Fixed

- **Job Extraction Failure**: Fixed issue where job extraction found 0 jobs even though job search successfully found cards
  - Updated `job_extractor.py` to use the exact same multi-method card detection as `job_search.py`
  - Now uses all 4 fallback methods: data-view-name, base-card class, jobs-list-item, and job links
  - Improved job ID and link extraction with multiple fallback methods
  - Ensures extraction JavaScript matches the successful search detection technique

### Changed

- **Job Extraction Logic**: Completely rewritten to match job search detection methods
- **Card Detection**: Uses identical fallback sequence as job_search.py for consistency

---

## [3.1.3] - 2025-11-03

### Fixed

- **False Manual Login Trigger**: Fixed issue where manual login was triggered even when user was already logged in
  - Improved `is_logged_in()` to use URL-based detection (LinkedIn feed is only accessible when logged in)
  - Added JavaScript-based login verification to avoid unnecessary navigation
  - Now properly detects logged-in state without triggering verification prompts

- **Job Cards Detection**: Fixed timeout waiting for job cards by using JavaScript injection instead of Selenium selectors
  - LinkedIn blocks Selenium selectors, so now uses client-side JavaScript to detect job cards
  - Multiple fallback methods: data-view-name, base-card class, jobs-list-item, and job links
  - Bypasses LinkedIn's blocking mechanism by executing JavaScript directly in browser

- **Browser Service Connection**: Improved connection logic to better handle suspended services
  - Better detection of Chrome processes on debug port
  - Clearer warnings when service is suspended vs crashed
  - More informative messages guiding users to resume service

### Changed

- **Login Detection**: Now primarily uses URL-based detection (can access /feed/ = logged in)
- **Job Card Detection**: Completely rewritten to use JavaScript injection with multiple fallback methods
- **Scrolling Logic**: Updated to use JavaScript for counting job cards instead of Selenium find_elements

### Technical Details

- Login check: Verifies URL first, then uses JavaScript to confirm login status
- Job cards: JavaScript injection with 4 different detection methods as fallbacks
- Browser connection: Enhanced process detection to distinguish suspended vs crashed services

---

## [3.1.2] - 2025-11-03

### Fixed

- **Port Conflict Resolution**: When port 9222 is in use by stale Chrome processes, automatically finds and uses alternative port (9223-9239) instead of failing
- **Renderer Connection Error**: Fixed "unable to connect to renderer" error that was caused by port conflicts preventing Chrome from starting
- **Stale Chrome Process Handling**: Better handling when port is occupied by orphaned Chrome processes from suspended browser service

### Changed

- **Dynamic Port Assignment**: Browser manager now automatically finds available port when default port (9222) is occupied
- **Port Availability Logic**: Improved port checking with proper availability detection (port is available if connection fails)
- **Error Recovery**: When unable to connect to existing browser, creates new instance on alternative port instead of failing

### Technical Details

- Port availability check: Port is considered available if socket connection fails (port not in use)
- Port range: Tries ports 9223-9239 when 9222 is unavailable
- Debug port saved to file for future connections
- Better error messages guide users to resolve port conflicts

---

## [3.1.1] - 2025-11-03

### Fixed

- **Chrome DevTools Protocol Verification**: Enhanced remote connection check to verify Chrome DevTools Protocol is actually responding, not just that port is open
- **Port Conflict Detection**: Added detection of port conflicts before attempting to create new browser instances
- **Xvfb Verification**: Added verification that Xvfb is actually running and accessible before using display :99
- **Suspended Service Detection**: Better handling when browser service is suspended (Ctrl+Z) but Chrome is still running

### Added

- **DevTools Protocol Check**: Verifies Chrome DevTools Protocol responds before attempting remote connection
- **Process Detection**: Checks which process is using port 9222 when conflicts occur
- **Display Accessibility Check**: Verifies display is accessible using xdpyinfo before launching Chrome
- **Xvfb Startup Verification**: Confirms Xvfb actually started before proceeding

### Improved

- **Better Error Messages**: More specific messages about suspended services and port conflicts
- **Xvfb Startup Reliability**: Increased wait time and added verification step
- **Port Conflict Warnings**: Clear warnings when port is in use and guidance on resolution

---

## [3.1.0] - 2025-11-03

### Fixed

- **Remote Debugging Connection**: Fixed issue where `search_jobs.py` couldn't connect to browser service's Chrome instance
  - Added port accessibility check before attempting remote connection
  - Improved error handling for connection failures
  - Better detection of when browser service Chrome is not accessible

- **Chrome Renderer Connection Error**: Fixed "unable to connect to renderer" error when creating new browser instances
  - Automatic Xvfb setup when DISPLAY not set in non-headless mode
  - Better Chrome options for non-headless stability
  - Improved error messages with troubleshooting steps

- **Non-Headless Mode Setup**: Enhanced automatic display server setup
  - Automatically starts Xvfb on display :99 if DISPLAY not set
  - Checks for existing Xvfb processes before starting new one
  - Provides clear error messages if Xvfb not available

### Added

- **Socket Port Check**: Added connection test before attempting remote debugging connection
  - Tests if Chrome debug port (9222) is accessible before connecting
  - Prevents timeout errors and provides faster failure detection

- **Automatic Display Setup**: Browser manager now automatically sets up Xvfb for non-headless mode
  - Detects missing DISPLAY environment variable
  - Automatically starts Xvfb if not running
  - Sets DISPLAY environment variable automatically

- **Enhanced Error Messages**: More detailed error messages for common Chrome launch failures
  - Specific messages for renderer connection errors
  - Specific messages for session creation failures
  - Troubleshooting steps included in error output

- **Better Logging**: Added more informative log messages during browser launch
  - Logs ChromeDriver path, Chrome binary path
  - Logs headless mode status and DISPLAY variable
  - Helps with debugging configuration issues

### Changed

- **Remote Connection Logic**: Improved remote debugging connection attempt
  - Now checks port accessibility before attempting connection
  - Better error handling and user feedback
  - Falls back to creating new browser more gracefully

- **Chrome Options**: Enhanced Chrome options for non-headless mode
  - Added `--disable-gpu` for non-headless mode stability
  - Added `--disable-software-rasterizer` for better compatibility
  - Better handling of headless vs non-headless modes

### Technical Details

- Socket connection test added before remote debugging connection
- Xvfb auto-setup checks for existing processes to avoid duplicates
- Display environment variable set automatically when Xvfb starts
- Enhanced error messages include platform-specific solutions

---

## [3.0.0] - 2024-01-15

### Major Reorganization

Complete project reorganization into standalone service architecture with enhanced security and scalability.

### Added

#### Core Features
- **Standalone Browser Service** (`browser_service.py`): Maintains persistent browser and LinkedIn authentication
- **Standalone Job Search Service** (`search_jobs.py`): Performs job searches and extracts job data
- **Security Module** (`linkedin_scraper/security.py`): Anti-detection measures and rate limiting
- **Enhanced Job Extraction**: Uses `data-job-id` attribute directly for more reliable extraction

#### Security Features
- Browser fingerprint masking and stealth scripts
- Rate limiting between searches (30-120 seconds)
- Human-like behavior patterns (random delays, scroll patterns)
- Random user agent rotation
- Automation detection bypass via CDP commands

#### Documentation
- **PROJECT.md**: Comprehensive project overview and architecture
- **BROWSER_SERVICE.md**: Detailed browser service documentation
- **JOB_SEARCH_SERVICE.md**: Job search service documentation
- **REMOTE_ACCESS.md**: Remote access setup guide (RealVNC, etc.)

#### JavaScript Extraction Improvements
- Primary method: Extract from `data-job-id` attribute
- Fallback methods: Parent element lookup, URL pattern extraction
- Better error handling and logging

### Changed

#### Architecture
- **Separated Services**: Browser/login and job search are now standalone services
- **Remote Debugging**: Enhanced remote debugging support for cross-process access
- **Single Instance**: Strict enforcement of single browser instance to prevent account flagging

#### Job Extraction
- **Updated JavaScript**: Now uses `data-job-id` attribute as primary extraction method
- **Improved Selectors**: Better handling of LinkedIn's dynamic content
- **Enhanced Fallbacks**: Multiple fallback methods for job ID extraction

#### Browser Manager
- **Enhanced Stealth**: Added stealth script injection on browser launch
- **Random User Agents**: Rotates user agent strings for each browser instance
- **Security Options**: Added more Chrome options for anti-detection

#### Job Search
- **Human-like Delays**: Random delays between actions (2-4 seconds)
- **Scroll Behavior**: Human-like scroll delays (0.5-2 seconds)
- **Authentication Checks**: Automatic authentication before each search

### Fixed

- Browser instance management across processes
- Job ID extraction reliability
- Authentication flow improvements
- Remote debugging connection stability

### Security

- Implemented rate limiting to prevent aggressive scraping
- Added stealth scripts to mask automation indicators
- Enhanced browser fingerprint masking
- Improved human-like behavior simulation

---

## Versioning

This project follows [Semantic Versioning](https://semver.org/):
- **MAJOR** version for incompatible API changes
- **MINOR** version for new functionality in a backward-compatible manner
- **PATCH** version for backward-compatible bug fixes

## Migration Notes

### From Version 3.0.0 to 3.1.0

No breaking changes. The update includes:
- Better error handling and automatic display setup
- Improved remote connection reliability
- Enhanced error messages for easier troubleshooting

If you experience connection issues:
1. Ensure Xvfb is installed: `sudo apt install xvfb`
2. Or set DISPLAY manually before running services
3. Or use headless mode: `HEADLESS_MODE=True` in `.env`

---

## Future Plans

- Batch job processing capabilities
- REST API wrapper for services
- Multi-account support with rotation
- Enhanced job details extraction
- Application automation features
- Database integration
- Webhook notifications
- Scheduled search automation

