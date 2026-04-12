# Start Kafka Native Services (Zookeeper and Kafka Server)
Write-Host "Starting Kafka Native Services..." -ForegroundColor Cyan

$kafkaHome = "C:\Services\kafka"

if (Test-Path $kafkaHome) {
    # 1. Start Zookeeper
    Write-Host "[1/2] Starting Zookeeper..." -ForegroundColor Yellow
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd $kafkaHome; .\bin\windows\zookeeper-server-start.bat .\config\zookeeper.properties" -WindowStyle Normal
    Write-Host "✓ Zookeeper starting in new window" -ForegroundColor Green
    
    Start-Sleep -Seconds 5
    
    # 2. Start Kafka Server
    Write-Host "[2/2] Starting Kafka Server..." -ForegroundColor Yellow
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd $kafkaHome; .\bin\windows\kafka-server-start.bat .\config\server.properties" -WindowStyle Normal
    Write-Host "✓ Kafka Server starting in new window" -ForegroundColor Green
}
else {
    Write-Host "✗ Kafka not found at $kafkaHome" -ForegroundColor Red
}
