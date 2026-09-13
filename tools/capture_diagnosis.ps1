# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Collect an on-camera diagnosis log for the Film Studio app through Wi-Fi ADB.
#
# Usage (from the project root, camera already reachable over ADB):
#   powershell -ExecutionPolicy Bypass -File tools\capture_diagnosis.ps1 -CameraIp CAMERA_IP
#
# Writes props.txt, package.txt, logcat.txt and logcat-filtered.txt into
# build-local\diagnosis\. Nothing is uploaded anywhere.
param(
    [Parameter(Mandatory = $true)][string]$CameraIp,
    [string]$Package = 'com.yuki.imaging.app.pictureeffectplus',
    [string]$OutDir = (Join-Path $PSScriptRoot '..\build-local\diagnosis')
)

$ErrorActionPreference = 'Stop'
$serial = $CameraIp + ':5555'
$OutDir = [System.IO.Path]::GetFullPath($OutDir)
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

function Adb([string[]]$AdbArgs) { & adb -s $serial @AdbArgs }

$adbCmd = Get-Command adb -ErrorAction SilentlyContinue
if (-not $adbCmd) { throw 'adb was not found on PATH. Install Android platform-tools and reopen the terminal.' }
Write-Host "== adb: $($adbCmd.Source)"
& adb version | Select-Object -First 1 | ForEach-Object { Write-Host "   $_" }

Write-Host "== connecting to $serial"
adb connect $serial | Write-Host

$state = (& adb -s $serial get-state 2>&1) -join ' '
if ($state -notmatch 'device') {
    Write-Host ''
    Write-Host 'The camera is not reachable yet:' -ForegroundColor Red
    Write-Host "   $state"
    Write-Host 'Check that:'
    Write-Host '  - camera and PC are on the same Wi-Fi network'
    Write-Host "  - OpenMemories:Tweak > Developer shows Enable Wifi + Enable ADB, and the IP matches $CameraIp"
    Write-Host '  - the camera has not gone to sleep (raise the auto power-off time)'
    Write-Host '  - a firewall/VPN is not blocking port 5555'
    return
}

Write-Host "== device properties"
Adb @('shell', 'getprop') | Out-File -Encoding utf8 (Join-Path $OutDir 'props.txt')
Get-Content (Join-Path $OutDir 'props.txt') |
    Select-String 'ro\.build\.version|ro\.product\.model' |
    ForEach-Object { Write-Host "   $_" }

Write-Host "== installed package"
Adb @('shell', 'dumpsys', 'package', $Package) | Out-File -Encoding utf8 (Join-Path $OutDir 'package.txt')
Get-Content (Join-Path $OutDir 'package.txt') |
    Select-String 'versionName|versionCode|codePath|signature' |
    Select-Object -First 8 | ForEach-Object { Write-Host "   $_" }

Write-Host "== clearing log buffer"
Adb @('logcat', '-c') | Out-Null

Write-Host ''
Write-Host 'NOW, ON THE CAMERA:' -ForegroundColor Yellow
Write-Host '  1) open the app from the camera application list (watch the app icon)'
Write-Host '  2) press the center key to open the filter chooser'
Write-Host '  3) step through several filters, a few seconds on each'
Write-Host '  4) open MENU -> filter strength and change it once'
Write-Host '  5) leave the app normally'
Write-Host ''
Read-Host 'Press Enter here when you are done'

Write-Host "== dumping log buffer"
$log = Adb @('logcat', '-d', '-v', 'time')
if (-not $log) { $log = Adb @('logcat', '-d') }
$log | Out-File -Encoding utf8 (Join-Path $OutDir 'logcat.txt')

$pattern = 'FujiDiag|FujiHook|FujiMovie|ResourceType|AssetManager|AndroidRuntime|dalvikvm|Resources'
Get-Content (Join-Path $OutDir 'logcat.txt') |
    Select-String $pattern | Out-File -Encoding utf8 (Join-Path $OutDir 'logcat-filtered.txt')

$filtered = @(Get-Content (Join-Path $OutDir 'logcat-filtered.txt'))
$total = @(Get-Content (Join-Path $OutDir 'logcat.txt')).Count
Write-Host ''
Write-Host "log lines total: $total, relevant: $($filtered.Count)" -ForegroundColor Green
$filtered | Select-Object -First 40 | ForEach-Object { Write-Host $_ }

# The debug build also appends to this file on the card; pull it when it exists.
$diagFile = Join-Path $OutDir 'FilmStudioDiag.txt'
Adb @('pull', '/mnt/sdcard/FilmStudioDiag.txt', $diagFile) 2>&1 | Out-Null
if (Test-Path $diagFile) {
    Write-Host ''
    Write-Host 'Card log (FilmStudioDiag.txt):' -ForegroundColor Green
    Get-Content $diagFile | Select-Object -First 40 | ForEach-Object { Write-Host $_ }
} else {
    Write-Host 'Card log not found (app may not have written it; logcat is still valid).'
}

Write-Host ''
Write-Host "Files written to $OutDir"
Write-Host 'Send logcat-filtered.txt for analysis.'
