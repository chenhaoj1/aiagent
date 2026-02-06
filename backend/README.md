# HF (Hugging Face Spaces) 部署配置
api: gradio
# Python 3.11
python_version: 3.11
# 预装的依赖
python_packages:
  - "fastapi==0.109.0"
  - "uvicorn[standard]==0.27.0"
  - "sqlalchemy==2.0.25"
  - "pymysql==1.1.0"
  - "redis==5.0.1"
  - "dashscope==1.14.0"
