$ErrorActionPreference = 'Stop'
$editorUrl = 'http://127.0.0.1:8765/'
try {
    $editorResponse = Invoke-WebRequest -Uri $editorUrl -UseBasicParsing -TimeoutSec 2
    if ($editorResponse.Content -notmatch 'Kaisetsu Video Studio') { throw 'Port 8765 is used by another application.' }
    Write-Output $editorUrl
    exit 0
} catch {
    if ($_.Exception.Message -eq 'Port 8765 is used by another application.') { throw }
}
$editorPython = (Get-Command python -ErrorAction Stop).Source
$editorScript = Join-Path $PSScriptRoot 'editor/server.py'
$editorStore = Join-Path $PSScriptRoot 'editor/workspace'
New-Item -ItemType Directory -Path $editorStore -Force | Out-Null
$editorProcess = Start-Process -FilePath $editorPython -ArgumentList @('"' + $editorScript + '"') -WorkingDirectory $PSScriptRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $editorStore 'server.log') -RedirectStandardError (Join-Path $editorStore 'server-error.log')
for ($editorAttempt = 0; $editorAttempt -lt 20; $editorAttempt++) {
    Start-Sleep -Milliseconds 250
    if ($editorProcess.HasExited) { throw 'Editor failed to start. See editor/workspace/server-error.log.' }
    try {
        $editorResponse = Invoke-WebRequest -Uri $editorUrl -UseBasicParsing -TimeoutSec 1
        if ($editorResponse.StatusCode -eq 200) {
            Write-Output $editorUrl
            Write-Output "Stop server: Stop-Process -Id $($editorProcess.Id)"
            exit 0
        }
    } catch { }
}
throw 'Editor did not respond. See editor/workspace/server-error.log.'
