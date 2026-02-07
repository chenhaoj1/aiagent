FROM python:3.11-slim

WORKDIR /app/backend

# 缓存破坏器 - 强制重建依赖层
ARG CACHEBUST=5

# 安装系统依赖（添加 CACHEBUST 引用以破坏缓存）
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    && echo "Cache bust: ${CACHEBUST}" \
    && rm -rf /var/lib/apt/lists/*

# 复制并安装 Python 依赖
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端代码（添加 CACHEBUST 以确保代码更新时重建）
COPY backend/ .
RUN echo "Code version: ${CACHEBUST}"

# 复制 Docker 启动脚本
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# 创建必要的目录
RUN mkdir -p uploads logs

# Railway 自动注入 PORT 环境变量，这里只是默认值
ENV PORT=8000
EXPOSE 8000

# 启动应用
CMD ["/usr/local/bin/docker-entrypoint.sh"]
