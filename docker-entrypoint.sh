#!/bin/sh
set -e

echo "========================================"
echo "Starting AI Agent Platform Backend"
echo "========================================"
echo "PORT=${PORT:-8000}"
echo "Working Directory: $(pwd)"
echo ""

# 确保在正确的目录
cd /app/backend

echo "Python version:"
python --version
echo ""

echo "Starting Uvicorn server..."
exec python -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --log-level info
