# 🌐 Sharing Your Project with Friends

## Quick Start - Using Ngrok (5 minutes)

### Step 1: Install Ngrok
```powershell
# Download from https://ngrok.com/download
# Sign up for free account at ngrok.com
# Install ngrok and authenticate
ngrok config add-authtoken YOUR_AUTH_TOKEN
```

### Step 2: Start All Services

**Terminal 1 - API Server:**
```powershell
cd C:\Users\sriva\Documents\kash_proj
C:\Users\sriva\anaconda3\envs\biomedical-search\python.exe -m uvicorn src.api.app:app --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend Server:**
```powershell
cd C:\Users\sriva\Documents\kash_proj\frontend
python -m http.server 8080
```

**Terminal 3 - Expose API:**
```powershell
ngrok http 8000
```
Copy the "Forwarding" URL (e.g., `https://abc123.ngrok-free.app`)

**Terminal 4 - Expose Frontend:**
```powershell
ngrok http 8080
```
Copy the "Forwarding" URL (e.g., `https://xyz789.ngrok-free.app`)

### Step 3: Update Frontend Configuration

```powershell
python scripts/update_frontend_url.py https://abc123.ngrok-free.app
```
(Use your actual ngrok API URL from step 2)

### Step 4: Share with Friends!

Send them the **Frontend URL**: `https://xyz789.ngrok-free.app`

**⚠️ Important Notes:**
- URLs expire when you close ngrok or restart computer
- Free tier: 1 connection at a time, URLs change each restart
- Your computer must stay on while friends use it

---

## 🏠 Option 2: Local Network Sharing (Same WiFi)

If friends are on your same WiFi network:

1. **Find your local IP:**
```powershell
ipconfig
# Look for IPv4 Address (e.g., 192.168.1.100)
```

2. **Update frontend:**
```powershell
python scripts/update_frontend_url.py http://192.168.1.100:8000
```

3. **Share URL with friends:**
```
http://192.168.1.100:8080
```

**Requirements:**
- Friends must be on same WiFi network
- Your firewall must allow connections
- Your computer must stay on

---

## ☁️ Option 3: Cloud Deployment (Permanent Access)

For permanent access, deploy to a cloud server:

### A. Free Hosting Options:

#### 1. **Railway.app** (Recommended - Free tier)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

#### 2. **Render.com** (Free tier available)
- Push code to GitHub
- Connect Render to your GitHub repo
- Auto-deploys on push

#### 3. **Fly.io** (Free tier for small apps)
```bash
# Install Fly CLI
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"

# Deploy
fly launch
fly deploy
```

### B. Paid Options ($5-20/month):

#### 1. **DigitalOcean Droplet** ($6/month)
- Get a Ubuntu server
- Follow DEPLOYMENT.md guide
- Get permanent domain

#### 2. **AWS EC2** (Free tier 1 year, then ~$10/month)
- Same as DigitalOcean
- More complex but scalable

#### 3. **Google Cloud Run** (Pay per use, ~$5-15/month)
- Containerized deployment
- Auto-scaling

---

## 🎯 Recommended Approach for You

Based on your needs:

### For Testing with Friends (Next Hour):
→ **Use Ngrok** (Option 1)
- Setup: 5 minutes
- Cost: Free
- Perfect for showing your project

### For Sharing with Multiple Friends (This Week):
→ **Deploy to Railway.app or Render.com**
- Setup: 30 minutes
- Cost: Free (with limits)
- Permanent URL
- Stays online 24/7

### For Serious/Production Use:
→ **DigitalOcean or AWS**
- Setup: 2-3 hours (follow DEPLOYMENT.md)
- Cost: $6-20/month
- Full control
- Your own domain (biomedical-search.com)

---

## 🚀 Quick Deploy to Railway (15 minutes)

Let me create the deployment files:

### 1. Create railway.json
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn src.api.app:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/api/v1/health",
    "restartPolicyType": "ON_FAILURE"
  }
}
```

### 2. Create Procfile
```
web: uvicorn src.api.app:app --host 0.0.0.0 --port $PORT
```

### 3. Update requirements.txt (add production dependencies)
```
gunicorn==21.2.0
```

### 4. Deploy Steps:
```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Initialize project
railway init

# 4. Link to new project
railway link

# 5. Deploy
railway up

# 6. Open in browser
railway open
```

Railway will give you a URL like: `https://your-app.railway.app`

---

## 📋 Pre-Deployment Checklist

Before sharing:

- [ ] All services running (API, Frontend, Elasticsearch)
- [ ] Data indexed (1,817 documents)
- [ ] Tests passing
- [ ] Frontend updated with correct API URL
- [ ] CORS enabled for your domain
- [ ] Environment variables configured

---

## 🆘 Troubleshooting

### Friends can't access:
1. **Check firewall** - Allow ports 8000, 8080
2. **Check ngrok** - Make sure it's running
3. **Check API URL** - Frontend must point to ngrok API URL

### Slow performance:
1. Your computer specs (CPU/RAM)
2. Internet upload speed
3. Number of simultaneous users

### Ngrok URL changed:
1. Restart ngrok → get new URL
2. Re-run: `python scripts/update_frontend_url.py NEW_URL`

---

## 💡 Next Steps

**Right now, to share with your friend:**

1. Run ngrok: `ngrok http 8000` and `ngrok http 8080`
2. Update frontend: `python scripts/update_frontend_url.py YOUR_API_URL`
3. Send friend the frontend ngrok URL
4. They can use it immediately!

**For permanent deployment:**
- Follow DEPLOYMENT.md for detailed cloud deployment
- Or use Railway/Render for quick free hosting

Would you like help with any of these options?
