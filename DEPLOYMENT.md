# AI智能体平台 - 生产环境部署指南

本文档介绍如何将 AI智能体平台 部署到互联网，实现前后端分离部署。

## 部署架构

```
┌─────────────────┐     ┌─────────────────┐
│   前端 (Vercel)  │     │  后端 (云服务器)  │
│                 │     │                 │
│   Nuxt.js 3     │────▶│   FastAPI       │
│   静态网站      │     │   + MySQL       │
│   全球 CDN      │     │   + Redis       │
│   免费          │     │   + Milvus      │
└─────────────────┘     └─────────────────┘
```

---

## 第一部分：前端部署 (Vercel)

### 1.1 准备工作

- 注册 [Vercel 账号](https://vercel.com)
- 安装 Git
- 准备前端代码

### 1.2 部署步骤

#### 方式一：通过 Vercel 网页部署 (推荐)

1. 登录 [Vercel](https://vercel.com)
2. 点击 "Add New Project"
3. 导入你的 Git 仓库 (GitHub/GitLab/Bitbucket)
4. 配置项目：
   - **Framework Preset**: Nuxt.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build` (自动检测)

5. 设置环境变量：
   | 名称 | 值 |
   |------|-----|
   | `NUXT_PUBLIC_API_URL` | `https://your-backend-domain.com` |

6. 点击 "Deploy"

#### 方式二：通过 Vercel CLI 部署

```bash
# 安装 Vercel CLI
npm i -g vercel

# 在 frontend 目录下执行
cd frontend
vercel

# 按提示操作
# - 登录 Vercel 账号
# - 设置项目名称
# - 设置环境变量 NUXT_PUBLIC_API_URL
```

### 1.3 配置自定义域名 (可选)

1. 在 Vercel 项目中，进入 "Settings" → "Domains"
2. 添加你的域名 (如: `www.your-domain.com`)
3. 按照提示配置 DNS 记录：
   - 类型: `A` / `CNAME`
   - 值: Vercel 提供的地址

### 1.4 前端部署成本

| 项目 | 价格 |
|------|------|
| Vercel Hobby (免费版) | $0/月 |
| 个人域名 | ~$10/年 |

---

## 第二部分：后端部署 (云服务器)

### 2.1 购买云服务器

推荐服务商：

| 服务商 | 配置建议 | 月费参考 |
|--------|----------|----------|
| 阿里云 ECS | 2核4GB | ¥60-100 |
| 腾讯云 CVM | 2核4GB | ¥60-100 |
| 华为云 ECS | 2核4GB | ¥60-100 |

### 2.2 服务器系统要求

- 操作系统: Ubuntu 20.04 / 22.04 LTS
- 已安装: Docker 和 Docker Compose
- 开放端口: 80, 443, 22

### 2.3 部署步骤

#### 步骤 1: 连接服务器

```bash
ssh root@your-server-ip
```

#### 步骤 2: 上传项目代码

```bash
# 在本地执行
scp -r ./aiapp root@your-server-ip:/opt/aiagent-platform

# 或使用 rsync
rsync -avz ./aiapp/ root@your-server-ip:/opt/aiagent-platform/
```

#### 步骤 3: 配置环境变量

```bash
# 在服务器上执行
cd /opt/aiagent-platform
cp backend/.env.example.production backend/.env
nano backend/.env
```

**必须修改的配置：**

```bash
# 生成随机密钥
SECRET_KEY=xxx  # 运行: openssl rand -hex 32

# 数据库密码
MYSQL_PASSWORD=xxx

# Redis 密码
REDIS_PASSWORD=xxx

# AI API Keys
QWEN_API_KEY=xxx
DASHSCOPE_API_KEY=xxx

# CORS 配置 - 添加你的 Vercel 域名
CORS_ORIGINS=["https://your-project.vercel.app"]
```

#### 步骤 4: 获取 SSL 证书

```bash
# 安装 certbot
apt update && apt install -y certbot

# 获取证书 (确保域名已解析到服务器 IP)
certbot certonly --standalone -d api.your-domain.com --email your@email.com --agree-tos

# 复制证书
mkdir -p docker/nginx/ssl
cp /etc/letsencrypt/live/api.your-domain.com/fullchain.pem docker/nginx/ssl/
cp /etc/letsencrypt/live/api.your-domain.com/privkey.pem docker/nginx/ssl/
```

#### 步骤 5: 更新 Nginx 配置

```bash
nano docker/nginx/nginx.conf

# 修改 server_name 为你的域名
server_name api.your-domain.com;
```

#### 步骤 6: 启动服务

```bash
docker-compose -f docker-compose.prod.yml up -d

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f backend
```

### 2.4 验证部署

访问以下地址确认：

| 地址 | 说明 |
|------|------|
| `https://api.your-domain.com` | 根路径 |
| `https://api.your-domain.com/health` | 健康检查 |
| `https://api.your-domain.com/docs` | API 文档 |

---

## 第三部分：数据库配置 (可选)

### 3.1 使用云数据库 (推荐生产环境)

| 数据库 | 推荐服务 |
|--------|----------|
| MySQL | 阿里云 RDS / 腾讯云 MySQL |
| Redis | 阿里云 Redis / 腾讯云 Redis |

配置示例：

```bash
# backend/.env
DATABASE_URL=mysql+pymysql://username:password@rm-xxxxx.mysql.rds.aliyuncs.com:3306/ai_agent_platform
REDIS_URL=redis://:password@r-xxxxx.redis.rds.aliyuncs.com:6379/0
```

---

## 第四部分：域名与 DNS 配置

### 4.1 域名配置示例

| 子域名 | 用途 | 指向 |
|--------|------|------|
| `www.your-domain.com` | 前端 | Vercel |
| `api.your-domain.com` | 后端 | 云服务器 IP |

### 4.2 DNS 记录

```
# 前端 (Vercel)
A     www    76.76.21.21

# 后端 (云服务器)
A     api    your-server-ip
```

---

## 第五部分：监控与维护

### 5.1 查看日志

```bash
# 后端日志
docker-compose -f docker-compose.prod.yml logs -f backend

# 所有服务日志
docker-compose -f docker-compose.prod.yml logs -f
```

### 5.2 更新代码

```bash
# 1. 拉取最新代码
git pull

# 2. 重新构建并启动
docker-compose -f docker-compose.prod.yml up -d --build

# 3. 清理旧镜像
docker image prune -f
```

### 5.3 备份数据

```bash
# 备份 MySQL
docker exec aiagent_mysql_prod mysqldump -u root -p ai_agent_platform > backup.sql

# 备份上传文件
tar -czf uploads-backup.tar.gz backend/uploads/
```

---

## 成本估算

| 项目 | 服务 | 月费 |
|------|------|------|
| 前端 | Vercel | $0 |
| 后端 | 阿里云 ECS 2核4GB | ¥60-100 |
| 数据库 | 使用云数据库 (可选) | ¥50-200 |
| 域名 | .com 域名 | ¥10/年 |
| **合计** | | **¥110-310/月** |

---

## 常见问题

### Q1: 前端无法连接后端 API？

检查：
1. 后端 CORS 配置是否包含前端域名
2. 后端服务是否正常运行
3. 防火墙是否开放 80/443 端口

### Q2: 如何设置自动部署？

- **前端**: Vercel 连接 Git 仓库，推送代码自动部署
- **后端**: 使用 CI/CD (GitHub Actions) 或 Webhook

### Q3: 如何优化成本？

- 前端使用 Vercel 免费版
- 后端使用按量计费的云服务器
- 数据库使用 Docker 部署而非云数据库

---

## 安全建议

1. **修改所有默认密码**
2. **定期更新系统和依赖**
3. **配置防火墙** (只开放必要端口)
4. **启用 HTTPS**
5. **定期备份数据**
6. **限制 API 访问频率**

---

## 联系支持

如有问题，请提交 Issue 或联系技术支持。
