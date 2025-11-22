Param (
    [int]$Port = 8000,
    [string]$Host = "127.0.0.1"
)

$scriptDir = if ($PSScriptRoot) {
    $PSScriptRoot
} elseif ($MyInvocation.MyCommand.Path) {
    Split-Path -Path $MyInvocation.MyCommand.Path -Parent
} else {
    Get-Location
}

Set-Location -Path $scriptDir

# allow this process to run scripts
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force

# ensure python exists
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Python not found in PATH. Install Python and re-run this script." -ForegroundColor Red
    exit 1
}

# create venv if missing
if (-not (Test-Path ".\venv\Scripts\python.exe")) {
    Write-Host "Creating virtual environment..."
    python -m venv venv
}

$venvPython = Join-Path $scriptDir "venv\Scripts\python.exe"
$baseUrl = "http://$($Host):$($Port)"

# install requirements if available
if (Test-Path ".\requirements.txt") {
    Write-Host "Installing Python dependencies into venv..."
    & $venvPython -m pip install --upgrade pip
    & $venvPython -m pip install -r requirements.txt
} else {
    Write-Host "No requirements.txt found — skipping pip install." -ForegroundColor Yellow
}

# start uvicorn using venv python
Write-Host "Starting uvicorn (using venv python)..."
$proc = Start-Process -FilePath $venvPython -ArgumentList "-m","uvicorn","main:app","--host",$Host,"--port",$Port,"--reload" -PassThru

# wait for server to report healthy
$tries = 0
while ($tries -lt 30) {
    try {
        $r = Invoke-WebRequest -Uri "$baseUrl/health" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
        if ($r.StatusCode -eq 200) { break }
    } catch { }
    Start-Sleep -Seconds 1
    $tries++
}

if ($tries -ge 30) {
    Write-Host "Server did not respond on $baseUrl within timeout." -ForegroundColor Red
    exit 1
}

# open Chrome if available, otherwise open default browser
try {
    Start-Process "chrome.exe" -ArgumentList $baseUrl -ErrorAction Stop
} catch {
    Start-Process "explorer.exe" -ArgumentList $baseUrl
}
