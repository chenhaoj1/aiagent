# AI智能体平台 - Render + Vercel 部署指南

本文档介绍如何使用 **Render** (后端) + **Vercel** (前端) 实现 0 成本部署。

---

## 部署架构

```
┌─────────────────────────┐     ┌─────────────────────────┐
│      Vercel (前端)        │     │      Render (后端)       │
│                         │     │                         │
│  - Nuxt.js 静态文件     │────▶│  - FastAPI              │
│  - 全球 CDN 加速         │     │  - PostgreSQL 数据库     │
│  - 自动 HTTPS            │     │  - Redis 缓存           │
│  - 免费                  │     │  - 免费 (有限制)         │
└─────────────────────────┘     └─────────────────────────┘
```

---

## 前置准备

### 1. 注册账号

| 平台 | 链接 | 说明 |
|------|------|------|
| Vercel | https://vercel.com | GitHub 登录 |
| Render | https://render.com | GitHub/GitLab 登录 |

### 2. 准备代码

确保代码已推送到 GitHub 仓库。

### 3. 获取 API Keys

| 服务 | 链接 | 用途 |
|------|------|------|
| 通义千问 | https://dashscope.aliyun.com | LLM 服务 |
| 通义万相 | https://dashscope.aliyun.com | AI 视频/图片 |

---

## 第一步：部署后端 (Render)

### 方式 A：使用 render.yaml 自动部署 (推荐)

1. **确认 `render.yaml` 在项目根目录**
   ```bash
   # 项目结构应该是：
   aiapp/
   ├── render.yaml          # Render 配置文件
   ├── backend/
   │   ├── Dockerfile.render
   │   ├── main.py
   │   ├── requirements.txt
   │   └── app/
   └── frontend/
   ```

2. **在 Render 创建新服务**
   - 访问 https://dashboard.render.com
   - 点击 "New +" → "Blueprint"
   - 连接你的 GitHub 仓库
   - 选择包含 `render.yaml` 的分支 (main/master)
   - Render 会自动识别配置并创建所有服务

3. **设置环境变量**
   在创建的服务中，手动添加以下环境变量：
   | Key | Value |
   |-----|-------|
   | `QWEN_API_KEY` | 你的通义千问 API Key |
   | `DASHSCOPE_API_KEY` | 你的万相 API Key |

4. **等待部署完成**
   - 后端服务: `https://aiagent-backend.onrender.com`
   - API 文档: `https://aiagent-backend.onrender.com/docs`

---

### 方式 B：手动创建服务

#### 1. 创建 PostgreSQL 数据库

1. Render Dashboard → "New +" → "PostgreSQL"
2. 配置:
   - Name: `aiagent-db`
   - Database: `aiagent_platform`
   - User: `aiagent`
   - Plan: Free
   - Region: Oregon (推荐)
3. 创建后记录 **Internal Database URL**

#### 2. 创建 Redis

1. Render Dashboard → "New +" → "Redis"
2. 配置:
   - Name: `aiagent-redis`
   - Plan: Free
   - Region: Oregon
3. 创建后记录 **Internal Redis URL**

#### 3. 创建后端 Web 服务

1. Render Dashboard → "New +" → "Web Service"
2. 连接 GitHub 仓库
3. 配置:
   | 项目 | 值 |
   |------|-----|
   | Name | `aiagent-backend` |
   | Environment | `Docker` |
   | Dockerfile Path | `./backend/Dockerfile.render` |
   | Context | `./backend` |
   | Plan | Free |
   | Region | Oregon |

4. 设置环境变量:
   | Key | Value |
   |-----|-------|
   | `DATABASE_URL` | (从 PostgreSQL 服务复制) |
   | `REDIS_URL` | (从 Redis 服务复制) |
   | `SECRET_KEY` | (自动生成或手动设置) |
   | `QWEN_API_KEY` | 你的 API Key |
   | `DASHSCOPE_API_KEY` | 你的 API Key |
   | `CORS_ORIGINS` | `["https://*.vercel.app"]` |

5. 点击 "Create Web Service"

---

## 第二步：部署前端 (Vercel)

### 1. 创建 Vercel 项目

1. 访问 https://vercel.com
2. 点击 "Add New" → "Project"
3. 导入你的 GitHub 仓库

### 2. 配置项目

| 项目 | 值 |
|------|-----|
| Framework Preset | `Nuxt.js` |
| Root Directory | `frontend` |
| Build Command | `npm run build` (自动检测) |
| Output Directory | `.output/public` (自动检测) |

### 3. 设置环境变量

在 "Environment Variables" 中添加：

| Key | Value |
|-----|-------|
| `NUXT_PUBLIC_API_URL` | `https://aiagent-backend.onrender.com` |

### 4. 部署

点击 "Deploy"，等待构建完成。

前端地址: `https://your-project.vercel.app`

---

## 第三步：配置 CORS

部署完成后，需要更新后端的 CORS 配置：

1. 在 Render 后端服务中，添加环境变量:
   ```bash
   CORS_ORIGINS=["https://your-project.vercel.app","https://*.vercel.app"]
   ```

2. 或者在 `backend/app/core/config.py` 中添加你的 Vercel 域名

---

## 验证部署

| 检查项 | 地址 |
|--------|------|
| 后端健康检查 | `https://aiagent-backend.onrender.com/health` |
| API 文档 | `https://aiagent-backend.onrender.com/docs` |
| 前端应用 | `https://your-project.vercel.app` |

---

## 自定义域名 (可选)

### 前端域名

1. Vercel 项目 → Settings → Domains
2. 添加域名 (如: `www.yourdomain.com`)
3. 配置 DNS: `CNAME www -> cname.vercel-dns.com`

### 后端域名

1. Render 服务 → Settings → Custom Domains
2. 添加域名 (如: `api.yourdomain.com`)
3. 配置 DNS: `CNAME api -> <your-render-service-url>`

---

## Render 免费层限制

| 项目 | 限制 |
|------|------|
| 运行时间 | 750 小时/月 (约 31 天连续) |
| 睡眠时间 | 15 分钟无请求后睡眠 |
| 唤醒时间 | 30-60 秒 |
| 内存 | 512 MB |
| CPU | 0.1 核 |
| 数据库 | 1 GB PostgreSQL (免费) |
| Redis | 25 MB Redis (免费) |

### 解决睡眠问题

如果需要 24/7 在线，可以考虑：
1. 使用 **Cron-job.org** 设置定时 ping (每 10 分钟)
2. 升级到 Render Starter ($7/月)
3. 使用 Railway ($5 免费额度)

---

## 更新代码

### 后端更新

```bash
# 推送代码到 GitHub
git add .
git commit -m "Update backend"
git push origin main
```

Render 会自动检测并重新部署。

### 前端更新

```bash
# 推送代码到 GitHub
git add .
git commit -m "Update frontend"
git push origin main
```

Vercel 会自动检测并重新部署。

---

## 查看日志

### Render

1. Render Dashboard → 选择服务
2. 点击 "Logs" 标签
3. 实时查看日志

### Vercel

1. Vercel Dashboard → 选择项目
2. 点击 "Deployments" → 选择部署
3. 点击 "View Function Logs"

---

## 常见问题

### Q: 后端部署失败？

A: 检查以下几点:
1. `Dockerfile.render` 路径是否正确
2. `requirements.txt` 是否包含所有依赖
3. 环境变量是否正确设置

### Q: 前端无法连接后端？

A: 检查:
1. 后端 CORS 配置是否包含前端域名
2. `NUXT_PUBLIC_API_URL` 是否正确
3. 后端服务是否正常运行

### Q: 数据库连接失败？

A: 确保:
1. 使用 Internal Database URL (不是 External)
2. 数据库服务已启动
3. 环境变量正确设置

### Q: 服务频繁睡眠？

A: 这是免费层限制。可以:
1. 设置定时 ping (每 10 分钟)
2. 升级到付费计划
3. 接受这个限制 (个人项目够用)

---

## 成本总结

| 项目 | 平台 | 费用 |
|------|------|------|
| 前端 | Vercel | ¥0 |
| 后端 | Render | ¥0 |
| 数据库 | Render PostgreSQL | ¥0 |
| 缓存 | Render Redis | ¥0 |
| 域名 (可选) | 你的域名商 | ¥10/年 |
| **总计** | | **¥0 - ¥10/年** |

---

## 下一步

1. [ ] 注册 Render 和 Vercel 账号
2. [ ] 推送代码到 GitHub
3. [ ] 获取 AI API Keys
4. [ ] 部署后端到 Render
5. [ ] 部署前端到 Vercel
6. [ ] 验证功能正常
7. [ ] (可选) 绑定自定义域名

祝部署顺利！如有问题请查看日志或提交 Issue。
