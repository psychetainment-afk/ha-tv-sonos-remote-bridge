param(
    [Parameter(Mandatory=$true)][string]$JdkPath,
    [Parameter(Mandatory=$true)][string]$AndroidJar,
    [Parameter(Mandatory=$true)][string]$BuildToolsPath,
    [Parameter(Mandatory=$true)][string]$KeyStorePath,
    [string]$KeyAlias='tvbridge'
)
$ErrorActionPreference='Stop'
if (-not $env:TVBRIDGE_KEYSTORE_PASSWORD) { throw 'Set TVBRIDGE_KEYSTORE_PASSWORD in the process environment; never store it in Git.' }
$root=Split-Path $PSScriptRoot -Parent
$source=Join-Path $root 'android\app\src\main'
foreach ($required in @($JdkPath,$AndroidJar,$BuildToolsPath,$KeyStorePath)) {
    if (-not (Test-Path -LiteralPath $required)) { throw 'A required tool or private keystore path does not exist.' }
}
$JdkPath=(Resolve-Path -LiteralPath $JdkPath).Path
$AndroidJar=(Resolve-Path -LiteralPath $AndroidJar).Path
$BuildToolsPath=(Resolve-Path -LiteralPath $BuildToolsPath).Path
$KeyStorePath=(Resolve-Path -LiteralPath $KeyStorePath).Path
$buildId=[DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfff')+'-'+[guid]::NewGuid().ToString('N').Substring(0,8)
$build=Join-Path $root ('build\'+$buildId)
$dist=Join-Path $root 'dist'
New-Item -ItemType Directory -Force -Path "$build\classes","$build\dex",$dist | Out-Null
[xml]$manifest=Get-Content -LiteralPath "$source\AndroidManifest.xml" -Raw
$version=$manifest.manifest.GetAttribute('versionName','http://schemas.android.com/apk/res/android')
if ($version -notmatch '^\d+(\.\d+)*$') { throw 'Unexpected app version in manifest.' }
$output=Join-Path $dist ('tv-sonos-remote-bridge-'+$version+'.apk')
$previousJavaHome=$env:JAVA_HOME
try {
    $env:JAVA_HOME=$JdkPath
    & "$BuildToolsPath\aapt.exe" package -f -M "$source\AndroidManifest.xml" -S "$source\res" -I $AndroidJar -F "$build\base.apk"
    if ($LASTEXITCODE -ne 0) { throw 'aapt failed' }
    $sources=@(Get-ChildItem -LiteralPath "$source\java" -Recurse -Filter '*.java' | ForEach-Object FullName)
    & "$JdkPath\bin\javac.exe" -encoding UTF-8 --release 8 -classpath $AndroidJar -d "$build\classes" @sources
    if ($LASTEXITCODE -ne 0) { throw 'javac failed' }
    $classes=@(Get-ChildItem -LiteralPath "$build\classes" -Recurse -Filter '*.class' | ForEach-Object FullName)
    & "$BuildToolsPath\d8.bat" --min-api 26 --lib $AndroidJar --output "$build\dex" @classes
    if ($LASTEXITCODE -ne 0) { throw 'd8 failed' }
    Copy-Item -LiteralPath "$build\base.apk" -Destination "$build\unsigned.apk"
    Push-Location "$build\dex"
    try { & "$BuildToolsPath\aapt.exe" add "$build\unsigned.apk" classes.dex } finally { Pop-Location }
    if ($LASTEXITCODE -ne 0) { throw 'DEX packaging failed' }
    & "$BuildToolsPath\zipalign.exe" -f 4 "$build\unsigned.apk" "$build\aligned.apk"
    if ($LASTEXITCODE -ne 0) { throw 'zipalign failed' }
    & "$BuildToolsPath\apksigner.bat" sign --ks $KeyStorePath --ks-key-alias $KeyAlias --ks-pass env:TVBRIDGE_KEYSTORE_PASSWORD --out $output "$build\aligned.apk"
    if ($LASTEXITCODE -ne 0) { throw 'APK signing failed' }
    & "$BuildToolsPath\apksigner.bat" verify --verbose $output
    if ($LASTEXITCODE -ne 0) { throw 'APK signature verification failed' }
    Write-Output $output
} finally {
    if ($null -eq $previousJavaHome) { Remove-Item Env:JAVA_HOME -ErrorAction SilentlyContinue } else { $env:JAVA_HOME=$previousJavaHome }
}
