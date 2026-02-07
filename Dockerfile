FROM python:3.11-slim

WORKDIR /app/backend

# 缓存破坏器 - 强制重建 (2026-02-07-10:30)
ARG CACHEBUST=6

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    && echo "Build: 2026-02-07-10:30-bust-${CACHEBUST}" \
    && rm -rf /var/lib/apt/lists/*

# 复制并安装 Python 依赖
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端代码
COPY backend/ .
RUN echo "Code deployed: 2026-02-07-10:30-v${CACHEBUST}"

# 复制 Docker 启动脚本
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# 创建必要的目录
RUN mkdir -p uploads logs

# Railway 自动注入 PORT 环境变量
ENV PORT=8000
EXPOSE 8000

# 启动应用
CMD ["/usr/local/bin/docker-entrypoint.sh"]
