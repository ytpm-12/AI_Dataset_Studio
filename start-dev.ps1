$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendPath = Join-Path $projectRoot 'backend'
$frontendPath = Join-Path $projectRoot 'frontend'
$pythonPath = Join-Path $projectRoot '.venv\Scripts\python.exe'
$celeryPath = Join-Path $projectRoot '.venv\Scripts\celery.exe'

if (-not (Test-Path -LiteralPath $pythonPath)) {
    throw "Environnement virtuel introuvable : $pythonPath"
}

Set-Location -LiteralPath $projectRoot
docker compose up -d redis

Start-Process powershell -WindowStyle Normal -ArgumentList @(
    '-NoExit',
    '-Command',
    "Set-Location -LiteralPath '$backendPath'; & '$pythonPath' manage.py runserver 127.0.0.1:8000"
)

Start-Process powershell -WindowStyle Normal -ArgumentList @(
    '-NoExit',
    '-Command',
    "Set-Location -LiteralPath '$backendPath'; & '$celeryPath' -A backend worker --loglevel=INFO --pool=solo"
)

Start-Process powershell -WindowStyle Normal -ArgumentList @(
    '-NoExit',
    '-Command',
    "Set-Location -LiteralPath '$frontendPath'; npm run dev"
)

Start-Sleep -Seconds 3
Start-Process 'http://127.0.0.1:5173'

Write-Host 'AI Dataset Studio demarre :' -ForegroundColor Green
Write-Host '  Frontend React : http://127.0.0.1:5173'
Write-Host '  API Django     : http://127.0.0.1:8000/api/v1/'
Write-Host '  Administration : http://127.0.0.1:8000/admin/'
