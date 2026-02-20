# 🆓 FREE AI Agent Setup with Groq

## ✅ You're Already Set Up!

Good news! Your OpenClaw is now configured to use **Groq's FREE tier** with **Llama 4 Maverick** - and you already have a Groq API key in your `.env` file!

---

## 🚀 What You Get (100% FREE)

- **Model**: Llama 4 Maverick (17B MoE)
- **Speed**: ⚡ Blazing fast (up to 800 tokens/second!)
- **Free Tier Limits**:
  - 30 requests per minute
  - 14,400 requests per day
  - 500,000 tokens per day
- **Cost**: $0.00 - Completely FREE forever!
- **No Credit Card**: Required ❌

---

## 🎯 Current Configuration

### ✅ Already Configured Files:

1. **`.env`** - Using your existing Groq API key
   ```bash
   OPENCLAW_API_KEY=${GROQ_API_KEY}
   OPENCLAW_API_BASE=https://api.groq.com/openai/v1
   ```

2. **`src/qa_module/groq_generator.py`** - Using `meta-llama/llama-4-maverick-17b-128e-instruct`

3. **`openclaw-hf/Dockerfile`** - Configured for Groq

---

## 🧪 Test It Now!

### Quick Test
```powershell
python test_kimi_k25.py
```

### Start Backend
```powershell
uvicorn src.api.app:app --reload
```

### Test Q&A Endpoint
```powershell
curl -X POST "http://localhost:8000/api/v1/qa" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the symptoms of diabetes?",
    "source": "pubmed",
    "top_k": 3
  }'
```

---

## 🎨 Features of Llama 3.3 70B

- ✅ **Excellent for Biomedical Q&A**: Strong reasoning capabilities
- ✅ **Fast Responses**: 1-3 seconds (vs 5-15s for paid models)
- ✅ **Good Context Understanding**: 128K token context window
- ✅ **Accurate Citations**: Properly references source material
- ✅ **Open Source**: Meta's latest Llama model

---

## 🚀 Deploy to Hugging Face

### Option 1: Web UI
1. Go to: https://huggingface.co/new-space
2. Create a Docker Space
3. Upload files from `openclaw-hf/` folder
4. Add Space Secret:
   - Name: `GROQ_API_KEY`
   - Value: Your Groq API key
   - Mark as "Secret" ✅

### Option 2: Git
```bash
git clone https://huggingface.co/spaces/YOUR_USERNAME/biosense-groq
cd biosense-groq
cp -r ../openclaw-hf/* .
git add .
git commit -m "Deploy with free Groq API"
git push
```

---

## 💡 Why Groq?

| Feature | Groq (FREE) | Kimi K2.5 (Paid) | GPT-4 (Paid) |
|---------|-------------|------------------|--------------|
| **Cost** | $0.00 | ~$0.01/query | ~$0.05/query |
| **Speed** | ⚡⚡⚡ Ultra-fast | Medium | Slow |
| **Quality** | Excellent | Excellent | Excellent |
| **Free Tier** | 14,400 req/day | None | Limited |
| **Setup** | ✅ Done! | Need API key | Need API key |

---

## 🔧 Troubleshooting

### Issue: "API key not found"
**Solution**: Your Groq API key is already in `.env` as `GROQ_API_KEY`. No action needed!

### Issue: Rate limit exceeded
**Solution**: Groq's free tier allows:
- 30 requests/minute
- 14,400 requests/day
If you hit the limit, wait a minute or upgrade to Groq's paid tier for higher limits.

### Issue: Slow responses
**Solution**: Groq is actually the FASTEST option! If it's slow:
1. Check your internet connection
2. Verify Groq API status: https://status.groq.com

---

## 📊 Comparison: Before vs After

### Before (Kimi K2.5)
- ❌ Requires OpenRouter account
- ❌ Requires credit card
- ❌ Costs $0.001-$0.05 per query
- ⏱️ 5-15 second responses

### After (Groq + Llama 3.3 70B)
- ✅ FREE forever
- ✅ No credit card needed
- ✅ Already configured!
- ⚡ 1-3 second responses
- ✅ 14,400 free requests/day

---

## 🎉 You're Ready!

Your setup is complete and ready to use! Just run:

```powershell
# Test it
python test_kimi_k25.py

# Or start the backend
uvicorn src.api.app:app --reload
```

---

## 📚 Additional Resources

- **Groq Console**: https://console.groq.com
- **Groq Docs**: https://console.groq.com/docs
- **Llama 3.3 Info**: https://www.llama.com
- **Rate Limits**: https://console.groq.com/docs/rate-limits

---

## 🆙 Want More?

If you need higher limits, Groq offers affordable paid tiers:
- **Pay-as-you-go**: $0.05 per 1M input tokens
- **No monthly fees**: Only pay for what you use
- **Higher rate limits**: Up to 6,000 req/min

But for most users, the **FREE tier is more than enough**! 🎉

---

**Made with ❤️ using Groq, Llama 3.3 70B, OpenClaw, and BioSense AI**
