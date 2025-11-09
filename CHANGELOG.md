# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## Version 5 (v5) - Current Version

**Previous versions (4.x.x and below) were part of Version 4 (v4)**

---

## [5.2.0] - 2025-01-XX

### Added

#### Advanced LinkedIn Job Search Filters
- **Job Type Filters (f_JT)**
  - Support for Full-time (F), Part-time (P), Contract (C), Temporary (T), Internship (I), Volunteer (V)
  - Multiple job types can be specified (comma-separated)
  - Command-line argument: `--jobtype` or `--job-type`
  - Example: `--jobtype F,C` for Full-time and Contract positions

- **Experience Level Filters (f_E)**
  - Support for all experience levels: Internship (1), Entry (2), Associate (3), Mid-Senior (4), Director (5), Executive (6)
  - Multiple levels can be specified (comma-separated)
  - Command-line argument: `--experience` or `--experience-level`
  - Example: `--experience 4,5,6` for Mid-Senior, Director, and Executive roles

- **Work Type Filters (f_WT)**
  - Support for On-site (1), Hybrid (2), Remote (3)
  - Multiple work types can be specified (comma-separated)
  - Command-line argument: `--worktype` or `--work-type`
  - Example: `--worktype 2,3` for Hybrid and Remote positions

- **Easy Apply Filter (f_EA)**
  - Filter for jobs with Easy Apply enabled
  - Command-line arguments: `--easy-apply` (enable) or `--no-easy-apply` (disable)
  - Boolean filter: `True` for Easy Apply only, `False` for all jobs

- **Actively Hiring Filter (f_AL)**
  - Filter for companies actively hiring
  - Command-line arguments: `--actively-hiring` (enable) or `--no-actively-hiring` (disable)
  - Boolean filter: `True` for actively hiring companies only

- **Verified Jobs Filter (f_VJ)**
  - Filter for verified job postings only
  - Command-line arguments: `--verified-jobs` (enable) or `--no-verified-jobs` (disable)
  - Helps avoid scam postings

- **Jobs at Connections Filter (f_JIYN)**
  - Filter for jobs at companies where you have connections
  - Command-line arguments: `--jobs-at-connections` (enable) or `--no-jobs-at-connections` (disable)
  - Requires LinkedIn login

- **Job Function Filters (f_F)**
  - Support for Sales (sale), Management (mgmt), Accounting (acct), IT (it), Marketing (mktg), HR (hr)
  - Multiple functions can be specified (comma-separated)
  - Command-line argument: `--job-function`
  - Example: `--job-function it,mktg` for IT and Marketing functions

- **Industry Filters (f_SB2)**
  - Support for industry codes (numeric strings)
  - Multiple industries can be specified (comma-separated)
  - Command-line argument: `--industry`
  - Example: `--industry 96,4` for Information Technology and Services (96) and Computer Software (4)
  - See `Docs/Linkedin_search_query.md` for complete industry codes list

- **Sorting Options (sortBy)**
  - Date Descending (DD): Sort by newest jobs first
  - Relevance (R): Default sorting by relevance
  - Command-line argument: `--sort-by`
  - Example: `--sort-by DD` for newest jobs first

- **Advanced Location Filters**
  - City ID filter (f_PP): Filter by specific city using numeric city ID
  - Command-line argument: `--city-id`
  - Company ID filter (f_C): Filter by specific company using numeric company ID
  - Command-line argument: `--company-id`

#### Enhanced URL Builder
- **Comprehensive Filter Support**
  - `JobSearch._build_search_url()` now supports all major LinkedIn search parameters
  - Automatic validation of filter values
  - Support for multiple values (comma-separated strings or lists)
  - Proper URL encoding for all parameters
  - Filter codes defined as class constants for easy reference

#### Command-Line Interface Enhancements
- **Extended CLI Arguments**
  - All filters available as command-line arguments in `search_jobs.py`
  - Backward compatible with existing positional arguments
  - Comprehensive help text with examples
  - Filter validation and error handling

### Changed

- **JobSearch.search_jobs() Method**
  - Extended method signature to accept all filter parameters
  - Filters are now passed as keyword arguments
  - Improved logging for applied filters
  - Better parameter documentation

- **search_jobs.py CLI**
  - Enhanced argument parser with all filter options
  - Support for combining multiple filters
  - Improved examples in help text
  - Filter parameters passed to search functions via dictionary

- **URL Building Logic**
  - Enhanced `_build_search_url()` to handle all LinkedIn search parameters
  - Improved parameter validation
  - Better handling of multiple values (comma-separated)
  - Automatic URL encoding

### Technical Details

#### Filter Implementation
- All filters are implemented according to LinkedIn's URL parameter specification
- Filter values are validated against predefined constants
- Multiple values are joined with commas (URL-encoded as `%2C`)
- Boolean filters use `true`/`false` string values
- Numeric filters (geo_id, city_id, company_id, industry) accept string or numeric inputs

#### Code Organization
- Filter codes defined as class constants in `JobSearch` class
- Constants include: `JOB_TYPE_CODES`, `EXPERIENCE_LEVEL_CODES`, `WORK_TYPE_CODES`, `JOB_FUNCTION_CODES`, `SORT_OPTIONS`
- Easy to extend with new filter options in the future

---

## [5.1.0] - 2025-11-05

### Added

#### Job Extractor Enhancements
- **Job Card Extraction**
  - Extracts job card component alongside job description
  - Supports both logged-in users (`div.artdeco-card`) and not logged-in users (`section.top-card-layout`)
  - Automatically detects which selector to use based on page structure
  - Job card includes job header information (title, company, location, etc.)

- **Enhanced HTML Output**
  - `save_job_description()` now saves both job card and job description in a single HTML file
  - Includes styled HTML structure with proper sections
  - Job card and job description are clearly separated with headers
  - Basic CSS styling for better readability

### Changed

- **Job Extraction Return Value**
  - `extract_job_details()` now returns `job_card` field in addition to `job_description`
  - Success logic updated: extraction succeeds if either job card or job description is found
  - Result dictionary includes: `job_id`, `job_description`, `job_card`, `success`, `error`

- **HTML Output Format**
  - Output HTML file now contains complete document structure with `<head>`, `<body>`, and styling
  - Job ID displayed at the top if available
  - Each component (job card, job description) in its own styled section

### Fixed

- **Syntax Error**: Fixed Unicode curly apostrophe (U+2019) in string literals that caused SyntaxError
  - Replaced with standard ASCII apostrophes (U+27)
  - Affected line 178 in `job_extractor.py`

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
4. Extract job card (for logged-in: `div.artdeco-card`, for not logged-in: `section.top-card-layout`)
5. Extract job description (multiple fallback selectors)
6. Return structured result dictionary with job_id, job_description, and job_card

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
- **5.2.0**: Advanced LinkedIn job search filters (job type, experience, work type, easy apply, etc.), enhanced CLI with filter arguments
- **5.1.0**: Job card extraction, enhanced HTML output with styled sections, fixed Unicode syntax error
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


