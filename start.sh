#!/bin/bash

echo "======================================"
echo "  AI智能体平台 - 快速启动脚本"
echo "======================================"
echo ""

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "错误: 未安装 Docker"
    echo "请先安装 Docker: https://www.docker.com/get-started"
    exit 1
fi

# 检查 Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "错误: 未安装 Docker Compose"
    echo "请先安装 Docker Compose"
    exit 1
fi

echo "1. 启动依赖服务 (MySQL, Redis, Milvus)..."
docker-compose up -d mysql redis milvus etcd minio

echo ""
echo "2. 等待服务启动..."
sleep 10

echo ""
echo "3. 检查后端环境..."
if [ ! -f "backend/.env" ]; then
    echo "   创建后端 .env 文件..."
    cp backend/.env.example backend/.env
    echo "   请编辑 backend/.env 文件，配置数据库连接和 API Key"
    echo ""
fi

echo "4. 检查前端环境..."
if [ ! -f "frontend/.env" ]; then
    echo "   创建前端 .env 文件..."
    cp frontend/.env.example frontend/.env
fi

echo ""
echo "======================================"
echo "  环境准备完成！"
echo "======================================"
echo ""
echo "后端启动："
echo "  cd backend"
echo "  python -m venv venv"
echo "  source venv/bin/activate  # Windows: venv\\Scripts\\activate"
echo "  pip install -r requirements.txt"
echo "  python main.py"
echo ""
echo "前端启动："
echo "  cd frontend"
echo "  npm install"
echo "  npm run dev"
echo ""
echo "或者使用 Docker 启动完整服务："
echo "  docker-compose up -d"
echo ""
