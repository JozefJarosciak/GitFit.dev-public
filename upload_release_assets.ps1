# PowerShell script to download GitHub Actions artifacts and upload to release
param(
    [string]$GitHubToken = $env:GITHUB_TOKEN
)

# Configuration
$RepoOwner = "JozefJarosciak"
$RepoName = "GitFit.dev-public"
$ReleaseId = "249724020"
$ActionsRunId = "17975326073"

# Check if GitHub token is available
if ([string]::IsNullOrEmpty($GitHubToken)) {
    Write-Host "ERROR: GitHub token not found" -ForegroundColor Red
    Write-Host "Please set GITHUB_TOKEN environment variable or pass as parameter" -ForegroundColor Yellow
    exit 1
}

Write-Host "🚀 GitFit.dev v1.0.0 Asset Upload Script" -ForegroundColor Green
Write-Host "=" * 50

# Setup headers for GitHub API
$Headers = @{
    "Authorization" = "token $GitHubToken"
    "Accept" = "application/vnd.github.v3+json"
    "User-Agent" = "GitFit.dev-Release-Script"
}

# Function to download and extract artifact
function Download-Artifact {
    param($ArtifactName, $OutputFileName)

    Write-Host "📥 Downloading artifact: $ArtifactName" -ForegroundColor Cyan

    try {
        # Get artifacts list from the Actions run
        $ActionsUrl = "https://api.github.com/repos/$RepoOwner/$RepoName/actions/runs/$ActionsRunId/artifacts"
        $ArtifactsResponse = Invoke-RestMethod -Uri $ActionsUrl -Headers $Headers

        # Find the specific artifact
        $Artifact = $ArtifactsResponse.artifacts | Where-Object { $_.name -eq $ArtifactName }

        if (-not $Artifact) {
            Write-Host "❌ Artifact '$ArtifactName' not found" -ForegroundColor Red
            return $false
        }

        # Download artifact ZIP
        $DownloadUrl = $Artifact.archive_download_url
        $ZipFile = "$ArtifactName.zip"

        Write-Host "   Downloading from: $DownloadUrl"
        Invoke-WebRequest -Uri $DownloadUrl -Headers $Headers -OutFile $ZipFile

        # Extract the ZIP file
        Write-Host "   Extracting artifact..." -ForegroundColor Yellow
        if (Test-Path $ZipFile) {
            Expand-Archive -Path $ZipFile -DestinationPath "temp_$ArtifactName" -Force

            # Find the executable or zip file inside
            $ExtractedFiles = Get-ChildItem "temp_$ArtifactName" -Recurse

            if ($ArtifactName -like "*portable*") {
                # Look for .exe file
                $ExeFile = $ExtractedFiles | Where-Object { $_.Extension -eq ".exe" } | Select-Object -First 1
                if ($ExeFile) {
                    Copy-Item $ExeFile.FullName -Destination $OutputFileName
                    Write-Host "   ✅ Extracted: $($ExeFile.Name) -> $OutputFileName" -ForegroundColor Green
                }
            } else {
                # Look for .zip file
                $ZipFile = $ExtractedFiles | Where-Object { $_.Extension -eq ".zip" } | Select-Object -First 1
                if ($ZipFile) {
                    Copy-Item $ZipFile.FullName -Destination $OutputFileName
                    Write-Host "   ✅ Extracted: $($ZipFile.Name) -> $OutputFileName" -ForegroundColor Green
                }
            }

            # Cleanup
            Remove-Item "temp_$ArtifactName" -Recurse -Force
            Remove-Item "$ArtifactName.zip" -Force

            return (Test-Path $OutputFileName)
        }

        return $false

    } catch {
        Write-Host "❌ Error downloading artifact: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Function to upload asset to release
function Upload-Asset {
    param($FilePath, $AssetName, $ContentType, $Label)

    if (-not (Test-Path $FilePath)) {
        Write-Host "❌ File not found: $FilePath" -ForegroundColor Red
        return $false
    }

    Write-Host "📤 Uploading: $AssetName" -ForegroundColor Cyan

    try {
        $UploadUrl = "https://uploads.github.com/repos/$RepoOwner/$RepoName/releases/$ReleaseId/assets"
        $UploadHeaders = @{
            "Authorization" = "token $GitHubToken"
            "Content-Type" = $ContentType
        }

        # Get file content as bytes
        $FileBytes = [System.IO.File]::ReadAllBytes($FilePath)
        $FileSize = $FileBytes.Length
        $FileSizeMB = [math]::Round($FileSize / 1MB, 2)

        Write-Host "   File size: $FileSizeMB MB" -ForegroundColor Yellow
        Write-Host "   Uploading to GitHub..." -ForegroundColor Yellow

        $Response = Invoke-RestMethod -Uri "$UploadUrl?name=$AssetName&label=$Label" -Method POST -Headers $UploadHeaders -Body $FileBytes

        Write-Host "   ✅ Upload successful!" -ForegroundColor Green
        Write-Host "   📁 Asset URL: $($Response.browser_download_url)" -ForegroundColor Blue

        return $true

    } catch {
        Write-Host "❌ Upload failed: $($_.Exception.Message)" -ForegroundColor Red
        if ($_.Exception.Response) {
            $ErrorBody = $_.Exception.Response.GetResponseStream()
            $Reader = New-Object System.IO.StreamReader($ErrorBody)
            $ErrorText = $Reader.ReadToEnd()
            Write-Host "   Error details: $ErrorText" -ForegroundColor Red
        }
        return $false
    }
}

# Main execution
Write-Host "🔍 Starting artifact download and upload process..." -ForegroundColor Yellow

# Download portable executable
$PortableSuccess = Download-Artifact -ArtifactName "GitFitDev-52fabb5729d462b6e0c026653001f6a727f98e-portable" -OutputFileName "GitFitDev-v1.0.0-Windows-Portable.exe"

# Download ZIP package
$ZipSuccess = Download-Artifact -ArtifactName "GitFitDev-52fabb5729d462b6e0c026653001f6a727f98e-zip" -OutputFileName "GitFitDev-v1.0.0-Windows.zip"

if (-not $PortableSuccess) {
    Write-Host "❌ Failed to download portable executable" -ForegroundColor Red
    exit 1
}

if (-not $ZipSuccess) {
    Write-Host "❌ Failed to download ZIP package" -ForegroundColor Red
    exit 1
}

Write-Host "`n📤 Uploading assets to release..." -ForegroundColor Yellow

# Upload portable executable
$PortableUpload = Upload-Asset -FilePath "GitFitDev-v1.0.0-Windows-Portable.exe" -AssetName "GitFitDev-v1.0.0-Windows-Portable.exe" -ContentType "application/octet-stream" -Label "Windows Portable Executable (No Installation Required)"

# Upload ZIP package
$ZipUpload = Upload-Asset -FilePath "GitFitDev-v1.0.0-Windows.zip" -AssetName "GitFitDev-v1.0.0-Windows.zip" -ContentType "application/zip" -Label "Windows ZIP Package"

# Summary
Write-Host "`n" + "=" * 50
if ($PortableUpload -and $ZipUpload) {
    Write-Host "🎉 SUCCESS! All assets uploaded to GitFit.dev v1.0.0" -ForegroundColor Green
    Write-Host "🔗 Release URL: https://github.com/$RepoOwner/$RepoName/releases/tag/v1.0.0" -ForegroundColor Blue
    Write-Host "🌐 Website downloads should now work: https://gitfit.dev" -ForegroundColor Blue

    # Cleanup downloaded files
    if (Test-Path "GitFitDev-v1.0.0-Windows-Portable.exe") { Remove-Item "GitFitDev-v1.0.0-Windows-Portable.exe" }
    if (Test-Path "GitFitDev-v1.0.0-Windows.zip") { Remove-Item "GitFitDev-v1.0.0-Windows.zip" }

    Write-Host "`n✅ GitFit.dev v1.0.0 release is now complete and ready for users!" -ForegroundColor Green
} else {
    Write-Host "❌ Some uploads failed. Check the errors above." -ForegroundColor Red
    exit 1
}

Write-Host "`nPress any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")