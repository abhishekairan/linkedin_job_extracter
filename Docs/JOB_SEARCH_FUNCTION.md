# LinkedIn Job Search Function Documentation

## Overview

The LinkedIn Job Search function provides a comprehensive interface for searching LinkedIn jobs with advanced filtering capabilities. It supports all major LinkedIn search parameters, allowing you to build precise, targeted job searches through both command-line interface and programmatic API.

**Key Features:**
- ✅ Automatic location-to-geo-id conversion
- ✅ Location filtering through URL parameters (geo-id)
- ✅ Multiple keywords and locations support
- ✅ Comprehensive filter options
- ✅ On-demand login detection
- ✅ Persistent browser sessions

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Architecture](#architecture)
3. [Location & Geo-ID System](#location--geo-id-system)
4. [Search Parameters](#search-parameters)
5. [Filter Options](#filter-options)
6. [Command-Line Usage](#command-line-usage)
7. [Programmatic Usage](#programmatic-usage)
8. [Examples](#examples)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)
11. [Reference](#reference)

---

## Quick Start

### Basic Command-Line Usage

```bash
# Simple search
python search_jobs.py "Python Developer"

# With location (automatically converted to geo-id)
python search_jobs.py "Data Scientist" "United States"

# Multiple keywords and locations
python search_jobs.py --keywords "Python Developer,Data Scientist" --locations "United States,Germany"

# Using geo-id directly
python search_jobs.py "Software Engineer" --geo-id 103644278
```

### Basic Programmatic Usage

```python
from linkedin_scraper.job_search import JobSearch
from linkedin_scraper.browser_manager import BrowserManager

# Initialize
browser_manager = BrowserManager()
driver = browser_manager.get_or_create_browser()
job_search = JobSearch(driver)

# Search
job_ids = job_search.search_jobs(
    keywords="Python Developer",
    geo_id="103644278"  # United States
)

# Extract results
jobs = job_search.extract_jobs(job_ids)
print(f"Found {len(jobs)} jobs")
```

---

## Architecture

### Components

#### 1. **Geo-ID Module** (`geo_id.py`)
- Location name to geo-id mapping
- Automatic conversion of location names to LinkedIn geo-ids
- Supports both location names and numeric geo-ids
- Location filtering applied through URL parameters

#### 2. **JobSearch Class** (`linkedin_scraper/job_search.py`)
- Core search functionality
- URL building with filter support
- Login detection and handling
- Job ID extraction

#### 3. **CLI Interface** (`search_jobs.py`)
- Command-line argument parsing
- Location-to-geo-id conversion
- Filter parameter processing
- Results output and file saving

#### 4. **Browser Service Integration**
- Connects to persistent browser instance
- Handles authentication automatically
- Maintains session for multiple searches

### Search Flow

```
1. Convert Locations to Geo-IDs (if needed)
   ↓
2. Build Search URL with Parameters (using geoId)
   ↓
3. Navigate to LinkedIn Job Search Page
   ↓
4. Check if Login Required
   ↓
5. Login if Needed (On-Demand)
   ↓
6. Extract Job IDs from Search Results
   ↓
7. Scroll to Load More Results
   ↓
8. Return List of Job IDs
   ↓
9. Convert Job IDs to Job Links Dictionary
```

### Key Methods

- **`search_jobs()`**: Main search method that accepts all filter parameters
- **`_build_search_url()`**: Builds LinkedIn search URL with query parameters (prioritizes geo_id)
- **`extract_jobs()`**: Converts job IDs to dictionary of job links
- **`_is_login_required()`**: Detects if LinkedIn requires login
- **`_scroll_to_load_more()`**: Scrolls page to load additional results

---

## Location & Geo-ID System

### Overview

The system uses **geo-ids** for location filtering, which are applied through URL parameters. Location names are automatically converted to geo-ids using the `geo_id.py` module.

### How It Works

1. **Location names** (e.g., "United States", "Germany") are automatically converted to geo-ids
2. **Geo-ids** are applied directly to the URL using the `geoId` parameter
3. For each location, all job titles are searched (location × keyword matrix)

### Usage Options

#### Option 1: Location Names (Recommended)
```bash
# Automatically converted to geo-id
python search_jobs.py "Developer" "United States"
python search_jobs.py "Developer" --locations "United States,Germany"
```

#### Option 2: Geo-IDs Directly
```bash
# Use numeric geo-ids directly
python search_jobs.py "Developer" --geo-id 103644278
python search_jobs.py "Developer" --geo-id "103644278,104514075"
```

#### Option 3: Mixed (Names and Geo-IDs)
```bash
# Mix location names and geo-ids
python search_jobs.py "Developer" --locations "United States,103644278,Germany"
```

### Supported Locations

The `geo_id.py` module includes mappings for:

- **Countries**: United States, United Kingdom, Germany, France, India, Canada, Australia, and more
- **Indian Cities**: Bengaluru, Hyderabad, Pune, Chennai, Delhi-NCR, Mumbai, Kochi
- **US Cities**: New York, San Francisco, Los Angeles, Chicago, Seattle, and more

### Common Geo-IDs

| Location | Geo ID |
|----------|--------|
| United States | 103644278 |
| United Kingdom | 104738473 |
| Germany | 104514075 |
| France | 104016111 |
| India | 102713980 |
| Canada | 103720260 |
| Australia | 104057199 |

> **Note**: See `Docs/Linkedin_search_query.md` for complete geo-ID reference.

### Search Behavior

When multiple locations and keywords are provided:
- **For each location**, **each keyword** is searched
- Results are combined and deduplicated automatically
- Example: 2 locations × 3 keywords = 6 searches

---

## Search Parameters

### Required Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `keywords` | str | Job search keywords or job titles | `"Python Developer"` |

### Core Location Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `location` | str | Location name (converted to geo-id automatically) | `"United States"` |
| `geo_id` | str | LinkedIn geo-id (takes precedence over location) | `"103644278"` |
| `distance` | int | Search radius in miles/km (default: 120) | `50`, `100` |

### Time Filter

| Parameter | Type | Options | Example |
|-----------|------|---------|---------|
| `time_filter` | str | `any`, `1hour`, `2hours`, `3hours`, `4hours`, `6hours`, `8hours`, `12hours`, `1day`, `week`, `month` | `week` |

---

## Filter Options

### 1. Job Type Filters (f_JT)

Filter jobs by employment type.

| Code | Description |
|------|-------------|
| `F` | Full-time |
| `P` | Part-time |
| `C` | Contract |
| `T` | Temporary |
| `I` | Internship |
| `V` | Volunteer |

**Usage:**
```bash
--jobtype F              # Single
--jobtype F,C            # Multiple
```

```python
job_types="F"            # Single
job_types="F,C"          # Multiple (string)
job_types=["F", "C"]     # Multiple (list)
```

### 2. Experience Level Filters (f_E)

Filter jobs by experience level required.

| Code | Description |
|------|-------------|
| `1` | Internship |
| `2` | Entry level |
| `3` | Associate |
| `4` | Mid-Senior level |
| `5` | Director |
| `6` | Executive |

**Usage:**
```bash
--experience 4           # Single
--experience 4,5,6       # Multiple
```

```python
experience_levels="4"            # Single
experience_levels="4,5,6"        # Multiple (string)
experience_levels=["4", "5", "6"]  # Multiple (list)
```

### 3. Work Type Filters (f_WT)

Filter jobs by work location type.

| Code | Description |
|------|-------------|
| `1` | On-site |
| `2` | Hybrid |
| `3` | Remote |

**Usage:**
```bash
--worktype 3            # Remote only
--worktype 2,3          # Hybrid and Remote
```

```python
work_types="3"          # Remote only
work_types="2,3"        # Hybrid and Remote
```

### 4. Easy Apply Filter (f_EA)

Filter for jobs with Easy Apply enabled.

**Usage:**
```bash
--easy-apply           # Enable filter
--no-easy-apply        # Disable filter
```

```python
easy_apply=True        # Enable
easy_apply=False       # Disable
```

### 5. Actively Hiring Filter (f_AL)

Filter for companies actively hiring.

**Usage:**
```bash
--actively-hiring      # Enable filter
--no-actively-hiring   # Disable filter
```

```python
actively_hiring=True   # Enable
```

### 6. Verified Jobs Filter (f_VJ)

Filter for verified job postings only (helps avoid scams).

**Usage:**
```bash
--verified-jobs        # Enable filter
--no-verified-jobs     # Disable filter
```

```python
verified_jobs=True     # Enable
```

### 7. Jobs at Connections Filter (f_JIYN)

Filter for jobs at companies where you have LinkedIn connections.

**Usage:**
```bash
--jobs-at-connections  # Enable filter
```

```python
jobs_at_connections=True  # Enable (requires login)
```

### 8. Job Function Filters (f_F)

Filter jobs by job function/department.

| Code | Description |
|------|-------------|
| `sale` | Sales |
| `mgmt` | Management |
| `acct` | Accounting |
| `it` | Information Technology |
| `mktg` | Marketing |
| `hr` | Human Resources |

**Usage:**
```bash
--job-function it           # Single
--job-function it,mktg      # Multiple
```

```python
job_function="it"           # Single
job_function="it,mktg"      # Multiple
```

### 9. Industry Filters (f_SB2)

Filter jobs by industry using numeric industry codes.

**Common Codes:**
- `4`: Computer Software
- `5`: Computer Networking
- `96`: Information Technology and Services
- `80`: Marketing and Advertising

**Usage:**
```bash
--industry 96          # Single
--industry 96,4        # Multiple
```

```python
industry="96"          # Single
industry="96,4"        # Multiple
```

> **Note**: See `Docs/Linkedin_search_query.md` for complete industry codes.

### 10. Sorting Options (sortBy)

Sort search results.

| Option | Description |
|--------|-------------|
| `DD` | Date Descending (newest jobs first) |
| `R` | Relevance (default) |

**Usage:**
```bash
--sort-by DD    # Newest first
--sort-by R     # Relevance
```

```python
sort_by="DD"    # Newest first
sort_by="R"     # Relevance
```

### 11. Advanced Filters

#### City ID Filter (f_PP)
```bash
--city-id 104842695
```
```python
city_id="104842695"
```

#### Company ID Filter (f_C)
```bash
--company-id 123456
```
```python
company_id="123456"
```

---

## Command-Line Usage

### Basic Syntax

```bash
python search_jobs.py <keywords> [location] [output_file] [filter_options]
```

### Basic Examples

```bash
# Simple search
python search_jobs.py "Python Developer"

# With location (converted to geo-id automatically)
python search_jobs.py "Data Scientist" "United States"

# Multiple keywords and locations
python search_jobs.py --keywords "Python Developer,Data Scientist" --locations "United States,Germany"

# Using geo-id directly
python search_jobs.py "Software Engineer" --geo-id 103644278
```

### Filter Examples

#### Job Type and Work Type
```bash
# Full-time remote jobs
python search_jobs.py "Software Engineer" --location "United States" --jobtype F --worktype 3

# Full-time and contract, hybrid or remote
python search_jobs.py "Developer" --location "New York" --jobtype F,C --worktype 2,3
```

#### Experience Level
```bash
# Mid-Senior to Executive levels
python search_jobs.py "Director" --location "United States" --experience 4,5,6

# Entry level positions
python search_jobs.py "Software Engineer" --experience 2
```

#### Time Filter and Sorting
```bash
# Jobs posted in the last week, sorted by newest first
python search_jobs.py "Python Developer" --location "United States" --time-filter week --sort-by DD

# Jobs posted in the last 24 hours
python search_jobs.py "Data Scientist" --time-filter 1day
```

#### Easy Apply and Actively Hiring
```bash
# Easy Apply jobs from actively hiring companies
python search_jobs.py "Marketing Manager" --location "United States" --easy-apply --actively-hiring

# Verified jobs only
python search_jobs.py "Software Engineer" --verified-jobs
```

#### Job Function and Industry
```bash
# IT and Marketing functions in tech industry
python search_jobs.py "Manager" --location "United States" --job-function it,mktg --industry 96,4

# Sales roles
python search_jobs.py "Sales" --job-function sale
```

### Complex Filter Combinations

```bash
# Full-time remote senior developer jobs with Easy Apply, posted this week
python search_jobs.py "Senior Software Engineer" \
  --location "United States" \
  --jobtype F \
  --worktype 3 \
  --experience 4,5 \
  --easy-apply \
  --time-filter week \
  --sort-by DD

# Director/Executive level management roles at actively hiring companies
python search_jobs.py "Director" \
  --location "United States" \
  --jobtype F \
  --experience 5,6 \
  --job-function mgmt \
  --actively-hiring \
  --verified-jobs
```

### Multiple Searches

```bash
# Search multiple keywords and locations (each location × each keyword)
python search_jobs.py \
  --keywords "Python Developer,Data Scientist,Software Engineer" \
  --locations "United States,Germany,United Kingdom" \
  --jobtype F \
  --worktype 2,3 \
  --output results.json
```

---

## Programmatic Usage

### Basic Usage

```python
from linkedin_scraper.job_search import JobSearch
from linkedin_scraper.browser_manager import BrowserManager

# Get browser instance
browser_manager = BrowserManager()
driver = browser_manager.get_or_create_browser()

# Create JobSearch instance
job_search = JobSearch(driver)

# Perform search with geo-id
job_ids = job_search.search_jobs(
    keywords="Python Developer",
    geo_id="103644278"  # United States
)

# Convert to job links
jobs = job_search.extract_jobs(job_ids)
print(f"Found {len(jobs)} jobs")
```

### Using Filters

```python
# Full-time remote jobs with Easy Apply
job_ids = job_search.search_jobs(
    keywords="Software Engineer",
    geo_id="103644278",
    job_types="F",
    work_types="3",
    easy_apply=True,
    time_filter="week",
    sort_by="DD"
)

# Mid-Senior to Executive levels in IT industry
job_ids = job_search.search_jobs(
    keywords="Director",
    geo_id="103644278",
    experience_levels=["4", "5", "6"],
    job_function="it",
    industry="96,4",
    actively_hiring=True
)
```

### Using Location Names (with geo_id module)

```python
from geo_id import get_geo_id

# Convert location name to geo-id
geo_id = get_geo_id("United States")  # Returns "103644278"

# Use in search
job_ids = job_search.search_jobs(
    keywords="Python Developer",
    geo_id=geo_id
)
```

### Complete Example

```python
from linkedin_scraper.job_search import JobSearch
from linkedin_scraper.browser_manager import BrowserManager
from geo_id import get_geo_id
import json

# Initialize
browser_manager = BrowserManager()
driver = browser_manager.get_or_create_browser()
job_search = JobSearch(driver)

# Get geo-id for location
geo_id = get_geo_id("United States")

# Search with multiple filters
job_ids = job_search.search_jobs(
    keywords="Senior Software Engineer",
    geo_id=geo_id,
    distance=50,
    job_types="F",
    work_types="2,3",
    experience_levels="4,5",
    easy_apply=True,
    actively_hiring=True,
    verified_jobs=True,
    job_function="it",
    industry="96,4",
    time_filter="week",
    sort_by="DD"
)

# Extract job links
jobs = job_search.extract_jobs(job_ids)

# Save results
with open("jobs.json", "w") as f:
    json.dump(jobs, f, indent=2)

print(f"Found {len(jobs)} jobs")
```

---

## Examples

### Example 1: Remote Full-Time Developer Jobs

**Command-line:**
```bash
python search_jobs.py "Python Developer" \
  --location "United States" \
  --jobtype F \
  --worktype 3 \
  --time-filter week \
  --sort-by DD \
  --output remote_python_jobs.json
```

**Programmatic:**
```python
job_ids = job_search.search_jobs(
    keywords="Python Developer",
    geo_id="103644278",
    job_types="F",
    work_types="3",
    time_filter="week",
    sort_by="DD"
)
```

### Example 2: Mid-Senior Marketing Roles with Easy Apply

**Command-line:**
```bash
python search_jobs.py "Marketing Manager" \
  --location "United States" \
  --jobtype F \
  --experience 4,5 \
  --job-function mktg \
  --easy-apply \
  --actively-hiring
```

**Programmatic:**
```python
job_ids = job_search.search_jobs(
    keywords="Marketing Manager",
    geo_id="103644278",
    job_types="F",
    experience_levels="4,5",
    job_function="mktg",
    easy_apply=True,
    actively_hiring=True
)
```

### Example 3: Recent Director Positions in Tech

**Command-line:**
```bash
python search_jobs.py "Director" \
  --geo-id 103644278 \
  --jobtype F \
  --experience 5,6 \
  --job-function it \
  --industry 96,4 \
  --worktype 2,3 \
  --time-filter 1day \
  --sort-by DD \
  --verified-jobs
```

**Programmatic:**
```python
job_ids = job_search.search_jobs(
    keywords="Director",
    geo_id="103644278",
    job_types="F",
    experience_levels="5,6",
    job_function="it",
    industry="96,4",
    work_types="2,3",
    time_filter="1day",
    sort_by="DD",
    verified_jobs=True
)
```

### Example 4: Multiple Locations and Keywords

**Command-line:**
```bash
python search_jobs.py \
  --keywords "Python Developer,Data Scientist" \
  --locations "United States,Germany,United Kingdom" \
  --jobtype F \
  --worktype 3 \
  --time-filter week \
  --output multi_location_jobs.json
```

This will perform 6 searches (2 keywords × 3 locations).

---

## Best Practices

### 1. Use Geo-IDs for Precision

Geo-IDs provide more precise location filtering than location names:

```bash
# Preferred: Use geo-id
python search_jobs.py "Developer" --geo-id 103644278

# Also works: Location name (automatically converted)
python search_jobs.py "Developer" --location "United States"
```

### 2. Use Time Filters

Always combine searches with time filters to find fresh opportunities:

```bash
--time-filter week --sort-by DD
```

### 3. Combine Boolean Filters

Use multiple boolean filters for better results:

```bash
--easy-apply --actively-hiring --verified-jobs
```

### 4. Use Multiple Work Types

Include both hybrid and remote for flexibility:

```bash
--worktype 2,3
```

### 5. Start with Broad Keywords

Begin with general keywords, then narrow with filters:

```bash
python search_jobs.py "Engineer" --location "United States" --job-function it
```

### 6. Rate Limiting

The system includes automatic rate limiting. Avoid making too many rapid searches to prevent account flagging.

### 7. Save Results

Always save results to a file for later analysis:

```bash
--output results.json
```

### 8. Multiple Keywords/Locations

Use multiple keywords and locations for comprehensive searches:

```bash
--keywords "Python,Java,JavaScript" --locations "United States,Germany,United Kingdom"
```

---

## Troubleshooting

### Common Issues

#### 1. No Results Found
- **Solution**: Try broadening filters (remove some filters)
- **Check**: Verify keywords are not too specific
- **Verify**: Location/geo-id is correct

#### 2. Login Required
- **Solution**: The system automatically handles login when needed
- **Ensure**: `.env` has correct credentials
- **Set**: `HEADLESS_MODE=False` if CAPTCHA is required

#### 3. Invalid Filter Values
- **Solution**: Check filter codes against documentation
- **Verify**: Comma-separated values are correctly formatted
- **Check**: Industry codes are numeric

#### 4. Rate Limiting
- **Solution**: Wait between searches (system includes automatic rate limiting)
- **Reduce**: Number of searches per session
- **Use**: Longer delays for multiple searches

#### 5. Location Not Found
- **Solution**: Use geo-id directly if location name is not recognized
- **Check**: Verify location name spelling
- **Use**: `--geo-id` with numeric geo-id directly

---

## Reference

### Filter Codes Summary

| Filter | Parameter | Codes | Example |
|--------|-----------|-------|---------|
| Job Type | f_JT | F, P, C, T, I, V | `F,C` |
| Experience | f_E | 1-6 | `4,5,6` |
| Work Type | f_WT | 1, 2, 3 | `2,3` |
| Easy Apply | f_EA | true/false | `true` |
| Actively Hiring | f_AL | true/false | `true` |
| Verified Jobs | f_VJ | true/false | `true` |
| Jobs at Connections | f_JIYN | true/false | `true` |
| Job Function | f_F | sale, mgmt, acct, it, mktg, hr | `it,mktg` |
| Industry | f_SB2 | Numeric codes | `96,4` |
| Sort | sortBy | DD, R | `DD` |

### Time Filter Options

| Option | Value | Description |
|--------|-------|-------------|
| any | None | No time filter |
| 1hour | r3600 | Last hour |
| 2hours | r7200 | Last 2 hours |
| 3hours | r10800 | Last 3 hours |
| 4hours | r14400 | Last 4 hours |
| 6hours | r21600 | Last 6 hours |
| 8hours | r28800 | Last 8 hours |
| 12hours | r43200 | Last 12 hours |
| 1day | r86400 | Last 24 hours |
| week | r604800 | Last week |
| month | r2592000 | Last month |

### Common Geo-IDs

| Location | Geo ID |
|----------|--------|
| United States | 103644278 |
| United Kingdom | 104738473 |
| Germany | 104514075 |
| France | 104016111 |
| India | 102713980 |
| Canada | 103720260 |
| Australia | 104057199 |
| Netherlands | 102890883 |
| Spain | 104277358 |
| Italy | 103350519 |

> **Note**: See `Docs/Linkedin_search_query.md` for complete lists of geo-IDs and industry codes.

### URL Building

LinkedIn job search URLs use the `geoId` parameter for location filtering:

```
https://www.linkedin.com/jobs/search-results/?keywords=Software%20Engineer&geoId=103644278&f_JT=F&f_WT=2%2C3
```

The system automatically:
1. Converts location names to geo-ids
2. Builds URLs with `geoId` parameter
3. Applies all filters as URL parameters

---

## Additional Resources

- **LinkedIn Search Query Documentation**: `Docs/Linkedin_search_query.md`
- **Job Search Service Documentation**: `Docs/JOB_SEARCH_SERVICE.md`
- **Project Documentation**: `Docs/PROJECT.md`
- **Changelog**: `CHANGELOG.md`

---

## Support

For issues, questions, or contributions, please refer to the project repository or documentation.
