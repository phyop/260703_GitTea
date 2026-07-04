param(
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot

function Find-Python {
    $pyLauncher = Get-Command py -ErrorAction SilentlyContinue
    if ($pyLauncher) {
        return @("py", "-3")
    }

    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($python) {
        return @("python")
    }

    throw "Python 3 was not found. Please install Python 3 or make py/python available in PowerShell."
}

if (-not (Test-Path -LiteralPath "credentials.json")) {
    Write-Host "Missing credentials.json." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Open credentials.json in this folder and replace the client_secret placeholder."
    Write-Host "Keep the double quotes and comma in the JSON file."
    exit 1
}

$pythonCmd = @(Find-Python)
$pythonExe = $pythonCmd[0]
$venvDir = ".venv-gmail-routing"
$venvPython = Join-Path $venvDir "Scripts\python.exe"

if (-not (Test-Path -LiteralPath $venvPython)) {
    $pythonArgs = @()
    if ($pythonCmd.Length -gt 1) {
        $pythonArgs = $pythonCmd[1..($pythonCmd.Length - 1)]
    }
    & $pythonExe @pythonArgs -m venv $venvDir
}

& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r requirements-gmail-routing.txt

$scriptArgs = @()
if ($DryRun) {
    $scriptArgs += "--dry-run"
}

& $venvPython route_1ib_to_tmp1.py @scriptArgs
