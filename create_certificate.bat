@echo off
setlocal enabledelayedexpansion

echo ===================================
echo GitFit.dev Certificate Creator
echo ===================================
echo.

REM Check if Windows SDK tools are available
where makecert >nul 2>&1
if errorlevel 1 (
    echo ERROR: makecert not found in PATH
    echo Please install Windows SDK and add tools to PATH
    echo Common locations:
    echo   - "C:\Program Files (x86)\Windows Kits\10\bin\x64"
    echo   - "C:\Program Files (x86)\Windows Kits\8.1\bin\x64"
    echo   - "C:\Program Files\Microsoft SDKs\Windows\v7.1\Bin"
    echo.
    echo You can also try running this from Visual Studio Developer Command Prompt
    echo.
    pause
    exit /b 1
)

where pvk2pfx >nul 2>&1
if errorlevel 1 (
    echo ERROR: pvk2pfx not found in PATH
    echo Please install Windows SDK and add tools to PATH
    pause
    exit /b 1
)

echo Windows SDK tools found. Creating self-signed certificate...
echo.

echo Step 1: Creating root certificate authority...
makecert -r -pe -n "CN=GitFit.dev" -ss CA -sr CurrentUser -a sha256 -cy authority -sky signature -sv GitFitDev.pvk GitFitDev.cer

if errorlevel 1 (
    echo ERROR: Failed to create root certificate
    pause
    exit /b 1
)

echo.
echo Step 2: Creating code signing certificate...
makecert -pe -n "CN=GitFit.dev" -a sha256 -cy end -sky signature -ic GitFitDev.cer -iv GitFitDev.pvk -sv GitFitDevSigning.pvk GitFitDevSigning.cer

if errorlevel 1 (
    echo ERROR: Failed to create signing certificate
    pause
    exit /b 1
)

echo.
echo Step 3: Converting to PFX format...
pvk2pfx -pvk GitFitDevSigning.pvk -spc GitFitDevSigning.cer -pfx GitFitDevSigning.pfx

if errorlevel 1 (
    echo ERROR: Failed to create PFX file
    pause
    exit /b 1
)

echo.
echo ===================================
echo Certificate Creation Complete!
echo ===================================
echo.
echo Created files:
echo   GitFitDev.cer - Root certificate
echo   GitFitDev.pvk - Root private key
echo   GitFitDevSigning.cer - Code signing certificate
echo   GitFitDevSigning.pvk - Code signing private key
echo   GitFitDevSigning.pfx - Combined certificate (for signing)
echo.
echo To use the certificate for signing:
echo   build_installer.bat --sign --cert=GitFitDevSigning.pfx
echo.
echo NOTE: This is a self-signed certificate. Users will see:
echo   "Unknown Publisher" but can still install the software.
echo.
echo For production use, consider purchasing a commercial certificate
echo from Sectigo, DigiCert, or GlobalSign.
echo.
pause