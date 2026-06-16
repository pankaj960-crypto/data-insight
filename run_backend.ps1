Param(
    [string]$venv = ".venv",
    [int]$port = 8000
)

# Resolve python in the specified venv
$pythonPath = Join-Path $PSScriptRoot "$venv\Scripts\python.exe"
if (-not (Test-Path $pythonPath)) {
    Write-Error "Python executable not found at $pythonPath. Activate your venv manually or pass correct path."
    exit 1
}

# Change to backend directory so `app` package is importable
Push-Location (Join-Path $PSScriptRoot "backend")
try {
    & $pythonPath -m uvicorn app.main:app --reload --host 0.0.0.0 --port $port
} finally {
    Pop-Location
}
