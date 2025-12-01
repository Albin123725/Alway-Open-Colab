# Minecraft Bot + Colab Keeper Project

Complete solution to keep your Minecraft server alive 24/7 and run Google Colab continuously on Render.

## 📁 Project Structure

```
minecraft-bot-complete/
├── src/
│   └── index.ts              # Main Minecraft bot code
├── colab-keeper/
│   ├── colab-keeper.py       # Colab auto-keeper script
│   ├── requirements.txt       # Python dependencies
│   ├── render-python.yaml     # Render deployment config
│   └── SETUP_GUIDE.md        # Detailed setup instructions
├── package.json              # Node.js dependencies
├── tsconfig.json             # TypeScript config
├── render.yaml               # Minecraft bot Render config
├── .env.example              # Environment variables template
└── README.md                 # This file
```

## 🚀 Quick Start

### Option 1: Deploy Minecraft Bot to Render

1. Push this folder to GitHub
2. Go to https://render.com
3. Create new Blueprint from GitHub repo
4. Use `render.yaml`
5. Add environment variables:
   - MINECRAFT_SERVER_HOST
   - MINECRAFT_SERVER_PORT
   - MINECRAFT_BOT_USERNAME
   - MINECRAFT_VERSION

### Option 2: Deploy Colab Keeper to Render

1. Push `colab-keeper/` folder to GitHub
2. Go to https://render.com
3. Create new Blueprint from GitHub repo
4. Use `colab-keeper/render-python.yaml`
5. Add environment variables:
   - GOOGLE_EMAIL: albin53532@gmail.com
   - GOOGLE_PASSWORD: (your password)
   - COLAB_NOTEBOOK_ID: 15vW4-hwRmew-bDm4B0uyhM8SLyxIfQs3

See `colab-keeper/SETUP_GUIDE.md` for detailed instructions.

## 📋 Features

### Minecraft Bot
- ✅ Automatic connection to Minecraft servers
- ✅ Reconnection on disconnect
- ✅ Health check endpoint
- ✅ Structured logging with Pino
- ✅ Prevents server shutdown on free tier hosting

### Colab Keeper
- ✅ Keeps Colab sessions alive 24/7
- ✅ Auto-login with credentials
- ✅ Runs completely on Render (no local laptop needed)
- ✅ Checks every 10 minutes
- ✅ Works within free tier

## 🔧 Development

### Local Testing (Minecraft Bot)

```bash
# Install dependencies
npm install

# Copy .env.example to .env and fill in your credentials
cp .env.example .env

# Run in development mode
npm run dev

# Build for production
npm run build

# Start production build
npm start
```

### Local Testing (Colab Keeper)

```bash
cd colab-keeper

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GOOGLE_EMAIL=your-email@gmail.com
export GOOGLE_PASSWORD=your-password
export COLAB_NOTEBOOK_ID=your-notebook-id

# Run
python colab-keeper.py
```

## 🌐 Environment Variables

### Minecraft Bot

```
MINECRAFT_SERVER_HOST=craftpixel-R1dt.aternos.me
MINECRAFT_SERVER_PORT=12635
MINECRAFT_BOT_USERNAME=AternosKeeper
MINECRAFT_VERSION=1.21.10
LOG_LEVEL=info
PORT=3000
```

### Colab Keeper

```
GOOGLE_EMAIL=your-email@gmail.com
GOOGLE_PASSWORD=your-password
COLAB_NOTEBOOK_ID=your-notebook-id
```

## 📊 Monitoring

### Minecraft Bot Health Check

```bash
curl https://your-render-app.onrender.com/health
```

Response:
```json
{
  "status": "connected",
  "bot": "AternosKeeper",
  "uptime": 3600,
  "timestamp": "2025-11-13T10:00:00.000Z"
}
```

### Colab Keeper Logs

Check Render dashboard → Your service → Logs tab

## 📚 Technology Stack

### Minecraft Bot
- **Runtime:** Node.js 22+
- **Language:** TypeScript
- **Framework:** Mineflayer
- **Logging:** Pino + Pino Pretty
- **Deployment:** Render

### Colab Keeper
- **Runtime:** Python 3
- **Browser Automation:** Selenium
- **Deployment:** Render

## ✅ Deployment Checklist

- [ ] Fork/clone to GitHub
- [ ] Add Render integration
- [ ] Configure environment variables
- [ ] Deploy using blueprint
- [ ] Check logs for errors
- [ ] Verify health endpoint (bot only)
- [ ] Monitor for 24 hours

## 🐛 Troubleshooting

### Bot won't connect
1. Check `MINECRAFT_SERVER_HOST` and `MINECRAFT_SERVER_PORT`
2. Verify server is online
3. Check logs for error messages

### Colab keeper stops
1. Verify Google credentials are correct
2. Check if 2FA is blocking login
3. Review Render logs for errors

## 📝 License

ISC

## 🤝 Support

For detailed setup guides, see:
- `colab-keeper/SETUP_GUIDE.md` - Colab deployment steps
- Render documentation: https://render.com/docs
