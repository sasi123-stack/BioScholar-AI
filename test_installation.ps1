# Simple Service Starter - Runs services in current terminal for debugging
# This makes it easier to see if there are any startup errors

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "BioMed Scholar - Simple Service Test" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Test Elasticsearch
Write-Host "[1/2] Testing Elasticsearch..." -ForegroundColor Yellow
if (Test-Path "C:\Services\elasticsearch\bin\elasticsearch.bat") {
    Write-Host "✓ Elasticsearch found" -ForegroundColor Green
    Write-Host "  Location: C:\Services\elasticsearch" -ForegroundColor Gray
    Write-Host "  To start: cd C:\Services\elasticsearch\bin; .\elasticsearch.bat" -ForegroundColor Gray
}
else {
    Write-Host "✗ Elasticsearch NOT found" -ForegroundColor Red
    Write-Host "  Expected: C:\Services\elasticsearch\bin\elasticsearch.bat" -ForegroundColor Gray
}

Write-Host ""

# Test Redis  
Write-Host "[2/2] Testing Redis..." -ForegroundColor Yellow
if (Test-Path "C:\Services\redis\redis-server.exe") {
    Write-Host "✓ Redis found" -ForegroundColor Green
    Write-Host "  Location: C:\Services\redis" -ForegroundColor Gray
    Write-Host "  To start: cd C:\Services\redis; .\redis-server.exe redis.windows.conf" -ForegroundColor Gray
}
else {
    Write-Host "✗ Redis NOT found" -ForegroundColor Red
    Write-Host "  Expected: C:\Services\redis\redis-server.exe" -ForegroundColor Gray
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Manual Start Instructions" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Open 2 separate PowerShell windows and run:" -ForegroundColor Yellow
Write-Host ""
Write-Host "Window 1 - Elasticsearch:" -ForegroundColor Cyan
Write-Host "  cd C:\Services\elasticsearch\bin" -ForegroundColor White
Write-Host "  .\elasticsearch.bat" -ForegroundColor White
Write-Host ""
Write-Host "Window 2 - Redis:" -ForegroundColor Cyan
Write-Host "  cd C:\Services\redis" -ForegroundColor White
Write-Host "  .\redis-server.exe redis.windows.conf" -ForegroundColor White
Write-Host ""
Write-Host "Wait 30-60 seconds, then test with:" -ForegroundColor Yellow
Write-Host "  curl http://localhost:9201" -ForegroundColor White
Write-Host ""
