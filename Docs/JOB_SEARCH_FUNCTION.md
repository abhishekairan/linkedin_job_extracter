# LinkedIn Job Search Function Documentation

## Overview

The LinkedIn Job Search function provides a comprehensive interface for searching LinkedIn jobs with advanced filtering capabilities. It supports all major LinkedIn search parameters, allowing you to build precise, targeted job searches through both command-line interface and programmatic API.

## Table of Contents

1. [Architecture](#architecture)
2. [Core Components](#core-components)
3. [Search Parameters](#search-parameters)
4. [Filter Options](#filter-options)
5. [Command-Line Usage](#command-line-usage)
6. [Programmatic Usage](#programmatic-usage)
7. [URL Building Process](#url-building-process)
8. [Filter Combinations](#filter-combinations)
9. [Examples](#examples)
10. [Best Practices](#best-practices)

---

## Architecture

### Components

1. **JobSearch Class** (`linkedin_scraper/job_search.py`)
   - Core search functionality
   - URL building with filter support
   - Login detection and handling
   - Job ID extraction

2. **CLI Interface** (`search_jobs.py`)
   - Command-line argument parsing
   - Filter parameter processing
   - Results output and file saving

3. **Browser Service Integration**
   - Connects to persistent browser instance
   - Handles authentication automatically
   - Maintains session for multiple searches

### Search Flow

```
1. Build Search URL with Parameters
   ↓
2. Navigate to LinkedIn Job Search Page
   ↓
3. Check if Login Required
   ↓
4. Login if Needed (On-Demand)
   ↓
5. Extract Job IDs from Search Results
   ↓
6. Scroll to Load More Results
   ↓
7. Return List of Job IDs
   ↓
8. Convert Job IDs to Job Links Dictionary
```

---

## Core Components

### JobSearch Class

The `JobSearch` class is the main interface for performing job searches.

#### Key Methods

- **`search_jobs()`**: Main search method that accepts all filter parameters
- **`_build_search_url()`**: Builds LinkedIn search URL with query parameters
- **`extract_jobs()`**: Converts job IDs to dictionary of job links
- **`_is_login_required()`**: Detects if LinkedIn requires login
- **`_scroll_to_load_more()`**: Scrolls page to load additional results

#### Filter Constants

The class defines constants for all filter codes:

- `JOB_TYPE_CODES`: Job type filter codes (F, P, C, T, I, V)
- `EXPERIENCE_LEVEL_CODES`: Experience level codes (1-6)
- `WORK_TYPE_CODES`: Work type codes (1, 2, 3)
- `JOB_FUNCTION_CODES`: Job function codes (sale, mgmt, acct, it, mktg, hr)
- `SORT_OPTIONS`: Sort option codes (DD, R)
- `TIME_FILTERS`: Time filter codes (r3600, r86400, etc.)

---

## Search Parameters

### Required Parameters

- **`keywords`** (str): Job search keywords or job titles
  - Example: `"Python Developer"`, `"Data Scientist"`, `"Software Engineer"`

### Optional Core Parameters

- **`location`** (str): Job location filter
  - Example: `"United States"`, `"New York"`, `"San Francisco"`
  
- **`geo_id`** (str): LinkedIn geo ID for location (more precise than location name)
  - Example: `"103644278"` (United States), `"104514075"` (Germany)
  - See `Docs/Linkedin_search_query.md` for geo ID codes

- **`distance`** (int): Search radius in miles/km from location
  - Default: `120`
  - Example: `25`, `50`, `100`

- **`time_filter`** (str): Time filter for job posting date
  - Options: `'any'`, `'1hour'`, `'2hours'`, `'3hours'`, `'4hours'`, `'6hours'`, `'8hours'`, `'12hours'`, `'1day'`, `'week'`, `'month'`
  - Example: `'week'` for jobs posted in the last week

---

## Filter Options

### 1. Job Type Filters (f_JT)

Filter jobs by employment type.

**Codes:**
- `F`: Full-time
- `P`: Part-time
- `C`: Contract
- `T`: Temporary
- `I`: Internship
- `V`: Volunteer

**Usage:**
- Single: `job_types='F'`
- Multiple: `job_types='F,C'` or `job_types=['F', 'C']`

**Command-line:**
```bash
--jobtype F
--jobtype F,C
```

### 2. Experience Level Filters (f_E)

Filter jobs by experience level required.

**Codes:**
- `1`: Internship
- `2`: Entry level
- `3`: Associate
- `4`: Mid-Senior level
- `5`: Director
- `6`: Executive

**Usage:**
- Single: `experience_levels='4'`
- Multiple: `experience_levels='4,5,6'` or `experience_levels=['4', '5', '6']`

**Command-line:**
```bash
--experience 4
--experience 4,5,6
```

### 3. Work Type Filters (f_WT)

Filter jobs by work location type.

**Codes:**
- `1`: On-site
- `2`: Hybrid
- `3`: Remote

**Usage:**
- Single: `work_types='3'`
- Multiple: `work_types='2,3'` or `work_types=['2', '3']`

**Command-line:**
```bash
--worktype 3
--worktype 2,3
```

### 4. Easy Apply Filter (f_EA)

Filter for jobs with Easy Apply enabled.

**Values:**
- `True`: Easy Apply jobs only
- `False`: All jobs (including external applications)

**Usage:**
- `easy_apply=True`

**Command-line:**
```bash
--easy-apply        # Enable filter
--no-easy-apply     # Disable filter (include all jobs)
```

### 5. Actively Hiring Filter (f_AL)

Filter for companies actively hiring.

**Values:**
- `True`: Companies actively hiring only
- `False`: All companies

**Usage:**
- `actively_hiring=True`

**Command-line:**
```bash
--actively-hiring        # Enable filter
--no-actively-hiring     # Disable filter
```

### 6. Verified Jobs Filter (f_VJ)

Filter for verified job postings only (helps avoid scams).

**Values:**
- `True`: Verified jobs only
- `False`: All job postings

**Usage:**
- `verified_jobs=True`

**Command-line:**
```bash
--verified-jobs        # Enable filter
--no-verified-jobs     # Disable filter
```

### 7. Jobs at Connections Filter (f_JIYN)

Filter for jobs at companies where you have LinkedIn connections.

**Values:**
- `True`: Jobs at companies with connections only
- `False`: All jobs

**Usage:**
- `jobs_at_connections=True`
- **Note:** Requires LinkedIn login

**Command-line:**
```bash
--jobs-at-connections        # Enable filter
--no-jobs-at-connections     # Disable filter
```

### 8. Job Function Filters (f_F)

Filter jobs by job function/department.

**Codes:**
- `sale`: Sales
- `mgmt`: Management
- `acct`: Accounting
- `it`: Information Technology
- `mktg`: Marketing
- `hr`: Human Resources

**Usage:**
- Single: `job_function='it'`
- Multiple: `job_function='it,mktg'` or `job_function=['it', 'mktg']`

**Command-line:**
```bash
--job-function it
--job-function it,mktg
```

### 9. Industry Filters (f_SB2)

Filter jobs by industry using numeric industry codes.

**Common Codes:**
- `4`: Computer Software
- `5`: Computer Networking
- `9`: Law Practice
- `96`: Information Technology and Services
- `80`: Marketing and Advertising

**Usage:**
- Single: `industry='96'`
- Multiple: `industry='96,4'` or `industry=['96', '4']`
- See `Docs/Linkedin_search_query.md` for complete industry codes list

**Command-line:**
```bash
--industry 96
--industry 96,4
```

### 10. Sorting Options (sortBy)

Sort search results.

**Options:**
- `DD`: Date Descending (newest jobs first)
- `R`: Relevance (default sorting)

**Usage:**
- `sort_by='DD'`

**Command-line:**
```bash
--sort-by DD    # Newest first
--sort-by R     # Relevance (default)
```

### 11. Advanced Location Filters

#### City ID Filter (f_PP)

Filter by specific city using numeric city ID.

**Usage:**
- `city_id='104842695'` (Delhi-NCR)

**Command-line:**
```bash
--city-id 104842695
```

#### Company ID Filter (f_C)

Filter by specific company using numeric company ID.

**Usage:**
- `company_id='123456'`

**Command-line:**
```bash
--company-id 123456
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

# With location
python search_jobs.py "Data Scientist" "New York"

# Multiple keywords/locations
python search_jobs.py --keywords "Python Developer,Data Scientist" --locations "United States,New York"
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

#### Complex Filter Combinations

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

### Advanced Examples

#### Using Geo ID

```bash
# More precise location using geo ID
python search_jobs.py "Developer" --geo-id 103644278 --distance 50
```

#### Multiple Searches

```bash
# Search multiple keywords and locations
python search_jobs.py \
  --keywords "Python Developer,Data Scientist,Software Engineer" \
  --locations "New York,San Francisco,Seattle" \
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

# Perform search
job_ids = job_search.search_jobs(
    keywords="Python Developer",
    location="United States"
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
    location="United States",
    job_types="F",
    work_types="3",
    easy_apply=True,
    time_filter="week",
    sort_by="DD"
)

# Mid-Senior to Executive levels in IT industry
job_ids = job_search.search_jobs(
    keywords="Director",
    location="United States",
    experience_levels=["4", "5", "6"],
    job_function="it",
    industry="96,4",
    actively_hiring=True
)
```

### Multiple Values

```python
# Multiple job types and work types
job_ids = job_search.search_jobs(
    keywords="Developer",
    location="New York",
    job_types="F,C",  # Full-time and Contract
    work_types=["2", "3"],  # Hybrid and Remote (list format)
    experience_levels="4,5"  # Mid-Senior and Director
)
```

### Complete Example

```python
from linkedin_scraper.job_search import JobSearch
from linkedin_scraper.browser_manager import BrowserManager
import json

# Initialize
browser_manager = BrowserManager()
driver = browser_manager.get_or_create_browser()
job_search = JobSearch(driver)

# Search with multiple filters
job_ids = job_search.search_jobs(
    keywords="Senior Software Engineer",
    location="United States",
    geo_id="103644278",
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

## URL Building Process

### URL Structure

LinkedIn job search URLs follow this structure:

```
https://www.linkedin.com/jobs/search-results/?<parameters>
```

### Parameter Encoding

- Parameters are separated by `&`
- Spaces are encoded as `%20`
- Commas are encoded as `%2C`
- Multiple values are comma-separated (e.g., `f_JT=F%2CC`)

### Example URL

```
https://www.linkedin.com/jobs/search-results/?keywords=Software%20Engineer&geoId=103644278&f_JT=F&f_WT=2%2C3&f_E=4%2C5&f_EA=true&f_TPR=r604800&sortBy=DD
```

This URL searches for:
- Keywords: "Software Engineer"
- Location: United States (geoId: 103644278)
- Job Type: Full-time (F)
- Work Type: Hybrid and Remote (2,3)
- Experience: Mid-Senior and Director (4,5)
- Easy Apply: Enabled
- Time Filter: Last week (r604800)
- Sort: Date Descending (DD)

### Internal URL Building

The `_build_search_url()` method:

1. Validates all filter parameters
2. Converts filter values to LinkedIn parameter codes
3. Joins multiple values with commas
4. URL-encodes all parameters
5. Builds complete search URL

---

## Filter Combinations

### Common Combinations

#### 1. Remote Tech Jobs

```bash
python search_jobs.py "Software Engineer" \
  --location "United States" \
  --jobtype F \
  --worktype 3 \
  --job-function it \
  --industry 96,4
```

#### 2. Recent Easy Apply Jobs

```bash
python search_jobs.py "Developer" \
  --location "New York" \
  --easy-apply \
  --time-filter 1day \
  --sort-by DD
```

#### 3. Senior Management Roles

```bash
python search_jobs.py "Director" \
  --location "United States" \
  --jobtype F \
  --experience 5,6 \
  --job-function mgmt \
  --actively-hiring
```

#### 4. Entry Level Positions

```bash
python search_jobs.py "Software Engineer" \
  --location "United States" \
  --experience 1,2 \
  --jobtype F,I
```

### Best Practices for Combinations

1. **Start Broad, Then Narrow**: Begin with keywords and location, then add filters
2. **Use Time Filters**: Combine with `--time-filter week` and `--sort-by DD` for fresh opportunities
3. **Combine Boolean Filters**: Use `--easy-apply` with `--actively-hiring` for better results
4. **Multiple Work Types**: Include `--worktype 2,3` for hybrid and remote flexibility
5. **Experience Ranges**: Use multiple experience levels like `--experience 4,5,6` for senior roles

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
    location="United States",
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
    location="United States",
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
  --location "United States" \
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
    location="United States",
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

---

## Best Practices

### 1. Use Time Filters

Always combine searches with time filters to find fresh opportunities:

```bash
--time-filter week --sort-by DD
```

### 2. Combine Boolean Filters

Use multiple boolean filters for better results:

```bash
--easy-apply --actively-hiring --verified-jobs
```

### 3. Use Multiple Work Types

Include both hybrid and remote for flexibility:

```bash
--worktype 2,3
```

### 4. Start with Broad Keywords

Begin with general keywords, then narrow with filters:

```bash
python search_jobs.py "Engineer" --location "United States" --job-function it
```

### 5. Use Geo ID for Precision

Use `--geo-id` instead of location name for more precise results:

```bash
--geo-id 103644278  # United States
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
--keywords "Python,Java,JavaScript" --locations "New York,San Francisco,Seattle"
```

---

## Troubleshooting

### Common Issues

1. **No Results Found**
   - Try broadening filters (remove some filters)
   - Check if keywords are too specific
   - Verify location is correct

2. **Login Required**
   - The system automatically handles login when needed
   - Ensure `.env` has correct credentials
   - Set `HEADLESS_MODE=False` if CAPTCHA is required

3. **Invalid Filter Values**
   - Check filter codes against documentation
   - Ensure comma-separated values are correctly formatted
   - Verify industry codes are numeric

4. **Rate Limiting**
   - Wait between searches (system includes automatic rate limiting)
   - Reduce number of searches per session
   - Use longer delays for multiple searches

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

### Common Geo IDs

| Location | Geo ID |
|----------|--------|
| United States | 103644278 |
| United Kingdom | 104738473 |
| Germany | 104514075 |
| India | 102713980 |
| Canada | 103720260 |

See `Docs/Linkedin_search_query.md` for complete lists of geo IDs and industry codes.

---

## Additional Resources

- **LinkedIn Search Query Documentation**: `Docs/Linkedin_search_query.md`
- **Job Search Service Documentation**: `JOB_SEARCH_SERVICE.md`
- **Project Documentation**: `PROJECT.md`
- **Changelog**: `CHANGELOG.md`

---

## Support

For issues, questions, or contributions, please refer to the project repository or documentation.

