FROM python:3.11-slim

WORKDIR /app/backend

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

# 创建必要的目录
RUN mkdir -p uploads logs

# Railway 自动注入 PORT 环境变量，这里只是默认值
ENV PORT=8000
EXPOSE 8000

# 创建启动脚本
RUN echo '#!/bin/sh\n\
echo "Starting application..."\n\
echo "PORT=$PORT"\n\
cd /app/backend\n\
echo "Working directory: $(pwd)"\n\
echo "Files in directory:"\n\
ls -la\n\
python -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}\n\
' > /start.sh && chmod +x /start.sh

# 启动应用
CMD ["/start.sh"]
