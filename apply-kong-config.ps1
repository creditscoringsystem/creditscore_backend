# PowerShell script for Windows
Write-Host "🚀 Applying Kong Declarative Config..." -ForegroundColor Green

# Wait for Kong to be ready
do {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8001/" -Method GET -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            break
        }
    }
    catch {
        Write-Host "Waiting for Kong Admin API..." -ForegroundColor Yellow
        Start-Sleep -Seconds 2
    }
} while ($true)

# Apply the YAML config (multipart form upload)
Write-Host "📄 Loading kong-config.yml..." -ForegroundColor Cyan
try {
    $configFile = Get-Item -Path "kong-config.yml"
    if (-not $configFile) { throw "kong-config.yml not found" }

    # Windows PowerShell 5.1: Use Invoke-WebRequest -Form for multipart
    $form = @{ config = $configFile }
    $resp = Invoke-WebRequest -Uri "http://localhost:8001/config" -Method POST -Form $form -TimeoutSec 30
    if ($resp.StatusCode -ne 201 -and $resp.StatusCode -ne 200) {
        throw "Kong /config returned status code $($resp.StatusCode)"
    }

    Write-Host ""; Write-Host "✅ Kong configuration applied!" -ForegroundColor Green
    Write-Host ""; Write-Host "🧪 Test endpoints:" -ForegroundColor Cyan
    Write-Host "   curl.exe http://localhost:8000/api/v1/user-ping"
    Write-Host "   curl.exe http://localhost:8000/api/v1/profile-health"
    Write-Host "   curl.exe http://localhost:8000/api/v1/alert-health"
    Write-Host "   curl.exe http://localhost:8000/api/v1/survey-health"
    Write-Host "   curl.exe http://localhost:8000/api/v1/score-health"
}
catch {
    Write-Host "⚠️  Invoke-WebRequest failed: $($_.Exception.Message)" -ForegroundColor Yellow
    Write-Host "↪️  Falling back to curl.exe -F multipart..." -ForegroundColor Yellow
    try {
        & curl.exe -sS -f -X POST -F "config=@kong-config.yml" "http://localhost:8001/config" | Out-Null
        Write-Host ""; Write-Host "✅ Kong configuration applied via curl.exe!" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Failed to apply Kong configuration: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
}
