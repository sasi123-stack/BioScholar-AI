# 🚀 Manual HuggingFace Spaces Deployment Steps

Since git push authentication is timing out, use this manual method instead.

## ⚡ Quick Manual Deployment (5 minutes)

### Step 1: Go to Your HF Space
1. Open: **https://huggingface.co/spaces/sasi123-stack/biomed-scholar-api**
2. Click the **Files** tab in the top menu

### Step 2: Trigger Rebuild (Easiest Method)
The simplest option is to force a rebuild of your existing Space:

1. In your Space, click **Settings** (top right)
2. Scroll down to **"Restart"** or **"Rebuild"** section
3. Click **"Restart this Space"** 
4. Wait 3-5 minutes for the app to rebuild with latest code

**Why this works:** HF Spaces auto-pulls from your GitHub main branch. Since your code is already on GitHub with the Maverick endpoints, this should deploy them.

---

### Step 3: Verify Deployment (Alternative if Restart doesn't work)

If restart doesn't work, use the **git clone → edit → git push** method:

1. **Clone the Space locally:**
   ```bash
   git clone https://huggingface.co/spaces/sasi123-stack/biomed-scholar-api hf-space-local
   cd hf-space-local
   ```

2. **Copy updated files from main repo:**
   ```bash
   # Copy the entire src directory with Maverick endpoints
   cp -r /workspaces/BioScholar-AI/src/* ./src/
   
   # Copy app.py and other key files
   cp /workspaces/BioScholar-AI/requirements.txt ./
   cp /workspaces/BioScholar-AI/Dockerfile ./
   ```

3. **Commit and push:**
   ```bash
   git add .
   git commit -m "Deploy: Add Maverick sync endpoints"
   git push
   ```

4. **Space will auto-rebuild** - watch the "App" tab for build status

---

### Step 4: Test Maverick Endpoint After Deployment

After rebuild completes (3-5 minutes), test with:

```bash
python test_maverick_sync.py
```

Expected output when working:
```
Status: 200
Response: {"answer": "...", "status": "success", ...}
```

---

## 🔍 What Changed (Maverick Endpoints)

The following commits added the missing endpoints to your codebase:

- ✅ **Route Definition**: `src/api/routes.py` (lines 611-676)
- ✅ **Models**: `src/api/models.py` (MaverickChatRequest, MaverickChatResponse)
- ✅ **Database Functions**: Maverick conversation history sync

The HF Space needs to use the LATEST version containing these endpoints.

---

## 📋 Option A: Use GitHub as Source (Recommended)

If your HF Space is linked to GitHub:

1. Go to Space **Settings**
2. Look for **"Repository"** or **"Source"** section
3. Ensure it's pointing to: `https://github.com/sasi123-stack/BioScholar-AI`
4. Click **Sync** or **Pull Latest**
5. Space auto-rebuilds

---

## 📋 Option B: Redeploy Complete Docker Image

If you want to be 100% sure, redeploy from scratch:

1. Delete the old Space (Settings → Danger Zone)
2. Create new Space with same name, SDK=Docker, Hardware=Free
3. Configure secrets (ELASTICSEARCH, REDIS, DATABASE_URL, GROQ_API_KEY)
4. Run: `git push huggingface main:main` (with proper auth)

---

## ✅ Verification Checklist

After deployment, verify:

```bash
# 1. Health check (should return 200)
curl https://sasidhara123-biomed-scholar-api.hf.space/api/v1/health

# 2. Maverick chat endpoint (should return 200, not 404)
python test_maverick_sync.py

# 3. Check version increased
# Edit DEPLOY_HF_BACKEND.md line with timestamp to track deploys
```

---

## 🆘 If Still Getting 404 After Rebuild

This means the code changes haven't been picked up. Try:

1. **Hard restart the Space** (Settings → Restart)
2. **Check logs** (App → Logs tab) for build errors
3. **Verify files were copied** (Files tab should show latest src/)
4. **Check Python version** - Ensure 3.9+ for proper FastAPI routing
5. **Review app.py** - Ensure `app.include_router(router)` is present

---

## ⏱️ Deployment Timeline

- ✅ **1-2 min**: Sync files from GitHub/git push
- ✅ **2-5 min**: Docker image rebuild
- ✅ **1-2 min**: Model loading and initialization  
- ✅ **Total: 4-8 minutes** before Maverick endpoints are live

