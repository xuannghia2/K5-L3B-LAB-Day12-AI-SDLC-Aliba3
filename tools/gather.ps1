# Two gather commands: .\tools\gather.ps1 test | .\tools\gather.ps1 play
param(
    [ValidateSet('test', 'play')][string]$Action = 'test',
    [int]$Seed = 1,
    [int]$Port = 8000
)
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$localPython = Join-Path (Split-Path -Parent $repoRoot) '.tools\python\Scripts\python.exe'
$candidates = @($env:CHONOI_PYTHON, $localPython)
foreach ($commandName in @('python3', 'python')) {
    $command = Get-Command $commandName -CommandType Application -ErrorAction SilentlyContinue
    if ($command -and $command.Source -notlike '*Microsoft\WindowsApps*') {
        $candidates += $command.Source
    }
}
$pythonPath = $candidates | Where-Object { $_ -and (Test-Path -LiteralPath $_) } | Select-Object -First 1
if (-not $pythonPath) { throw 'Set CHONOI_PYTHON to a Python 3 executable, then retry.' }
$oldPath = $env:PATH
$oldPythonPath = $env:PYTHONPATH
$oldUtf8 = $env:PYTHONUTF8
Push-Location $repoRoot
try {
    $env:PATH = (Split-Path -Parent $pythonPath) + ';' + $env:PATH
    $env:PYTHONPATH = 'tests;.'
    $env:PYTHONUTF8 = '1'
    if ($Action -eq 'play') {
        & $pythonPath -m chonoi.live --mode gather --seed $Seed --port $Port
    } else {
        # Phase 4: QA fixed the old TEAM fixture; run the whole suite.
        & $pythonPath -m unittest discover -s tests -v
    }
    $runExitCode = $LASTEXITCODE
} finally {
    Pop-Location
    $env:PATH = $oldPath
    $env:PYTHONPATH = $oldPythonPath
    $env:PYTHONUTF8 = $oldUtf8
}
exit $runExitCode
