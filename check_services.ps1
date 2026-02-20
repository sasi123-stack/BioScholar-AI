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
