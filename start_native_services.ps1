# Start Native Elasticsearch, Redis, and PostgreSQL
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Native Services" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Start Elasticsearch
Write-Host "[1/3] Starting Elasticsearch..." -ForegroundColor Yellow
if (Test-Path "C:\Services\elasticsearch\bin\elasticsearch.bat") {
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd C:\Services\elasticsearch\bin; .\elasticsearch.bat" -WindowStyle Normal
    Write-Host "✓ Elasticsearch starting in new window" -ForegroundColor Green
}
else {
    Write-Host "✗ Elasticsearch not found at C:\Services\elasticsearch" -ForegroundColor Red
}

Start-Sleep -Seconds 2

# 2. Start Redis
Write-Host "`n[2/3] Starting Redis..." -ForegroundColor Yellow
if (Test-Path "C:\Services\redis\redis-server.exe") {
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd C:\Services\redis; .\redis-server.exe redis.windows.conf" -WindowStyle Normal
    Write-Host "✓ Redis starting in new window" -ForegroundColor Green
}
else {
    Write-Host "✗ Redis not found at C:\Services\redis" -ForegroundColor Red
}

Start-Sleep -Seconds 2

# 3. Start PostgreSQL
Write-Host "`n[3/3] Starting PostgreSQL..." -ForegroundColor Yellow
$started = $false
$serviceNames = @("postgresql-x64-18", "postgresql-x64-17", "postgresql-x64-16", "postgresql-x64-15", "postgresql-x64-14", "postgresql")

foreach ($name in $serviceNames) {
    try {
        $service = Get-Service -Name $name -ErrorAction Stop
        if ($service.Status -eq "Running") {
            Write-Host "POSTGRESQL ($name) IS ALREADY RUNNING" -ForegroundColor Green
            $started = $true
            break
        }
        else {
            Start-Service $name -ErrorAction Stop
            Write-Host "POSTGRESQL ($name) STARTED" -ForegroundColor Green
            $started = $true
            break
        }
    }
    catch {
        # Continue to next service name
        continue
    }
}

if (-not $started) {
    Write-Host "X PostgreSQL service not found" -ForegroundColor Red
    Write-Host "  Please ensure PostgreSQL is installed as a Windows service" -ForegroundColor Yellow

}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Services Started!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Elasticsearch: http://localhost:9201" -ForegroundColor White
Write-Host "Redis: localhost:6380" -ForegroundColor White
Write-Host "PostgreSQL: localhost:5432" -ForegroundColor White
Write-Host "`nWait 30 seconds for Elasticsearch to fully start" -ForegroundColor Yellow
Write-Host "Press Ctrl+C in each service window to stop" -ForegroundColor White
