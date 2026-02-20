# Deploy BioMed Scholar to Free Cloud

This guide walks through deploying the application to free cloud hosting platforms.

## Backend: Render.com

### Step 1: Create Render Account
1. Visit https://render.com/
2. Sign up with GitHub

### Step 2: Deploy Backend
1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Select the `kash_proj` repository
4. Configure:
   - **Name**: `biomed-scholar-api`
   - **Environment**: Python 3
   - **Build Command**: `pip install --upgrade pip && pip install -r requirements.txt`
   - **Start Command**: `uvicorn src.api.app:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free

### Step 3: Set Environment Variables
In Render dashboard, add these environment variables:

```
ELASTICSEARCH_HOST=assertive-mahogany-11.bonsai.io
ELASTICSEARCH_PORT=443
ELASTICSEARCH_SCHEME=https
ELASTICSEARCH_USERNAME=0204784e62
ELASTICSEARCH_PASSWORD=38aa998d6c5c2891232c
REDIS_HOST=redis-19579.c330.asia-south1-1.gce.cloud.redislabs.com
REDIS_PORT=19579
REDIS_PASSWORD=FDpRjGKD5DKYqzPWA7HJFFdzvyZoWsfp
REDIS_DB=0
DATABASE_URL=postgresql://postgres:-DDcVxS8p39S?eH@db.ewujfnpjrjxvgdpgniox.supabase.co:5432/postgres
ENVIRONMENT=production
LOG_LEVEL=INFO
MAX_WORKERS=2
ALLOWED_ORIGINS=*
```

### Step 4: Deploy
- Click "Create Web Service"
- Wait 5-10 minutes for deployment
- Get your service URL: `https://biomed-scholar-api.onrender.com`

### Step 5: Verify Backend
```bash
curl https://biomed-scholar-api.onrender.com/api/v1/health
```

---

## Frontend: Vercel

### Step 1: Create Vercel Account
1. Visit https://vercel.com/
2. Sign up with GitHub

### Step 2: Import Project
1. Click "Add New..." → "Project"
2. Import your `kash_proj` repository
3. Configure:
   - **Framework Preset**: Other
   - **Root Directory**: `frontend`
   - **Build Command**: (leave empty)
   - **Output Directory**: `.`

### Step 3: Deploy
- Click "Deploy"
- Wait ~2 minutes
- Get URL: `https://biomed-scholar.vercel.app` (or similar)

### Step 4: Update Backend URL
After getting your Render backend URL, update `frontend/app.js`:
```javascript
const RENDER_BACKEND_URL = 'https://YOUR-ACTUAL-URL.onrender.com/api/v1';
```

Push to GitHub and Vercel will auto-redeploy.

---

## Verification

1. Open your Vercel URL
2. Check status indicator (should be green "Online")
3. Test search: "COVID-19 treatment"
4. Verify results are returned

---

## Important Notes

⚠️ **Render Free Tier**: Service spins down after 15 min inactivity (~30s cold start on first request)

✅ **100% Free**: All services remain free within usage limits

📊 **Monitor**: Keep an eye on Elasticsearch storage (125 MB limit)
