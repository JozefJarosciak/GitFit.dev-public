# Simple PowerShell script to upload GitHub release assets
$GitHubToken = $env:GITHUB_TOKEN
$RepoOwner = "JozefJarosciak"
$RepoName = "GitFit.dev-public"
$ReleaseId = "249724020"

if ([string]::IsNullOrEmpty($GitHubToken)) {
    Write-Host "ERROR: GitHub token not found. Please set GITHUB_TOKEN environment variable." -ForegroundColor Red
    exit 1
}

Write-Host "GitFit.dev v1.0.0 Asset Upload Script" -ForegroundColor Green
Write-Host "======================================"

# Check if files exist
$PortableFile = "GitFitDev-v1.0.0-Windows-Portable.exe"
$ZipFile = "GitFitDev-v1.0.0-Windows.zip"

if (-not (Test-Path $PortableFile)) {
    Write-Host "Missing: $PortableFile" -ForegroundColor Red
    Write-Host "Please download and place the portable executable in this directory." -ForegroundColor Yellow
    Write-Host "Download from: https://github.com/$RepoOwner/$RepoName/actions/runs/17975326073" -ForegroundColor Blue
    exit 1
}

if (-not (Test-Path $ZipFile)) {
    Write-Host "Missing: $ZipFile" -ForegroundColor Red
    Write-Host "Please download and place the ZIP package in this directory." -ForegroundColor Yellow
    Write-Host "Download from: https://github.com/$RepoOwner/$RepoName/actions/runs/17975326073" -ForegroundColor Blue
    exit 1
}

# Upload function
function Upload-Asset($FilePath, $AssetName, $ContentType, $Label) {
    Write-Host "Uploading: $AssetName" -ForegroundColor Cyan

    $UploadUrl = "https://uploads.github.com/repos/$RepoOwner/$RepoName/releases/$ReleaseId/assets"
    $Headers = @{
        "Authorization" = "token $GitHubToken"
        "Content-Type" = $ContentType
    }

    try {
        $FileBytes = [System.IO.File]::ReadAllBytes($FilePath)
        $FileSizeMB = [math]::Round($FileBytes.Length / 1MB, 2)
        Write-Host "  File size: $FileSizeMB MB" -ForegroundColor Yellow

        $Response = Invoke-RestMethod -Uri "$UploadUrl?name=$AssetName&label=$Label" -Method POST -Headers $Headers -Body $FileBytes

        Write-Host "  SUCCESS! Asset uploaded." -ForegroundColor Green
        Write-Host "  Download URL: $($Response.browser_download_url)" -ForegroundColor Blue
        return $true
    }
    catch {
        Write-Host "  FAILED: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Upload assets
Write-Host "`nUploading assets to GitHub release..." -ForegroundColor Yellow

$Success1 = Upload-Asset -FilePath $PortableFile -AssetName $PortableFile -ContentType "application/octet-stream" -Label "Windows Portable Executable"
$Success2 = Upload-Asset -FilePath $ZipFile -AssetName $ZipFile -ContentType "application/zip" -Label "Windows ZIP Package"

Write-Host "`n======================================"
if ($Success1 -and $Success2) {
    Write-Host "SUCCESS! All assets uploaded to GitFit.dev v1.0.0" -ForegroundColor Green
    Write-Host "Release URL: https://github.com/$RepoOwner/$RepoName/releases/tag/v1.0.0" -ForegroundColor Blue
    Write-Host "Website: https://gitfit.dev" -ForegroundColor Blue
} else {
    Write-Host "Some uploads failed. Check the errors above." -ForegroundColor Red
}

Write-Host "`nPress any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")