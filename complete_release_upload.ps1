# Complete GitFit.dev v1.0.0 Release Asset Script
# Downloads artifacts from GitHub Actions and uploads to release
param(
    [string]$GitHubToken = $env:GITHUB_TOKEN
)

# Configuration
$RepoOwner = "JozefJarosciak"
$RepoName = "GitFit.dev-public"
$ReleaseId = "249724020"
$ActionsRunId = "17975326073"

# Check GitHub token
if ([string]::IsNullOrEmpty($GitHubToken)) {
    Write-Host "ERROR: GitHub token not found" -ForegroundColor Red
    Write-Host "Please set GITHUB_TOKEN environment variable" -ForegroundColor Yellow
    exit 1
}

Write-Host "🚀 GitFit.dev v1.0.0 Complete Release Script" -ForegroundColor Green
Write-Host "=============================================="
Write-Host "This script will:"
Write-Host "1. Download build artifacts from GitHub Actions"
Write-Host "2. Extract and prepare release files"
Write-Host "3. Upload assets to GitHub release"
Write-Host ""

# API Headers
$Headers = @{
    "Authorization" = "token $GitHubToken"
    "Accept" = "application/vnd.github.v3+json"
    "User-Agent" = "GitFit.dev-Release-Script"
}

# Step 1: Get artifacts from Actions run
Write-Host "📥 Step 1: Downloading GitHub Actions artifacts..." -ForegroundColor Cyan

try {
    $ActionsUrl = "https://api.github.com/repos/$RepoOwner/$RepoName/actions/runs/$ActionsRunId/artifacts"
    Write-Host "   Fetching artifacts list..." -ForegroundColor Yellow
    $ArtifactsResponse = Invoke-RestMethod -Uri $ActionsUrl -Headers $Headers

    Write-Host "   Found $($ArtifactsResponse.artifacts.Count) artifacts" -ForegroundColor Green

    # Find our specific artifacts
    $PortableArtifact = $ArtifactsResponse.artifacts | Where-Object { $_.name -like "*portable*" }
    $ZipArtifact = $ArtifactsResponse.artifacts | Where-Object { $_.name -like "*zip*" }

    if (-not $PortableArtifact) {
        Write-Host "   ERROR: Portable artifact not found" -ForegroundColor Red
        exit 1
    }

    if (-not $ZipArtifact) {
        Write-Host "   ERROR: ZIP artifact not found" -ForegroundColor Red
        exit 1
    }

    Write-Host "   ✅ Found portable artifact: $($PortableArtifact.name)" -ForegroundColor Green
    Write-Host "   ✅ Found ZIP artifact: $($ZipArtifact.name)" -ForegroundColor Green

} catch {
    Write-Host "   ERROR: Failed to get artifacts list: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 2: Download and extract portable executable
Write-Host "`n📦 Step 2: Processing portable executable..." -ForegroundColor Cyan

try {
    Write-Host "   Downloading portable artifact..." -ForegroundColor Yellow
    $PortableZip = "portable_artifact.zip"
    Invoke-WebRequest -Uri $PortableArtifact.archive_download_url -Headers $Headers -OutFile $PortableZip

    Write-Host "   Extracting portable artifact..." -ForegroundColor Yellow
    Expand-Archive -Path $PortableZip -DestinationPath "temp_portable" -Force

    # Find the .exe file
    $ExeFile = Get-ChildItem "temp_portable" -Recurse -Filter "*.exe" | Select-Object -First 1

    if ($ExeFile) {
        $FinalPortableName = "GitFitDev-v1.0.0-Windows-Portable.exe"
        Copy-Item $ExeFile.FullName -Destination $FinalPortableName
        Write-Host "   ✅ Created: $FinalPortableName ($([math]::Round($ExeFile.Length / 1MB, 2)) MB)" -ForegroundColor Green

        # Cleanup
        Remove-Item $PortableZip -Force
        Remove-Item "temp_portable" -Recurse -Force
    } else {
        Write-Host "   ERROR: No .exe file found in portable artifact" -ForegroundColor Red
        exit 1
    }

} catch {
    Write-Host "   ERROR: Failed to process portable executable: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 3: Download and extract ZIP package
Write-Host "`n📦 Step 3: Processing ZIP package..." -ForegroundColor Cyan

try {
    Write-Host "   Downloading ZIP artifact..." -ForegroundColor Yellow
    $ZipArtifactFile = "zip_artifact.zip"
    Invoke-WebRequest -Uri $ZipArtifact.archive_download_url -Headers $Headers -OutFile $ZipArtifactFile

    Write-Host "   Extracting ZIP artifact..." -ForegroundColor Yellow
    Expand-Archive -Path $ZipArtifactFile -DestinationPath "temp_zip" -Force

    # Find the .zip file inside
    $InnerZipFile = Get-ChildItem "temp_zip" -Recurse -Filter "*.zip" | Select-Object -First 1

    if ($InnerZipFile) {
        $FinalZipName = "GitFitDev-v1.0.0-Windows.zip"
        Copy-Item $InnerZipFile.FullName -Destination $FinalZipName
        Write-Host "   ✅ Created: $FinalZipName ($([math]::Round($InnerZipFile.Length / 1MB, 2)) MB)" -ForegroundColor Green

        # Cleanup
        Remove-Item $ZipArtifactFile -Force
        Remove-Item "temp_zip" -Recurse -Force
    } else {
        Write-Host "   ERROR: No .zip file found in ZIP artifact" -ForegroundColor Red
        exit 1
    }

} catch {
    Write-Host "   ERROR: Failed to process ZIP package: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 4: Upload assets to release
Write-Host "`n🚀 Step 4: Uploading assets to GitHub release..." -ForegroundColor Cyan

$UploadUrl = "https://uploads.github.com/repos/$RepoOwner/$RepoName/releases/$ReleaseId/assets"
$UploadHeaders = @{
    "Authorization" = "token $GitHubToken"
}

# Upload portable executable
try {
    Write-Host "   Uploading portable executable..." -ForegroundColor Yellow
    $PortableBytes = [System.IO.File]::ReadAllBytes($FinalPortableName)
    $PortableSizeMB = [math]::Round($PortableBytes.Length / 1MB, 2)

    $UploadHeaders["Content-Type"] = "application/octet-stream"
    $Response1 = Invoke-RestMethod -Uri "$UploadUrl?name=$FinalPortableName&label=Windows+Portable+Executable+(No+Installation+Required)" -Method POST -Headers $UploadHeaders -Body $PortableBytes

    Write-Host "   ✅ Portable executable uploaded successfully! ($PortableSizeMB MB)" -ForegroundColor Green
    Write-Host "      Download: $($Response1.browser_download_url)" -ForegroundColor Blue

} catch {
    Write-Host "   ERROR: Failed to upload portable executable: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $ErrorStream = $_.Exception.Response.GetResponseStream()
        $Reader = New-Object System.IO.StreamReader($ErrorStream)
        $ErrorBody = $Reader.ReadToEnd()
        Write-Host "   Details: $ErrorBody" -ForegroundColor Red
    }
    exit 1
}

# Upload ZIP package
try {
    Write-Host "   Uploading ZIP package..." -ForegroundColor Yellow
    $ZipBytes = [System.IO.File]::ReadAllBytes($FinalZipName)
    $ZipSizeMB = [math]::Round($ZipBytes.Length / 1MB, 2)

    $UploadHeaders["Content-Type"] = "application/zip"
    $Response2 = Invoke-RestMethod -Uri "$UploadUrl?name=$FinalZipName&label=Windows+ZIP+Package" -Method POST -Headers $UploadHeaders -Body $ZipBytes

    Write-Host "   ✅ ZIP package uploaded successfully! ($ZipSizeMB MB)" -ForegroundColor Green
    Write-Host "      Download: $($Response2.browser_download_url)" -ForegroundColor Blue

} catch {
    Write-Host "   ERROR: Failed to upload ZIP package: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $ErrorStream = $_.Exception.Response.GetResponseStream()
        $Reader = New-Object System.IO.StreamReader($ErrorStream)
        $ErrorBody = $Reader.ReadToEnd()
        Write-Host "   Details: $ErrorBody" -ForegroundColor Red
    }
    exit 1
}

# Step 5: Cleanup and summary
Write-Host "`n🧹 Step 5: Cleaning up temporary files..." -ForegroundColor Cyan
if (Test-Path $FinalPortableName) { Remove-Item $FinalPortableName -Force }
if (Test-Path $FinalZipName) { Remove-Item $FinalZipName -Force }
Write-Host "   ✅ Temporary files cleaned up" -ForegroundColor Green

# Final success message
Write-Host "`n" + "=" * 50
Write-Host "🎉 SUCCESS! GitFit.dev v1.0.0 Release Complete!" -ForegroundColor Green
Write-Host "=" * 50
Write-Host "✅ Portable executable uploaded ($PortableSizeMB MB)"
Write-Host "✅ ZIP package uploaded ($ZipSizeMB MB)"
Write-Host ""
Write-Host "🔗 Release URL: https://github.com/$RepoOwner/$RepoName/releases/tag/v1.0.0" -ForegroundColor Blue
Write-Host "🌐 Website: https://gitfit.dev" -ForegroundColor Blue
Write-Host ""
Write-Host "The release now has downloadable assets and the website downloads should work!" -ForegroundColor Green
Write-Host ""
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")