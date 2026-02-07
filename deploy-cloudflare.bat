@echo off
REM Cloudflare Pages Deployment Script
REM This script builds and deploys the frontend to Cloudflare Pages

echo ========================================
echo Cloudflare Pages Deployment Script
echo ========================================
echo.

REM Check if wrangler is installed
where npx >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: npx not found. Please install Node.js first.
    pause
    exit /b 1
)

echo Step 1: Installing dependencies...
cd frontend
call npm install
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)
echo.

echo Step 2: Building frontend...
call npm run generate
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to build frontend
    pause
    exit /b 1
)
echo.

echo Step 3: Deploying to Cloudflare Pages...
echo NOTE: You will be prompted to select your Cloudflare Pages project
echo.
call npx wrangler pages deploy .output/public --project-name=aiagent-aze

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo Deployment successful!
    echo Your site should be available at:
    echo https://aiagent-aze.pages.dev
    echo ========================================
) else (
    echo.
    echo Error: Deployment failed
    echo Please check the error messages above
)

pause
