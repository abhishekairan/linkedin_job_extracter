# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

