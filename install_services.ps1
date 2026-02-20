# Automated Installation Script for BioMed Scholar Services
# This script downloads and installs Elasticsearch, Redis, and PostgreSQL

param(
    [switch]$SkipElasticsearch,
    [switch]$SkipRedis,
    [switch]$SkipPostgres
)

$ErrorActionPreference = "Stop"
$ServicesDir = "C:\Services"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "BioMed Scholar Services Installer" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "WARNING: Not running as Administrator. Some operations may fail." -ForegroundColor Yellow
    Write-Host "Consider running: Start-Process powershell -Verb RunAs -ArgumentList '-File $PSCommandPath'" -ForegroundColor Yellow
    Write-Host ""
}

# Create Services directory
if (-not (Test-Path $ServicesDir)) {
    Write-Host "Creating services directory: $ServicesDir" -ForegroundColor Green
    New-Item -ItemType Directory -Path $ServicesDir -Force | Out-Null
}

# Function to download file with progress
function Download-File {
    param(
        [string]$Url,
        [string]$OutputPath
    )
    
    Write-Host "Downloading from: $Url" -ForegroundColor Yellow
    Write-Host "Saving to: $OutputPath" -ForegroundColor Yellow
    
    try {
        $ProgressPreference = 'SilentlyContinue'
        Invoke-WebRequest -Uri $Url -OutFile $OutputPath -UseBasicParsing
        $ProgressPreference = 'Continue'
        Write-Host "Download complete!" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "Download failed: $_" -ForegroundColor Red
        return $false
    }
}

# ============================================
# ELASTICSEARCH INSTALLATION
# ============================================
if (-not $SkipElasticsearch) {
    Write-Host "`n[1/3] Installing Elasticsearch 8.11.0..." -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    
    $esDir = "$ServicesDir\elasticsearch"
    
    if (Test-Path $esDir) {
        Write-Host "Elasticsearch directory already exists. Skipping..." -ForegroundColor Yellow
    }
    else {
        $esZip = "$ServicesDir\elasticsearch-8.11.0.zip"
        $esUrl = "https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-8.11.0-windows-x86_64.zip"
        
        if (Download-File -Url $esUrl -OutputPath $esZip) {
            Write-Host "Extracting Elasticsearch..." -ForegroundColor Yellow
            Expand-Archive -Path $esZip -DestinationPath $ServicesDir -Force
            Rename-Item "$ServicesDir\elasticsearch-8.11.0" $esDir
            Remove-Item $esZip
            
            # Create elasticsearch.yml configuration
            $esConfig = @"
# Network settings
network.host: 0.0.0.0
http.port: 9201
transport.port: 9301

# Discovery settings
discovery.type: single-node

# Security settings (disabled for local development)
xpack.security.enabled: false
xpack.security.enrollment.enabled: false
xpack.security.http.ssl.enabled: false
xpack.security.transport.ssl.enabled: false

# Cluster settings
cluster.name: biomedical-elasticsearch
node.name: node-1

# Path settings
path.data: $esDir\data
path.logs: $esDir\logs
"@
            $esConfig | Out-File -FilePath "$esDir\config\elasticsearch.yml" -Encoding UTF8 -Force
            
            # Update JVM options for heap size
            $jvmOptions = Get-Content "$esDir\config\jvm.options"
            $jvmOptions = $jvmOptions -replace '-Xms.*', '-Xms2g'
            $jvmOptions = $jvmOptions -replace '-Xmx.*', '-Xmx2g'
            $jvmOptions | Out-File -FilePath "$esDir\config\jvm.options" -Encoding UTF8 -Force
            
            Write-Host "✓ Elasticsearch installed successfully!" -ForegroundColor Green
        }
        else {
            Write-Host "✗ Elasticsearch installation failed!" -ForegroundColor Red
        }
    }
}

# ============================================
# REDIS INSTALLATION
# ============================================
if (-not $SkipRedis) {
    Write-Host "`n[2/3] Installing Redis..." -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    
    $redisDir = "$ServicesDir\redis"
    
    if (Test-Path $redisDir) {
        Write-Host "Redis directory already exists. Skipping..." -ForegroundColor Yellow
    }
    else {
        $redisZip = "$ServicesDir\redis.zip"
        # Using Microsoft's archived Redis for Windows
        $redisUrl = "https://github.com/microsoftarchive/redis/releases/download/win-3.2.100/Redis-x64-3.2.100.zip"
        
        if (Download-File -Url $redisUrl -OutputPath $redisZip) {
            Write-Host "Extracting Redis..." -ForegroundColor Yellow
            Expand-Archive -Path $redisZip -DestinationPath $redisDir -Force
            Remove-Item $redisZip
            
            # Create redis configuration
            $redisConfigPath = "$redisDir\redis.windows.conf"
            $redisConfigContent = "# Redis configuration for BioMed Scholar`nport 6380`nbind 0.0.0.0`nprotected-mode no`ndir $redisDir"
            $redisConfigContent | Out-File -FilePath $redisConfigPath -Encoding UTF8 -Force
            
            Write-Host "✓ Redis installed successfully!" -ForegroundColor Green
        }
        else {
            Write-Host "✗ Redis installation failed!" -ForegroundColor Red
        }
    }
}

# ============================================
# POSTGRESQL INSTALLATION
# ============================================
if (-not $SkipPostgres) {
    Write-Host "`n[3/3] Installing PostgreSQL 15..." -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    
    Write-Host "PostgreSQL requires a full installer." -ForegroundColor Yellow
    Write-Host "Please download and install PostgreSQL manually from:" -ForegroundColor Yellow
    Write-Host "https://www.postgresql.org/download/windows/" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Installation settings:" -ForegroundColor Yellow
    Write-Host "  - Port: 5433" -ForegroundColor White
    Write-Host "  - Password: password" -ForegroundColor White
    Write-Host "  - Database: biomedical_search" -ForegroundColor White
    Write-Host "  - User: user" -ForegroundColor White
    Write-Host ""
    Write-Host "After installation, run the following SQL commands:" -ForegroundColor Yellow
    Write-Host @"
CREATE USER "user" WITH PASSWORD 'password';
CREATE DATABASE biomedical_search OWNER "user";
GRANT ALL PRIVILEGES ON DATABASE biomedical_search TO "user";
"@ -ForegroundColor White
}

# ============================================
# SUMMARY
# ============================================
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Installation Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

if (Test-Path "$ServicesDir\elasticsearch") {
    Write-Host "✓ Elasticsearch: Installed at $ServicesDir\elasticsearch" -ForegroundColor Green
}
else {
    Write-Host "✗ Elasticsearch: Not installed" -ForegroundColor Red
}

if (Test-Path "$ServicesDir\redis") {
    Write-Host "✓ Redis: Installed at $ServicesDir\redis" -ForegroundColor Green
}
else {
    Write-Host "✗ Redis: Not installed" -ForegroundColor Red
}

Write-Host "⚠ PostgreSQL: Manual installation required" -ForegroundColor Yellow

Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Install PostgreSQL manually (if not done)" -ForegroundColor White
Write-Host "2. Run: .\start_services.ps1" -ForegroundColor White
Write-Host "3. Run: .\check_services.ps1 to verify" -ForegroundColor White
Write-Host ""
