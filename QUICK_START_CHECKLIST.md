# Quick Start Checklist for Option A Deployment

## 📋 Step-by-Step Checklist

### Phase 1: Database Setup (Do These First!)

#### ✅ Step 1: Bonsai Elasticsearch
- [ ] Go to: https://bonsai.io/
- [ ] Click "Start Free Trial"
- [ ] Sign up (no credit card needed)
- [ ] Create a FREE cluster
- [ ] Copy connection URL
- [ ] Save credentials:
  ```
  Host: ___________________.bonsai.io
  Port: 443
  Username: ___________________
  Password: ___________________
  ```

#### ✅ Step 2: Redis Cloud
- [ ] Go to: https://redis.com/try-free/
- [ ] Click "Get Started Free"
- [ ] Sign up (no credit card needed)
- [ ] Create FREE database (30 MB)
- [ ] Copy connection details
- [ ] Save credentials:
  ```
  Host: ___________________
  Port: ___________________
  Password: ___________________
  ```

#### ✅ Step 3: Supabase PostgreSQL
- [ ] Go to: https://supabase.com/
- [ ] Click "Start your project"
- [ ] Sign up with GitHub or email
- [ ] Create new project
- [ ] Set database password (SAVE THIS!)
- [ ] Wait for initialization (~2 min)
- [ ] Go to Settings → Database
- [ ] Copy connection string
- [ ] Save credentials:
  ```
  Connection String: postgresql://postgres:___@db.___.supabase.co:5432/postgres
  ```

---

### Phase 2: Google Cloud Setup

#### ✅ Step 4: Install Google Cloud CLI
- [ ] Download from: https://cloud.google.com/sdk/docs/install
- [ ] Run installer
- [ ] Restart terminal
- [ ] Verify: `gcloud --version`

#### ✅ Step 5: Create Google Cloud Account
- [ ] Go to: https://console.cloud.google.com/
- [ ] Sign in with Google account
- [ ] Accept terms
- [ ] (Optional) Enable billing - still free within limits

---

### Phase 3: Configuration

#### ✅ Step 6: Create .env.production File
- [ ] Copy `.env.production.template` to `.env.production`
- [ ] Fill in Elasticsearch credentials
- [ ] Fill in Redis credentials
- [ ] Fill in PostgreSQL credentials
- [ ] Save file

#### ✅ Step 7: Initialize Google Cloud
```powershell
# Run these commands:
gcloud auth login
gcloud projects create biomed-scholar --name="BioMed Scholar"
gcloud config set project biomed-scholar
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

---

### Phase 4: Deployment

#### ✅ Step 8: Deploy to Cloud Run
```powershell
cd c:\Users\sasid\Downloads\kash_proj
.\deploy-cloudrun.ps1
```

#### ✅ Step 9: Set Environment Variables
```powershell
# Copy the command from OPTION_A_FREE_DEPLOYMENT.md
# Replace with your actual credentials
gcloud run services update biomed-scholar-api --update-env-vars ...
```

#### ✅ Step 10: Get Your URL
```powershell
gcloud run services describe biomed-scholar-api --region us-central1 --format 'value(status.url)'
```

---

### Phase 5: Data & Testing

#### ✅ Step 11: Index Data (Small Dataset)
```powershell
# Update local config to use cloud databases
python scripts/ingest_full_dataset.py --max-per-query 40 --max-per-condition 40
```

#### ✅ Step 12: Update Frontend
- [ ] Open `frontend/app.js`
- [ ] Update API_URL to Cloud Run URL
- [ ] Deploy: `firebase deploy`

#### ✅ Step 13: Test Everything
- [ ] Visit your Cloud Run URL
- [ ] Test search functionality
- [ ] Check frontend integration
- [ ] Verify data is indexed

---

## 🎯 Current Status

**What to do RIGHT NOW:**

1. **Open these 3 URLs in your browser:**
   - Bonsai: https://bonsai.io/
   - Redis Cloud: https://redis.com/try-free/
   - Supabase: https://supabase.com/

2. **Sign up for all three services** (15-20 minutes)

3. **Save all credentials** in a text file

4. **Download Google Cloud CLI:**
   - https://cloud.google.com/sdk/docs/install

5. **Come back when done!**

---

## 📝 Credentials Template

Copy this and fill it in as you sign up:

```
=== BONSAI ELASTICSEARCH ===
URL: https://___:___@___.bonsai.io
Host: ___.bonsai.io
Port: 443
Username: ___
Password: ___

=== REDIS CLOUD ===
Host: ___
Port: ___
Password: ___

=== SUPABASE POSTGRESQL ===
Connection String: postgresql://postgres:___@db.___.supabase.co:5432/postgres
Password: ___

=== GOOGLE CLOUD ===
Project ID: biomed-scholar
Cloud Run URL: (will get after deployment)
```

---

## ⏱️ Time Estimate

- Database signups: 15-20 minutes
- Google Cloud CLI install: 5 minutes
- Configuration: 10 minutes
- Deployment: 10-15 minutes
- Data indexing: 20-30 minutes

**Total: ~60-90 minutes**

---

## 🆘 Need Help?

If you get stuck:
1. Check the detailed guide: `OPTION_A_FREE_DEPLOYMENT.md`
2. Check database dashboards for connection info
3. Verify each step is complete before moving on

---

**Ready? Start with the database signups!** 🚀
