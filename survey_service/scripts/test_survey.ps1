<#
  Survey Service quick test script (PowerShell)

  Usage:
    - Open PowerShell
    - cd survey_service/scripts
    - .\test_survey.ps1 -Port 9002 -CsvPath "..\sample_questions.csv" -UserId "user_123"

  Notes:
    - Service should run with AUTH_MODE=dev for easiest testing
    - Admin endpoints require X-Dev-User=admin_user
#>

param(
  [int]$Port = 9002,
  [string]$Host = "http://127.0.0.1",
  [string]$UserId = "user_123",
  [string]$AdminUser = "admin_user",
  [string]$CsvPath = "..\sample_questions.csv"
)

$base = "$Host:$Port/survey"

function Invoke-Api {
  param(
    [string]$Method,
    [string]$Url,
    $Body = $null,
    [hashtable]$Headers = @{},
    $Form = $null
  )
  try {
    if ($Form) {
      return Invoke-RestMethod -Method $Method -Uri $Url -Headers $Headers -Form $Form
    } elseif ($Body) {
      $json = $Body | ConvertTo-Json -Depth 6
      return Invoke-RestMethod -Method $Method -Uri $Url -Headers $Headers -ContentType 'application/json' -Body $json
    } else {
      return Invoke-RestMethod -Method $Method -Uri $Url -Headers $Headers
    }
  } catch {
    Write-Error $_
    if ($_.Exception.Response -and ($_.Exception.Response.ContentLength -gt 0)) {
      $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
      $respBody = $reader.ReadToEnd()
      Write-Host "Response:" $respBody
    }
    throw
  }
}

Write-Host "==> GET /survey/questions"
$headers = @{ 'X-Dev-User' = $UserId }
Invoke-Api -Method GET -Url "$base/questions" -Headers $headers | ConvertTo-Json -Depth 6

if (Test-Path $CsvPath) {
  Write-Host "==> POST /survey/admin/import-questions (file: $CsvPath)"
  $adminHeaders = @{ 'X-Dev-User' = $AdminUser }
  $form = @{ file = Get-Item -LiteralPath $CsvPath }
  Invoke-Api -Method POST -Url "$base/admin/import-questions" -Headers $adminHeaders -Form $form | ConvertTo-Json -Depth 6
} else {
  Write-Warning "CSV not found: $CsvPath (skip import)"
}

Write-Host "==> POST /survey/submit"
$submitBody = @{
  user_id = $UserId
  answers = @(
    @{ question_id = 1; answer = 'Nam' },
    @{ question_id = 2; answer = @('Thẻ tín dụng') }
  )
}
Invoke-Api -Method POST -Url "$base/submit" -Headers $headers -Body $submitBody | ConvertTo-Json -Depth 6

Write-Host "==> PATCH /survey/answer"
$singleBody = @{ user_id = $UserId; question_id = 3; answer = 27 }
Invoke-Api -Method PATCH -Url "$base/answer" -Headers $headers -Body $singleBody | ConvertTo-Json -Depth 6

Write-Host "==> GET /survey/answers/$UserId"
Invoke-Api -Method GET -Url "$base/answers/$UserId" -Headers $headers | ConvertTo-Json -Depth 6

Write-Host "==> GET /survey/progress/$UserId"
Invoke-Api -Method GET -Url "$base/progress/$UserId" -Headers $headers | ConvertTo-Json -Depth 6

Write-Host "Done."


