# Deploy Colab Keeper to Render as Web Service

Follow these steps to create a web service manually on Render and auto-fill environment variables.

## 🔧 Colab Keeper Web Service Setup

### Step 1: Create Web Service on Render

1. Go to https://render.com
2. Click **"New +"** → **"Web Service"**
3. Select **"Public Git Repository"**
4. Enter your GitHub repo URL: `https://github.com/YOUR-USERNAME/colab-keeper`
5. Click **"Connect"**

### Step 2: Configure Web Service

Fill in these fields:

| Field | Value |
|-------|-------|
| **Name** | `colab-keeper` |
| **Environment** | `Python 3` |
| **Region** | `Oregon` (or your choice) |
| **Branch** | `main` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `python colab-keeper.py` |
| **Plan** | `Starter` (free tier) |

### Step 3: Auto-Fill Environment Variables

Copy and paste these into the **Environment** section (one by one):

```
Key: GOOGLE_EMAIL
Value: albin53532@gmail.com
```

```
Key: GOOGLE_PASSWORD
Value: (your-password)
```

```
Key: COLAB_NOTEBOOK_ID
Value: 15vW4-hwRmew-bDm4B0uyhM8SLyxIfQs3
```

### Step 4: Deploy

Click **"Create Web Service"**

Render will automatically:
- ✅ Build your app
- ✅ Install dependencies
- ✅ Start the service
- ✅ Keep it running 24/7

### Step 5: Verify

1. Click on your service
2. Go to **"Logs"** tab
3. Look for:
```
[INFO] 🟢 Starting Colab Keeper on Render
[INFO] Cycle 1: Keeping Colab session alive...
[INFO] ✅ Colab session active
```

**Done!** Your Colab runs 24/7 on Render! 🎉

---

## 📋 Environment Variables

```
GOOGLE_EMAIL=albin53532@gmail.com
GOOGLE_PASSWORD=(your-password)
COLAB_NOTEBOOK_ID=15vW4-hwRmew-bDm4B0uyhM8SLyxIfQs3
```

---

## ✅ Deployment Checklist

- [ ] Create GitHub repo with colab-keeper files
- [ ] Go to Render and create Web Service
- [ ] Select Python 3 environment
- [ ] Enter Build and Start commands (see Step 2)
- [ ] Add all environment variables (see Step 3)
- [ ] Click "Create Web Service"
- [ ] Check Logs for success
- [ ] Monitor for a few hours

## 🆘 Troubleshooting

**Service keeps restarting?**
- Check the Logs tab for errors
- Verify all environment variables are set correctly
- Make sure all files are in your GitHub repo

**Colab keeper won't log in?**
- Verify email and password are correct
- Disable 2FA temporarily or use app-specific password
- Check Render logs for authentication errors

**Service stops after a while?**
- Check if Colab requires additional verification
- Review Render logs for errors
- Verify Google credentials haven't changed
