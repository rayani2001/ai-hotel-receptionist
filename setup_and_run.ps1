<#
setup_and_run.ps1
A convenience script to set up a Python venv, install dependencies, and run the app.
#>

param(
    [switch]$NoRun,
    [switch]$Help,
    [string]$PythonPath = 'python'
)

function Write-Info($m) { Write-Host "[info]  $m" -ForegroundColor Cyan }
function Write-Warn($m) { Write-Host "[warn]  $m" -ForegroundColor Yellow }
function Write-Err($m)  { Write-Host "[error] $m" -ForegroundColor Red }

Write-Info "AI Hotel Receptionist setup_and_run.ps1"
$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptRoot

if ($Help) {
    Write-Host "Usage: .\setup_and_run.ps1 [-NoRun] [-Help] [-PythonPath path\to\python.exe]"
    exit 0
}

$pythonCmd = Get-Command $PythonPath -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Err "Python not found on PATH."
    exit 1
}

$pv = & $PythonPath --version 2>&1
Write-Info "Found Python: $pv"

$venvDir = Join-Path $scriptRoot 'venv'
if (-not (Test-Path $venvDir)) {
    Write-Info "Creating virtual environment..."
    & $PythonPath -m venv $venvDir
    if ($LASTEXITCODE -ne 0) {
        Write-Err "Failed to create venv."
        exit $LASTEXITCODE
    }
} else {
    Write-Info "Virtual environment already exists."
}

function Get-VenvPython($venvPath) {
    $candidates = @(
        (Join-Path $venvPath 'Scripts\python.exe'),
        (Join-Path $venvPath 'Scripts\python3.exe'),
        (Join-Path $venvPath 'bin\python'),
        (Join-Path $venvPath 'bin\python3')
    )
    foreach ($p in $candidates) {
        if (Test-Path $p) { return $p }
    }
    return $null
}

$venvPython = Get-VenvPython $venvDir
if (-not $venvPython) {
    Write-Err "No Python interpreter found in venv."
    exit 2
}

$PythonPath = $venvPython
Write-Info "Using venv python: $PythonPath"

$activateScript = Join-Path $venvDir 'Scripts\Activate.ps1'
if (Test-Path $activateScript) {
    Write-Info "Activating venv..."
    . $activateScript
}

Write-Info "Upgrading pip..."
& $PythonPath -m pip install --upgrade pip

$reqFile = Join-Path $scriptRoot 'requirements.txt'
if (Test-Path $reqFile) {
    Write-Info "Installing requirements..."
    & $PythonPath -m pip install -r $reqFile
} else {
    Write-Warn "requirements.txt not found."
}

if ($NoRun) {
    Write-Info "Setup complete."
    exit 0
}

Write-Info "Starting app with uvicorn..."
& $PythonPath -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
exit $LASTEXITCODE
