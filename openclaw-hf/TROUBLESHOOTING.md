# 🔧 OpenClaw Docker Build - Troubleshooting Guide

## ✅ Latest Fixes Applied

### Fix 1: Alpine Linux → Debian Slim
**Problem**: `node-llama-cpp` requires `glibc`, not available in Alpine  
**Solution**: Changed to `FROM node:24-slim` (Debian-based)

### Fix 2: Missing Config Error
**Problem**: "Missing config. Run `openclaw setup`"  
**Solution**: 
- Added explicit `--config` flag to CMD
- Created config in multiple locations as fallback
- Added API key and baseURL to config

---

## 🐛 Common Build Errors & Solutions

### Error 1: "cmake not found" or "glibc not detected"

```
[node-llama-cpp] The prebuilt binaries cannot be used in this Linux distro, 
as `glibc` is not detected
```

**Solution**: ✅ Fixed in latest Dockerfile
- Use `node:24-slim` instead of `node:24-alpine`
- Added `cmake` to dependencies

---

### Error 2: "Missing config" at runtime

```
Missing config. Run `openclaw setup` or set gateway.mode=local
```

**Solution**: ✅ Fixed in latest Dockerfile
- Config now created with explicit API key
- Added `--config` flag to startup command
- Config copied to multiple locations

---

### Error 3: "OPENROUTER_API_KEY not found"

**Cause**: Environment variable not set in Hugging Face Space

**Solution**:
1. Go to Space → Settings → Variables and secrets
2. Click "New secret"
3. Name: `OPENROUTER_API_KEY`
4. Value: Your OpenRouter API key
5. Mark as "Secret" ✅
6. Restart the Space

---

### Error 4: npm install fails with permission errors

**Cause**: Running npm as root user

**Solution**: ✅ Already fixed in Dockerfile
```dockerfile
USER node  # Switch to non-root user before npm install
```

---

### Error 5: "Port 7860 already in use"

**Cause**: Another process using port 7860

**Solution**: Hugging Face handles this automatically. If testing locally:
```bash
docker run -p 8080:7860 ...  # Use different host port
```

---

## 🚀 Verified Working Configuration

### Dockerfile Summary
```dockerfile
FROM node:24-slim                    # ✅ Debian-based with glibc
RUN apt-get install cmake g++ ...    # ✅ Build dependencies
USER node                            # ✅ Non-root user
RUN npm install openclaw             # ✅ Install OpenClaw
COPY workspace ...                   # ✅ Copy agent config
RUN echo '{ config }' > openclaw.json # ✅ Create config
CMD ["npx", "openclaw", "gateway", "--config", "..."] # ✅ Explicit config
```

### Required Environment Variables
- `OPENROUTER_API_KEY` - Your OpenRouter API key (required)

### Optional Environment Variables
- `OPENCLAW_HOME` - Default: `/home/node/.openclaw`
- `OPENCLAW_GATEWAY_PORT` - Default: `7860`
- `NODE_ENV` - Default: `production`

---

## 🧪 Testing Locally

### Build the Image
```bash
cd openclaw-hf
docker build -t openclaw-test .
```

### Run with API Key
```bash
docker run -p 7860:7860 \
  -e OPENROUTER_API_KEY=sk-or-v1-YOUR_KEY_HERE \
  openclaw-test
```

### Check Logs
```bash
docker logs <container_id>
```

### Expected Output
```
✅ OpenClaw gateway started on port 7860
✅ Config loaded from /home/node/.openclaw/openclaw.json
✅ Model: meta-llama/llama-3.3-70b-instruct
✅ Ready to accept connections
```

---

## 📊 Build Time Expectations

| Stage | Time | Notes |
|-------|------|-------|
| Base image pull | 1-2 min | First time only |
| System dependencies | 1-2 min | apt-get install |
| npm install openclaw | 5-10 min | Builds node-llama-cpp |
| Copy workspace | <10 sec | Small files |
| Create config | <5 sec | JSON generation |
| **Total** | **8-15 min** | First build |

Subsequent builds: ~2-5 minutes (cached layers)

---

## 🔍 Debugging Steps

### 1. Check Build Logs
Look for these success indicators:
- ✅ `Successfully installed openclaw`
- ✅ `node-llama-cpp` build completed
- ✅ Config file created

### 2. Check Runtime Logs
Look for:
- ✅ Gateway started on port 7860
- ✅ Config loaded successfully
- ❌ Any error messages

### 3. Verify Environment Variables
```bash
docker exec <container_id> env | grep OPENROUTER
```

Should show:
```
OPENROUTER_API_KEY=sk-or-v1-...
```

### 4. Check Config File
```bash
docker exec <container_id> cat /home/node/.openclaw/openclaw.json
```

Should show valid JSON with your model config.

---

## 🆘 Still Having Issues?

### Check These:

1. **API Key Valid?**
   - Test at: https://openrouter.ai/dashboard
   - Verify it starts with `sk-or-v1-`

2. **Hugging Face Space Settings?**
   - API key added as **Secret** (not Variable)
   - Space using **Docker SDK**
   - Hardware: CPU basic (free tier works)

3. **Dockerfile Syntax?**
   - No Windows line endings (CRLF)
   - Valid JSON in config
   - Proper escape characters

4. **Network Issues?**
   - OpenRouter API accessible
   - No firewall blocking
   - DNS resolution working

---

## 📚 Additional Resources

- **OpenClaw Docs**: https://openclaw.ai/docs
- **Node.js Docker**: https://hub.docker.com/_/node
- **Hugging Face Spaces**: https://huggingface.co/docs/hub/spaces
- **OpenRouter Status**: https://status.openrouter.ai

---

## ✅ Success Checklist

Before deploying, verify:

- [ ] Using `node:24-slim` (not Alpine)
- [ ] `cmake` and `g++` installed
- [ ] Config file created with API key
- [ ] `--config` flag in CMD
- [ ] `OPENROUTER_API_KEY` set in HF Secrets
- [ ] Workspace files copied
- [ ] Port 7860 exposed
- [ ] Non-root user (node)

---

**Last Updated**: 2026-02-17  
**Dockerfile Version**: v2.0 (Debian Slim + Fixed Config)
