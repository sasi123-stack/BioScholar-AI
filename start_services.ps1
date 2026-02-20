# Quick Start Script - Starts Elasticsearch and Redis (No PostgreSQL needed for basic testing)
# Run this after installation completes

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting BioMed Scholar Services" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Elasticsearch is installed
if (Test-Path "C:\Services\elasticsearch\bin\elasticsearch.bat") {
    Write-Host "[1/2] Starting Elasticsearch..." -ForegroundColor Yellow
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd C:\Services\elasticsearch\bin; .\elasticsearch.bat" -WindowStyle Normal
    Write-Host "✓ Elasticsearch starting in new window" -ForegroundColor Green
}
else {
    Write-Host "✗ Elasticsearch not found at C:\Services\elasticsearch" -ForegroundColor Red
    Write-Host "  Run: .\install_services.ps1 first" -ForegroundColor Yellow
}

Start-Sleep -Seconds 2

# Check if Redis is installed
if (Test-Path "C:\Services\redis\redis-server.exe") {
    Write-Host "`n[2/2] Starting Redis..." -ForegroundColor Yellow
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd C:\Services\redis; .\redis-server.exe redis.windows.conf" -WindowStyle Normal
    Write-Host "✓ Redis starting in new window" -ForegroundColor Green
}
else {
    Write-Host "`n✗ Redis not found at C:\Services\redis" -ForegroundColor Red
    Write-Host "  Run: .\install_services.ps1 first" -ForegroundColor Yellow
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Services Started!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Elasticsearch: http://localhost:9201" -ForegroundColor White
Write-Host "Redis: localhost:6380" -ForegroundColor White
Write-Host "`nWait 30 seconds for Elasticsearch to fully start" -ForegroundColor Yellow
Write-Host "Then run: .\check_services.ps1 to verify" -ForegroundColor Yellow
Write-Host "`nPress Ctrl+C in each service window to stop" -ForegroundColor White
