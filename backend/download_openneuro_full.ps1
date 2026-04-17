param(
    [string]$Dataset = "ds004504",
    [string]$Version = "1.0.8",
    [string]$TargetDir = ""
)

$ErrorActionPreference = "Stop"

function Require-Command {
    param([string]$Name)
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Required command not found: $Name"
    }
}

Require-Command git
if ([string]::IsNullOrWhiteSpace($TargetDir)) {
    $TargetDir = "${Dataset}_annex"
}

if (-not (Get-Command git-annex -ErrorAction SilentlyContinue)) {
    throw "git-annex is required to download EEG annex files. Install from https://downloads.kitenet.net/git-annex/windows/current/git-annex-installer.exe"
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoDir = Join-Path $scriptDir $TargetDir
$repoUrl = "https://github.com/OpenNeuroDatasets/$Dataset.git"

if (-not (Test-Path $repoDir)) {
    Write-Host "Cloning $repoUrl ..."
    git clone $repoUrl $repoDir
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to clone dataset repository"
    }
}

if (-not (Test-Path (Join-Path $repoDir ".git"))) {
    throw "Target directory exists but is not a git repository: $repoDir"
}

Push-Location $repoDir
try {
    $originUrl = git remote get-url origin
    if ($LASTEXITCODE -ne 0) {
        throw "Could not read git remote from $repoDir"
    }

    if ($originUrl -notmatch "OpenNeuroDatasets/$Dataset(\.git)?$") {
        throw "Repository origin does not match OpenNeuro dataset repo. Found: $originUrl"
    }

    Write-Host "Fetching tags ..."
    git fetch --tags
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to fetch dataset tags"
    }

    Write-Host "Checking out snapshot $Version ..."
    git checkout $Version
    if ($LASTEXITCODE -ne 0) {
        throw "Could not checkout snapshot tag $Version"
    }

    Write-Host "Enabling OpenNeuro public S3 remote ..."
    git-annex enableremote s3-PUBLIC
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to enable s3-PUBLIC annex remote"
    }

    Write-Host "Downloading annexed EEG files (this can take a while) ..."
    git-annex get .
    if ($LASTEXITCODE -ne 0) {
        throw "Failed while downloading annexed files"
    }

    Write-Host "Done. Dataset is at: $repoDir"
} finally {
    Pop-Location
}
