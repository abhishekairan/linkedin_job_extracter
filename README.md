# LinkedIn Job Scraper

A Python automation tool that maintains a persistent Chrome browser instance to search LinkedIn for jobs and extract job listings using JavaScript injection.

## Features

- **Persistent Browser Session**: Maintains a single Chrome process to avoid repeated logins
- **Secure Credential Management**: Stores credentials in `.env` file (never hardcoded)
- **Cross-Platform Support**: Primary focus on Linux, secondary support for Windows
- **Account Protection**: Minimizes login attempts to avoid account flagging
- **Job Data Extraction**: Returns results as dictionary format `{job_id: job_link}`

## Installation

### Prerequisites

- Python 3.7 or higher
- Chrome browser installed
- ChromeDriver installed and accessible in PATH

## Installation on Linux VPS

### Step 1: Update System Packages

```bash
# For Ubuntu/Debian
sudo apt update && sudo apt upgrade -y

# For CentOS/RHEL
sudo yum update -y
```

### Step 2: Install Python and pip

```bash
# For Ubuntu/Debian
sudo apt install python3 python3-pip python3-venv -y

# For CentOS/RHEL
sudo yum install python3 python3-pip -y

# Verify installation
python3 --version
pip3 --version
```

### Step 3: Install System Dependencies for Chrome

```bash
# For Ubuntu/Debian
sudo apt install -y \
    wget \
    curl \
    unzip \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xdg-utils \
    libu2f-udev \
    libvulkan1

# For CentOS/RHEL
sudo yum install -y \
    wget \
    curl \
    unzip \
    gnupg \
    ca-certificates \
    liberation-fonts \
    alsa-lib \
    atk \
    cups-libs \
    dbus-glib \
    gtk3 \
    libXcomposite \
    libXcursor \
    libXdamage \
    libXext \
    libXi \
    libXrandr \
    libXScrnSaver \
    libXtst \
    pango \
    xorg-x11-fonts-100dpi \
    xorg-x11-fonts-75dpi \
    xorg-x11-utils
```

### Step 4: Install Google Chrome or Chromium

**Option A: Install Google Chrome (Recommended)**

```bash
# For Ubuntu/Debian
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update
sudo apt install google-chrome-stable -y

# Verify installation
google-chrome --version
```

**Option B: Install Chromium (Lightweight Alternative)**

```bash
# For Ubuntu/Debian
sudo apt install chromium-browser -y

# For CentOS/RHEL
sudo yum install chromium -y

# Verify installation
chromium-browser --version
# or
chromium --version
```

### Step 5: Install ChromeDriver

**Method 1: Using ChromeDriver Manager (Automatic - Recommended)**

This will be handled automatically if you use a package like `webdriver-manager`, but for manual installation:

```bash
# Get Chrome version
CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d. -f1)
# or for Chromium:
# CHROME_VERSION=$(chromium-browser --version | awk '{print $2}' | cut -d. -f1)

# Download matching ChromeDriver
CHROMEDRIVER_VERSION=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_${CHROME_VERSION}")
wget -O /tmp/chromedriver.zip "https://storage.googleapis.com/chrome-for-testing-public/${CHROMEDRIVER_VERSION}/linux64/chromedriver-linux64.zip"

# Extract and install
unzip /tmp/chromedriver.zip -d /tmp/
sudo mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver
sudo chmod +x /usr/local/bin/chromedriver

# Verify installation
chromedriver --version
```

**Method 2: Manual Installation**

```bash
# Check Chrome version first
google-chrome --version

# Download ChromeDriver matching your Chrome version from:
# https://googlechromelabs.github.io/chrome-for-testing/

# Example for version 120
wget -O /tmp/chromedriver.zip https://storage.googleapis.com/chrome-for-testing-public/120.0.6099.109/linux64/chromedriver-linux64.zip
unzip /tmp/chromedriver.zip -d /tmp/
sudo mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver
sudo chmod +x /usr/local/bin/chromedriver
```

### Step 6: Create Virtual Environment (Recommended)

```bash
# Navigate to project directory
cd /path/to/linkedin-job-scraper

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Verify you're using the venv Python
which python  # Should show: /path/to/venv/bin/python
```

### Step 7: Install Python Dependencies

```bash
# Make sure virtual environment is activated
source venv/bin/activate  # If not already activated

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Verify installation
pip list
```

### Step 8: Configure Environment File

```bash
# Copy example environment file
cp .env.example .env

# Edit the .env file with your credentials
nano .env
# or use vim
# vim .env
```

**Configure `.env` with correct paths:**

```bash
LINKEDIN_EMAIL=your-email@example.com
LINKEDIN_PASSWORD=your-password

# Path to ChromeDriver (use which chromedriver to find it)
CHROMEDRIVER_PATH=/usr/local/bin/chromedriver

# Path to Chrome binary (use which google-chrome or which chromium-browser)
CHROME_BINARY_PATH=/usr/bin/google-chrome
# OR for Chromium:
# CHROME_BINARY_PATH=/usr/bin/chromium-browser

# For headless mode on VPS (recommended)
HEADLESS_MODE=True

# Wait time in seconds
WAIT_TIME=10
```

### Step 9: Set Permissions

```bash
# Ensure logs directory is writable
mkdir -p logs
chmod 755 logs

# Make sure ChromeDriver is executable
sudo chmod +x /usr/local/bin/chromedriver

# If using custom ChromeDriver path
chmod +x /path/to/your/chromedriver
```

### Step 10: Test Installation

```bash
# Activate virtual environment if not already
source venv/bin/activate

# Test Python imports
python3 -c "from selenium import webdriver; print('Selenium installed successfully')"

# Test ChromeDriver
chromedriver --version

# Test Chrome
google-chrome --version
# or
chromium-browser --version

# Run a quick test (optional)
python3 -c "from linkedin_scraper.config import Config; print('Configuration module loaded')"
```

### Troubleshooting Linux VPS Installation

**Issue: Chrome won't start in headless mode**

```bash
# Install additional dependencies
sudo apt install -y xvfb
# Run with virtual display
xvfb-run -a python3 main.py
```

**Issue: Permission denied for ChromeDriver**

```bash
sudo chmod +x /usr/local/bin/chromedriver
# Or add to PATH
export PATH=$PATH:/path/to/chromedriver
```

**Issue: Shared memory size too small**

```bash
# Mount tmpfs with larger size
sudo mount -o remount,size=2G /dev/shm
```

**Issue: Font rendering issues**

```bash
# Install fonts
sudo apt install -y fonts-liberation fonts-dejavu-core fonts-dejavu-extra
```

### Running as a Service (Optional)

Create a systemd service for automated runs:

```bash
sudo nano /etc/systemd/system/linkedin-scraper.service
```

```ini
[Unit]
Description=LinkedIn Job Scraper
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/linkedin-job-scraper
Environment="PATH=/path/to/linkedin-job-scraper/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/path/to/linkedin-job-scraper/venv/bin/python3 /path/to/linkedin-job-scraper/main.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable linkedin-scraper
sudo systemctl start linkedin-scraper
sudo systemctl status linkedin-scraper
```

### Setup Steps

1. **Clone or download this repository**

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Create `.env` file**:
   Copy `.env.example` to `.env` and fill in your credentials:
   ```bash
   cp .env.example .env
   ```

4. **Configure `.env` file**:
   ```
   LINKEDIN_EMAIL=your-email@example.com
   LINKEDIN_PASSWORD=your-password
   CHROMEDRIVER_PATH=/path/to/chromedriver
   CHROME_BINARY_PATH=/usr/bin/chromium-browser
   HEADLESS_MODE=False
   WAIT_TIME=10
   ```

### ChromeDriver Setup

**Linux**:
- Download ChromeDriver from [ChromeDriver Downloads](https://chromedriver.chromium.org/downloads)
- Extract and place in `/usr/bin/` or update `CHROMEDRIVER_PATH` in `.env`

**Windows**:
- Download ChromeDriver matching your Chrome version
- Place in a directory and update `CHROMEDRIVER_PATH` in `.env`

## Usage

### Basic Usage

Run the main script with default example parameters:

```bash
python main.py
```

This will:
- Search for "Python Developer" jobs in "United States"
- Extract 25 job listings
- Save results to `jobs_output.json`
- Display results in console

### Programmatic Usage

```python
from linkedin_scraper.config import Config
from linkedin_scraper.browser_manager import BrowserManager
from linkedin_scraper.linkedin_auth import LinkedInAuth
from linkedin_scraper.job_search import JobSearch
from linkedin_scraper.job_extractor import JobExtractor

# Validate configuration
Config.validate()

# Get or create browser (maintains persistence)
browser_manager = BrowserManager()
driver = browser_manager.get_or_create_browser()

# Authenticate (checks if already logged in)
auth = LinkedInAuth(driver)
if not auth.is_logged_in():
    auth.login()

# Search jobs
job_search = JobSearch(driver)
job_search.search_jobs("Software Engineer", "San Francisco", num_results=50)

# Extract jobs
extractor = JobExtractor(driver)
jobs = extractor.extract_jobs()  # Returns {job_id: job_link}

# Or get detailed information
jobs_with_details = extractor.extract_jobs_with_details()
```

## Project Structure

```
linkedin-job-scraper/
├── .env                  # Credentials (not in git)
├── .env.example          # Template for .env
├── .gitignore            # Git ignore file
├── requirements.txt      # Python dependencies
├── main.py              # Entry point script
├── linkedin_scraper/
│   ├── __init__.py      # Package initialization
│   ├── config.py        # Configuration management
│   ├── browser_manager.py  # Browser instance management
│   ├── linkedin_auth.py    # Authentication logic
│   ├── job_search.py       # Job search operations
│   └── job_extractor.py    # JavaScript injection & extraction
├── logs/                # Log files directory
└── README.md            # This file
```

## Configuration

### Environment Variables

- `LINKEDIN_EMAIL`: Your LinkedIn email address (required)
- `LINKEDIN_PASSWORD`: Your LinkedIn password (required)
- `CHROMEDRIVER_PATH`: Path to ChromeDriver executable (required)
- `CHROME_BINARY_PATH`: Path to Chrome/Chromium binary (optional, defaults to `/usr/bin/chromium-browser`)
- `HEADLESS_MODE`: Run browser in headless mode - `True` or `False` (default: `False`)
- `WAIT_TIME`: Implicit wait time in seconds (default: `10`)

## Output Format

The scraper returns a dictionary mapping job IDs to job links:

```json
{
  "12345678": "https://www.linkedin.com/jobs/view/12345678/",
  "23456789": "https://www.linkedin.com/jobs/view/23456789/",
  ...
}
```

For detailed extraction (using `extract_jobs_with_details()`):

```json
{
  "12345678": {
    "link": "https://www.linkedin.com/jobs/view/12345678/",
    "title": "Senior Python Developer",
    "company": "Tech Corp Inc."
  },
  ...
}
```

## Logging

All operations are logged to:
- Console output (stdout)
- `logs/linkedin_scraper.log` file

Log format: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`

## Troubleshooting

### ChromeDriver Version Mismatch

**Error**: `SessionNotCreatedException` or `chromedriver version mismatch`

**Solution**: Ensure ChromeDriver version matches your Chrome browser version. Check Chrome version with `google-chrome --version` and download matching ChromeDriver.

### Login Issues

**Error**: "Login verification failed" or "CAPTCHA required"

**Solution**:
- **Manual Verification**: The script now supports manual verification automatically
  - Set `HEADLESS_MODE=False` in `.env` (required for manual verification)
  - When verification is needed, the script will pause and wait for you
  - Complete CAPTCHA/2FA in the browser window
  - Navigate to LinkedIn feed manually if needed
  - Script automatically detects when login is complete
- **First-Time Login**: Always do first login manually to establish session
- **See**: `MANUAL_LOGIN_GUIDE.md` for detailed manual verification instructions
- Check credentials in `.env` file

### Browser Not Found

**Error**: `ChromeDriver not found` or `Chrome binary not found`

**Solution**:
- Verify paths in `.env` file are correct
- Use absolute paths on Windows: `C:\\path\\to\\chromedriver.exe`
- Ensure ChromeDriver has execute permissions: `chmod +x /path/to/chromedriver`

### No Jobs Found

**Error**: "No jobs found or error occurred"

**Possible causes**:
- LinkedIn changed their HTML structure (selectors may need updating)
- Search terms returned no results
- Network/timeout issues

**Solution**: Check `logs/linkedin_scraper.log` for detailed error messages.

## Security Notes

⚠️ **IMPORTANT**:
- Never commit `.env` file to version control (it's in `.gitignore`)
- Never hardcode credentials in source code
- Use strong LinkedIn passwords
- Be mindful of LinkedIn's rate limits and terms of service
- Consider using a VPN if scraping frequently

## Account Protection

The scraper is designed to minimize account flagging:
- Reuses browser sessions to avoid repeated logins
- Checks login status before attempting new login
- Uses standard browser user agents
- Implements reasonable wait times between actions

## License

This project is for educational purposes. Use responsibly and in accordance with LinkedIn's Terms of Service.

## Contributing

Contributions are welcome! Please ensure:
- Code follows PEP 8 style guidelines
- All modules have proper docstrings
- Error handling is comprehensive
- Logging is informative

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review logs in `logs/linkedin_scraper.log`
3. Verify configuration in `.env` file
4. Ensure ChromeDriver and Chrome versions match

