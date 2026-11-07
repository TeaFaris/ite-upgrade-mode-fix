# itefix installer for Windows (PowerShell)
#   irm https://raw.githubusercontent.com/TeaFaris/ite-upgrade-mode-fix/main/install.ps1 | iex
$ErrorActionPreference = 'Stop'
$repo = 'TeaFaris/ite-upgrade-mode-fix'
$dir = Join-Path $env:LOCALAPPDATA 'itefix'
New-Item -ItemType Directory -Force -Path $dir | Out-Null

function Find-Python {
    foreach ($c in 'py', 'python', 'python3') {
        $cmd = Get-Command $c -ErrorAction SilentlyContinue
        if ($cmd -and $cmd.Source -notmatch 'WindowsApps') { return $cmd.Source }
    }
    return $null
}

$py = Find-Python
if (-not $py) {
    Write-Host 'python not found, installing Python 3.12 with winget ...'
    winget install -e --id Python.Python.3.12 --scope user --accept-package-agreements --accept-source-agreements
    $env:Path = [Environment]::GetEnvironmentVariable('Path', 'User') + ';' + [Environment]::GetEnvironmentVariable('Path', 'Machine')
    $py = Find-Python
    if (-not $py) { throw 'could not install python. Get it from python.org and run this again.' }
}

Invoke-WebRequest "https://raw.githubusercontent.com/$repo/main/itefix.py" -OutFile (Join-Path $dir 'itefix.py') -UseBasicParsing
Set-Content -Path (Join-Path $dir 'itefix.cmd') -Value "@`"$py`" `"%~dp0itefix.py`" %*" -Encoding ASCII

$userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
if (-not $userPath) { $userPath = '' }
if (($userPath -split ';') -notcontains $dir) {
    [Environment]::SetEnvironmentVariable('Path', ($userPath.TrimEnd(';') + ';' + $dir).TrimStart(';'), 'User')
}
$env:Path += ";$dir"

Write-Host ''
Write-Host "installed to $dir"
& (Join-Path $dir 'itefix.cmd') status
Write-Host ''
Write-Host 'open a new terminal later and just type: itefix status'
