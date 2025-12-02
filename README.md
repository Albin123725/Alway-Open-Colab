# 🎮 Colab Keeper - Browser Edition (AI Advanced)

Keep your Google Colab sessions open **24/7** using real browser automation with Selenium. Features **AI-powered auto-restart** to keep everything running perfectly!

## ✨ Features

### Core Features
- ✅ **Real Browser Automation** - Uses Selenium with Chrome/Firefox (not fake HTTP requests)
- ✅ **Simulates Real User Activity** - Scrolling, clicking, keyboard input
- ✅ **Bypasses Google Security** - Acts like a real person, not a bot
- ✅ **24/7 Uptime** - Keep Colab sessions alive indefinitely
- ✅ **Health Monitoring** - HTTP endpoint for Render health checks
- ✅ **Automatic Reconnection** - Handles disconnections gracefully

### 🤖 AI-Powered Auto-Restart (NEW!)
- ✅ **Cell Monitoring** - Detects stuck/frozen cells
- ✅ **Auto-Restart Cells** - Automatically stops and restarts stuck cells
- ✅ **Runtime Monitoring** - Detects runtime crashes
- ✅ **Auto-Restart Runtime** - Automatically restarts the entire runtime when needed
- ✅ **Health Score** - AI calculates Colab health (0-100)
- ✅ **Crash Prediction** - Predicts when Colab will crash and prevents it
- ✅ **Auto-Recovery** - Automatically recovers from disconnections

## 🚀 How It Works

```
Your Minecraft Server in Colab
    ↓
Colab Keeper (Render) opens browser
    ↓
🤖 AI monitors every 30 seconds
    ↓
If cells stuck → Auto-restart them
If runtime crashes → Auto-restart runtime
If connection lost → Auto-reconnect
    ↓
✅ Colab never times out
    ↓
🎮 Minecraft server runs forever!
```

## 📋 Prerequisites

1. **Google Account** - Your Gmail email
2. **App-Specific Password** - [Create here](https://myaccount.google.com/apppasswords)
3. **Colab Notebook ID** - From your notebook URL
4. **Render Account** - For hosting

## 🔑 Getting Your Credentials

### 1. Get App-Specific Password (IMPORTANT!)

⚠️ **Do NOT use your regular Google password!** Google blocks automation with regular passwords.

1. Go to: https://myaccount.google.com/apppasswords
2. Select: Mail → Windows Computer (or any device)
3. Google generates a 16-character password
4. **Copy this password** - you'll need it

### 2. Get Colab Notebook ID

Open your Colab notebook and copy the ID from the URL:
```
https://colab.research.google.com/drive/1jckV8xUJSmLhhol6wZwVJzpybsimiRw1
                                         ↑ This is your notebook ID
```

## 🛠️ Local Development (Optional)

```bash
# Create .env file
cp .env.example .env

# Edit with your credentials
nano .env

# Install dependencies
pip install -r requirements.txt

# Run locally
python colab-keeper-browser.py

# Check health
curl http://localhost:3000/health
```

## 🌐 Deploy to Render

### 1. Create New Web Service

1. Go to https://render.com
2. Click "New +" → "Web Service"
3. Connect your GitHub repo (or use this code)

### 2. Configure Environment Variables

In Render dashboard → Environment:

```
GOOGLE_EMAIL = albinnn07@gmail.com
GOOGLE_PASSWORD = your-app-password (16 chars from step above)
COLAB_NOTEBOOK_ID = 1jckV8xUJSmLhhol6wZwVJzpybsimiRw1
PORT = 3000
LOG_LEVEL = INFO
KEEP_ALIVE_INTERVAL = 300
MONITOR_INTERVAL = 30
AUTO_RESTART_ENABLED = true
```

### 3. Configure Build & Start Commands

**Build Command:**
```
pip install -r requirements.txt && apt-get update && apt-get install -y chromium-browser firefox-geckodriver
```

**Start Command:**
```
python colab-keeper-browser.py
```

### 4. Deploy

Click "Deploy" and Render will:
- Install Python dependencies
- Install Chrome/Firefox
- Start the Colab keeper
- Keep your Colab open 24/7 ✅
- Auto-restart any stuck cells ✅
- Auto-restart runtime if it crashes ✅

## 📊 Monitoring

### Health Endpoint

Check if Colab keeper is working:

```bash
curl https://your-service.onrender.com/health
```

Response:
```json
{
  "status": "ok",
  "is_connected": true,
  "last_activity": "2024-12-02 10:30:45.123456",
  "uptime_seconds": 3600,
  "session_count": 1,
  "cells_restarted": 2,
  "runtime_restarted": 0,
  "ai_health_score": 95,
  "disconnects_recovered": 1,
  "error": null
}
```

### View Logs

In Render dashboard:
1. Click your service
2. Go to "Logs" tab
3. See real-time activity

Example logs:
```
🤖 [AI] Running health check cycle...
📊 AI Health Score: 95/100
   Runtime: ✅
   Cells: ✅ (Running: 1, Stuck: 0)
   Connection: ✅
🖱️ Simulating user activity...
✅ Activity simulated successfully
```

## 🎯 Configuration Options

### KEEP_ALIVE_INTERVAL (seconds)
- `300` (5 min) - Default, good for Colab
- `600` (10 min) - Less frequent, saves resources
- `180` (3 min) - More frequent, more reliable

### MONITOR_INTERVAL (seconds)
- `30` - Default, checks health every 30 seconds
- `60` - Check every minute (less CPU)
- `15` - Check every 15 seconds (more responsive)

### AUTO_RESTART_ENABLED
- `true` - AI auto-restarts stuck cells and runtime (RECOMMENDED!)
- `false` - Only monitoring, no auto-restart

### LOG_LEVEL
- `INFO` - Normal operation (recommended)
- `DEBUG` - Very detailed logs
- `WARNING` - Only warnings/errors
- `ERROR` - Only critical errors

## 🤖 AI Auto-Restart Features Explained

### Cell Monitoring & Restart
Colab Keeper watches all cells in your notebook:
- **Every 30 seconds**: Checks if any cells are stuck/frozen
- **Auto-restart**: If a cell is running for too long, it stops and restarts it
- **Recovery**: Waits 2 seconds, then resumes execution

Example scenario:
```
Minecraft cell starts running (starting server)
     ↓
30 seconds later: AI checks status
     ↓
If stuck for >5 min: AI stops it
     ↓
Waits 2 seconds
     ↓
Cell restarts automatically
     ↓
Server back online! ✅
```

### Runtime Monitoring & Restart
Colab Keeper detects runtime crashes:
- **Connection check**: Every 30 seconds, verifies runtime is responsive
- **Error detection**: Scans for crash messages
- **Auto-restart**: If runtime is unresponsive, restarts it
- **Recovery time**: 10 seconds to restart, then resumes

### Health Score (0-100)
AI calculates overall Colab health:
- **100/100**: Everything perfect
- **70/100**: Minor issues, still working
- **50/100**: Significant problems
- **<50/100**: Critical, AI will restart

### Crash Prediction
AI learns from patterns:
- Tracks health history (last 100 checks)
- If trend shows declining health → **Predicts crash**
- Takes preventive action before crash happens
- Prevents unexpected outages

### Auto-Recovery
When things go wrong:
- **Connection lost**: Automatically reconnects
- **Session expired**: Logs back in
- **Runtime crashed**: Restarts runtime
- **Cells frozen**: Stops and restarts them

## 🎮 Using with Minecraft Server

1. **In your Colab notebook**, have your Minecraft server code with auto-restart logic
2. **Deploy ColabKeeper** to Render (this)
3. **Result**: Minecraft runs 24/7! 🎮

```python
# Your Colab notebook should have something like:
while True:
    try:
        # Start minecraft server
        run_minecraft_server()
    except Exception as e:
        print(f"Server crashed: {e}")
        time.sleep(5)  # Wait 5 seconds, then restart
```

**ColabKeeper keeps your Colab open 24/7** + **Your code auto-restarts the server** = **Perfect 24/7 Minecraft!** 🎉

## 🐛 Troubleshooting

### "Google login failed"
- ✅ Check you're using **app-specific password**, not your regular password
- ✅ Verify email is correct
- ✅ Try generating a new app password

### "Failed to open Colab notebook"
- ✅ Check notebook ID is exactly correct
- ✅ Make sure notebook is shared/accessible
- ✅ Try opening in browser manually to verify

### "Runtime keeps restarting"
- ✅ Check if your code has errors (would cause crashes)
- ✅ Temporarily set `AUTO_RESTART_ENABLED=false` to diagnose
- ✅ Check Colab logs for error messages

### "Cells don't auto-restart"
- ✅ Verify `AUTO_RESTART_ENABLED=true` in environment variables
- ✅ Check `MONITOR_INTERVAL` is reasonable (30-60 seconds)
- ✅ Check logs for "stuck cell" detection

### "Browser window closed"
- ✅ Check Render logs for errors
- ✅ Render may have restarted - it will automatically reconnect
- ✅ This is normal and expected

### Still having issues?
- Check `/health` endpoint for error messages
- Read Render logs in real-time
- Verify all environment variables are set
- Enable `DEBUG` log level for detailed output

## 📈 Performance & Resource Usage

- **CPU**: ~5-10% while idle, 20-30% during restarts
- **RAM**: ~300-500MB
- **Bandwidth**: ~1-5MB per day
- **Render free tier**: More than enough!

## 🔒 Security Notes

- ✅ Use **app-specific password**, not your regular password
- ✅ Never commit `.env` file with real credentials
- ✅ Use Render's secret management (not in code)
- ✅ Credentials are only used for browser login, not stored

## 📝 Advanced Configuration

You can extend the AI system by editing `colab-keeper-browser.py`:

```python
# Adjust these constants to change behavior:
KEEP_ALIVE_INTERVAL = 300      # How often to simulate activity
MONITOR_INTERVAL = 30           # How often to check health
AUTO_RESTART_ENABLED = True     # Enable/disable auto-restart
```

## 📄 License

MIT - Use freely!

## 🎮 Your Minecraft Server

Now that Colab Keeper is deployed with AI auto-restart:

1. **Your Colab notebook** = Minecraft server code
2. **ColabKeeper (Render)** = Keeps Colab open + Auto-restarts everything
3. **Result** = 100% reliable 24/7 Minecraft! 🚀

Players can join your server anytime, it's always online and always working!

---

**Ready to run 24/7 with AI protection?** Deploy to Render now! 🚀
