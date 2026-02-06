# AI智能体平台 - 0成本部署指南

本文档介绍如何使用**完全免费**的服务部署 AI智能体平台。

---

## 部署方案对比

| 方案 | 平台 | 免费额度 | 优点 | 缺点 |
|------|------|----------|------|------|
| **方案 A** | Vercel + HF Spaces | 完全免费 | 最简单，稳定 | 代码公开 |
| **方案 B** | Vercel + Render | 750小时/月 | 功能完整 | 15分钟睡眠 |
| **方案 C** | Vercel + Railway | $5/月 | 性能好 | 额度用完需付费 |

---

## 推荐方案：Vercel + Hugging Face (完全免费)

### 架构图

```
┌─────────────────────┐     ┌─────────────────────┐
│   Vercel (前端)      │     │  HF Spaces (后端)   │
│                     │     │                     │
│   - Nuxt.js 静态    │────▶│   - FastAPI         │
│   - 全球 CDN         │     │   - CPU 2核         │
│   - 免费             │     │   - 16GB RAM        │
│   - 自定义域名        │     │   - 免费             │
└─────────────────────┘     └─────────────────────┘
                                      │
                         ┌────────────┴────────────┐
                         ▼                         ▼
                  ┌─────────────┐          ┌─────────────┐
                  │ PlanetScale │          │  Upstash    │
                  │  (MySQL)    │          │  (Redis)    │
                  │   免费      │          │   免费      │
                  └─────────────┘          └─────────────┘
```

---

## 第一步：免费数据库配置

### 1.1 PlanetScale (MySQL) - 免费

1. 访问 [PlanetScale](https://planetscale.com/)
2. 注册账号 (GitHub 登录)
3. 创建数据库：
   - 数据库名: `aiagent_platform`
   - 区域: 选择 `ap-northeast` (东京，延迟低)
4. 获取连接字符串：
   ```
   mysql://xxx:pscale_pw_xxx@aws.connect.psdb.cloud/aiagent_platform?sslaccept=strict
   ```

### 1.2 Upstash Redis - 免费

1. 访问 [Upstash](https://upstash.com/)
2. 注册账号
3. 创建 Redis 数据库：
   - 区域: 选择 `ap-northeast-1`
   - 免费额度: 10,000 命令/天
4. 获取连接字符串：
   ```
   redis://default:xxxxx@xxxxx.upstash.io:6379
   ```

---

## 第二步：后端部署 (Hugging Face)

### 2.1 创建 Space

1. 访问 [Hugging Face Spaces](https://huggingface.co/spaces)
2. 点击 "Create new Space"
3. 配置：
   - Space 名称: `aiagent-platform`
   - License: MIT
   - Visibility: Public (必须公开才能免费)
   - SDK: Gradio (或 Docker)
   - Hardware: CPU basic (免费)

### 2.2 上传代码

**方式一：Git 推送**

```bash
# 在 backend 目录创建 HF 专用文件
cd backend

# 复制 HF 依赖文件
cp requirements_hf.txt requirements.txt

# 初始化 Git 并推送到 HF
git init
git add .
git commit -m "Initial commit"

# 添加 HF 远程仓库
git remote add origin https://huggingface.co/spaces/your-username/aiagent-platform

# 推送
git push origin main
```

**方式二：网页上传**

直接在 HF Spaces 网页上传文件：
- `app.py` (入口文件)
- `main.py`
- `requirements_hf.txt` (重命名为 `requirements.txt`)
- `app/` 目录

### 2.3 设置环境变量

在 HF Space 设置中添加 Secrets：

| Key | Value |
|-----|-------|
| `DATABASE_URL` | PlanetScale 连接字符串 |
| `REDIS_URL` | Upstash 连接字符串 |
| `QWEN_API_KEY` | 你的通义千问 API Key |
| `DASHSCOPE_API_KEY` | 你的万相 API Key |
| `SECRET_KEY` | 随机生成的密钥 |

### 2.4 修改代码以支持 PostgreSQL (可选)

HF + Render/Railway 提供 PostgreSQL，如果使用需修改：

```python
# backend/app/core/config.py
DATABASE_URL = os.getenv("DATABASE_URL")  # HF 自动提供 PostgreSQL

# 或者保持 SQLite (完全免费)
DATABASE_URL = "sqlite:///./ai_agent_platform.db"
```

### 2.5 部署完成

等待构建完成，访问：
- `https://huggingface.co/spaces/your-username/aiagent-platform`
- API 地址: `https://your-username-aiagent-platform.hf.space`

---

## 第三步：前端部署 (Vercel)

### 3.1 部署步骤

1. 访问 [Vercel](https://vercel.com)
2. 导入你的 GitHub 仓库
3. 配置：
   - Root Directory: `frontend`
   - Framework: Nuxt.js

### 3.2 设置环境变量

在 Vercel 项目设置中添加：

| Key | Value |
|-----|-------|
| `NUXT_PUBLIC_API_URL` | `https://your-username-aiagent-platform.hf.space` |

### 3.3 自定义域名 (可选)

在 Vercel 设置中添加你的域名，DNS 配置：
```
CNAME www -> cname.vercel-dns.com
```

---

## 方案 B：Render 部署 (备选)

### Render 配置

1. 访问 [Render](https://render.com)
2. 连接 GitHub 仓库
3. 使用 `render.yaml` 配置自动部署
4. 或手动创建：
   - Web Service → Docker
   - PostgreSQL → 数据库
   - Redis → 缓存

### 注意事项

- Render 免费服务 **15分钟无活动后睡眠**
- 首次访问可能需要 30-60秒唤醒
- 适合个人项目或演示

---

## 方案 C：Railway 部署

### Railway 配置

1. 访问 [Railway](https://railway.app)
2. 点击 "New Project"
3. 选择 "Deploy from GitHub repo"
4. 添加服务：
   - Backend (Docker)
   - PostgreSQL
   - Redis
5. 设置环境变量

### 注意事项

- 新账号 $5 免费额度
- 用完后需付费
- 性能比 Render 好

---

## 数据库配置总结

### SQLite (最简单)

**优点**：无需外部服务，完全免费
**缺点**：HF 重启后数据丢失

```python
# backend/.env
DATABASE_URL=sqlite:///./ai_agent_platform.db
```

### PlanetScale MySQL

**优点**：数据持久化，免费 5GB
**缺点**：需要配置

```bash
DATABASE_URL=mysql://xxx:pscale_pw_xxx@aws.connect.psdb.cloud/aiagent_platform?sslaccept=strict
```

### Railway/Render PostgreSQL

**优点**：自动配置，持久化
**缺点**：平台绑定

```bash
DATABASE_URL=postgresql://xxx:xxx@xxx.railway.app:5432/railway
```

---

## 成本对比

| 方案 | 月费 | 数据存储 |
|------|------|----------|
| Vercel + HF | ¥0 | SQLite (临时) |
| Vercel + HF + PlanetScale | ¥0 | 5GB MySQL |
| Vercel + HF + Railway | ¥0 (首月) | 1GB PostgreSQL |
| Vercel + Render | ¥0 | 1GB PostgreSQL |

---

## 快速开始

### 最简方案 (10分钟)

```bash
# 1. 修改后端配置
cd backend
cp .env.example.railway .env
# 修改: 使用 SQLite + 你的 API Keys

# 2. 推送到 HF
git init
git add .
git commit -m "Deploy to HF"
git remote add hf https://huggingface.co/spaces/your-name/aiagent
git push hf main

# 3. 部署前端到 Vercel
# 在 vercel.com 导入仓库，设置 API_URL
```

---

## 常见问题

### Q: HF Spaces 部署后数据丢失？

A: 使用 SQLite 数据会丢失。解决方案：
- 使用 PlanetScale MySQL (免费)
- 或使用 Railway PostgreSQL ($5/月)

### Q: API 唤醒太慢？

A: 免费服务有限制。解决方案：
- 使用 Railway ($5/月)
- 或购买云服务器

### Q: 如何隐藏代码？

A: HF 免费版必须公开代码。如需私密：
- 使用 Render (私密)
- 或购买 HF Pro 订阅

---

## 下一步

1. 注册各平台账号
2. 获取 API Keys (通义千问)
3. 按照"快速开始"部署
4. 绑定自定义域名

祝部署顺利！
