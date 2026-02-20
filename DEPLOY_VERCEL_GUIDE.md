# Deploying to Vercel

Vercel is great for the **frontend**, but it has strict limits for the backend (Serverless Functions):
1.  **Function Size Limit**: 250MB (This is very small for Python + AI libraries).
2.  **Execution Time**: 10 seconds (default) to 60 seconds (Pro).
3.  **Memory**: 1024MB.

**CRITICAL WARNING:** You CANNOT run BioBERT/ClinicalBERT or local Cross-Encoders on Vercel. They are too large.
You MUST set `LOW_MEMORY_MODE=true` to use only external APIs (Groq/Gemini).

## 🚀 Steps to Deploy

### 1. Install CLI
```bash
npm install -g vercel
```

### 2. Configure Project
We have already created:
*   `vercel.json`: Configured for mixed Python/Frontend app.
*   `requirements-vercel.txt`: A lightweight dependency list.

### 3. Deploy
Run the following command in your terminal:
```bash
vercel
```
*   Set up and deploy? **Yes**
*   Scope: **Your Name**
*   Link to existing project? **No**
*   Project Name: `biomed-scholar-full`
*   Directory: `./` (Default)

### 4. Environment Variables
After deployment fails (it likely will, due to missing secrets), go to your Vercel Project Dashboard -> Settings -> Environment Variables.
Add:
*   `ELASTICSEARCH_HOST`, `PORT`, `USER`, `PASSWORD`
*   `REDIS_HOST`, `PORT`, `PASSWORD`
*   `DATABASE_URL`
*   `GROQ_API_KEY`
*   `LOW_MEMORY_MODE` = `true`

### 5. Redeploy
```bash
vercel --prod
```
