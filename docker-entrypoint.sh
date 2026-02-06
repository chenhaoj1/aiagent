#!/bin/sh

echo "========================================"
echo "Starting AI Agent Platform Backend"
echo "========================================"
echo "PORT=${PORT:-8000}"
echo "Working Directory: $(pwd)"
echo ""

# 确保在正确的目录
cd /app/backend || exit 1

echo "Python version:"
python --version || echo "Python not found!"
echo ""

echo "Current directory contents:"
ls -la || echo "Cannot list directory"
echo ""

echo "Testing app import..."
python -c "from main import app; print('Import successful')" || echo "Import failed!"
echo ""

echo "Starting Uvicorn server on 0.0.0.0:${PORT:-8000}..."
python -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --log-level debug
