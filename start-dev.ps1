$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendPath = Join-Path $projectRoot 'backend'
$frontendPath = Join-Path $projectRoot 'frontend'
$pythonPath = Join-Path $projectRoot '.venv\Scripts\python.exe'
$celeryPath = Join-Path $projectRoot '.venv\Scripts\celery.exe'

function Test-ListeningPort {
    param([int]$Port)
    return [bool](Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue)
}

if (-not (Test-Path -LiteralPath $pythonPath)) {
    throw "Environnement virtuel introuvable : $pythonPath"
}

Set-Location -LiteralPath $projectRoot
docker compose up -d redis

if (-not (Test-ListeningPort -Port 8000)) {
    Start-Process powershell -WindowStyle Normal -ArgumentList @(
        '-NoExit',
        '-Command',
        "Set-Location -LiteralPath '$backendPath'; & '$pythonPath' manage.py runserver 127.0.0.1:8000"
    )
}
else {
    Write-Host 'Django utilise deja le port 8000.' -ForegroundColor DarkYellow
}

$celeryRunning = Get-CimInstance Win32_Process -Filter "Name = 'celery.exe'" -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -like '*-A backend worker*' }
if (-not $celeryRunning) {
    Start-Process powershell -WindowStyle Normal -ArgumentList @(
        '-NoExit',
        '-Command',
        "Set-Location -LiteralPath '$backendPath'; & '$celeryPath' -A backend worker --loglevel=INFO --pool=solo"
    )
}
else {
    Write-Host 'Un worker Celery est deja actif.' -ForegroundColor DarkYellow
}

$backendReady = $false
Write-Host 'Attente du backend Django...' -ForegroundColor Yellow
for ($attempt = 1; $attempt -le 60; $attempt++) {
    try {
        $response = Invoke-WebRequest `
            -Uri 'http://127.0.0.1:8000/api/v1/auth/csrf/' `
            -UseBasicParsing `
            -TimeoutSec 2
        if ($response.StatusCode -eq 200) {
            $backendReady = $true
            break
        }
    }
    catch {
        Start-Sleep -Seconds 1
    }
}

if (-not $backendReady) {
    throw 'Django ne repond pas sur le port 8000. Consultez le terminal Backend.'
}

Write-Host 'Backend Django pret.' -ForegroundColor Green

if (-not (Test-ListeningPort -Port 5173)) {
    Start-Process powershell -WindowStyle Normal -ArgumentList @(
        '-NoExit',
        '-Command',
        "Set-Location -LiteralPath '$frontendPath'; npm run dev"
    )
}
else {
    Write-Host 'React/Vite utilise deja le port 5173.' -ForegroundColor DarkYellow
}

Start-Sleep -Seconds 2
Start-Process 'http://127.0.0.1:5173'

Write-Host 'AI Dataset Studio demarre :' -ForegroundColor Green
Write-Host '  Frontend React : http://127.0.0.1:5173'
Write-Host '  API Django     : http://127.0.0.1:8000/api/v1/'
Write-Host '  Administration : http://127.0.0.1:8000/admin/'
