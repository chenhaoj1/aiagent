"""
Hugging Face Spaces 入口文件
"""
import os
import sys

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(__file__))

# 从 main.py 导入 FastAPI app
from main import app

# HF Spaces 需要这个
import gradio as gr

# 创建一个简单的 Gradio 界面 (可选)
def greet(name):
    return f"欢迎使用 AI智能体平台 API! 访问 /docs 查看 API 文档"

demo = gr.Interface(fn=greet, inputs="text", outputs="text")

if __name__ == "__main__":
    # 本地开发时使用 uvicorn
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
else:
    # HF Spaces 部署时使用 Gradio
    demo.launch()
