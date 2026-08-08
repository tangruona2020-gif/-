$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $ProjectRoot
$env:PLAYWRIGHT_BROWSERS_PATH = Join-Path $ProjectRoot 'data\playwright-browsers'
& .\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
