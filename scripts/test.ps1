$ErrorActionPreference = 'Stop'
$hanseRoot = Split-Path -Parent $PSScriptRoot
$hansePython = Join-Path $hanseRoot 'web_ui/backend/.venv/Scripts/python.exe'
$hansePreviousDbPath = $env:HANSE_DB_PATH
$hanseTestDbPath = Join-Path ([IO.Path]::GetTempPath()) ('die-hanse-tests-' + [guid]::NewGuid() + '.db')
try {
    $env:HANSE_DB_PATH = $hanseTestDbPath
    Push-Location (Join-Path $hanseRoot 'web_ui/backend')
    try {
        & $hansePython -m ruff check .
        if ($LASTEXITCODE -ne 0) { throw 'Ruff fehlgeschlagen' }
        & $hansePython -m pytest
        if ($LASTEXITCODE -ne 0) { throw 'Backend-Tests fehlgeschlagen' }
    } finally { Pop-Location }
    npm.cmd --prefix (Join-Path $hanseRoot 'web_ui/frontend') test
    if ($LASTEXITCODE -ne 0) { throw 'Frontend-Tests fehlgeschlagen' }
    npm.cmd --prefix (Join-Path $hanseRoot 'web_ui/frontend') run build
    if ($LASTEXITCODE -ne 0) { throw 'Frontend-Build fehlgeschlagen' }
} finally { $env:HANSE_DB_PATH = $hansePreviousDbPath }
