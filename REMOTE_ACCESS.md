# Remote Access Guide - RealVNC Viewer

This guide explains how to set up remote access to monitor the browser service using RealVNC Viewer or alternative remote desktop solutions.

## Overview

When running the browser service on a VPS or remote server, you may need to:

- Monitor the browser visually
- Handle manual verification (CAPTCHA/2FA)
- Debug browser behavior
- Verify job search results

This guide covers multiple remote access solutions.

## Method 1: RealVNC Viewer (Recommended)

### Step 1: Install VNC Server on VPS

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install tigervnc-standalone-server tigervnc-common -y

# CentOS/RHEL
sudo yum install tigervnc-server -y
```

### Step 2: Set Up VNC Password

```bash
vncserver :1
# Enter password when prompted (6-8 characters recommended)
# Enter view-only password (optional, press Enter to skip)
```

### Step 3: Kill Initial VNC Session

```bash
vncserver -kill :1
```

### Step 4: Configure VNC Startup Script

Create startup script:

```bash
nano ~/.vnc/xstartup
```

Add content:

```bash
#!/bin/bash
xrdb $HOME/.Xresources
xsetroot -solid grey
export XKL_XMODMAP_DISABLE=1
export XDG_CURRENT_DESKTOP="GNOME-Flashback:GNOME"
export XDG_MENU_PREFIX="gnome-flashback-"
gnome-session --session=gnome-flashback-metacity --disable-acceleration-check &
```

Make executable:

```bash
chmod +x ~/.vnc/xstartup
```

### Step 5: Start VNC Server

```bash
vncserver :1 -geometry 1920x1080 -depth 24
```

### Step 6: Configure Firewall

```bash
# Allow VNC port (5901 for display :1)
sudo ufw allow 5901/tcp

# Or for CentOS/RHEL
sudo firewall-cmd --permanent --add-port=5901/tcp
sudo firewall-cmd --reload
```

### Step 7: Install RealVNC Viewer

**Windows/Mac/Linux**: Download from https://www.realvnc.com/download/viewer/

### Step 8: Connect via RealVNC Viewer

1. Open RealVNC Viewer
2. Enter server address: `your-vps-ip:5901`
   - Or `your-vps-ip::5901` if using port format
3. Click Connect
4. Enter VNC password when prompted
5. You should see the remote desktop

### Step 9: Configure Browser Service for VNC

Ensure `.env` has:

```env
HEADLESS_MODE=False
```

This makes the browser visible in VNC session.

### Step 10: Run Browser Service

In VNC session terminal:

```bash
export DISPLAY=:1
python browser_service.py
```

The browser window should appear in VNC viewer.

## Method 2: X11 Forwarding (SSH)

### Step 1: Enable X11 Forwarding in SSH

```bash
ssh -X username@your-vps-ip
# Or for trusted X11 forwarding:
ssh -Y username@your-vps-ip
```

### Step 2: Set DISPLAY Variable

```bash
export DISPLAY=:10.0
# Or check with: echo $DISPLAY
```

### Step 3: Run Browser Service

```bash
python browser_service.py
```

Browser should appear on your local machine.

**Note**: Requires X server on local machine (XQuartz for Mac, Xming/VcXsrv for Windows).

## Method 3: NoVNC (Web-based VNC)

### Step 1: Install NoVNC

```bash
git clone https://github.com/novnc/noVNC.git
cd noVNC
./utils/launch.sh --vnc localhost:5901
```

### Step 2: Access via Browser

Open browser and go to: `http://your-vps-ip:6080`

### Step 3: Enter VNC Server

Enter: `localhost:5901` and connect.

## Method 4: Chrome Remote Desktop

### Step 1: Install Chrome on VPS

```bash
# Follow Chrome installation guide for your OS
```

### Step 2: Install Chrome Remote Desktop

1. Open Chrome on VPS
2. Install Chrome Remote Desktop extension
3. Set up remote access
4. Get access code

### Step 3: Connect from Local Machine

1. Install Chrome Remote Desktop on local machine
2. Enter access code
3. Connect to VPS desktop

## Method 5: Xvfb + VNC (Headless Server)

For servers without display:

### Step 1: Install Xvfb and VNC

```bash
sudo apt install xvfb x11vnc -y
```

### Step 2: Start Xvfb (Virtual Display)

```bash
Xvfb :99 -screen 0 1024x768x24 &
```

### Step 3: Start VNC on Virtual Display

```bash
x11vnc -display :99 -nopw -listen localhost -xkb -forever -shared &
```

### Step 4: Set DISPLAY and Run

```bash
export DISPLAY=:99
python browser_service.py
```

### Step 5: Connect via VNC Viewer

Connect to `your-vps-ip:5900` (x11vnc default port).

## Troubleshooting

### VNC Connection Refused

**Solutions**:
1. Check VNC server is running: `vncserver -list`
2. Verify firewall allows VNC port
3. Check VNC server process: `ps aux | grep vnc`

### Browser Not Visible in VNC

**Solutions**:
1. Verify `HEADLESS_MODE=False` in `.env`
2. Check DISPLAY variable: `echo $DISPLAY`
3. Set DISPLAY before running: `export DISPLAY=:1`
4. Restart VNC server

### Slow/Unresponsive VNC

**Solutions**:
1. Reduce VNC resolution: `vncserver :1 -geometry 1280x720`
2. Lower color depth: `-depth 16`
3. Check network connection
4. Use SSH tunnel (see below)

### SSH Tunnel for Secure VNC (Recommended)

Instead of exposing VNC port directly:

```bash
# On local machine
ssh -L 5901:localhost:5901 username@your-vps-ip

# Then connect VNC Viewer to: localhost:5901
```

## Security Best Practices

### 1. Use SSH Tunneling

Always use SSH tunnel instead of exposing VNC port publicly:

```bash
ssh -L 5901:localhost:5901 username@your-vps-ip
```

### 2. Strong VNC Password

Use strong password (8+ characters, mix of letters/numbers).

### 3. Firewall Configuration

Only allow VNC port from trusted IPs:

```bash
sudo ufw allow from YOUR_IP to any port 5901
```

### 4. VPN Access

Use VPN instead of direct VNC access for better security.

### 5. VNC Timeout

Configure VNC to timeout idle sessions.

## Using RealVNC Viewer Features

### File Transfer

RealVNC Viewer supports file transfer:
- Drag and drop files between local and remote
- Access via menu: Transfer Files

### Clipboard Sharing

Clipboard is shared automatically between local and remote.

### Multiple Displays

If VPS has multiple displays, you can access them:
- Display :1 = Port 5901
- Display :2 = Port 5902
- etc.

### Scaling Options

Adjust scaling for better viewing:
- Menu → View → Scaling
- Options: Auto, Fit to window, Custom

## Alternative: Screen Sharing Software

### TeamViewer

1. Install TeamViewer on VPS
2. Get ID and password
3. Connect from local machine

### AnyDesk

1. Install AnyDesk on VPS
2. Get AnyDesk address
3. Connect from local machine

### RustDesk (Open Source)

1. Install RustDesk server on VPS
2. Get ID and password
3. Connect from local machine

## Monitoring Browser Service

Once connected via remote access:

### View Browser Window

- Browser should be visible if `HEADLESS_MODE=False`
- Can interact with browser manually
- See job search results in real-time

### Monitor Logs

```bash
# In VNC terminal
tail -f logs/browser_service.log
```

### Check Service Status

```bash
# In VNC terminal - read status file directly
cat browser_service_status.json
```

### Manual Verification

When CAPTCHA/2FA is required:
1. Browser window appears in VNC
2. Complete verification in browser
3. Service automatically detects completion

## Quick Reference

### Start VNC Server

```bash
vncserver :1 -geometry 1920x1080 -depth 24
```

### Stop VNC Server

```bash
vncserver -kill :1
```

### List VNC Sessions

```bash
vncserver -list
```

### Connect via SSH Tunnel

```bash
ssh -L 5901:localhost:5901 username@vps-ip
```

### Check DISPLAY

```bash
echo $DISPLAY
```

### Set DISPLAY for VNC

```bash
export DISPLAY=:1
```

## Next Steps

- See **BROWSER_SERVICE.md** for browser service details
- See **JOB_SEARCH_SERVICE.md** for job search operations
- See **PROJECT.md** for overall architecture

