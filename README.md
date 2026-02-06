# AI智能体平台

一个面向内容创作者、教育机构和自媒体从业者的 AI 生态系统平台，提供 AI 短视频生成、智能助手、知识库管理等核心功能。

## 项目概述

**AI智能体平台** 是一个全栈 AI 应用，帮助用户高效创作和管理 AI 内容。

### 核心功能

| 模块 | 功能 | 状态 |
|------|------|------|
| **用户系统** | 注册/登录、会员管理、权限控制 | ✅ 已完成 |
| **知识库管理** | 文档上传、向量检索、智能问答 | ✅ 已完成 |
| **AI 视频生成** | 文案转视频、视频模板、任务管理 | ✅ 已完成 |

### 技术栈

#### 前端
- **Nuxt.js 3** - Vue SSR 框架
- **Vue 3** - 核心前端框架
- **Element Plus** - UI 组件库
- **TailwindCSS** - 原子化 CSS 框架

#### 后端
- **FastAPI** - 高性能 API 框架
- **SQLAlchemy** - ORM 框架
- **MySQL 8.0** - 关系型数据库
- **Redis** - 缓存和消息队列
- **Milvus** - 向量数据库

#### AI 服务
- **通义千问** - 大语言模型
- **剪映 API** - AI 视频生成
- **自建向量检索** - RAG 知识库

## 快速开始

### 环境要求

- Python 3.11+
- Node.js 18+
- MySQL 8.0+
- Redis 7.0+
- Milvus 2.3+ (可选，用于知识库功能)

### 使用 Docker Compose（推荐）

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f backend

# 停止服务
docker-compose down
```

### 手动安装

#### 1. 克隆项目

```bash
git clone https://github.com/your-repo/aiagent-platform.git
cd aiagent-platform
```

#### 2. 启动依赖服务

使用 Docker 启动 MySQL、Redis、Milvus：

```bash
docker-compose up -d mysql redis milvus etcd minio
```

#### 3. 后端设置

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 复制环境配置
cp .env.example .env

# 编辑 .env 文件，配置数据库连接和 API Key

# 初始化数据库
python -c "from app.core.database import init_db; init_db()"

# 启动后端
python main.py
```

#### 4. 前端设置

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 访问应用

- **前端**: http://localhost:5173
- **后端 API**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs

## 配置说明

### 环境变量 (.env)

```bash
# 通义千问 API Key (必需)
QWEN_API_KEY=your-qwen-api-key

# 数据库连接
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/ai_agent_platform

# Redis 连接
REDIS_URL=redis://localhost:6379/0

# Milvus 向量数据库
MILVUS_HOST=localhost
MILVUS_PORT=19530
```

### 获取 API Key

1. **通义千问**: [阿里云百炼平台](https://dashscope.aliyun.com/)
2. **剪映 API**: [剪映开放平台](https://open.jianying.com/)

## 项目结构

```
aiapp/
├── backend/                 # 后端 FastAPI 项目
│   ├── app/
│   │   ├── api/            # API 路由
│   │   ├── core/           # 核心配置
│   │   ├── models/         # 数据库模型
│   │   ├── schemas/        # Pydantic 模式
│   │   ├── services/       # 业务逻辑
│   │   └── utils/          # 工具函数
│   ├── main.py             # 主入口文件
│   ├── requirements.txt    # Python 依赖
│   └── .env.example        # 环境变量示例
├── frontend/               # 前端 Nuxt.js 项目
│   ├── pages/              # 页面
│   ├── components/         # 组件
│   ├── composables/        # 组合式函数
│   ├── stores/             # 状态管理
│   └── nuxt.config.ts      # Nuxt 配置
├── docker-compose.yml      # Docker Compose 配置
└── README.md               # 项目说明
```

## API 文档

启动后端服务后，访问 http://localhost:8000/docs 查看完整的 API 文档。

### 主要 API 端点

| 模块 | 端点 | 说明 |
|------|------|------|
| 认证 | `POST /api/v1/auth/login` | 用户登录 |
| 认证 | `POST /api/v1/auth/register` | 用户注册 |
| 知识库 | `POST /api/v1/knowledge-bases` | 创建知识库 |
| 知识库 | `POST /api/v1/knowledge-bases/{id}/documents` | 上传文档 |
| 知识库 | `POST /api/v1/knowledge-bases/{id}/query` | 知识库问答 |
| 视频 | `POST /api/v1/video/generate` | 创建视频生成任务 |
| 视频 | `GET /api/v1/video/tasks` | 获取任务列表 |

## 开发计划

- [x] 用户系统
- [x] 知识库管理
- [x] AI 视频生成
- [ ] 前端页面开发
- [ ] AI 文案创作
- [ ] AI 图片生成
- [ ] 智能客服
- [ ] 支付集成
- [ ] 应用市场

## 贡献指南

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 联系方式

- 项目地址: [GitHub](https://github.com/your-repo/aiagent-platform)
- 问题反馈: [Issues](https://github.com/your-repo/aiagent-platform/issues)

---

> **注意**: 本项目仅供学习参考，请遵守相关 AI 服务的使用条款。
