# 🚀 Deploy OpenClaw to Hugging Face - Complete Guide

## 📋 Prerequisites

- ✅ Hugging Face account (free)
- ✅ OpenRouter API key (free - get from https://openrouter.ai/keys)
- ✅ Files in `openclaw-hf/` folder ready

---

## 🎯 Deployment Steps

### Step 1: Create Hugging Face Space

1. **Go to**: https://huggingface.co/new-space

2. **Fill in details**:
   - **Owner**: Your username
   - **Space name**: `biosense-ai-agent` (or any name you like)
   - **License**: MIT
   - **Select SDK**: **Docker** ⚠️ Important!
   - **Space hardware**: CPU basic - free tier ✅
   - **Visibility**: Public or Private (your choice)

3. **Click**: "Create Space"

---

### Step 2: Upload Files

#### Option A: Web Upload (Easiest)

1. **In your new Space**, click "Files" tab

2. **Click**: "Add file" → "Upload files"

3. **Upload ALL files** from `openclaw-hf/` folder:
   ```
   openclaw-hf/
   ├── Dockerfile          ← Upload this
   ├── README.md           ← Upload this
   └── workspace/          ← Upload entire folder
       ├── AGENTS.md
       ├── SOUL.md
       ├── IDENTITY.md
       ├── TOOLS.md
       ├── HEARTBEAT.md
       ├── BOOTSTRAP.md
       ├── USER.md
       └── .openclaw/
           └── workspace-state.json
   ```

4. **Commit**: Add commit message "Initial deployment"

#### Option B: Git Upload (Advanced)

```bash
# Clone your Space
git clone https://huggingface.co/spaces/YOUR_USERNAME/biosense-ai-agent
cd biosense-ai-agent

# Copy files
cp -r ../openclaw-hf/* .

# Commit and push
git add .
git commit -m "Deploy OpenClaw with Llama 3.3 70B"
git push
```

---

### Step 3: Add API Key (CRITICAL!)

1. **Go to**: Your Space → **Settings** tab

2. **Scroll to**: "Variables and secrets"

3. **Click**: "New secret"

4. **Add secret**:
   - **Name**: `OPENROUTER_API_KEY`
   - **Value**: Your OpenRouter API key (starts with `sk-or-v1-`)
   - **Description**: "OpenRouter API key for Llama 3.3 70B"

5. **Important**: Make sure it's a **Secret** (not a Variable)!

6. **Click**: "Save"

---

### Step 4: Wait for Build

1. **Go to**: "App" tab

2. **Watch the build logs**:
   - Building Docker image (~5-10 minutes)
   - Installing dependencies
   - Starting OpenClaw gateway

3. **Look for**:
   ```
   ✅ OpenClaw gateway started on port 7860
   ✅ Ready to accept connections
   ```

4. **If build fails**: Check the logs and see troubleshooting below

---

### Step 5: Test Your Agent

1. **Once running**, you'll see the OpenClaw chat interface

2. **Test with a simple message**:
   ```
   Hello! Can you help me with biomedical research?
   ```

3. **Test biomedical Q&A**:
   ```
   What are the main symptoms of Type 2 diabetes?
   ```

4. **Verify citations**:
   - Agent should reference sources with [1], [2], etc.
   - Responses should be evidence-based

---

## 🎨 Customize Your Space

### Update Space Card

Edit the README.md header in your Space:

```yaml
---
title: My BioMed AI Assistant
emoji: 🔬
colorFrom: blue
colorTo: purple
sdk: docker
pinned: true
---
```

### Customize Agent Behavior

Edit `workspace/SOUL.md` to change personality:

```markdown
# SOUL.md

You are a friendly biomedical research assistant specializing in...
```

### Change Authentication Token

Edit Dockerfile, line 48:
```dockerfile
"token": "your-custom-token-here"
```

---

## 🔧 Troubleshooting

### Build Fails: "npm install openclaw failed"

**Solution**: Node 24 Alpine might have compatibility issues. Try:

```dockerfile
# In Dockerfile, line 1, change to:
FROM node:24-slim
```

### Build Fails: "Permission denied"

**Solution**: Ensure COPY commands have correct ownership:

```dockerfile
COPY --chown=node:node workspace $OPENCLAW_HOME/workspace
```

### Runtime Error: "API key not found"

**Solutions**:
1. Verify you added `OPENROUTER_API_KEY` as a **Secret** (not Variable)
2. Check the key starts with `sk-or-v1-`
3. Restart the Space after adding the secret

### Gateway Won't Start

**Check**:
1. Port 7860 is exposed in Dockerfile
2. Environment variables are set correctly
3. Review build logs for errors

### "Rate limit exceeded"

**Solution**: Free tier allows 50 requests/day
- Wait 24 hours for reset
- Or upgrade to OpenRouter paid tier
- Or switch to Groq (14,400 req/day free)

---

## 📊 Monitoring Your Space

### Check Usage

1. **Go to**: Space → Settings → Analytics
2. **View**: Request count, uptime, errors
3. **Monitor**: API usage on OpenRouter dashboard

### View Logs

1. **Go to**: Space → Logs tab
2. **Check**: Real-time container logs
3. **Debug**: Any runtime errors

---

## 🔄 Update Your Deployment

### Update Code

```bash
# Make changes locally
cd openclaw-hf
# Edit files...

# Push to Space
git add .
git commit -m "Update agent configuration"
git push
```

### Update API Key

1. Go to Settings → Variables and secrets
2. Delete old `OPENROUTER_API_KEY`
3. Add new secret with updated key
4. Restart Space

---

## 💰 Cost Optimization

### Free Tier Limits

**OpenRouter Free**:
- 50 requests/day
- 20 requests/minute
- $0.00 cost

**Hugging Face Free**:
- CPU basic (free)
- 16 GB RAM
- 2 vCPU cores

### Upgrade Options

**If you need more**:

1. **OpenRouter Paid**: ~$0.50 per 1M tokens
2. **HF Upgraded Hardware**: $0.60/hour for better CPU
3. **Switch to Groq**: 14,400 free req/day

---

## 🌟 Best Practices

### Security

- ✅ Always use Secrets for API keys
- ✅ Don't commit API keys to Git
- ✅ Use authentication tokens
- ✅ Set Space to Private if handling sensitive data

### Performance

- ✅ Use Alpine images for smaller size
- ✅ Cache npm dependencies
- ✅ Monitor response times
- ✅ Set appropriate rate limits

### Reliability

- ✅ Add health checks
- ✅ Monitor error logs
- ✅ Have fallback API keys
- ✅ Test before deploying

---

## 📚 Additional Resources

- **Hugging Face Docs**: https://huggingface.co/docs/hub/spaces
- **OpenClaw Docs**: https://openclaw.ai/docs
- **OpenRouter Docs**: https://openrouter.ai/docs
- **Docker Best Practices**: https://docs.docker.com/develop/dev-best-practices/

---

## 🎉 Success Checklist

- [ ] Space created on Hugging Face
- [ ] All files uploaded
- [ ] `OPENROUTER_API_KEY` added to Secrets
- [ ] Build completed successfully
- [ ] Gateway started on port 7860
- [ ] Agent responds to test messages
- [ ] Citations working correctly
- [ ] Space URL shared with team

---

## 🆘 Need Help?

1. **Check logs**: Space → Logs tab
2. **Review docs**: `OPENROUTER_FREE_SETUP.md`
3. **Test locally**: Use Docker to debug
4. **Community**: HF forums or OpenClaw Discord

---

**Made with ❤️ for easy deployment to Hugging Face Spaces**

*Happy deploying! 🚀*
