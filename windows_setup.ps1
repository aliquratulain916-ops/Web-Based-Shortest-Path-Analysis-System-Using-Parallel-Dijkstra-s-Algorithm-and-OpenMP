<#
Windows setup helper for the Dijkstra OpenMP project.
Run this from the project root in PowerShell.
#>

$ErrorActionPreference = 'Stop'

Write-Host "=== Dijkstra Windows Setup ==="

if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
    Write-Warning "Python launcher 'py' not found. Install Python 3.8+ and add it to PATH."
    exit 1
}

Write-Host "Installing Python dependencies..."
py -m pip install -r requirements.txt

if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    Write-Warning "npm not found. Install Node.js and npm to use the frontend."
} else {
    Write-Host "Installing frontend dependencies..."
    Push-Location .\frontend
    npm install
    Pop-Location
}

Write-Host "Building OpenMP solver..."
if (Test-Path .\build_openmp.bat) {
    .\build_openmp.bat
} else {
    Write-Warning "build_openmp.bat not found."
}

Write-Host "Setup complete."
Write-Host "To run the project:"
Write-Host "  py -m uvicorn api:app --reload --port 8000"
Write-Host "  cd frontend; npm run dev -- --host 127.0.0.1 --port 5173"
Write-Host "Open the browser at http://127.0.0.1:5173"
