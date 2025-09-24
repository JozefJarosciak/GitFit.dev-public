@echo off
echo Creating GitFit.dev v1.0.0 Release...

if "%GITHUB_TOKEN%"=="" (
    echo ERROR: GITHUB_TOKEN environment variable not set
    echo Please set it with: set GITHUB_TOKEN=your_token_here
    pause
    exit /b 1
)

echo Testing GitHub API access...
curl -s -H "Authorization: token %GITHUB_TOKEN%" ^
     -H "Accept: application/vnd.github.v3+json" ^
     https://api.github.com/user > temp_user.json

if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to access GitHub API
    del temp_user.json 2>nul
    pause
    exit /b 1
)

echo GitHub API access successful!
del temp_user.json 2>nul

echo Creating release v1.0.0...

curl -X POST ^
  -H "Authorization: token %GITHUB_TOKEN%" ^
  -H "Accept: application/vnd.github.v3+json" ^
  -H "Content-Type: application/json" ^
  -d @release_data.json ^
  https://api.github.com/repos/JozefJarosciak/GitFit.dev-public/releases

if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to create release
    pause
    exit /b 1
)

echo.
echo ✅ GitFit.dev v1.0.0 release created successfully!
echo.
echo Next steps:
echo 1. Download build artifacts from: https://github.com/JozefJarosciak/GitFit.dev-public/actions
echo 2. Upload artifacts to: https://github.com/JozefJarosciak/GitFit.dev-public/releases/tag/v1.0.0
echo 3. Visit your release: https://github.com/JozefJarosciak/GitFit.dev-public/releases/tag/v1.0.0
echo.
pause