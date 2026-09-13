param([string]$PythonExe = "")
$ErrorActionPreference = "Stop"
$hanseRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$hanseBackend = [IO.Path]::GetFullPath((Join-Path $hanseRoot "..\web_ui\backend"))
if (!$PythonExe) { $PythonExe = Join-Path $hanseBackend ".venv\Scripts\python.exe" }
if (!(Test-Path -LiteralPath $PythonExe)) { throw "Python-3.11-Umgebung fehlt. Siehe lokal_exe/README.md." }
& $PythonExe -c "import sys; assert sys.version_info[:2] == (3, 11), 'Python 3.11 erforderlich'"
if ($LASTEXITCODE -ne 0) { throw "Falsche Python-Version" }
$hanseDist = [IO.Path]::GetFullPath((Join-Path $hanseRoot "backend-dist"))
$hanseTmp = Join-Path $hanseRoot "tmp"
if (!$hanseDist.StartsWith($hanseRoot + [IO.Path]::DirectorySeparatorChar)) { throw "Unsicheres Buildziel" }
New-Item -ItemType Directory -Force -Path $hanseDist,$hanseTmp | Out-Null
& $PythonExe -m PyInstaller --noconfirm --clean --onedir --name hanse-backend `
  --distpath $hanseDist --workpath (Join-Path $hanseTmp "pyinstaller-build") `
  --specpath (Join-Path $hanseTmp "pyinstaller-spec") --paths $hanseBackend `
  --collect-all uvicorn --hidden-import sqlalchemy.sql.default_comparator `
  (Join-Path $hanseBackend "app\desktop_entry.py")
if ($LASTEXITCODE -ne 0) { throw "PyInstaller fehlgeschlagen" }
$hanseScenarios = Join-Path $hanseDist "data\scenarios"
New-Item -ItemType Directory -Force -Path $hanseScenarios | Out-Null
Get-ChildItem -LiteralPath (Join-Path $hanseRoot "..\web_ui\data\scenarios") -Filter '*.json' | ForEach-Object { Copy-Item -LiteralPath $_.FullName -Destination $hanseScenarios }
Write-Host "Backend-Bundle bereit: $hanseDist"
