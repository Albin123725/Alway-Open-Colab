# Keep Google Colab Open 24/7 on Render

This solution automatically keeps your Google Colab session alive on Render servers.

## How It Works

1. **Render runs Python automation** that opens your Colab notebook
2. **Automatically logs in** with your Google credentials
3. **Keeps the session active** by accessing it every 10 minutes
4. **Runs 24/7** - no laptop needed!

## Setup Instructions

### Step 1: Get Your Colab Notebook ID

1. Open your Colab notebook
2. Look at the URL: `https://colab.research.google.com/drive/**NOTEBOOK_ID**`
3. Copy the NOTEBOOK_ID (long string of characters)

**Your ID:** `15vW4-hwRmew-bDm4B0uyhM8SLyxIfQs3`

### Step 2: Create GitHub Repository

1. Go to GitHub.com
2. Create new repository named `colab-keeper`
3. Clone to your computer: `git clone https://github.com/YOUR-USERNAME/colab-keeper.git`
4. Copy these files into the folder:
   - colab-keeper.py
   - requirements.txt
   - render-python.yaml

5. Push to GitHub:
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

### Step 3: Deploy to Render

1. Go to https://render.com
2. Sign in to your account
3. Click **"New +"** button (top right)
4. Click **"Blueprint"**
5. Select your `colab-keeper` GitHub repository
6. Click **"Create from Blueprint"**

### Step 4: Add Environment Variables

In Render dashboard, enter:

```
GOOGLE_EMAIL = albin53532@gmail.com
GOOGLE_PASSWORD = (your-password)
COLAB_NOTEBOOK_ID = 15vW4-hwRmew-bDm4B0uyhM8SLyxIfQs3
```

Click **"Deploy"**

### Step 5: Verify It's Working

1. Go to your service in Render
2. Click **"Logs"** tab
3. You should see:
```
[INFO] 🟢 Starting Colab Keeper on Render
[INFO] Cycle 1: Keeping Colab session alive...
[INFO] ✅ Colab session active
```

**Done!** Your Colab is now 24/7 alive! 🎉

## What Happens

Every 10 minutes:
- ✅ Logs into your Google account
- ✅ Opens your Colab notebook
- ✅ Keeps it active
- ✅ Logs the status

## Security Notes

⚠️ Your Google password is stored in Render environment variables (encrypted).

For extra security:
- Use an app-specific password from Google Account Settings
- Enable 2FA on your Google account
- Regularly check Render logs

## Monitoring

1. Go to your service in Render
2. Click "Logs" tab
3. Watch the keep-alive cycles

## Free Tier Note

- Render free tier: 750 hours/month
- This runs continuously: ~720 hours/month
- Just fits in free tier!

For guaranteed 24/7, upgrade to paid ($7/month).
