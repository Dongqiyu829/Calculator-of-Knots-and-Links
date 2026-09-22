[CmdletBinding()]
param(
    [string]$Python = "python",
    [switch]$SkipTests,
    [switch]$SkipInstaller
)

$ErrorActionPreference = "Stop"
$env:PYTHONNOUSERSITE = "1"
$RepositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$DistRoot = Join-Path $RepositoryRoot "dist"
$FrozenDirectory = Join-Path $DistRoot "Calculator-of-Knots-and-Links"
$FrozenExecutable = Join-Path $FrozenDirectory "Calculator-of-Knots-and-Links.exe"
$ArtifactRoot = Join-Path $RepositoryRoot "artifacts"
$PortableZip = Join-Path $ArtifactRoot "Calculator-of-Knots-and-Links-Windows-x64-Portable.zip"
$InstallerOutput = Join-Path $ArtifactRoot "Calculator-of-Knots-and-Links-Windows-x64-Setup.exe"
$ChecksumOutput = Join-Path $ArtifactRoot "SHA256SUMS.txt"

New-Item -ItemType Directory -Force -Path $ArtifactRoot | Out-Null
foreach ($StaleArtifact in @($PortableZip, $InstallerOutput, $ChecksumOutput)) {
    if (Test-Path -LiteralPath $StaleArtifact) { Remove-Item -LiteralPath $StaleArtifact -Force }
}

$Version = (& $Python -c "from src.version import __version__; print(__version__)").Trim()
if ($LASTEXITCODE -ne 0 -or $Version -notmatch '^\d+\.\d+\.\d+$') {
    throw "Could not read a valid maintained application version."
}

if (-not $SkipTests) {
    & $Python -m pytest -q -m "not slow and not gui"
    if ($LASTEXITCODE -ne 0) { throw "Fast regression tests failed." }
}

& $Python -s -m PyInstaller --clean --noconfirm (Join-Path $RepositoryRoot "packaging\Calculator-of-Knots-and-Links.spec")
if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $FrozenExecutable)) {
    throw "PyInstaller build failed."
}

& $FrozenExecutable --smoke-test
if ($LASTEXITCODE -ne 0) { throw "Packaged application smoke test failed." }
& $FrozenExecutable --version
if ($LASTEXITCODE -ne 0) { throw "Packaged application version check failed." }

Compress-Archive -Path $FrozenDirectory -DestinationPath $PortableZip -Force
$TempRoot = if ($env:RUNNER_TEMP) { $env:RUNNER_TEMP } else { [IO.Path]::GetTempPath() }
$PortableSmokeRoot = Join-Path $TempRoot "calculator-of-knots-and-links-portable-smoke"
if (Test-Path -LiteralPath $PortableSmokeRoot) { Remove-Item -LiteralPath $PortableSmokeRoot -Recurse -Force }
Expand-Archive -LiteralPath $PortableZip -DestinationPath $PortableSmokeRoot
$PortableExecutable = Join-Path $PortableSmokeRoot "Calculator-of-Knots-and-Links\Calculator-of-Knots-and-Links.exe"
if (-not (Test-Path -LiteralPath $PortableExecutable)) { throw "Portable ZIP did not contain the expected executable." }
& $PortableExecutable --smoke-test
if ($LASTEXITCODE -ne 0) { throw "Extracted portable application smoke test failed." }
& $PortableExecutable --version
if ($LASTEXITCODE -ne 0) { throw "Extracted portable application version check failed." }

if (-not $SkipInstaller) {
    $IsccCandidates = @(
        (Get-Command ISCC.exe -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source -ErrorAction SilentlyContinue),
        (Join-Path ${env:ProgramFiles(x86)} "Inno Setup 6\ISCC.exe"),
        (Join-Path $env:ProgramFiles "Inno Setup 6\ISCC.exe")
    ) | Where-Object { $_ -and (Test-Path -LiteralPath $_) }
    $Iscc = $IsccCandidates | Select-Object -First 1
    if (-not $Iscc) { throw "Inno Setup 6 compiler (ISCC.exe) was not found." }

    $InstallerScript = Join-Path $PSScriptRoot "installer.iss"
    & $Iscc "/DMyAppVersion=$Version" "/DMyAppSource=$FrozenDirectory" "/DMyOutputDir=$ArtifactRoot" $InstallerScript
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $InstallerOutput)) {
        throw "Inno Setup build failed."
    }

}

$ChecksumTargets = @($PortableZip)
if (Test-Path -LiteralPath $InstallerOutput) { $ChecksumTargets += $InstallerOutput }
$ChecksumLines = foreach ($Path in $ChecksumTargets) {
    $Hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToLowerInvariant()
    "$Hash  $([IO.Path]::GetFileName($Path))"
}
$ChecksumLines | Set-Content -LiteralPath $ChecksumOutput -Encoding ascii

foreach ($Required in @($PortableZip, $ChecksumOutput)) {
    if (-not (Test-Path -LiteralPath $Required)) { throw "Missing expected artifact: $Required" }
}
if (-not $SkipInstaller -and -not (Test-Path -LiteralPath $InstallerOutput)) {
    throw "Missing expected installer artifact: $InstallerOutput"
}

Write-Host "Version: $Version"
Write-Host "Portable archive: $PortableZip"
if (Test-Path -LiteralPath $InstallerOutput) { Write-Host "Installer: $InstallerOutput" }
Write-Host "Checksums: $ChecksumOutput"
