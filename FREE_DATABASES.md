# Free Database Options for Cloud Deployment

## 🎯 Recommended Free Database Services

### 1. Elasticsearch - Bonsai (FREE TIER)

**Free Plan:**
- ✅ 125 MB storage
- ✅ Shared cluster
- ✅ No credit card required
- ✅ Perfect for testing/development

**Setup:**
1. Sign up: https://bonsai.io/
2. Create a cluster (select free tier)
3. Get connection URL
4. Add to your Cloud Run environment variables

**Connection String Format:**
```
https://username:password@your-cluster.bonsai.io
```

---

### 2. Redis - Redis Cloud (FREE TIER)

**Free Plan:**
- ✅ 30 MB storage
- ✅ 30 connections
- ✅ No credit card required
- ✅ Good for caching

**Setup:**
1. Sign up: https://redis.com/try-free/
2. Create database (select free tier)
3. Get connection details
4. Add to your Cloud Run environment variables

**Connection Format:**
```
Host: redis-xxxxx.c1.us-east-1-2.ec2.cloud.redislabs.com
Port: 12345
Password: your-password
```

---

### 3. PostgreSQL - ElephantSQL (FREE TIER)

**Free Plan (Tiny Turtle):**
- ✅ 20 MB storage
- ✅ 5 concurrent connections
- ✅ No credit card required
- ✅ Shared server

**Setup:**
1. Sign up: https://www.elephantsql.com/
2. Create instance (select Tiny Turtle - Free)
3. Get connection URL
4. Add to your Cloud Run environment variables

**Connection String Format:**
```
postgresql://username:password@host.db.elephantsql.com/database
```

**Alternative: Supabase (Better Free Tier)**
- ✅ 500 MB storage
- ✅ Unlimited API requests
- ✅ No credit card required
- Sign up: https://supabase.com/

---

## 📊 Storage Comparison

| Service | Free Storage | Best For |
|---------|--------------|----------|
| **Bonsai Elasticsearch** | 125 MB | ~1,000-2,000 documents |
| **Redis Cloud** | 30 MB | Caching, sessions |
| **ElephantSQL** | 20 MB | Small datasets |
| **Supabase PostgreSQL** | 500 MB | Better for production |

---

## 🚀 Quick Setup Guide

### Step 1: Sign Up for All Services

```bash
# Open these URLs in your browser:
# 1. Bonsai: https://bonsai.io/
# 2. Redis Cloud: https://redis.com/try-free/
# 3. Supabase: https://supabase.com/
```

### Step 2: Get Connection Details

After signing up, you'll receive:
- **Elasticsearch**: Full URL with credentials
- **Redis**: Host, port, password
- **PostgreSQL**: Connection string

### Step 3: Create .env.production File

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

# PostgreSQL (from Supabase or ElephantSQL)
DATABASE_URL=postgresql://user:pass@host:5432/database
```

### Step 4: Set Environment Variables in Cloud Run

```bash
# Set all environment variables at once
gcloud run services update biomed-scholar-api \
  --update-env-vars \
ELASTICSEARCH_HOST=your-cluster.bonsai.io,\
ELASTICSEARCH_PORT=443,\
ELASTICSEARCH_SCHEME=https,\
ELASTICSEARCH_USERNAME=your-username,\
ELASTICSEARCH_PASSWORD=your-password,\
REDIS_HOST=your-redis-host,\
REDIS_PORT=12345,\
REDIS_PASSWORD=your-redis-password,\
DATABASE_URL=postgresql://user:pass@host:5432/database
```

---

## ⚠️ Important Limitations

### Free Tier Constraints:

1. **Elasticsearch (125 MB)**
   - Can store ~1,000-2,000 documents
   - Good for testing, not production
   - Consider upgrading to paid tier ($10/month) for more data

2. **Redis (30 MB)**
   - Sufficient for caching
   - May need to clear old cache regularly

3. **PostgreSQL (20 MB ElephantSQL / 500 MB Supabase)**
   - ElephantSQL: Very limited
   - Supabase: Better option, more generous

### Recommendations:

**For Development/Testing:**
- ✅ Use all free tiers
- ✅ Index a small dataset (~1,000 documents)
- ✅ Perfect for demos and testing

**For Production:**
- Consider paid tiers:
  - Bonsai Elasticsearch: $10-15/month
  - Redis Cloud: Free tier is usually sufficient
  - Supabase: Free tier is generous, or $25/month for more

---

## 🎯 Optimized Setup for Your Project

### Recommended Configuration:

1. **Elasticsearch**: Bonsai Free (125 MB)
   - Index only the most important 1,000-2,000 articles
   - Use filters to select high-quality papers

2. **Redis**: Redis Cloud Free (30 MB)
   - Use for caching search results
   - Set TTL to auto-expire old cache

3. **PostgreSQL**: Supabase Free (500 MB)
   - Store user data, preferences
   - Store metadata (not full documents)

### Modified Ingestion Script:

```python
# For free tier, use smaller limits
python scripts/ingest_full_dataset.py --max-per-query 50 --max-per-condition 50

# This will give you ~1,250 documents total
# Perfect for the 125 MB Elasticsearch free tier
```

---

## 📝 Setup Checklist

- [ ] Sign up for Bonsai Elasticsearch
- [ ] Sign up for Redis Cloud
- [ ] Sign up for Supabase PostgreSQL
- [ ] Get all connection credentials
- [ ] Create `.env.production` file
- [ ] Test connections locally
- [ ] Deploy to Cloud Run
- [ ] Set environment variables
- [ ] Run small data ingestion
- [ ] Test the deployed API

---

## 🔗 Quick Links

- **Bonsai Elasticsearch**: https://bonsai.io/
- **Redis Cloud**: https://redis.com/try-free/
- **Supabase**: https://supabase.com/
- **ElephantSQL**: https://www.elephantsql.com/
- **Google Cloud Run**: https://cloud.google.com/run

---

## 💡 Pro Tip

Start with the free tiers to test your deployment. Once everything works, you can:
1. Upgrade databases to paid tiers (~$20-30/month total)
2. Index your full dataset
3. Keep Cloud Run free (within 2M requests/month)

**Total Cost for Production:**
- Cloud Run: $0 (free tier)
- Databases: $20-30/month
- **Total: ~$25/month** for a fully cloud-hosted solution
