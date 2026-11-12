param([Parameter(ValueFromRemainingArguments = $true)][string[]]$ExperimentArgs)
$ErrorActionPreference = 'Stop'
$pythonCommand = Get-Command python -ErrorAction SilentlyContinue
$bundledPython = Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
if ($pythonCommand) {
    $executable = $pythonCommand.Source
} elseif (Test-Path -LiteralPath $bundledPython) {
    $executable = $bundledPython
} else {
    throw 'Python 3.10+ is required. Install Python and run this script again.'
}
& $executable (Join-Path $PSScriptRoot 'experiment.py') @ExperimentArgs
exit $LASTEXITCODE
