# PowerShell script for Windows
Write-Host "🚀 Starting Credit Score Backend System..." -ForegroundColor Green

# Start all services
Write-Host "📦 Building and starting containers..." -ForegroundColor Cyan
docker-compose up -d --build

# Wait a bit for services to start
Write-Host "⏳ Waiting for services to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Apply Kong configuration
Write-Host "🔧 Applying Kong configuration..." -ForegroundColor Cyan
& ".\apply-kong-config.ps1"

Write-Host ""
Write-Host "✅ System started successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Service Status:" -ForegroundColor Cyan
Write-Host "   Kong Gateway: http://localhost:8000"
Write-Host "   Kong Admin:   http://localhost:8001"
Write-Host "   User Service: http://localhost:8002"
Write-Host "   Profile Service: http://localhost:8003"
Write-Host "   Alert Service: http://localhost:8004"
Write-Host "   Survey Service: http://localhost:8005"
Write-Host "   Score Service: http://localhost:8007"
Write-Host "   PostgreSQL: localhost:5432"
