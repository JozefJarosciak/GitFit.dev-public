@echo off
echo ===================================
echo GitFit.dev Certificate Creator
echo ===================================
echo.

echo Checking for Windows SDK tools...

REM Try to find makecert in common locations
set "MAKECERT_PATH="
set "PVK2PFX_PATH="

REM Check PATH first
makecert.exe /? >nul 2>&1
if not errorlevel 1 (
    set "MAKECERT_PATH=makecert.exe"
    set "PVK2PFX_PATH=pvk2pfx.exe"
    echo Found Windows SDK tools in PATH
    goto :tools_found
)

REM Check common Windows SDK locations
for %%P in (
    "C:\Program Files (x86)\Windows Kits\10\bin\x64"
    "C:\Program Files (x86)\Windows Kits\10\bin\x86"
    "C:\Program Files (x86)\Windows Kits\8.1\bin\x64"
    "C:\Program Files (x86)\Windows Kits\8.1\bin\x86"
    "C:\Program Files\Microsoft SDKs\Windows\v7.1\Bin"
) do (
    if exist "%%~P\makecert.exe" (
        set "MAKECERT_PATH=%%~P\makecert.exe"
        set "PVK2PFX_PATH=%%~P\pvk2pfx.exe"
        echo Found Windows SDK tools at %%~P
        goto :tools_found
    )
)

echo ERROR: Windows SDK tools not found!
echo.
echo Please install Windows SDK or Visual Studio with C++ tools
echo Then either:
echo   1. Add SDK bin directory to your PATH, or
echo   2. Run this from Visual Studio Developer Command Prompt
echo.
echo Download Windows SDK from:
echo https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/
echo.
pause
exit /b 1

:tools_found
echo.
echo Creating self-signed certificate for GitFit.dev...
echo.

echo Step 1: Creating root certificate authority...
"%MAKECERT_PATH%" -r -pe -n "CN=GitFit.dev Root CA" -ss CA -sr CurrentUser -a sha256 -cy authority -sky signature -sv GitFitDev.pvk GitFitDev.cer
if errorlevel 1 (
    echo ERROR: Failed to create root certificate
    pause
    exit /b 1
)

echo.
echo Step 2: Creating code signing certificate...
"%MAKECERT_PATH%" -pe -n "CN=GitFit.dev Code Signing" -a sha256 -cy end -sky signature -ic GitFitDev.cer -iv GitFitDev.pvk -sv GitFitDevSigning.pvk GitFitDevSigning.cer
if errorlevel 1 (
    echo ERROR: Failed to create signing certificate
    pause
    exit /b 1
)

echo.
echo Step 3: Converting to PFX format...
"%PVK2PFX_PATH%" -pvk GitFitDevSigning.pvk -spc GitFitDevSigning.cer -pfx GitFitDevSigning.pfx
if errorlevel 1 (
    echo ERROR: Failed to create PFX file
    pause
    exit /b 1
)

echo.
echo ===================================
echo SUCCESS: Certificate Created!
echo ===================================
echo.
echo Files created:
echo   GitFitDevSigning.pfx - Use this file for code signing
echo.
echo To build a signed installer:
echo   build_installer.bat --sign --cert=GitFitDevSigning.pfx
echo.
echo NOTE: This is a self-signed certificate.
echo Users will see "Unknown Publisher" but can install the software.
echo.
pause