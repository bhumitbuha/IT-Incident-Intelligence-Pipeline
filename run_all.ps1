param(
    [switch]$SkipInstall,
    [switch]$Dashboard
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Cyan
    python -m venv .venv
}

$activate = ".\.venv\Scripts\Activate.ps1"
. $activate

if (-not $SkipInstall) {
    Write-Host "Installing requirements..." -ForegroundColor Cyan
    pip install --quiet -r requirements.txt
}

Write-Host "Generating sample data..." -ForegroundColor Cyan
python scripts\generate_sample_data.py

Write-Host "Running ETL pipeline..." -ForegroundColor Cyan
python -m etl.run_pipeline

Write-Host "Printing insight reports..." -ForegroundColor Cyan
python -m analysis.insights

if ($Dashboard) {
    Write-Host "Launching Streamlit dashboard..." -ForegroundColor Cyan
    streamlit run dashboard\app.py
}
