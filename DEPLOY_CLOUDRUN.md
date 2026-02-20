# Google Cloud Run Deployment Guide

## Prerequisites

1. **Google Cloud Account** (Free tier - no credit card required initially)
   - Sign up at: https://cloud.google.com/free

2. **Install Google Cloud CLI**
   - Download: https://cloud.google.com/sdk/docs/install
   - Or use Cloud Shell (browser-based, no installation needed)

## Important: Database Setup

⚠️ **Your application requires external databases:**
- Elasticsearch
- Redis  
- PostgreSQL

### Database Options:

#### Option 1: Use Managed Services (Recommended but costs money)
- **Elasticsearch**: Elastic Cloud (14-day free trial)
- **Redis**: Redis Cloud (free tier: 30MB)
- **PostgreSQL**: Google Cloud SQL (costs ~$10/month)

#### Option 2: Use Free External Services
- **Elasticsearch**: Bonsai Elasticsearch (free tier: 125MB)
  - https://bonsai.io/
- **Redis**: Redis Cloud (free tier: 30MB)
  - https://redis.com/try-free/
- **PostgreSQL**: ElephantSQL (free tier: 20MB)
  - https://www.elephantsql.com/

#### Option 3: Keep Databases Local + Ngrok (Current Setup)
- Keep using your local databases
- Use ngrok to expose them
- Cloud Run connects to your local services via ngrok

## Deployment Steps

### 1. Install Google Cloud CLI

**Windows (PowerShell):**
```powershell
# Download and run the installer
# https://cloud.google.com/sdk/docs/install

# Or use Chocolatey
choco install gcloudsdk
```

### 2. Initialize and Login

```bash
# Login to Google Cloud
gcloud auth login

# Set your project (or create a new one)
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### 3. Configure Environment Variables

Create a `.env.production` file with your database URLs:

```env
# Elasticsearch
ELASTICSEARCH_HOST=your-elasticsearch-url
ELASTICSEARCH_PORT=9200

# Redis
REDIS_HOST=your-redis-url
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password

# PostgreSQL
DATABASE_URL=postgresql://user:password@host:port/dbname

# Optional: API Keys
PUBMED_API_KEY=your-key
CLINICAL_TRIALS_API_KEY=your-key
```

### 4. Build and Deploy

**Option A: Deploy with gcloud (Recommended)**

```bash
# Navigate to project directory
cd c:\Users\sasid\Downloads\kash_proj

# Deploy to Cloud Run
gcloud run deploy biomed-scholar-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10 \
  --env-vars-file .env.production

# Note: This will build the Docker image automatically
```

**Option B: Build Docker Image First**

```bash
# Build the image
docker build -f Dockerfile.cloudrun -t gcr.io/YOUR_PROJECT_ID/biomed-scholar-api .

# Push to Google Container Registry
docker push gcr.io/YOUR_PROJECT_ID/biomed-scholar-api

# Deploy to Cloud Run
gcloud run deploy biomed-scholar-api \
  --image gcr.io/YOUR_PROJECT_ID/biomed-scholar-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300
```

### 5. Set Environment Variables (After Deployment)

```bash
# Set environment variables
gcloud run services update biomed-scholar-api \
  --update-env-vars ELASTICSEARCH_HOST=your-host,REDIS_HOST=your-host,DATABASE_URL=your-url
```

### 6. Get Your Cloud Run URL

```bash
# Get the service URL
gcloud run services describe biomed-scholar-api --region us-central1 --format 'value(status.url)'
```

## Cost Estimation

### Free Tier Limits:
- **2 million requests/month** (free)
- **360,000 GB-seconds memory** (free)
- **180,000 vCPU-seconds** (free)

### Typical Usage:
- Small app: **$0/month** (within free tier)
- Medium app: **$5-10/month**
- Heavy usage: **$20-50/month**

## Quick Start (Simplified)

If you want to deploy quickly with local databases:

```bash
# 1. Login
gcloud auth login

# 2. Create project
gcloud projects create biomed-scholar --name="BioMed Scholar"
gcloud config set project biomed-scholar

# 3. Enable billing (required even for free tier)
# Visit: https://console.cloud.google.com/billing

# 4. Deploy
cd c:\Users\sasid\Downloads\kash_proj
gcloud run deploy biomed-scholar-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## Monitoring

```bash
# View logs
gcloud run services logs read biomed-scholar-api --region us-central1

# View metrics
gcloud run services describe biomed-scholar-api --region us-central1
```

## Updating Your Deployment

```bash
# Redeploy after code changes
gcloud run deploy biomed-scholar-api \
  --source . \
  --region us-central1
```

## Troubleshooting

### Issue: Container fails to start
- Check logs: `gcloud run services logs read biomed-scholar-api`
- Verify environment variables are set correctly
- Ensure databases are accessible from Cloud Run

### Issue: Cold starts are slow
- Increase minimum instances: `--min-instances 1`
- Note: This will use more free tier quota

### Issue: Out of memory
- Increase memory: `--memory 4Gi`
- Optimize your code to use less memory

## Next Steps

1. ✅ Set up free database services (see options above)
2. ✅ Deploy to Cloud Run
3. ✅ Update your frontend to use the Cloud Run URL
4. ✅ Test the deployment
5. ✅ Monitor usage to stay within free tier

## Important Notes

⚠️ **Database Consideration:**
Your app is data-heavy with Elasticsearch indexing. The free tier databases might be too small. Consider:
- Starting with a small dataset for testing
- Using paid database tiers for production
- Or keeping databases local with ngrok (development only)

🎯 **Recommendation:**
For true production deployment, budget ~$20-30/month for:
- Cloud Run: Free (within limits)
- Elasticsearch: ~$10-15/month
- PostgreSQL: ~$7-10/month  
- Redis: Free tier sufficient
