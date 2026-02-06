@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   AI智能体平台 - 一键启动
echo ========================================
echo.

cd /d "%~dp0"

:: 检查 Docker
docker ps >nul 2>&1
if %errorlevel% neq 0 (
    echo [1/4] 启动 Docker Desktop...
    echo 请手动启动 Docker Desktop，然后按任意键继续...
    pause >nul
)

:: 启动依赖服务
echo [1/4] 启动依赖服务 (MySQL, Redis, Milvus)...
docker-compose up -d mysql redis milvus etcd minio 2>nul
if %errorlevel% neq 0 (
    echo 跳过 Docker 服务（可能已启动或 Docker 未就绪）
)
echo.

:: 启动后端
echo [2/4] 启动后端服务...
cd backend
if not exist "venv" (
    echo 创建虚拟环境...
    python -m venv venv
)
call venv\Scripts\activate.bat
start "AI平台-后端" cmd /k "python main.py"
cd ..
echo 后端已启动：http://localhost:8000
echo.

:: 等待后端启动
echo 等待后端服务就绪...
timeout /t 3 /nobreak >nul

:: 启动前端
echo [3/4] 启动前端服务...
cd frontend
start "AI平台-前端" cmd /k "npm run dev"
cd ..
echo 前端已启动：http://127.0.0.1:5173
echo.

echo [4/4] 启动完成！
echo.
echo ========================================
echo   服务访问地址
echo ========================================
echo   前端： http://127.0.0.1:5173
echo   后端： http://localhost:8000
echo   API文档：http://localhost:8000/docs
echo.
echo   登录账号：
echo   用户名：testuser
echo   密码：123456
echo ========================================
echo.
echo 按任意键关闭此窗口...
pause >nul
