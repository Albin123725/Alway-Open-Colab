# Colab Keeper - Keep Google Colab Open 24/7 on Render

Keep your Google Colab notebook running 24/7 on Render servers without needing your laptop!

## 📁 Project Structure

```
colab-keeper/
├── colab-keeper.py           # Colab automation script
├── requirements.txt           # Python dependencies (Selenium)
├── render-python.yaml         # Blueprint deployment config
├── .env.example               # Environment variables template
└── SETUP_GUIDE.md            # Detailed setup instructions
```

## 🚀 Quick Start

### Your Colab Details (Pre-filled)
```
Email: albin53532@gmail.com
Notebook ID: 15vW4-hwRmew-bDm4B0uyhM8SLyxIfQs3
```

### Deploy to Render (3 Steps)

**See `RENDER_WEB_SERVICE_SETUP.md` for detailed instructions with:**
- ✅ Step-by-step screenshots guide
- ✅ Copy-paste environment variables
- ✅ Troubleshooting tips

Or **see `colab-keeper/SETUP_GUIDE.md` for Blueprint deployment**

## ✨ Features

- ✅ Keeps Colab sessions alive 24/7
- ✅ Auto-login with your Google credentials
- ✅ Runs completely on Render (no local laptop needed)
- ✅ Checks every 10 minutes to keep session active
- ✅ Works on Render free tier (750 hrs/month)
- ✅ Minimal resource usage

## 🔧 How It Works

1. **Render server** automatically logs into your Google account
2. **Opens your Colab notebook** continuously
3. **Keeps the session active** every 10 minutes
4. **Runs 24/7** - your Colab never sleeps!

Your laptop can be **closed, turned off, unplugged** - Colab still runs! 🎉

## 📋 Environment Variables

```
GOOGLE_EMAIL = albin53532@gmail.com
GOOGLE_PASSWORD = your-google-password
COLAB_NOTEBOOK_ID = 15vW4-hwRmew-bDm4B0uyhM8SLyxIfQs3
```

## 🧪 Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GOOGLE_EMAIL=your-email@gmail.com
export GOOGLE_PASSWORD=your-password
export COLAB_NOTEBOOK_ID=your-notebook-id

# Run
python colab-keeper.py
```

## 📊 Monitoring

Check Render dashboard:
1. Go to your service
2. Click **"Logs"** tab
3. Look for:
```
[INFO] 🟢 Starting Colab Keeper on Render
[INFO] Cycle 1: Keeping Colab session alive...
[INFO] ✅ Colab session active
```

## ⚙️ Technology Stack

- **Runtime:** Python 3
- **Browser Automation:** Selenium
- **Deployment:** Render
- **Hosting:** Free tier (works in 750 hrs/month)

## 📚 Setup Guides

- **Quick Web Service Setup:** `RENDER_WEB_SERVICE_SETUP.md` ← Start here!
- **Blueprint Deployment:** `colab-keeper/SETUP_GUIDE.md`
- **Render Docs:** https://render.com/docs

## 🆓 Free Tier Usage

- **Runtime:** ~720 hours/month (just fits in 750 hour free tier)
- **Cost:** $0/month on free tier
- **Upgrade:** $7+/month for guaranteed 24/7 uptime

## 🆘 Troubleshooting

**Service won't start?**
- Check that all 3 environment variables are set
- Verify GitHub repo has all files
- Check Render logs for error messages

**Colab keeper stops logging in?**
- Verify email and password are correct
- Disable 2FA or use app-specific password from Google Account
- Try changing password and updating in Render

**Session expires quickly?**
- Google may require additional verification
- Check Render logs for details
- Try using an app-specific password instead of main password

## 📝 License

ISC

## 🤝 Support

For help, check:
1. `RENDER_WEB_SERVICE_SETUP.md` - Detailed step-by-step guide
2. `colab-keeper/SETUP_GUIDE.md` - Alternative deployment guide
3. Render documentation: https://render.com/docs
