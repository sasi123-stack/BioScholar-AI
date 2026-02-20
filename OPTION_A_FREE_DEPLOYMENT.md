# Option A: Fully Free Cloud Deployment - Step by Step Guide

## 🎯 Goal
Deploy your BioMed Scholar application completely free using:
- Google Cloud Run (Free tier)
- Bonsai Elasticsearch (Free tier - 125 MB)
- Redis Cloud (Free tier - 30 MB)
- Supabase PostgreSQL (Free tier - 500 MB)

**Total Cost: $0/month**

---

## 📋 Prerequisites Checklist

Before starting, make sure you have:
- [ ] Google account (for Cloud Run)
- [ ] Email address (for database signups)
- [ ] Google Cloud CLI installed
- [ ] Your project code ready

---

## Step 1: Set Up Free Databases (30 minutes)

### 1.1 Bonsai Elasticsearch (FREE - 125 MB)

**Sign Up:**
1. Go to: https://bonsai.io/
2. Click "Start Free Trial" or "Sign Up"
3. Choose the **FREE plan** (Sandbox)
4. No credit card required!

**Get Connection Details:**
1. After signup, go to your dashboard
2. Click on your cluster
3. Copy the **Access URL** (looks like: `https://username:password@cluster.bonsai.io`)
4. Save these details:
   ```
   Full URL: https://username:password@your-cluster.bonsai.io
   Host: your-cluster.bonsai.io
   Port: 443
   Username: [from URL]
   Password: [from URL]
   ```

---

### 1.2 Redis Cloud (FREE - 30 MB)

**Sign Up:**
1. Go to: https://redis.com/try-free/
2. Click "Get Started Free"
3. Sign up with email
4. Select **FREE tier** (30 MB)
5. No credit card required!

**Get Connection Details:**
1. Go to your database dashboard
2. Click "Connect"
3. Copy the connection details:
   ```
   Host: redis-xxxxx.c1.us-east-1-2.ec2.cloud.redislabs.com
   Port: 12345
   Password: your-password
   ```

---

### 1.3 Supabase PostgreSQL (FREE - 500 MB)

**Sign Up:**
1. Go to: https://supabase.com/
2. Click "Start your project"
3. Sign in with GitHub or email
4. Create a new project
5. Choose a **Database Password** (save this!)
6. Select region (choose closest to you)
7. Wait for project to initialize (~2 minutes)

**Get Connection Details:**
1. Go to Project Settings → Database
2. Scroll to "Connection string"
3. Select "URI" tab
4. Copy the connection string:
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres
   ```
5. Replace `[YOUR-PASSWORD]` with your actual password

---

## Step 2: Create Environment Variables File

Create a file called `.env.production` in your project folder:

```env
# Elasticsearch (from Bonsai)
ELASTICSEARCH_HOST=your-cluster.bonsai.io
ELASTICSEARCH_PORT=443
ELASTICSEARCH_SCHEME=https
ELASTICSEARCH_USERNAME=your-username
ELASTICSEARCH_PASSWORD=your-password

# Redis (from Redis Cloud)
REDIS_HOST=redis-xxxxx.c1.us-east-1-2.ec2.cloud.redislabs.com
REDIS_PORT=12345
REDIS_PASSWORD=your-redis-password
REDIS_DB=0

# PostgreSQL (from Supabase)
DATABASE_URL=postgresql://postgres:your-password@db.xxxxx.supabase.co:5432/postgres

# Application Settings
ENVIRONMENT=production
LOG_LEVEL=INFO
ALLOWED_ORIGINS=*
```

**Action Required:**
1. Open: `c:\Users\sasid\Downloads\kash_proj\.env.production.template`
2. Copy it to: `c:\Users\sasid\Downloads\kash_proj\.env.production`
3. Fill in your actual database credentials

---

## Step 3: Install Google Cloud CLI

### Windows Installation:

**Option A: Download Installer**
1. Go to: https://cloud.google.com/sdk/docs/install
2. Download the Windows installer
3. Run the installer
4. Follow the prompts
5. Restart your terminal

**Option B: Using Chocolatey**
```powershell
choco install gcloudsdk
```

**Verify Installation:**
```powershell
gcloud --version
```

---

## Step 4: Initialize Google Cloud

```powershell
# 1. Login to Google Cloud
gcloud auth login

# 2. Create a new project (or use existing)
gcloud projects create biomed-scholar --name="BioMed Scholar"

# 3. Set the project
gcloud config set project biomed-scholar

# 4. Enable billing (required even for free tier)
# You'll need to visit: https://console.cloud.google.com/billing
# Link a billing account (no charges within free tier limits)

# 5. Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

---

## Step 5: Prepare Your Application

### 5.1 Update Configuration Files

Check that your app can read environment variables. The code should already support this.

### 5.2 Reduce Dataset Size (Important for Free Tier!)

Since Bonsai free tier is only 125 MB, we need to index fewer documents:

```powershell
# Edit the ingestion script to use smaller limits
# Already done - just use these parameters when indexing:
python scripts/ingest_full_dataset.py --max-per-query 40 --max-per-condition 40

# This will give you ~1,000 documents total
# Perfect for the 125 MB free tier
```

---

## Step 6: Deploy to Google Cloud Run

### Option A: Using the Automated Script (Recommended)

```powershell
cd c:\Users\sasid\Downloads\kash_proj
.\deploy-cloudrun.ps1
```

### Option B: Manual Deployment

```powershell
cd c:\Users\sasid\Downloads\kash_proj

gcloud run deploy biomed-scholar-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10
```

**This will:**
1. Build your Docker container
2. Push it to Google Container Registry
3. Deploy to Cloud Run
4. Give you a public URL

---

## Step 7: Set Environment Variables in Cloud Run

After deployment, set your database credentials:

```powershell
gcloud run services update biomed-scholar-api \
  --region us-central1 \
  --update-env-vars \
ELASTICSEARCH_HOST=your-cluster.bonsai.io,\
ELASTICSEARCH_PORT=443,\
ELASTICSEARCH_SCHEME=https,\
ELASTICSEARCH_USERNAME=your-username,\
ELASTICSEARCH_PASSWORD=your-password,\
REDIS_HOST=your-redis-host,\
REDIS_PORT=12345,\
REDIS_PASSWORD=your-redis-password,\
DATABASE_URL=postgresql://postgres:password@db.xxxxx.supabase.co:5432/postgres,\
ENVIRONMENT=production,\
ALLOWED_ORIGINS=*
```

**Important:** Replace all the placeholder values with your actual credentials!

---

## Step 8: Get Your Cloud Run URL

```powershell
gcloud run services describe biomed-scholar-api \
  --region us-central1 \
  --format 'value(status.url)'
```

**Save this URL!** You'll need it for your frontend.

Example: `https://biomed-scholar-api-xxxxx-uc.a.run.app`

---

## Step 9: Index Your Data

Now that your backend is deployed, index some data:

### Option A: Index from Local Machine

```powershell
# Update your local .env to point to cloud databases
# Then run ingestion
python scripts/ingest_full_dataset.py --max-per-query 40 --max-per-condition 40
```

### Option B: Index via Cloud Run (Advanced)

You can trigger indexing through your API endpoints once deployed.

---

## Step 10: Update Your Frontend

Update your Firebase-hosted frontend to use the new Cloud Run URL:

1. Open: `c:\Users\sasid\Downloads\kash_proj\frontend\app.js`
2. Find the API URL configuration
3. Replace with your Cloud Run URL:
   ```javascript
   const API_URL = 'https://biomed-scholar-api-xxxxx-uc.a.run.app';
   ```
4. Deploy to Firebase:
   ```powershell
   cd frontend
   firebase deploy
   ```

---

## Step 11: Test Your Deployment

```powershell
# Test health endpoint
curl https://your-cloud-run-url.app/

# Test search
curl "https://your-cloud-run-url.app/api/search?query=cancer"
```

---

## 🎉 Success Checklist

- [ ] Bonsai Elasticsearch account created
- [ ] Redis Cloud account created
- [ ] Supabase PostgreSQL account created
- [ ] `.env.production` file created with credentials
- [ ] Google Cloud CLI installed
- [ ] Google Cloud project created
- [ ] Deployed to Cloud Run
- [ ] Environment variables set
- [ ] Data indexed
- [ ] Frontend updated with Cloud Run URL
- [ ] Everything tested and working

---

## 📊 What You Get

### Your Fully Free Cloud Setup:

✅ **Backend API**: Hosted on Google Cloud Run
- URL: `https://your-app.run.app`
- Always online
- Scales automatically
- 2M requests/month free

✅ **Elasticsearch**: Bonsai free tier
- 125 MB storage
- ~1,000-2,000 documents
- Full-text search

✅ **Redis**: Redis Cloud free tier
- 30 MB storage
- Caching enabled

✅ **PostgreSQL**: Supabase free tier
- 500 MB storage
- Metadata and user data

✅ **Frontend**: Firebase Hosting
- Already deployed
- Global CDN
- Free tier

**Total Monthly Cost: $0** 🎉

---

## 🔧 Troubleshooting

### Issue: Deployment fails
```powershell
# Check logs
gcloud run services logs read biomed-scholar-api --region us-central1
```

### Issue: Can't connect to databases
- Verify credentials in `.env.production`
- Check database dashboards for connection strings
- Ensure databases are active

### Issue: Out of memory
- Reduce dataset size
- Increase Cloud Run memory (still free within limits)

---

## 📝 Important Notes

### Free Tier Limits:

**Google Cloud Run:**
- 2M requests/month
- 360,000 GB-seconds memory
- 180,000 vCPU-seconds

**Bonsai Elasticsearch:**
- 125 MB storage (~1,000-2,000 documents)
- Shared cluster

**Redis Cloud:**
- 30 MB storage
- 30 concurrent connections

**Supabase:**
- 500 MB database
- Unlimited API requests
- 2 GB bandwidth

### Tips to Stay Within Free Tier:

1. **Index selectively** - Only high-quality papers
2. **Use caching** - Reduce database queries
3. **Monitor usage** - Check dashboards regularly
4. **Optimize queries** - Efficient search patterns

---

## 🚀 Next Steps After Deployment

1. **Monitor your usage:**
   - Google Cloud Console: https://console.cloud.google.com/
   - Bonsai Dashboard: https://app.bonsai.io/
   - Redis Cloud Dashboard: https://app.redislabs.com/
   - Supabase Dashboard: https://app.supabase.com/

2. **Set up alerts** for when approaching limits

3. **Optimize your application** for better performance

4. **Consider upgrading** if you need more capacity (~$35/month for production)

---

## 💡 Pro Tips

- **Start small**: Index 500-1,000 documents first
- **Test thoroughly**: Make sure everything works before full indexing
- **Monitor costs**: Even though it's free, keep an eye on usage
- **Have a backup**: Keep your local setup as a fallback

---

## 🆘 Need Help?

If you encounter issues:
1. Check the logs: `gcloud run services logs read biomed-scholar-api`
2. Verify database connections in their dashboards
3. Test each service individually
4. Review the deployment guide: `DEPLOY_CLOUDRUN.md`

---

**Ready to deploy? Let's start with Step 1!** 🚀
