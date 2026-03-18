<#
Creates/activates a local virtual environment and installs requirements.
Run from the repo root:

  .\setup.ps1
#>

$ErrorActionPreference = 'Stop'

Write-Host "Creating virtual environment (if missing)..." -ForegroundColor Cyan
if (-not (Test-Path -Path '.venv')) {
    python -m venv .venv
}

Write-Host "Activating virtual environment..." -ForegroundColor Cyan
. .\venv\Scripts\Activate.ps1

Write-Host "Installing dependencies..." -ForegroundColor Cyan
pip install -r requirements.txt

Write-Host "\n✅ Setup complete. Run the generator with: `python src/main.py`" -ForegroundColor Green
