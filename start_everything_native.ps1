# Start All Services for BioMed Scholar (Native)
Write-Host "Starting BioMed Scholar Native Services..." -ForegroundColor Green

$rootDir = (Get-Location).Path

# 1. Start Elasticsearch
Write-Host "`n[1/5] Starting Elasticsearch..." -ForegroundColor Yellow
if (Test-Path "C:\Services\elasticsearch\bin\elasticsearch.bat") {
    Start-Process powershell -ArgumentList "-NoExit -Command `"cd C:\Services\elasticsearch\bin; .\elasticsearch.bat`"" -WindowStyle Normal
    Write-Host "  [OK] Elasticsearch starting in new window" -ForegroundColor Green
}
else {
    Write-Host "  [FAIL] Elasticsearch not found at C:\Services\elasticsearch" -ForegroundColor Red
}

# 2. Start Redis
Write-Host "`n[2/5] Starting Redis..." -ForegroundColor Yellow
if (Test-Path "C:\Services\redis\redis-server.exe") {
    Start-Process powershell -ArgumentList "-NoExit -Command `"cd C:\Services\redis; .\redis-server.exe redis.windows.conf`"" -WindowStyle Normal
    Write-Host "  [OK] Redis starting in new window" -ForegroundColor Green
}
else {
    Write-Host "  [FAIL] Redis not found at C:\Services\redis" -ForegroundColor Red
}

# 3. Start PostgreSQL
Write-Host "`n[3/5] Starting PostgreSQL..." -ForegroundColor Yellow
# Try to start it as a service first (various possible names)
$pgStarted = $false
foreach ($name in @("postgresql-x64-18", "postgresql-x64-17", "postgresql-x64-16", "postgresql-x64-15", "postgresql-x64-14")) {
    $service = Get-Service -Name $name -ErrorAction SilentlyContinue
    if ($service) {
        if ($service.Status -eq 'Running') {
            Write-Host "  [OK] PostgreSQL ($name) is already running" -ForegroundColor Green
        }
        else {
            Start-Service $name -ErrorAction SilentlyContinue
            Write-Host "  [OK] PostgreSQL ($name) started" -ForegroundColor Green
        }
        $pgStarted = $true
        break
    }
}

if (-not $pgStarted) {
    # Check both ports 5433 (default for this install) and 5432
    $pgPort = 0
    foreach ($port in @(5433, 5432)) {
        try {
            $tcp = New-Object System.Net.Sockets.TcpClient
            $tcp.Connect("localhost", $port)
            $tcp.Close()
            $pgPort = $port
            break
        }
        catch { }
    }

    if ($pgPort -gt 0) {
        Write-Host "  [OK] PostgreSQL is already running on port $pgPort" -ForegroundColor Green
    }
    else {
        $pgCtl = "C:\Program Files\PostgreSQL\18\bin\pg_ctl.exe"
        $pgDataDir = "C:\Program Files\PostgreSQL\18\data"
        if (Test-Path $pgCtl) {
            Write-Host "  Starting PostgreSQL with elevated permissions (UAC prompt may appear)..." -ForegroundColor Cyan
            try {
                Start-Process -FilePath $pgCtl -ArgumentList "start -D `"$pgDataDir`"" -Verb RunAs -WindowStyle Hidden -Wait
            }
            catch {
                Write-Host "  [WARN] UAC prompt was declined or elevation failed" -ForegroundColor Yellow
            }
            Start-Sleep -Seconds 3
            # Verify it started on either port
            $verified = $false
            foreach ($port in @(5433, 5432)) {
                try {
                    $tcp = New-Object System.Net.Sockets.TcpClient
                    $tcp.Connect("localhost", $port)
                    $tcp.Close()
                    Write-Host "  [OK] PostgreSQL started successfully (port $port)" -ForegroundColor Green
                    $verified = $true
                    break
                }
                catch { }
            }
            if (-not $verified) {
                Write-Host "  [WARN] PostgreSQL may still be starting. Check ports 5432/5433." -ForegroundColor Yellow
            }
        }
        else {
            Write-Host "  [FAIL] PostgreSQL not found at C:\Program Files\PostgreSQL\18" -ForegroundColor Red
        }
    }
}

# Wait a moment for infrastructure services to initialize
Write-Host "`nWaiting 5 seconds for infrastructure services to initialize..." -ForegroundColor Cyan
Start-Sleep -Seconds 5

# 4. Start Backend
Write-Host "`n[4/5] Starting Backend API..." -ForegroundColor Yellow
$activateScript = Join-Path $rootDir ".venv\Scripts\activate"
if (Test-Path $activateScript) {
    Start-Process powershell -ArgumentList "-NoExit -Command `"cd '$rootDir'; .\.venv\Scripts\activate; uvicorn src.api.app:app --host 0.0.0.0 --port 8000 --reload`"" -WindowStyle Normal
    Write-Host "  [OK] Backend API starting in new window" -ForegroundColor Green
}
else {
    Write-Host "  [FAIL] Virtual environment not found at $activateScript" -ForegroundColor Red
}

# 5. Start Ngrok
Write-Host "`n[5/5] Starting Ngrok..." -ForegroundColor Yellow
$ngrokConfig = Join-Path $rootDir "ngrok_config.yml"
if (Test-Path $ngrokConfig) {
    Start-Process powershell -ArgumentList "-NoExit -Command `"cd '$rootDir'; ngrok start api --config '$ngrokConfig'`"" -WindowStyle Normal
    Write-Host "  [OK] Ngrok starting in new window" -ForegroundColor Green
}
else {
    Write-Host "  [FAIL] Ngrok config not found at $ngrokConfig" -ForegroundColor Red
}

Write-Host "`n==========================================" -ForegroundColor Green
Write-Host "  All services are starting up!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host "  Elasticsearch : http://localhost:9201"
Write-Host "  Redis         : localhost:6379"
Write-Host "  PostgreSQL    : localhost:5433"
Write-Host "  Backend API   : http://localhost:8000"
Write-Host "  Ngrok         : Check the ngrok window for public URL"
Write-Host "`nUse '.\check_services.ps1' to verify status later."
