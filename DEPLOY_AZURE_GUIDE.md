# ☁️ Deploying Backend to Azure Web Apps

Azure is an excellent, professional choice for hosting your backend.
**Recommended Service**: **Azure App Service (Web Apps)**. 
**Plan**: **B1 (Basic)** is the cheapest valid option (~$13/mo) because Free (F1) has strict CPU quotas that AI models will hit immediately.

---

## ✅ Prerequisites

1.  **Azure Account**: You need an active subscription.
2.  **Azure CLI**: Installed on your machine.
    *   PowerShell: `winget install -e --id Microsoft.AzureCLI`

---

## 🚀 Step 1: Create External Databases (Same as before)

Azure Web Apps are stateless containers. You STILL need external databases.
(If you already made these for Hugging Face, **reuse them!**).

1.  **Elasticsearch**: Bonsai.io (Free Sandbox)
2.  **Redis**: Upstash (Free)
3.  **PostgreSQL**: Neon (Free) or Azure Database for PostgreSQL (Paid).

---

## 🛠️ Step 2: Prepare the Code

1.  **Login to Azure**:
    ```powershell
    az login
    ```

2.  **Create a Resource Group**:
    ```powershell
    az group create --name BiomedResourceGroup --location eastus
    ```

3.  **Create an App Service Plan (The Server)**:
    *   We use the **B1** sku (Basic) for 1.75GB RAM.
    *   *Note: AI Models might still be tight on 1.75GB. Consider P1v2 (3.5GB) for production.*
    ```powershell
    az appservice plan create --name BiomedPlan --resource-group BiomedResourceGroup --sku B1 --is-linux
    ```

4.  **Create the Web App**:
    ```powershell
    az webapp create --resource-group BiomedResourceGroup --plan BiomedPlan --name biomed-scholar-api-YOURNAME --runtime "PYTHON:3.9"
    ```

---

## 🔐 Step 3: Configure Environment Variables

You need to set your secrets in Azure.

```powershell
az webapp config appsettings set --name biomed-scholar-api-YOURNAME --resource-group BiomedResourceGroup --settings "SCM_DO_BUILD_DURING_DEPLOYMENT=true" "ELASTICSEARCH_HOST=..." "ELASTICSEARCH_PORT=443" "ELASTICSEARCH_SCHEME=https" "ELASTICSEARCH_USERNAME=..." "ELASTICSEARCH_PASSWORD=..." "REDIS_HOST=..." "REDIS_PORT=6379" "REDIS_PASSWORD=..." "DATABASE_URL=..." "GROQ_API_KEY=..." "APP_ENV=production" "LOW_MEMORY_MODE=false"
```
*(Replace `...` with your actual values from Step 1)*

---

## 🚢 Step 4: Deploy

We will use "Local Git" deployment (easiest for this setup).

1.  **Configure Deployment User** (If you haven't before):
    ```powershell
    az webapp deployment user set --user-name uniqueUser123 --password StrongPassword123!
    ```

2.  **Get Git URL**:
    ```powershell
    $gitUrl = az webapp deployment source config-local-git --name biomed-scholar-api-YOURNAME --resource-group BiomedResourceGroup --query url --output tsv
    Write-Host "Git URL: $gitUrl"
    ```

3.  **Push Code**:
    ```powershell
    git remote add azure $gitUrl
    git push azure master:master
    ```

---

## 🌐 Step 5: Update Frontend

1.  Your new API URL is: `https://biomed-scholar-api-YOURNAME.azurewebsites.net`
2.  Update `frontend/app.js` with this URL.
3.  Deploy frontend to Firebase/Vercel.

---

## ⚠️ Troubleshooting

1.  **"Application Error"**:
    *   Go to Azure Portal -> Your App -> Log Stream.
    *   It's likely a missing variable or "Out of Memory" (OOM).
2.  **OOM Errors**:
    *   If the app crashes on startup, the B1 plan (1.75GB RAM) might be too small for BioBERT + ClinicalBERT.
    *   **Fix**: Set `LOW_MEMORY_MODE=true` in App Settings OR upgrade plan to P1v2.
