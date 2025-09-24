@echo off
echo Uploading assets to GitFit.dev v1.0.0 release...

if "%GITHUB_TOKEN%"=="" (
    echo ERROR: GITHUB_TOKEN environment variable not set
    pause
    exit /b 1
)

set RELEASE_ID=249724020
set UPLOAD_URL=https://uploads.github.com/repos/JozefJarosciak/GitFit.dev-public/releases/%RELEASE_ID%/assets

echo.
echo Please ensure you have downloaded and renamed the files:
echo - GitFitDev-v1.0.0-Windows-Portable.exe
echo - GitFitDev-v1.0.0-Windows.zip
echo.
echo Files should be in the current directory.
echo.
pause

if not exist "GitFitDev-v1.0.0-Windows-Portable.exe" (
    echo ERROR: GitFitDev-v1.0.0-Windows-Portable.exe not found
    echo Please download and rename the portable executable first
    pause
    exit /b 1
)

if not exist "GitFitDev-v1.0.0-Windows.zip" (
    echo ERROR: GitFitDev-v1.0.0-Windows.zip not found
    echo Please download and rename the ZIP package first
    pause
    exit /b 1
)

echo Uploading portable executable...
curl -X POST ^
  -H "Authorization: token %GITHUB_TOKEN%" ^
  -H "Content-Type: application/octet-stream" ^
  --data-binary @GitFitDev-v1.0.0-Windows-Portable.exe ^
  "%UPLOAD_URL%?name=GitFitDev-v1.0.0-Windows-Portable.exe&label=Windows Portable Executable"

echo.
echo Uploading ZIP package...
curl -X POST ^
  -H "Authorization: token %GITHUB_TOKEN%" ^
  -H "Content-Type: application/zip" ^
  --data-binary @GitFitDev-v1.0.0-Windows.zip ^
  "%UPLOAD_URL%?name=GitFitDev-v1.0.0-Windows.zip&label=Windows ZIP Package"

echo.
echo ✅ Assets uploaded successfully!
echo Visit: https://github.com/JozefJarosciak/GitFit.dev-public/releases/tag/v1.0.0
echo.
pause