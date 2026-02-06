# AI智能体平台 - 部署检查清单

## 准备阶段

- [ ] 注册 [Vercel](https://vercel.com) 账号 (GitHub 登录)
- [ ] 注册 [Render](https://render.com) 账号 (GitHub 登录)
- [ ] 将代码推送到 GitHub 仓库
- [ ] 获取通义千问 API Key: https://dashscope.aliyun.com
- [ ] 获取通义万相 API Key: https://dashscope.aliyun.com

---

## 后端部署 (Render)

### 方式 A：自动部署 (推荐)

- [ ] 确认 `render.yaml` 在项目根目录
- [ ] Render Dashboard → "New +" → "Blueprint"
- [ ] 连接 GitHub 仓库并选择分支
- [ ] 等待自动创建所有服务
- [ ] 在服务中设置环境变量:
  - [ ] `QWEN_API_KEY`
  - [ ] `DASHSCOPE_API_KEY`

### 方式 B：手动部署

- [ ] 创建 PostgreSQL 数据库 (`aiagent-db`)
- [ ] 创建 Redis (`aiagent-redis`)
- [ ] 创建 Web Service (`aiagent-backend`)
  - [ ] 选择 Docker 环境
  - [ ] Dockerfile: `./backend/Dockerfile.render`
  - [ ] 设置环境变量:
    - [ ] `DATABASE_URL` (从 PostgreSQL 复制)
    - [ ] `REDIS_URL` (从 Redis 复制)
    - [ ] `SECRET_KEY`
    - [ ] `QWEN_API_KEY`
    - [ ] `DASHSCOPE_API_KEY`
    - [ ] `CORS_ORIGINS`

- [ ] 等待部署完成
- [ ] 验证: 访问 `https://xxx.onrender.com/health`

---

## 前端部署 (Vercel)

- [ ] Vercel Dashboard → "Add New" → "Project"
- [ ] 导入 GitHub 仓库
- [ ] 配置:
  - [ ] Root Directory: `frontend`
  - [ ] Framework: `Nuxt.js`
- [ ] 设置环境变量:
  - [ ] `NUXT_PUBLIC_API_URL` = 后端 Render 地址
- [ ] 点击 Deploy
- [ ] 等待部署完成
- [ ] 验证: 访问 Vercel 提供的域名

---

## 部署后配置

- [ ] 更新后端 CORS 配置，添加前端域名
- [ ] 测试前后端连接
- [ ] 测试用户注册/登录
- [ ] 测试 AI 功能
- [ ] (可选) 配置自定义域名

---

## 完成后记录

| 项目 | 地址 |
|------|------|
| 前端 URL | `https://xxxxx.vercel.app` |
| 后端 URL | `https://xxxxx.onrender.com` |
| API 文档 | `https://xxxxx.onrender.com/docs` |
| Render Dashboard | [链接] |
| Vercel Dashboard | [链接] |

---

## 常用命令

```bash
# 查看后端日志
# Render Dashboard → Services → aiagent-backend → Logs

# 查看前端日志
# Vercel Dashboard → Project → Deployments → Logs

# 触发重新部署
git commit --allow-empty -m "Trigger redeploy"
git push origin main
```
