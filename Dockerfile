FROM python:3.11-slim

WORKDIR /app/backend

# 缓存破坏器 - 强制重建依赖层
ARG CACHEBUST=2

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制并安装 Python 依赖
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端代码
COPY backend/ .

# 复制 Docker 启动脚本
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# 创建必要的目录
RUN mkdir -p uploads logs

# Railway 自动注入 PORT 环境变量，这里只是默认值
ENV PORT=8000
EXPOSE 8000

# 测试 Python 导入
RUN python -c "from main import app; print('App import successful')"

# 启动应用
CMD ["/usr/local/bin/docker-entrypoint.sh"]
