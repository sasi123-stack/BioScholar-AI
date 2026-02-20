# Quick deployment script for Google Cloud Run (Windows PowerShell)
# This script automates the deployment process

$ErrorActionPreference = "Stop"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "🚀 Google Cloud Run Deployment Script" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# Configuration
$PROJECT_ID = "biomed-scholar"
$SERVICE_NAME = "biomed-scholar-api"
$REGION = "us-central1"
$MEMORY = "2Gi"
$CPU = "2"
$MAX_INSTANCES = "10"
$TIMEOUT = "300"

# Check if gcloud is installed
try {
    $null = gcloud --version
}
catch {
    Write-Host "❌ Error: gcloud CLI is not installed" -ForegroundColor Red
    Write-Host "Please install it from: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "📋 Deployment Configuration:" -ForegroundColor Yellow
Write-Host "  Project ID: $PROJECT_ID" -ForegroundColor White
Write-Host "  Service Name: $SERVICE_NAME" -ForegroundColor White
Write-Host "  Region: $REGION" -ForegroundColor White
Write-Host "  Memory: $MEMORY" -ForegroundColor White
Write-Host "  CPU: $CPU" -ForegroundColor White
Write-Host ""

# Prompt for confirmation
# $response = Read-Host "Continue with deployment? (y/n)"
# if ($response -ne "y" -and $response -ne "Y") {
#     Write-Host "Deployment cancelled." -ForegroundColor Yellow
#     exit 0
# }

Write-Host ""
Write-Host "🔐 Step 1: Skipping auth (already logged in)..." -ForegroundColor Cyan
# gcloud auth login

Write-Host ""
Write-Host "📦 Step 2: Setting project..." -ForegroundColor Cyan
gcloud config set project $PROJECT_ID --quiet

Write-Host ""
Write-Host "🔧 Step 3: Enabling required APIs..." -ForegroundColor Cyan
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

Write-Host ""
Write-Host "🏗️  Step 4: Building and deploying to Cloud Run..." -ForegroundColor Cyan
gcloud run deploy $SERVICE_NAME `
    --source . `
    --platform managed `
    --region $REGION `
    --allow-unauthenticated `
    --memory $MEMORY `
    --cpu $CPU `
    --timeout $TIMEOUT `
    --max-instances $MAX_INSTANCES `
    --quiet

Write-Host ""
Write-Host "✅ Deployment complete!" -ForegroundColor Green
Write-Host ""

# Get the service URL
$SERVICE_URL = gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)'

Write-Host "=========================================" -ForegroundColor Green
Write-Host "🎉 Your API is now live!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host "URL: $SERVICE_URL" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Set environment variables:" -ForegroundColor White
Write-Host "   gcloud run services update $SERVICE_NAME --update-env-vars KEY=VALUE" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Update your frontend to use this URL" -ForegroundColor White
Write-Host ""
Write-Host "3. View logs:" -ForegroundColor White
Write-Host "   gcloud run services logs read $SERVICE_NAME --region $REGION" -ForegroundColor Gray
Write-Host "=========================================" -ForegroundColor Green
