# Running Services Natively on Windows (Without Docker)

This guide will help you install and run Elasticsearch, Redis, and PostgreSQL directly on Windows without Docker Desktop.

## Prerequisites

- Windows 10/11
- PowerShell (Administrator access)
- At least 4GB of free RAM
- Internet connection for downloads

---

## 1. Install Elasticsearch 8.11.0

### Download and Install

1. **Download Elasticsearch**:
   ```powershell
   # Create a directory for services
   mkdir C:\Services
   cd C:\Services
   
   # Download Elasticsearch 8.11.0
   Invoke-WebRequest -Uri "https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-8.11.0-windows-x86_64.zip" -OutFile "elasticsearch-8.11.0.zip"
   
   # Extract
   Expand-Archive -Path "elasticsearch-8.11.0.zip" -DestinationPath "C:\Services"
   Rename-Item "C:\Services\elasticsearch-8.11.0" "C:\Services\elasticsearch"
   ```

2. **Configure Elasticsearch**:
   
   Edit `C:\Services\elasticsearch\config\elasticsearch.yml`:
   ```yaml
   # Network settings
   network.host: 0.0.0.0
   http.port: 9201
   transport.port: 9301
   
   # Discovery settings
   discovery.type: single-node
   
   # Security settings (disabled to match Docker setup)
   xpack.security.enabled: false
   xpack.security.enrollment.enabled: false
   xpack.security.http.ssl.enabled: false
   xpack.security.transport.ssl.enabled: false
   
   # Cluster name
   cluster.name: biomedical-elasticsearch
   node.name: node-1
   
   # Path settings
   path.data: C:\Services\elasticsearch\data
   path.logs: C:\Services\elasticsearch\logs
   ```

3. **Set Java Heap Size**:
   
   Edit `C:\Services\elasticsearch\config\jvm.options`:
   ```
   -Xms2g
   -Xmx2g
   ```

4. **Start Elasticsearch**:
   ```powershell
   cd C:\Services\elasticsearch\bin
   .\elasticsearch.bat
   ```

5. **Verify**:
   ```powershell
   # In a new terminal
   curl http://localhost:9201
   ```

---

## 2. Install Redis 7

### Using Memurai (Redis-compatible for Windows)

Redis doesn't have official Windows support, so we'll use **Memurai** (Redis-compatible) or **Redis for Windows** from Microsoft's archive.

#### Option A: Memurai (Recommended)

1. **Download Memurai**:
   - Visit: https://www.memurai.com/get-memurai
   - Download the free developer edition
   - Install using the installer

2. **Configure Memurai**:
   
   Edit `C:\Program Files\Memurai\memurai.conf`:
   ```
   port 6380
   bind 0.0.0.0
   ```

3. **Start Memurai**:
   ```powershell
   # Memurai runs as a Windows service by default
   # To restart with new config:
   Restart-Service Memurai
   ```

#### Option B: Redis from Microsoft Archive

1. **Download Redis**:
   ```powershell
   cd C:\Services
   Invoke-WebRequest -Uri "https://github.com/microsoftarchive/redis/releases/download/win-3.2.100/Redis-x64-3.2.100.zip" -OutFile "redis.zip"
   Expand-Archive -Path "redis.zip" -DestinationPath "C:\Services\redis"
   ```

2. **Configure Redis**:
   
   Edit `C:\Services\redis\redis.windows.conf`:
   ```
   port 6380
   bind 0.0.0.0
   ```

3. **Start Redis**:
   ```powershell
   cd C:\Services\redis
   .\redis-server.exe redis.windows.conf
   ```

4. **Verify**:
   ```powershell
   # In a new terminal
   cd C:\Services\redis
   .\redis-cli.exe -p 6380
   # Type: ping
   # Should respond: PONG
   ```

---

## 3. Install PostgreSQL 15

### Download and Install

1. **Download PostgreSQL**:
   - Visit: https://www.postgresql.org/download/windows/
   - Download PostgreSQL 15 installer from EnterpriseDB
   - Run the installer

2. **Installation Settings**:
   - **Port**: `5433` (to match Docker setup)
   - **Password**: `password` (or your preferred password)
   - **Locale**: Default
   - Install all components including pgAdmin

3. **Create Database and User**:
   
   Open PowerShell and run:
   ```powershell
   # Set PostgreSQL bin path (adjust version if needed)
   $env:Path += ";C:\Program Files\PostgreSQL\15\bin"
   
   # Connect to PostgreSQL
   psql -U postgres -p 5433
   ```
   
   In the PostgreSQL prompt:
   ```sql
   -- Create user
   CREATE USER "user" WITH PASSWORD 'password';
   
   -- Create database
   CREATE DATABASE biomedical_search OWNER "user";
   
   -- Grant privileges
   GRANT ALL PRIVILEGES ON DATABASE biomedical_search TO "user";
   
   -- Exit
   \q
   ```

4. **Verify**:
   ```powershell
   psql -U user -d biomedical_search -p 5433
   # Enter password: password
   ```

---

## 4. Create Startup Scripts

### Start All Services Script

Create `C:\Users\sasid\Downloads\kash_proj\start_services.ps1`:

```powershell
# Start All Services for BioMed Scholar
Write-Host "Starting BioMed Scholar Services..." -ForegroundColor Green

# Start Elasticsearch
Write-Host "`nStarting Elasticsearch..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd C:\Services\elasticsearch\bin; .\elasticsearch.bat" -WindowStyle Normal

# Wait a bit
Start-Sleep -Seconds 2

# Start Redis (if using Option B - manual Redis)
Write-Host "Starting Redis..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd C:\Services\redis; .\redis-server.exe redis.windows.conf" -WindowStyle Normal

# PostgreSQL runs as a Windows service, so just check status
Write-Host "`nChecking PostgreSQL service..." -ForegroundColor Yellow
$pgService = Get-Service -Name "postgresql-x64-15" -ErrorAction SilentlyContinue
if ($pgService) {
    if ($pgService.Status -eq "Running") {
        Write-Host "PostgreSQL is already running" -ForegroundColor Green
    } else {
        Start-Service "postgresql-x64-15"
        Write-Host "PostgreSQL started" -ForegroundColor Green
    }
} else {
    Write-Host "PostgreSQL service not found. Please start it manually." -ForegroundColor Red
}

Write-Host "`n==================================" -ForegroundColor Green
Write-Host "Services Starting..." -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green
Write-Host "Elasticsearch: http://localhost:9201"
Write-Host "Redis: localhost:6380"
Write-Host "PostgreSQL: localhost:5433"
Write-Host "`nPress Ctrl+C in each window to stop services"
```

### Check Services Status Script

Create `C:\Users\sasid\Downloads\kash_proj\check_services.ps1`:

```powershell
# Check Services Status
Write-Host "Checking BioMed Scholar Services..." -ForegroundColor Green

# Check Elasticsearch
Write-Host "`nElasticsearch (port 9201):" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:9201" -UseBasicParsing -TimeoutSec 5
    Write-Host "✓ Running" -ForegroundColor Green
    $response.Content | ConvertFrom-Json | Select-Object name, cluster_name, version
} catch {
    Write-Host "✗ Not running" -ForegroundColor Red
}

# Check Redis
Write-Host "`nRedis (port 6380):" -ForegroundColor Yellow
try {
    $redis = New-Object System.Net.Sockets.TcpClient("localhost", 6380)
    if ($redis.Connected) {
        Write-Host "✓ Running" -ForegroundColor Green
        $redis.Close()
    }
} catch {
    Write-Host "✗ Not running" -ForegroundColor Red
}

# Check PostgreSQL
Write-Host "`nPostgreSQL (port 5433):" -ForegroundColor Yellow
try {
    $pg = New-Object System.Net.Sockets.TcpClient("localhost", 5433)
    if ($pg.Connected) {
        Write-Host "✓ Running" -ForegroundColor Green
        $pg.Close()
    }
} catch {
    Write-Host "✗ Not running" -ForegroundColor Red
}
```

---

## 5. Quick Start

### First Time Setup

1. Install all three services following the instructions above
2. Configure each service with the correct ports and settings
3. Use the startup script to launch all services

### Daily Usage

```powershell
# Start all services
cd C:\Users\sasid\Downloads\kash_proj
.\start_services.ps1

# Check if services are running
.\check_services.ps1

# Start your backend
uvicorn src.api.app:app --host 0.0.0.0 --port 8000 --reload
```

---

## 6. Service Configuration Summary

| Service | Port | Credentials | Data Location |
|---------|------|-------------|---------------|
| **Elasticsearch** | 9201 (HTTP), 9301 (Transport) | No auth | `C:\Services\elasticsearch\data` |
| **Redis** | 6380 | No auth | `C:\Services\redis` or Memurai default |
| **PostgreSQL** | 5433 | user: `user`<br>password: `password`<br>database: `biomedical_search` | PostgreSQL default data directory |

---

## 7. Troubleshooting

### Elasticsearch won't start
- Check Java is installed: `java -version`
- Check logs: `C:\Services\elasticsearch\logs`
- Ensure ports 9201 and 9301 are not in use

### Redis connection refused
- Verify Redis is running: `netstat -an | findstr 6380`
- Check firewall settings
- For Memurai, check Windows Services

### PostgreSQL connection issues
- Verify service is running: `Get-Service postgresql-x64-15`
- Check `pg_hba.conf` for connection permissions
- Ensure port 5433 is not blocked

### Port conflicts
If any ports are already in use, you'll need to either:
1. Stop the conflicting service
2. Change the port in both the service config and your application's `.env` file

---

## 8. Stopping Services

### Stop Elasticsearch
- Press `Ctrl+C` in the Elasticsearch terminal window

### Stop Redis
- Press `Ctrl+C` in the Redis terminal window
- Or for Memurai: `Stop-Service Memurai`

### Stop PostgreSQL
```powershell
Stop-Service postgresql-x64-15
```

---

## Notes

- **Memory Usage**: These services will use approximately 3-4GB of RAM combined
- **Auto-start**: PostgreSQL can be set to start automatically with Windows. Elasticsearch and Redis need to be started manually or set up as Windows services
- **Data Persistence**: All data is stored locally and persists between restarts
- **Security**: This setup matches the Docker configuration with security disabled for local development. **Do not use in production!**
