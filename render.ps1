param([string]$ScriptFile = 'demo.json')
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$env:PYTHONIOENCODING = 'utf-8'
try { Invoke-RestMethod 'http://localhost:50021/version' -TimeoutSec 3 | Out-Null }
catch {
    $vvPackage = Get-ItemProperty 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*' | Where-Object { $_.DisplayName -eq 'VOICEVOX' } | Select-Object -First 1
    if (-not $vvPackage) { throw 'VOICEVOXを起動してから再実行してください。' }
    $vvBinary = Get-ChildItem -LiteralPath $vvPackage.InstallLocation -Filter run.exe -Recurse | Where-Object { $_.FullName -match 'vv-engine' } | Select-Object -First 1
    if (-not $vvBinary) { throw 'VOICEVOXを起動してから再実行してください。' }
    New-Item -ItemType Directory -Force output | Out-Null
    Start-Process -FilePath $vvBinary.FullName -WorkingDirectory $vvBinary.DirectoryName -WindowStyle Hidden -RedirectStandardOutput "$PSScriptRoot\output\engine.log" -RedirectStandardError "$PSScriptRoot\output\engine-error.log"
    $vvReady = $false
    for ($attempt = 0; $attempt -lt 60; $attempt++) {
        try { Invoke-RestMethod 'http://localhost:50021/version' -TimeoutSec 2 | Out-Null; $vvReady = $true; break }
        catch { Start-Sleep -Seconds 1 }
    }
    if (-not $vvReady) { throw 'VOICEVOXの起動が完了しませんでした。output/engine-error.logを確認してください。' }
}
python studio.py $ScriptFile
if ($LASTEXITCODE -ne 0) { throw '動画の生成に失敗しました。上のエラーを確認してください。' }
