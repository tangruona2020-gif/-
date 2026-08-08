$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $ProjectRoot
$Uv = Join-Path $ProjectRoot 'tools\uv\uv.exe'
if (-not (Test-Path -LiteralPath '.venv\Scripts\python.exe')) { throw 'Project .venv is missing.' }
if (-not (Test-Path -LiteralPath 'uv.lock')) { throw 'Reviewed uv.lock is required.' }
if (-not (Test-Path -LiteralPath $Uv)) { throw 'Reviewed project-local uv.exe is required.' }
& $Uv sync --frozen --extra dev --python '.\.venv\Scripts\python.exe'
