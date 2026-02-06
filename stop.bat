@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   AI智能体平台 - 一键停止
echo ========================================
echo.

cd /d "%~dp0"

:: 停止后端
echo [1/3] 停止后端服务...
for /f "tokens=2" %%i in ('netstat -ano ^| findstr ":8000"') do (
    taskkill /F /PID %%i >nul 2>&1
)
echo 后端已停止

:: 停止前端
echo [2/3] 停止前端服务...
for /f "tokens=2" %%i in ('netstat -ano ^| findstr ":5173"') do (
    taskkill /F /PID %%i >nul 2>&1
)
echo 前端已停止

:: 停止 Docker 服务
echo [3/3] 停止 Docker 依赖服务...
docker-compose down 2>nul
echo Docker 服务已停止

echo.
echo 所有服务已停止！
echo.
pause
