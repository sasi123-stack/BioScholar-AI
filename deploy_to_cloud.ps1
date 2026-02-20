# Cloud Deployment Script
Write-Host "Starting Cloud Deployment Process..." -ForegroundColor Cyan

# 1. Login to Railway (This will open your browser)
Write-Host "`n[1/3] Logging into Railway..." -ForegroundColor Yellow
npx railway login

# 2. Initialize Project
Write-Host "`n[2/3] Initializing Railway Project..." -ForegroundColor Yellow
npx railway init

# 3. Deploy
Write-Host "`n[3/3] Deploying to Cloud..." -ForegroundColor Yellow
npx railway up

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "Cloud Deployment Initiated!" -ForegroundColor Green
Write-Host "Once finished, your site will be live at the URL provided by Railway." -ForegroundColor White
Write-Host "========================================" -ForegroundColor Green
