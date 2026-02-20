# PostgreSQL Installation Script for BioMed Scholar
# Simplified version - downloads and launches installer

$ErrorActionPreference = "Continue"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PostgreSQL 15 Installer" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if PostgreSQL is already installed
$pgInstalled = Test-Path "C:\Program Files\PostgreSQL\15\bin\psql.exe"
if ($pgInstalled) {
    Write-Host "PostgreSQL 15 is already installed!" -ForegroundColor Green
    Write-Host "Location: C:\Program Files\PostgreSQL\15" -ForegroundColor Gray
    Write-Host ""
    
    # Check if service is running
    $pgService = Get-Service -Name "postgresql-x64-15" -ErrorAction SilentlyContinue
    if ($pgService) {
        if ($pgService.Status -eq "Running") {
            Write-Host "PostgreSQL service is running" -ForegroundColor Green
        }
        else {
            Write-Host "PostgreSQL service is stopped. Starting..." -ForegroundColor Yellow
            Start-Service "postgresql-x64-15"
            Write-Host "PostgreSQL service started" -ForegroundColor Green
        }
    }
    
    Write-Host ""
    Write-Host "Proceeding to database setup..." -ForegroundColor Yellow
    $skipInstall = $true
}
else {
    Write-Host "PostgreSQL 15 not found. Starting download..." -ForegroundColor Yellow
    Write-Host ""
    
    # Download PostgreSQL installer
    $downloadUrl = "https://get.enterprisedb.com/postgresql/postgresql-15.10-1-windows-x64.exe"
    $installerPath = "$env:TEMP\postgresql-15-installer.exe"
    
    Write-Host "Downloading PostgreSQL 15.10 (approximately 200MB)..." -ForegroundColor Yellow
    Write-Host "This may take several minutes..." -ForegroundColor Gray
    Write-Host ""
    
    $ProgressPreference = 'SilentlyContinue'
    Invoke-WebRequest -Uri $downloadUrl -OutFile $installerPath -UseBasicParsing
    $ProgressPreference = 'Continue'
    
    Write-Host "Download complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Running PostgreSQL Installer" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "IMPORTANT: Use these settings during installation:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  Installation Directory: C:\Program Files\PostgreSQL\15" -ForegroundColor White
    Write-Host "  Port: 5433" -ForegroundColor White
    Write-Host "  Password: password" -ForegroundColor White
    Write-Host "  Locale: Default (English, United States)" -ForegroundColor White
    Write-Host ""
    Write-Host "The installer will launch in 5 seconds..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    
    # Run installer
    Start-Process -FilePath $installerPath -Wait
    
    Write-Host ""
    Write-Host "Installation completed!" -ForegroundColor Green
    Write-Host "Please wait while we set up the database..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    $skipInstall = $false
}

# Database setup
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Database Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if psql is available
$psqlPath = "C:\Program Files\PostgreSQL\15\bin\psql.exe"
if (-not (Test-Path $psqlPath)) {
    Write-Host "PostgreSQL not found at expected location" -ForegroundColor Red
    Write-Host "Please ensure PostgreSQL is installed correctly" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "You can manually install from:" -ForegroundColor Yellow
    Write-Host "https://www.postgresql.org/download/windows/" -ForegroundColor Cyan
    exit 1
}

# Add PostgreSQL to PATH for this session
$env:Path += ";C:\Program Files\PostgreSQL\15\bin"

Write-Host "Creating database and user..." -ForegroundColor Yellow
Write-Host ""

# Create SQL commands file
$sqlCommands = @"
CREATE USER "user" WITH PASSWORD 'password';
CREATE DATABASE biomedical_search OWNER "user";
GRANT ALL PRIVILEGES ON DATABASE biomedical_search TO "user";
"@

$sqlFile = "$env:TEMP\setup_db.sql"
$sqlCommands | Out-File -FilePath $sqlFile -Encoding ASCII

Write-Host "Running database setup commands..." -ForegroundColor Yellow
Write-Host "You will be prompted for the PostgreSQL 'postgres' password." -ForegroundColor Yellow
Write-Host "(This is the password you set during installation)" -ForegroundColor Gray
Write-Host ""

# Run psql command
& $psqlPath -U postgres -p 5433 -f $sqlFile

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Database setup completed successfully!" -ForegroundColor Green
}
else {
    Write-Host ""
    Write-Host "Database setup encountered an issue." -ForegroundColor Yellow
    Write-Host "You can manually run these SQL commands:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  psql -U postgres -p 5433" -ForegroundColor White
    Write-Host ""
    Write-Host "Then execute:" -ForegroundColor White
    Write-Host $sqlCommands -ForegroundColor Gray
}

# Clean up
Remove-Item $sqlFile -ErrorAction SilentlyContinue

# Test connection
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Testing Connection" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$testConn = New-Object System.Net.Sockets.TcpClient
try {
    $testConn.Connect("localhost", 5433)
    if ($testConn.Connected) {
        Write-Host "PostgreSQL is running on port 5433" -ForegroundColor Green
        $testConn.Close()
    }
}
catch {
    Write-Host "Cannot connect to PostgreSQL on port 5433" -ForegroundColor Red
    Write-Host "Please check if the service is running" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Installation Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "PostgreSQL Configuration:" -ForegroundColor Yellow
Write-Host "  Host: localhost" -ForegroundColor White
Write-Host "  Port: 5433" -ForegroundColor White
Write-Host "  Database: biomedical_search" -ForegroundColor White
Write-Host "  User: user" -ForegroundColor White
Write-Host "  Password: password" -ForegroundColor White
Write-Host ""
Write-Host "Connection string:" -ForegroundColor Yellow
Write-Host "  postgresql://user:password@localhost:5433/biomedical_search" -ForegroundColor White
Write-Host ""
Write-Host "To test the connection:" -ForegroundColor Yellow
Write-Host "  psql -U user -d biomedical_search -p 5433" -ForegroundColor White
Write-Host ""
Write-Host "All services are now ready!" -ForegroundColor Green
Write-Host "Run: .\start_services.ps1 to start Elasticsearch and Redis" -ForegroundColor White
Write-Host ""
