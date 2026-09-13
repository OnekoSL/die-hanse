$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot

$vsDevCmdCandidates = @(
  "C:\Program Files\Microsoft Visual Studio\2022\BuildTools\Common7\Tools\VsDevCmd.bat",
  "C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\Tools\VsDevCmd.bat",
  "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\Common7\Tools\VsDevCmd.bat"
)
$vsDevCmd = $vsDevCmdCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $vsDevCmd) {
  throw "VsDevCmd.bat nicht gefunden. Installiere Visual Studio Build Tools oder Community mit C++ Workload."
}

$cargoExe = Join-Path $env:USERPROFILE ".cargo\bin\cargo.exe"
if (!(Test-Path $cargoExe)) {
  throw "cargo.exe nicht gefunden unter $cargoExe. Installiere Rust via rustup."
}

$kernelLib = Get-ChildItem "C:\Program Files (x86)\Windows Kits\10\Lib" -Recurse -Filter kernel32.lib -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $kernelLib) {
  throw "Windows SDK (kernel32.lib) fehlt. Installiere in Visual Studio Installer die Windows 10/11 SDK-Komponente."
}

Write-Host "Nutze VS Dev Command: $vsDevCmd"
Write-Host "Gefundene SDK-Lib: $($kernelLib.FullName)"

$cmd = @"
call "$vsDevCmd" -arch=x64 && set PATH=$env:USERPROFILE\.cargo\bin;!PATH! && cd /d "$root" && npm.cmd run build:web && npm.cmd run build:backend && npx.cmd tauri build --bundles msi
"@

cmd.exe /V:ON /c $cmd
if ($LASTEXITCODE -ne 0) {
  throw "MSI-Build fehlgeschlagen mit Exit-Code $LASTEXITCODE"
}

Write-Host "MSI-Build erfolgreich. Ausgabe unter src-tauri\\target\\release\\bundle\\msi"
