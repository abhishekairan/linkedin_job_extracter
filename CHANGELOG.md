# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## Version 5 (v5) - Current Version

**Previous versions (4.x.x and below) were part of Version 4 (v4)**

---

## [5.0.0] - 2025-11-04

### Major Version Update: v5

This version represents a major architectural improvement with on-demand authentication, optimized direct URL navigation, and enhanced job extraction capabilities.

### Added

#### Core Features
- **On-Demand Authentication System**
  - Browser service maintains browser instance without pre-authentication
  - Login handled automatically by job_search when LinkedIn requires it
  - Eliminates unnecessary login attempts when guest access works
  - Faster service startup without waiting for authentication

- **Direct URL Navigation for Job Search**
  - Builds and navigates directly to LinkedIn job search URL with query parameters
  - Supports advanced filters: keywords, location, time filter (1 hour, 24 hours, week, month), geo ID, distance
  - More control over search parameters without UI interaction
  - No need to interact with search bar or UI elements

- **Smart Login Detection**
  - Checks if login is required by examining URL redirects and page content
  - Detects redirects to `/uas/login` page
  - Checks for login elements and "Sign in" prompts
  - Verifies if job cards are visible (guest access might work)
  - Only triggers login when actually required

- **Enhanced Job Extractor with Stealth Mode**
  - `job_extractor.py` runs in full stealth mode
  - Uses `SecurityManager` for stealth scripts injection
  - Random user agent rotation
  - Anti-detection Chrome options
  - Job ID extraction with multiple fallback methods
  - Comprehensive job not found error handling

#### Security Features
- **Stealth Scripts**: Masks automation indicators using CDP commands
- **Random User Agents**: Rotates user agent strings for each browser instance
- **Rate Limiting**: Prevents aggressive scraping (30-120 seconds between searches)
- **Human-like Behavior**: Random delays, scroll patterns, mouse movements
- **Browser Fingerprint Masking**: Removes automation properties

### Changed

#### Architecture
- **Minimized Login Process**
  - Removed pre-authentication from `browser_service.py`
  - Removed pre-authentication from `search_jobs.py`
  - Login check moved to after job search attempt
  - Login detection happens within `job_search.search_jobs()` method
  - Only one login check per search operation

- **Optimized Job Search Flow**
  - Step 1: Direct URL search (builds search URL with parameters)
  - Step 2: Smart login detection (checks if login required)
  - Step 3: Conditional login (only if LinkedIn requires it)
  - Step 4: Enhanced job extraction (improved scrolling and ID collection)

- **Simplified JavaScript Injection**
  - Changed job searching dataset to job IDs
  - Removed separate javascript injection for finding and extracting jobs
  - Merged job extraction part into finding job
  - Returns list of job IDs instead of boolean

- **Return Types**
  - `search_jobs()` now returns list of job IDs (was boolean)
  - `extract_jobs()` converts job IDs to dict of `{"job_id": "job_link"}`
  - `job_extractor.py` returns structured dictionary with job_id, description, success status, and error messages

- **Job Extractor Module**
  - Completely rewritten `job_extractor.py`
  - Now uses `BrowserManager` to get browser instance (respects `.env` configuration)
  - Uses project's `Config` and `SecurityManager` for consistency
  - Integrated with existing stealth infrastructure and browser management system
  - Reuses browser from `browser_service.py` if available (via remote debugging)
  - Creates new browser with `.env` configuration if needed (Chrome paths, headless mode, etc.)
  - Can accept existing WebDriver instance or get from BrowserManager
  - Browser persistence maintained (doesn't close shared browser instances)
  - Context manager support (`with JobExtractor() as extractor:`)
  - Command-line interface for standalone usage

### Fixed

- **Browser Session Creation**: Fixed "chrome not reachable" errors
  - Removed problematic Chrome options (`--disable-web-security`, `--disable-features=IsolateOrigins,site-per-process`)
  - Added critical stability options
  - Improved remote debugging configuration
  - Enhanced error messages with troubleshooting steps

- **Job Extraction Consistency**: Fixed issue where job_search could find jobs but extraction failed
  - Consolidated extraction into JobSearch module
  - Uses exact same multi-method detection for consistency
  - Removed separate `job_extractor.py` module from job search flow

- **Login Detection**: Fixed false manual login triggers
  - Simplified `is_logged_in()` to use simple URL-based check
  - Only checks for `/feed` redirect (logged in users can access feed)
  - Removed unnecessary manual verification triggers

- **Job Not Found Errors**: Comprehensive error handling in `job_extractor.py`
  - Detects 404/error pages
  - Checks for "job no longer available" messages
  - Verifies job description container exists
  - Returns clear error messages

### Technical Details

#### Job Search Process
1. Build search URL directly with query parameters
2. Navigate to search URL
3. Check if login is required (URL redirects, page content analysis)
4. Login only if required (maintains session if already authenticated)
5. Extract job IDs using JavaScript injection
6. Scroll to load all available results
7. Return unique job IDs

#### Job Extraction Process
1. Navigate to job page in stealth mode
2. Check if job not found (multiple detection methods)
3. Extract job ID (URL, page attributes, meta tags)
4. Extract job description (multiple fallback selectors)
5. Return structured result dictionary

#### Stealth Mode Implementation
- Uses `SecurityManager.inject_stealth_scripts()` for automation masking
- Random user agent rotation
- CDP commands for navigator property overrides
- Anti-detection Chrome options
- Human-like delays and behavior patterns

### Architecture Improvements
- **On-Demand Authentication**: Login only happens when LinkedIn requires it
- **Faster Startup**: Browser service starts without waiting for authentication
- **Better Resource Usage**: Eliminates unnecessary login attempts
- **Guest Access Support**: Works with LinkedIn guest access when available
- **Single Login Check**: Only one login check per search operation
- **Consistent Extraction**: Job search and extraction use same detection methods

---

## Version History

### Version 5 (v5) - Current
- **5.0.0**: On-demand authentication, optimized direct URL navigation, enhanced job extractor with stealth mode

### Version 4 (v4) - Previous
- All versions 4.x.x and below were part of Version 4
- Included standalone service architecture, remote debugging, security features

---

## Versioning

This project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html):
- **MAJOR** version for incompatible API changes or major architectural updates
- **MINOR** version for new functionality in a backward-compatible manner
- **PATCH** version for backward-compatible bug fixes

---

## Migration Notes

### From Version 4 to Version 5

**Breaking Changes:**
- `search_jobs()` now returns `list` of job IDs instead of `bool`
- `job_extractor.py` is now a standalone module (not used in job search flow)
- Browser service no longer performs login during initialization

**Migration Steps:**
1. Update code that calls `search_jobs()` to handle list return type
2. Use `JobSearch.extract_jobs()` instead of separate `JobExtractor` for job search flow
3. Use `job_extractor.py` for extracting individual job descriptions (standalone usage)
4. Browser service will start faster (no login wait)

**Benefits:**
- Faster startup (no pre-authentication)
- More efficient (login only when needed)
- Better guest access support
- Consistent job extraction

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

