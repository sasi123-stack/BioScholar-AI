# 🆓 FREE OpenRouter Setup - Llama 3.3 70B

## ✅ Configuration Complete!

Your OpenClaw is now configured to use **OpenRouter's FREE tier** with **Meta Llama 3.3 70B Instruct**!

---

## 🚀 Quick Setup (2 Minutes)

### Step 1: Get Your FREE OpenRouter API Key
1. Visit: **https://openrouter.ai/keys**
2. Sign up with Google/GitHub (no credit card needed!)
3. Click "Create Key"
4. Copy your API key (starts with `sk-or-v1-`)

### Step 2: Update Your `.env` File
Open `.env` and replace the placeholder:

```bash
# Find this line:
OPENCLAW_API_KEY=sk-or-v1-YOUR_OPENROUTER_API_KEY_HERE

# Replace with your actual key:
OPENCLAW_API_KEY=sk-or-v1-abc123xyz...
```

### Step 3: Test It!
```powershell
# Test the integration
python test_kimi_k25.py

# Or start the backend
uvicorn src.api.app:app --reload
```

---

## 🎁 What You Get (100% FREE)

- **Model**: Meta Llama 3.3 70B Instruct
- **Free Tier Limits**:
  - 50 requests per day
  - 20 requests per minute
  - No credit card required!
- **Cost**: $0.00 forever
- **Quality**: Excellent for biomedical Q&A

---

## 🎯 Current Configuration

### ✅ Files Already Updated:

1. **`.env`** - Configured for OpenRouter
   ```bash
   OPENCLAW_API_BASE=https://openrouter.ai/api/v1
   ```

2. **`src/qa_module/openclaw_generator.py`** - Using `meta-llama/llama-3.3-70b-instruct`

3. **`openclaw-hf/Dockerfile`** - Configured for OpenRouter deployment

---

## 🧪 Test Commands

### Test Q&A Endpoint
```powershell
curl -X POST "http://localhost:8000/api/v1/qa" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is diabetes?",
    "source": "pubmed",
    "top_k": 3
  }'
```

### Expected Response
```json
{
  "answer": "Diabetes is a chronic metabolic disorder...",
  "confidence": 0.90,
  "confidence_level": "high",
  "title": "OpenClaw AI Synthesis"
}
```

---

## 🚀 Deploy to Hugging Face

### Add Environment Variable
When deploying to Hugging Face Spaces:

1. Go to your Space Settings
2. Add a new Secret:
   - **Name**: `OPENROUTER_API_KEY`
   - **Value**: Your OpenRouter API key
   - Mark as "Secret" ✅

3. The Dockerfile will automatically use it!

---

## 💡 Why OpenRouter?

| Feature | OpenRouter (FREE) | Groq (FREE) | Direct API |
|---------|-------------------|-------------|------------|
| **Setup** | 2 minutes | 2 minutes | Complex |
| **Free Tier** | 50 req/day | 14,400 req/day | Varies |
| **Models** | 100+ models | 10+ models | 1 model |
| **Switching** | Easy | Need new key | Need new code |
| **Reliability** | High | High | Medium |

---

## 🔧 Troubleshooting

### Issue: "Invalid API key"
**Solution**: 
1. Check your key starts with `sk-or-v1-`
2. Verify you copied the entire key
3. Make sure there are no extra spaces

### Issue: "Rate limit exceeded"
**Solution**: Free tier allows 50 requests/day. Options:
- Wait 24 hours for reset
- Upgrade to paid tier ($0.50 per 1M tokens)
- Use Groq instead (14,400 req/day free)

### Issue: "Model not found"
**Solution**: Ensure model name is exactly:
```python
model="meta-llama/llama-3.3-70b-instruct"
```

---

## 📊 Free Tier Comparison

### OpenRouter Free Tier
- ✅ 50 requests/day
- ✅ 20 requests/minute
- ✅ Access to 100+ models
- ✅ No credit card
- ⚠️ Lower daily limit

### Groq Free Tier (Alternative)
- ✅ 14,400 requests/day
- ✅ 30 requests/minute
- ✅ Ultra-fast inference
- ✅ No credit card
- ⚠️ Fewer model options

**Recommendation**: Start with OpenRouter for flexibility, switch to Groq if you need higher limits!

---

## 🎨 Features of Llama 3.3 70B

- ✅ **Excellent Reasoning**: Strong logical capabilities
- ✅ **Biomedical Knowledge**: Good for medical Q&A
- ✅ **Citation Support**: Properly references sources
- ✅ **128K Context**: Large context window
- ✅ **Open Source**: Meta's latest model
- ✅ **Fast**: 2-5 second responses

---

## 🔄 Switch Between Providers

Want to try different providers? Just update `.env`:

### Use Groq (More free requests)
```bash
OPENCLAW_API_KEY=${GROQ_API_KEY}
OPENCLAW_API_BASE=https://api.groq.com/openai/v1
```
And change model to: `llama-3.3-70b-versatile`

### Use OpenRouter (More models)
```bash
OPENCLAW_API_KEY=sk-or-v1-YOUR_KEY
OPENCLAW_API_BASE=https://openrouter.ai/api/v1
```
And change model to: `meta-llama/llama-3.3-70b-instruct`

---

## 📚 Resources

- **OpenRouter Dashboard**: https://openrouter.ai/dashboard
- **API Keys**: https://openrouter.ai/keys
- **Model List**: https://openrouter.ai/models
- **Documentation**: https://openrouter.ai/docs
- **Pricing**: https://openrouter.ai/pricing

---

## 🎉 You're Almost Ready!

Just 2 steps left:

1. ✅ Get your free OpenRouter API key
2. ✅ Add it to `.env`
3. ✅ Run `python test_kimi_k25.py`

That's it! You'll have a powerful AI agent running for FREE! 🚀

---

**Made with ❤️ using OpenRouter, Llama 3.3 70B, OpenClaw, and BioSense AI**
