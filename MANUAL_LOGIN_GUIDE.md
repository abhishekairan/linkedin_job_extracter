# Manual Login Verification Guide

This guide explains how to handle manual login verification when LinkedIn requires CAPTCHA or security challenges.

## When Manual Verification is Needed

LinkedIn may require manual verification in these cases:
- CAPTCHA challenges
- Two-factor authentication (2FA)
- Unusual activity detection
- New device/IP address login
- Security verification requests

## How It Works

The scraper now includes automatic detection and manual verification support:

1. **Automatic Detection**: The script detects when LinkedIn requires manual verification
2. **Browser Pause**: The browser stays open and waits for you to complete the verification
3. **Auto-Detection**: Once you complete verification, the script automatically continues

## Setup for Manual Verification on VPS

### Option 1: Using X11 Forwarding (Recommended for Manual Verification)

If you're accessing your VPS via SSH and want to see the browser:

```bash
# SSH with X11 forwarding enabled
ssh -X username@your-vps-ip
# or for trusted X11 forwarding
ssh -Y username@your-vps-ip

# Set DISPLAY variable
export DISPLAY=:10.0

# Ensure HEADLESS_MODE=False in .env
# Run the scraper
python3 main.py
```

### Option 2: Using VNC or Remote Desktop

1. Install VNC server on VPS:
```bash
sudo apt install tigervnc-standalone-server tigervnc-common -y
```

2. Set up VNC (create password):
```bash
vncserver :1
```

3. Connect via VNC client from your local machine

4. Set `HEADLESS_MODE=False` in `.env`

5. Run the scraper in the VNC session

### Option 3: Using NoVNC (Web-based VNC)

Install and configure NoVNC for web-based browser access.

### Option 4: Using Remote Display (Xvfb + VNC)

For persistent browser sessions:

```bash
# Install Xvfb and VNC
sudo apt install xvfb x11vnc -y

# Start Xvfb (virtual display)
Xvfb :99 -screen 0 1024x768x24 &

# Start VNC server on the virtual display
x11vnc -display :99 -nopw -listen localhost -xkb -forever -shared &

# Set DISPLAY
export DISPLAY=:99

# Run scraper
python3 main.py
```

## Step-by-Step Manual Verification Process

### When the Script Detects Verification Needed

1. **Script Output**: You'll see this message:
   ```
   ============================================================
   MANUAL VERIFICATION REQUIRED
   ============================================================
   Please complete the following in the browser:
   1. Solve any CAPTCHA if present
   2. Complete 2FA if required
   3. Navigate to LinkedIn feed (https://www.linkedin.com/feed/)
   4. The script will automatically detect when you're logged in
   ============================================================
   ```

2. **Access the Browser**:
   - If using X11 forwarding: Browser should appear on your local screen
   - If using VNC: Connect via VNC client and you'll see the browser
   - If using remote desktop: Access via your remote desktop client

3. **Complete Verification**:
   - Solve any CAPTCHA shown
   - Complete 2FA if prompted (enter code from authenticator app)
   - Navigate to LinkedIn feed manually if needed: `https://www.linkedin.com/feed/`

4. **Wait for Auto-Detection**: 
   - Script checks every 5 seconds
   - Automatically continues when login is detected
   - Maximum wait time: 5 minutes (300 seconds)

## Configuration

### Enable Manual Verification

Manual verification is **enabled by default** in `main.py`:

```python
login_success = auth.login(manual_verification=True)
```

To disable it, change to:
```python
login_success = auth.login(manual_verification=False)
```

### Set HEADLESS_MODE

**Important**: For manual verification to work, you MUST set:

```bash
# In .env file
HEADLESS_MODE=False
```

If `HEADLESS_MODE=True`, you won't be able to see/interact with the browser.

## Example Session Flow

```
1. Script starts
2. Browser opens (headless=False)
3. Credentials entered automatically
4. Login button clicked
5. LinkedIn shows CAPTCHA
6. Script detects verification needed
7. Script pauses and waits
8. YOU: Solve CAPTCHA in browser
9. YOU: Navigate to feed if needed
10. Script detects successful login
11. Script continues with job search
```

## Troubleshooting

### "Browser not visible"

**Solution**: 
- Ensure `HEADLESS_MODE=False` in `.env`
- Check X11 forwarding: `echo $DISPLAY` should show a value
- For VNC: Verify VNC server is running

### "Script times out"

**Solution**:
- The default timeout is 5 minutes (300 seconds)
- If you need more time, edit `_wait_for_manual_verification(timeout=600)` in `linkedin_auth.py`
- Complete verification faster or increase timeout

### "Can't interact with browser"

**Solution**:
- Make sure you're in a graphical session (not pure headless)
- Use X11 forwarding, VNC, or remote desktop
- Check browser window is actually open and visible

### "Verification not detected"

**Solution**:
- After completing verification, manually navigate to: `https://www.linkedin.com/feed/`
- Wait a few seconds for the script to detect
- Check logs for detection messages

## Quick Reference Commands

```bash
# Check if X11 forwarding works
echo $DISPLAY

# Start Xvfb (virtual display)
Xvfb :99 -screen 0 1024x768x24 &

# Set display
export DISPLAY=:99

# Check HEADLESS_MODE setting
grep HEADLESS_MODE .env

# Run with manual verification
python3 main.py
```

## Tips for VPS Usage

1. **First Time Setup**: 
   - Always do first login manually to establish session
   - After first login, browser sessions persist (unless cleared)

2. **Subsequent Runs**:
   - If already logged in, script skips login
   - No manual verification needed if session is valid

3. **Session Persistence**:
   - Browser manager maintains persistent sessions
   - Re-login only needed when session expires

4. **Headless vs Non-Headless**:
   - Use `HEADLESS_MODE=True` for automated runs (no manual intervention)
   - Use `HEADLESS_MODE=False` for first-time setup or when verification needed

## Advanced: Running in Background

If you want to run with manual verification in background but still access browser:

```bash
# Use screen or tmux
screen -S linkedin-scraper
# or
tmux new -s linkedin-scraper

# Run script
python3 main.py

# Detach: Ctrl+A then D (screen) or Ctrl+B then D (tmux)

# Reattach later to complete verification
screen -r linkedin-scraper
# or
tmux attach -t linkedin-scraper
```

## Security Note

⚠️ **Important**: 
- Never commit your `.env` file
- Keep your VPS secure
- Use strong passwords
- Consider VPN for additional security

