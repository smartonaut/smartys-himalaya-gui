# Baut die Windows-Fassung. Aufruf in PowerShell im Projektordner:
#   .\packaging\build-windows.ps1
#
# Ergebnis: dist\SmartysHimalayaGUI.exe
# Voraussetzung: Python 3.11+ und himalaya.exe im PATH.

$ErrorActionPreference = "Stop"
$Hier = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Hier

Write-Host "Python:" -NoNewline
python --version

Write-Host "Installiere Abhaengigkeiten ..."
python -m pip install --quiet --upgrade pip pyinstaller pywebview

Write-Host "Baue .exe ..."
python -m PyInstaller --noconfirm --clean packaging\smartys-himalaya-gui.spec

$Exe = Join-Path $Hier "dist\SmartysHimalayaGUI.exe"
if (-not (Test-Path $Exe)) {
    Write-Error "Build fehlgeschlagen: $Exe fehlt"
}

$Groesse = [math]::Round((Get-Item $Exe).Length / 1MB, 1)
Write-Host ""
Write-Host "Fertig: $Exe ($Groesse MB)"
Write-Host ""
Write-Host "Voraussetzung auf dem Zielrechner: himalaya.exe"
Write-Host "  Download: https://github.com/pimalaya/himalaya/releases"
Write-Host "  Danach einmalig Konten einrichten — die Oberflaeche fuehrt hindurch."
