# Browser & Login Service Documentation

## Overview

The **Browser Service** (`browser_service.py`) is a standalone service that maintains a persistent Chrome browser instance and handles LinkedIn authentication. This service ensures only one browser instance is active, preventing account flagging from multiple logins.

## Purpose

- Maintain single browser instance across all operations
- Handle LinkedIn login and session management
- Monitor browser health and re-authenticate when needed
- Provide browser access via remote debugging protocol
- Prevent account flagging by avoiding multiple browser instances

## Features

### 1. Single Instance Management

- Creates only one browser instance
- Reuses existing browser if available
- Prevents multiple logins that could flag your account

### 2. Persistent Session

- Browser stays alive across service restarts
- Maintains login session
- Avoids repeated authentication requests

### 3. Health Monitoring

- Periodic health checks (every 60 seconds)
- Automatic re-authentication if session expires
- Browser crash detection and recovery

### 4. Remote Access

- Exposes browser via remote debugging port (9222)
- Enables other services to connect to browser
- Supports RealVNC/remote desktop monitoring

## Installation & Setup

### Prerequisites

1. Python 3.7+ installed
2. Chrome browser installed
3. ChromeDriver installed
4. `.env` file configured with LinkedIn credentials

### Configuration

Create `.env` file in project root:

```env
LINKEDIN_EMAIL=your_email@example.com
LINKEDIN_PASSWORD=your_password
CHROMEDRIVER_PATH=/usr/bin/chromedriver
CHROME_BINARY_PATH=/usr/bin/chromium-browser
HEADLESS_MODE=False
WAIT_TIME=10
```

## Usage

### Starting the Service

```bash
python browser_service.py
```

### Service Output

```
============================================================
LinkedIn Browser Service
============================================================
This service maintains a persistent browser and LinkedIn login.
Press Ctrl+C or create 'stop_service' file to stop.
============================================================
Validating configuration...
Initializing browser service...
Launching Chrome browser on Linux...
Remote debugging enabled on port 9222
Browser launched successfully and stored as persistent instance
Not logged in, attempting login...
Email entered
Password entered
Login button clicked
✓ Browser service initialized and authenticated
Service running. Browser is ready for job searches.
Status file: browser_service_status.json
```

### Service Behavior

1. **Initialization**:
   - Validates configuration
   - Launches Chrome with remote debugging
   - Authenticates to LinkedIn
   - Updates status file

2. **Running State**:
   - Checks browser health every 60 seconds
   - Monitors login status
   - Updates status file periodically
   - Listens for stop signals

3. **Health Checks**:
   - Verifies browser is responsive
   - Checks if still logged in
   - Re-authenticates if needed
   - Logs any issues

## Service Control

### Stopping the Service

**Method 1: Keyboard Interrupt**
```bash
# Press Ctrl+C in the terminal running the service
```

**Method 2: Stop File**
```bash
touch stop_service
# Service checks for this file every 5 seconds
```

### Checking Service Status

The service creates `browser_service_status.json`:

```json
{
  "running": true,
  "browser_alive": true,
  "logged_in": true,
  "timestamp": 1703123456.789
}
```

You can check status programmatically:

```python
import json
from pathlib import Path

status_file = Path('browser_service_status.json')
if status_file.exists():
    with open(status_file) as f:
        status = json.load(f)
    print(f"Running: {status['running']}")
    print(f"Browser Alive: {status['browser_alive']}")
    print(f"Logged In: {status['logged_in']}")
```

You can check status programmatically using the status file as shown above.

## Authentication Process

### Automatic Login

1. Service navigates to LinkedIn login page
2. Fills in credentials from `.env` file
3. Clicks login button
4. Waits for authentication

### Manual Verification

If LinkedIn requires CAPTCHA or 2FA:

1. Service detects verification requirement
2. Logs message about manual verification needed
3. Waits up to 5 minutes for completion
4. Automatically detects when login succeeds

**Requirements for Manual Verification:**
- `HEADLESS_MODE=False` in `.env`
- Browser must be visible (use VNC/remote desktop)

### Session Persistence

- First login creates session cookies
- Browser maintains cookies across restarts
- Service reuses session if still valid
- Re-authenticates only when session expires

## Remote Debugging

### How It Works

The browser service launches Chrome with:

```bash
--remote-debugging-port=9222
```

This enables:
- Other services to connect via `debuggerAddress`
- RealVNC/remote desktop access
- Browser inspection tools

### Connection Details

- **Port**: 9222 (default, configurable)
- **Host**: 127.0.0.1 (localhost)
- **Protocol**: Chrome DevTools Protocol (CDP)

### Debug Port File

Service saves port info to `browser_debug_port.json`:

```json
{
  "port": 9222,
  "timestamp": "1703123456.789"
}
```

## Security Features

### Anti-Detection Measures

1. **Stealth Scripts**: Masks automation indicators
2. **Random User Agents**: Rotates user agent strings
3. **Fingerprint Masking**: Removes automation properties
4. **Realistic Behavior**: Human-like delays and patterns

### Browser Options

The service uses Chrome options optimized for stealth:

- `--disable-blink-features=AutomationControlled`
- `--disable-web-security`
- Random realistic user agents
- Stealth JavaScript injection

## Logging

### Log Files

Service logs to: `logs/browser_service.log`

### Log Levels

- **INFO**: Normal operations
- **WARNING**: Non-critical issues
- **ERROR**: Failures requiring attention

### Example Log Entries

```
2024-01-15 10:30:00 - INFO - Browser service initialized and authenticated
2024-01-15 10:31:00 - INFO - Health check passed
2024-01-15 10:32:00 - WARNING - Not logged in, attempting to re-login...
2024-01-15 10:32:05 - INFO - ✓ Authentication successful
```

## Troubleshooting

### Browser Won't Start

**Symptoms**: Service fails to launch browser

**Solutions**:
1. Check ChromeDriver path in `.env`
2. Verify Chrome binary path
3. Check system permissions
4. Review logs for specific errors

### Login Fails

**Symptoms**: Authentication unsuccessful

**Solutions**:
1. Verify credentials in `.env`
2. Check if CAPTCHA/2FA required (set `HEADLESS_MODE=False`)
3. Review login logs
4. Try manual login first

### Browser Crashes

**Symptoms**: Browser becomes unresponsive

**Solutions**:
1. Restart browser service
2. Check system resources (memory, CPU)
3. Review crash logs
4. Verify Chrome installation

### Service Won't Stop

**Symptoms**: Ctrl+C doesn't stop service

**Solutions**:
1. Create `stop_service` file
2. Kill process: `kill <pid>`
3. Check for hung browser processes

## Best Practices

1. **Keep Service Running**: Don't restart frequently
2. **Monitor Logs**: Check for warnings/errors regularly
3. **Use Headless Mode**: Set `HEADLESS_MODE=True` for production
4. **Secure Credentials**: Never commit `.env` file
5. **Health Checks**: Monitor status file periodically

## Integration with Other Services

### Job Search Service

The job search service connects to browser service:

```python
from linkedin_scraper.browser_manager import BrowserManager

browser_manager = BrowserManager()
driver = browser_manager.get_or_create_browser()  # Connects via remote debugging
```

### Remote Monitoring

Access browser via:
- RealVNC Viewer (see REMOTE_ACCESS.md)
- Chrome DevTools: `chrome://inspect`
- Remote desktop connection

## File Structure

```
browser_service.py          # Main service script
browser_service_status.json # Status file (created at runtime)
browser_debug_port.json     # Debug port info (created at runtime)
logs/
  └── browser_service.log   # Service logs
```

## Next Steps

- See **JOB_SEARCH_SERVICE.md** for job search operations
- See **REMOTE_ACCESS.md** for remote monitoring setup
- See **PROJECT.md** for overall architecture

