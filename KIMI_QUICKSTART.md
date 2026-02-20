# 🚀 Kimi K2.5 Quick Start

## 1️⃣ Get Your API Key
Visit: **https://openrouter.ai/keys**
- Sign up / Log in
- Create new API key
- Add $10 credits (recommended for testing)

## 2️⃣ Configure Environment
Edit `.env`:
```bash
OPENCLAW_API_KEY=sk-or-v1-YOUR_ACTUAL_KEY_HERE
OPENCLAW_API_BASE=https://openrouter.ai/api/v1
```

## 3️⃣ Test Integration
```powershell
python test_kimi_k25.py
```

## 4️⃣ Start Backend
```powershell
uvicorn src.api.app:app --reload
```

## 5️⃣ Test Q&A
```powershell
curl -X POST "http://localhost:8000/api/v1/qa" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is COVID-19?", "source": "pubmed", "top_k": 3}'
```

## 📚 Full Documentation
- **Setup Guide**: `KIMI_K2.5_SETUP.md`
- **Changes Log**: `KIMI_K2.5_CHANGES.md`

## 🆘 Troubleshooting
- API key not working? Check it starts with `sk-or-v1-`
- Slow responses? Normal for deep reasoning (5-15s)
- 401 error? Verify credits in OpenRouter account

---
**Model**: `moonshot/kimi-k2.5` | **Cost**: ~$0.001-0.05 per query
