$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $ProjectRoot
$Python = Join-Path $env:LOCALAPPDATA 'Programs\Python\Python312\python.exe'
if (-not (Test-Path -LiteralPath $Python)) {
  throw 'Python 3.12 was not found in the reviewed per-user location.'
}
if (-not (Test-Path -LiteralPath '.venv\Scripts\python.exe')) {
  & $Python -m venv .venv
}
New-Item -ItemType Directory -Force data\images,data\logs,data\tmp | Out-Null
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
Write-Output 'Local environment prepared. No dependencies or browsers were installed.'
Write-Output 'Review DEPENDENCIES.md, LOCKING.md and uv.lock before any installation.'
