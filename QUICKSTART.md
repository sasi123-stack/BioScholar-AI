# Quick Start Guide

## 🚀 Get Started in 3 Minutes

### Prerequisites
- Python 3.9+ installed
- Docker Desktop running
- Conda installed

### Step 1: Start Docker Services (30 seconds)

```bash
cd C:\Users\sriva\Documents\kash_proj
docker-compose -f docker/docker-compose.yml up -d
```

Wait for services to be healthy:
- ✅ Elasticsearch on port 9201
- ✅ Redis on port 6380
- ✅ PostgreSQL on port 5433

### Step 2: Start API Server (2 minutes)

```bash
# Activate environment
conda activate biomedical-search

# Start API
cd C:\Users\sriva\Documents\kash_proj
python -m uvicorn src.api.app:app --host 0.0.0.0 --port 8000
```

Wait for models to load (~15 seconds):
- ✅ BioBERT loaded
- ✅ ClinicalBERT loaded
- ✅ BioBERT QA loaded
- ✅ Cross-encoder loaded

### Step 3: Start Web Interface (10 seconds)

```bash
# In a NEW terminal
cd C:\Users\sriva\Documents\kash_proj\frontend
python -m http.server 8080
```

### Step 4: Open Your Browser

Navigate to: **http://localhost:8080**

## 🎯 Try It Out

### Search Example
1. Click "Search Documents" tab
2. Type: `COVID-19 treatment`
3. Click "Search"
4. See results with relevance scores

### Question Answering Example
1. Click "Ask Questions" tab
2. Type: `What is the treatment for diabetes?`
3. Click "Get Answer"
4. See AI-generated answer with confidence score

## 🔧 Troubleshooting

**API won't start?**
```bash
# Check if port 8000 is in use
netstat -an | findstr 8000

# Kill process if needed
taskkill /F /PID <process_id>
```

**Frontend shows "Offline"?**
- Ensure API server is running
- Check http://localhost:8000/api/v1/health
- Look for CORS errors in browser console

**Docker services not starting?**
```bash
# Check Docker is running
docker ps

# Restart Docker Desktop if needed
# Then restart services
docker-compose -f docker/docker-compose.yml restart
```

**Models taking too long?**
- First load takes 15-20 seconds
- Subsequent requests are faster
- Models are cached in `models/` directory

## 📚 Next Steps

- Read [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) for complete overview
- Check [frontend/README.md](frontend/README.md) for UI details
- Explore API at http://localhost:8000/docs
- Run tests with `python scripts/test_api.py`

## 🛑 Stopping Services

```bash
# Stop API server: Press Ctrl+C in terminal

# Stop frontend server: Press Ctrl+C in terminal

# Stop Docker services
cd C:\Users\sriva\Documents\kash_proj
docker-compose -f docker/docker-compose.yml down
```

## 💡 Tips

- Use Chrome/Edge for best experience
- First search may be slow (model warmup)
- Try both search modes (Search vs QA)
- Adjust search balance slider for different results
- Enable/disable reranking to see difference

Enjoy your biomedical search engine! 🎉
