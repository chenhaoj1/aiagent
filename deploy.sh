#!/bin/bash
# ============================================
# AI智能体平台 - 后端部署脚本
# ============================================

set -e

echo "======================================"
echo "AI智能体平台 - 后端部署脚本"
echo "======================================"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查是否为 root 用户
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}请使用 root 用户或 sudo 运行此脚本${NC}"
    exit 1
fi

# 步骤 1: 更新系统
echo -e "${YELLOW}[1/7] 更新系统...${NC}"
apt update && apt upgrade -y

# 步骤 2: 安装 Docker 和 Docker Compose
echo -e "${YELLOW}[2/7] 安装 Docker...${NC}"
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    systemctl enable docker
    systemctl start docker
fi

if ! command -v docker-compose &> /dev/null; then
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

echo -e "${GREEN}Docker 版本: $(docker --version)${NC}"
echo -e "${GREEN}Docker Compose 版本: $(docker-compose --version)${NC}"

# 步骤 3: 安装 Certbot (用于 SSL 证书)
echo -e "${YELLOW}[3/7] 安装 Certbot...${NC}"
apt install -y certbot

# 步骤 4: 创建项目目录
echo -e "${YELLOW}[4/7] 创建项目目录...${NC}"
PROJECT_DIR="/opt/aiagent-platform"
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

# 步骤 5: 上传或克隆项目代码
echo -e "${YELLOW}[5/7] 请上传项目代码到 $PROJECT_DIR${NC}"
echo "你可以使用以下方式之一:"
echo "1. 使用 scp 上传: scp -r ./aiapp root@your-server-ip:$PROJECT_DIR"
echo "2. 使用 git clone: git clone https://github.com/your-repo/aiapp.git ."
echo ""
read -p "按回车继续..."

# 步骤 6: 配置环境变量
echo -e "${YELLOW}[6/7] 配置环境变量...${NC}"
if [ ! -f ./backend/.env ]; then
    cp ./backend/.env.example.production ./backend/.env
    echo -e "${RED}请编辑 backend/.env 文件，设置以下重要配置:${NC}"
    echo "  - SECRET_KEY (运行: openssl rand -hex 32)"
    echo "  - MYSQL_PASSWORD"
    echo "  - REDIS_PASSWORD"
    echo "  - QWEN_API_KEY"
    echo "  - DASHSCOPE_API_KEY"
    echo ""
    read -p "按回车继续..."
fi

# 步骤 7: 获取 SSL 证书
echo -e "${YELLOW}[7/7] 配置 SSL 证书...${NC}"
read -p "请输入你的域名 (例如: api.example.com): " DOMAIN

if [ -n "$DOMAIN" ]; then
    # 停止可能占用 80 端口的容器
    docker-compose -f docker-compose.prod.yml down 2>/dev/null || true

    # 获取证书
    certbot certonly --standalone -d $DOMAIN --email your-email@example.com --agree-tos --non-interactive

    # 复制证书到 Nginx 目录
    mkdir -p ./docker/nginx/ssl
    cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem ./docker/nginx/ssl/
    cp /etc/letsencrypt/live/$DOMAIN/privkey.pem ./docker/nginx/ssl/

    # 更新 Nginx 配置中的域名
    sed -i "s/your-domain.com/$DOMAIN/g" ./docker/nginx/nginx.conf
fi

# 启动服务
echo -e "${GREEN}启动服务...${NC}"
docker-compose -f docker-compose.prod.yml up -d

# 等待服务启动
echo -e "${YELLOW}等待服务启动...${NC}"
sleep 10

# 检查服务状态
echo -e "${GREEN}服务状态:${NC}"
docker-compose -f docker-compose.prod.yml ps

echo ""
echo -e "${GREEN}======================================"
echo "部署完成！"
echo "======================================${NC}"
echo ""
echo "后端 API: https://$DOMAIN"
echo "API 文档: https://$DOMAIN/docs"
echo ""
echo "常用命令:"
echo "  查看日志: docker-compose -f docker-compose.prod.yml logs -f backend"
echo "  重启服务: docker-compose -f docker-compose.prod.yml restart"
echo "  停止服务: docker-compose -f docker-compose.prod.yml down"
echo ""
