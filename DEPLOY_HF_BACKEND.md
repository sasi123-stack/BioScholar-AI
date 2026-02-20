# 🌍 The Ultimate Guide to Deploying Backend on Hugging Face Spaces

This guide will walk you through deploying your `biomed-scholar-api` to **Hugging Face Spaces**. 
Spaces offers a generous **16GB RAM Free Tier**, which is perfect for running our AI models (BioBERT, ClinicalBERT) that would crash on other free platforms.

---

## ✅ Prerequisites

Before we start, you will need to create accounts on three external services. This is because Hugging Face Spaces (like Heroku or Render) is "ephemeral" - it resets every time you deploy, so it cannot store your database files permanently.

### 1. Elasticsearch (The Search Engine)
We will use **Bonsai.io** for a free managed Elasticsearch cluster.
1.  Go to [Bonsai.io](https://bonsai.io/signup) and sign up.
2.  Create a new Cluster (Select "US East" or similar).
3.  Name it `biomed-search`.
4.  Once created, go to the **"Access"** tab or dashboard.
5.  **Build your Credentials**:
    *   Find your **Full URL**: It typically looks like `https://username:password@redwood-12345.us-east-1.bonsai.io`.
    *   **Action**: Copy this URL. We will need to split it into parts later.

### 2. Redis (The Cache & Queue)
We will use **Upstash** for a serverless Redis instance.
1.  Go to [Upstash Console](https://console.upstash.com/login).
2.  Create a Database -> Name: `biomed-cache` -> Region: `US-East-1`.
3.  Scroll down to "Connect" section.
4.  **Copy these values**:
    *   `Endpoint` (e.g., `us1-running-cat-32145.upstash.io`) - This is your **REDIS_HOST**.
    *   `Port` (e.g., `6379`) - This is your **REDIS_PORT**.
    *   `Password` (e.g., `87234...`) - This is your **REDIS_PASSWORD**.

### 3. PostgreSQL (The Main Database)
We will use **Neon** for a serverless Postgres database.
1.  Go to [Neon.tech](https://neon.tech/).
2.  Sign up and create a Project -> Name: `biomed-db`.
3.  It will show you a "Connection String".
4.  **Copy the Postgres URL**: It looks like `postgresql://user:pass@ep-shiny-...aws.neon.tech/neondb?sslmode=require`.

---

## 🛰️ Step 4: Create Your Space

1.  Log in to [Hugging Face](https://huggingface.co/).
2.  Click on your profile picture -> **New Space**.
3.  **Owner**: Your username.
4.  **Space Name**: `biomed-scholar-api` (This will determine your URL).
5.  **License**: `MIT`.
6.  **SDK**: Select **Docker** (Crucial!).
7.  **Hardware**: Select **Free (2 vCPU, 16GB RAM)**.
8.  Click **Create Space**.

---

## 🔐 Step 5: Configure Environment Secrets

Your Space is public, but your passwords must be secret.
1.  In your new Space, click on the **Settings** tab.
2.  Scroll down to the **Variables and secrets** section.
3.  Click **New Secret** for each of the following (Case Sensitive!):

| Secret Name | How to Fill |
|-------------|-------------|
| `ELASTICSEARCH_HOST` | The domain part of your Bonsai URL (e.g., `redwood-12345.us-east-1.bonsai.io`) |
| `ELASTICSEARCH_PORT` | `443` |
| `ELASTICSEARCH_SCHEME`| `https` |
| `ELASTICSEARCH_USERNAME`| The username part from your Bonsai URL (before the `:`) |
| `ELASTICSEARCH_PASSWORD`| The password part from your Bonsai URL (after the `:`) |
| `REDIS_HOST` | Your Upstash Endpoint (e.g., `us1-running-cat...upstash.io`) |
| `REDIS_PORT` | `6379` |
| `REDIS_PASSWORD` | Your Upstash Password |
| `DATABASE_URL` | Your full Neon connection string |
| `GROQ_API_KEY` | Your Groq API Key |
| `GEMINI_API_KEY` | Your Gemini API Key |
| `APP_ENV` | `production` |
| `LOW_MEMORY_MODE` | `false` (IMPORTANT: Set to false to enable AI models) |
| `Secret Key` | Generate a random string (e.g. `sup3rs3cr3t`) |

---

## 🚀 Step 6: Power Up & Deploy!

We have prepared a script to automate the pushing of code.

1.  Open your local terminal in the project root.
2.  Run the deployment script:
    ```powershell
    .\scripts\deploy_to_hf_spaces.ps1
    ```
3.  The script will ask for your **Space URL**. Paste it (e.g., `https://huggingface.co/spaces/yourname/biomed-scholar-api`).
4.  It will push your code. You might be asked to log in to Hugging Face Config if you haven't already.

**The Build Process:**
*   Go to your Space's **App** tab.
*   You will see a "Building" status.
*   **Wait**: It usually takes 5-10 minutes to build the Docker image and download the large AI models.
*   **Watch Logs**: You can click "Logs" to see the build progress.

---

## 🌐 Step 7: Update Frontend

Once your Space shows "Running", you will have a public API URL.
It will look like: `https://yourname-biomed-scholar-api.hf.space`

1.  Test it: Go to `https://yourname-biomed-scholar-api.hf.space/docs`. You should see the Swagger UI.
2.  Update your `frontend/app.js`:
    ```javascript
    // Update this line
    const RENDER_BACKEND_URL = 'https://yourname-biomed-scholar-api.hf.space/api/v1';
    ```
3.  Redeploy your frontend (Firebase/Vercel).

---

## ⚠️ Checklist for Success

*   [ ] Did you create the `.dockerignore` file? (We did this for you)
*   [ ] Is `LOW_MEMORY_MODE` set to `false` in Secrets? (Needed for Reranking)
*   [ ] Is your Space Hardware set to 16GB? (Default is usually correct)

## 🐛 Troubleshooting

*   **"Space Build Failed"**: Check the logs. Usually it's a missing dependency in `requirements.txt`.
*   **"500 Internal Server Error"**: Check your Database/Redis credentials in the Secrets.
*   **"Search returns 0 results"**: Remember, your Cloud Elasticsearch is **EMPTY**. You need to run the ingestion script from your local machine, pointing it to the Cloud credentials, to upload data.

