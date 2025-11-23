# Docker 部署指南

本文档详细说明如何在服务器上使用 Docker 部署 MegaLLM API 代理服务。

## 目录

- [前置要求](#前置要求)
- [快速部署](#快速部署)
- [详细步骤](#详细步骤)
- [配置说明](#配置说明)
- [生产部署](#生产部署)
- [维护管理](#维护管理)
- [故障排查](#故障排查)

---

## 前置要求

### 1. 服务器要求

- **操作系统**: Linux (推荐 Ubuntu 20.04+ / CentOS 8+)
- **CPU**: 2核+
- **内存**: 2GB+
- **磁盘**: 10GB+
- **网络**: 可访问外网（访问 MegaLLM API）

### 2. 安装 Docker

**Ubuntu/Debian:**

```bash
# 更新软件包
sudo apt-get update

# 安装依赖
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# 添加 Docker 官方 GPG 密钥
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
    sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# 设置 Docker 仓库
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 安装 Docker
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 启动 Docker
sudo systemctl start docker
sudo systemctl enable docker

# 验证安装
docker --version
docker compose version
```

**CentOS/RHEL:**

```bash
# 安装依赖
sudo yum install -y yum-utils

# 添加 Docker 仓库
sudo yum-config-manager \
    --add-repo \
    https://download.docker.com/linux/centos/docker-ce.repo

# 安装 Docker
sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 启动 Docker
sudo systemctl start docker
sudo systemctl enable docker

# 验证安装
docker --version
docker compose version
```

### 3. 配置 Docker 权限（可选）

```bash
# 将当前用户添加到 docker 组
sudo usermod -aG docker $USER

# 重新登录或运行
newgrp docker

# 测试（无需 sudo）
docker ps
```

---

## 快速部署

### 方式一：使用 Docker Compose（推荐）

```bash
# 1. 上传项目到服务器
cd /opt
git clone <your-repo-url> megallm2api
cd megallm2api

# 或使用 scp 上传
# scp -r ./megallm2api user@server:/opt/

# 2. 配置密钥文件
cat > data/keys.txt << 'EOF'
sk-your-api-key-1
sk-your-api-key-2
sk-your-api-key-3
EOF

# 3. 构建并启动
docker compose up -d

# 4. 查看日志
docker compose logs -f

# 5. 测试服务
curl http://localhost:8000/health
```

### 方式二：使用 Docker 命令

```bash
# 1. 构建镜像
docker build -t megallm-proxy:latest .

# 2. 创建数据目录
mkdir -p /opt/megallm-data/logs

# 3. 创建密钥文件
cat > /opt/megallm-data/keys.txt << 'EOF'
sk-your-api-key-1
sk-your-api-key-2
EOF

# 4. 运行容器
docker run -d \
  --name megallm-proxy \
  --restart unless-stopped \
  -p 8000:8000 \
  -v /opt/megallm-data/keys.txt:/app/data/keys.txt:ro \
  -v /opt/megallm-data/logs:/app/logs \
  -e LOG_LEVEL=INFO \
  megallm-proxy:latest

# 5. 查看日志
docker logs -f megallm-proxy

# 6. 测试服务
curl http://localhost:8000/health
```

---

## 详细步骤

### 步骤 1: 准备项目文件

#### 1.1 上传项目到服务器

```bash
# 方法 1: Git 克隆
ssh user@your-server
cd /opt
git clone https://github.com/your-username/megallm2api.git
cd megallm2api

# 方法 2: SCP 上传
# 在本地执行
scp -r ./megallm2api user@your-server:/opt/

# 方法 3: 使用 rsync
rsync -avz --exclude='.git' --exclude='__pycache__' \
  ./megallm2api/ user@your-server:/opt/megallm2api/
```

#### 1.2 验证文件结构

```bash
cd /opt/megallm2api
tree -L 2 -a

# 应该看到:
# ├── Dockerfile
# ├── docker-compose.yml
# ├── requirements.txt
# ├── main.py
# ├── api/
# ├── config/
# ├── core/
# ├── models/
# ├── data/
# └── logs/
```

### 步骤 2: 配置环境

#### 2.1 创建密钥文件

```bash
# 确保 data 目录存在
mkdir -p data

# 创建密钥文件
nano data/keys.txt

# 或使用 vim
vim data/keys.txt

# 内容格式（每行一个密钥）：
sk-mega-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
sk-mega-yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy
sk-mega-zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz
```

#### 2.2 创建环境变量文件（可选）

```bash
# 复制示例文件
cp .env.example .env

# 编辑配置
nano .env

# 示例内容：
# MEGALLM_BASE_URL=https://ai.megallm.io/v1
# MEGALLM_TIMEOUT=120.0
# MEGALLM_MAX_RETRIES=3
# MAX_KEY_RETRIES=3
# HOST=0.0.0.0
# PORT=8000
# LOG_LEVEL=INFO
```

#### 2.3 创建日志目录

```bash
# 创建日志目录并设置权限
mkdir -p logs
chmod 755 logs
```

### 步骤 3: 构建镜像

```bash
# 使用 Docker Compose 构建
docker compose build

# 或使用 Docker 命令构建
docker build -t megallm-proxy:latest .

# 查看构建的镜像
docker images | grep megallm-proxy

# 预期输出：
# REPOSITORY       TAG       IMAGE ID       CREATED          SIZE
# megallm-proxy    latest    abc123def456   10 seconds ago   ~200MB
```

**镜像大小说明：**
- 基础镜像 (python:3.12-slim): ~130MB
- 应用依赖 (8个核心包): ~50MB
- 应用代码: ~5MB
- 总计: 约 **200MB**（优化后）

**优化技巧：**
- ✅ 使用 slim 镜像而非 full 镜像
- ✅ 多阶段构建（如需要）
- ✅ .dockerignore 排除不必要文件
- ✅ 使用 `--no-cache-dir` 安装依赖

### 步骤 4: 启动服务

```bash
# 使用 Docker Compose 启动
docker compose up -d

# 查看容器状态
docker compose ps

# 或使用 Docker 命令启动
docker run -d \
  --name megallm-proxy \
  --restart unless-stopped \
  -p 8000:8000 \
  -v $(pwd)/data/keys.txt:/app/data/keys.txt:ro \
  -v $(pwd)/logs:/app/logs \
  -e LOG_LEVEL=INFO \
  megallm-proxy:latest

# 查看容器状态
docker ps | grep megallm-proxy
```

### 步骤 5: 验证部署

```bash
# 1. 查看容器日志
docker compose logs -f
# 或
docker logs -f megallm-proxy

# 2. 健康检查
curl http://localhost:8000/health

# 应该返回:
# {
#   "status": "healthy",
#   "key_stats": {
#     "total": 3,
#     "available": 3,
#     "failed": 0
#   },
#   "version": "1.0.0"
# }

# 3. 测试聊天接口
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "你好"}
    ]
  }'

# 4. 查看 API 文档
curl http://localhost:8000/docs
# 或在浏览器访问: http://your-server-ip:8000/docs
```

---

## 配置说明

### Docker Compose 配置

`docker-compose.yml` 主要配置项：

```yaml
ports:
  - "8000:8000"          # 端口映射（主机:容器）

volumes:
  - ./data/keys.txt:/app/data/keys.txt:ro  # 密钥文件（只读）
  - ./logs:/app/logs                        # 日志目录（读写）
  - ./.env:/app/.env:ro                     # 环境变量（可选）

environment:
  - LOG_LEVEL=INFO      # 日志级别: DEBUG, INFO, WARNING, ERROR
  - HOST=0.0.0.0        # 监听地址
  - PORT=8000           # 监听端口

restart: unless-stopped  # 自动重启策略

deploy:
  resources:
    limits:
      cpus: '2.0'       # CPU 限制
      memory: 2G        # 内存限制
```

### 环境变量说明

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `MEGALLM_BASE_URL` | https://ai.megallm.io/v1 | MegaLLM API 地址 |
| `MEGALLM_TIMEOUT` | 120.0 | 请求超时时间（秒） |
| `MEGALLM_MAX_RETRIES` | 3 | 单个密钥最大重试次数 |
| `MAX_KEY_RETRIES` | 3 | 密钥失败后最大切换次数 |
| `HOST` | 0.0.0.0 | 服务监听地址 |
| `PORT` | 8000 | 服务端口 |
| `LOG_LEVEL` | INFO | 日志级别 |

---

## 生产部署

### 1. 使用 Nginx 反向代理

#### 1.1 安装 Nginx

```bash
# Ubuntu/Debian
sudo apt-get install -y nginx

# CentOS/RHEL
sudo yum install -y nginx

# 启动 Nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

#### 1.2 配置反向代理

创建 Nginx 配置文件 `/etc/nginx/sites-available/megallm-proxy`:

```nginx
upstream megallm_backend {
    server 127.0.0.1:8000;

    # 如果部署多个实例
    # server 127.0.0.1:8001;
    # server 127.0.0.1:8002;

    keepalive 32;
}

server {
    listen 80;
    server_name api.yourdomain.com;  # 修改为你的域名

    # 访问日志
    access_log /var/log/nginx/megallm-access.log;
    error_log /var/log/nginx/megallm-error.log;

    # 客户端请求体大小限制
    client_max_body_size 10M;

    location / {
        proxy_pass http://megallm_backend;

        # 代理头设置
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # 超时设置
        proxy_connect_timeout 180s;
        proxy_send_timeout 180s;
        proxy_read_timeout 180s;

        # 缓冲设置
        proxy_buffering off;
        proxy_request_buffering off;

        # HTTP/1.1 支持
        proxy_http_version 1.1;
        proxy_set_header Connection "";
    }

    # 健康检查端点
    location /health {
        proxy_pass http://megallm_backend/health;
        access_log off;
    }
}
```

启用配置：

```bash
# 创建软链接
sudo ln -s /etc/nginx/sites-available/megallm-proxy \
           /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重载配置
sudo systemctl reload nginx
```

#### 1.3 配置 HTTPS (使用 Let's Encrypt)

```bash
# 安装 Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d api.yourdomain.com

# 自动续期（已自动配置 cron）
sudo certbot renew --dry-run
```

### 2. 配置防火墙

```bash
# UFW (Ubuntu)
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8000/tcp  # 如果需要直接访问
sudo ufw enable

# firewalld (CentOS)
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

### 3. 设置系统服务（可选）

创建 systemd 服务文件 `/etc/systemd/system/megallm-proxy.service`:

```ini
[Unit]
Description=MegaLLM API Proxy Service
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/megallm2api
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

启用服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable megallm-proxy
sudo systemctl start megallm-proxy
sudo systemctl status megallm-proxy
```

---

## 维护管理

### 日常操作

```bash
# 查看运行状态
docker compose ps

# 查看日志
docker compose logs -f

# 查看实时日志（最近 100 行）
docker compose logs --tail=100 -f

# 重启服务
docker compose restart

# 停止服务
docker compose stop

# 启动服务
docker compose start

# 完全删除容器（保留数据）
docker compose down
```

### 更新部署

```bash
# 1. 拉取最新代码
cd /opt/megallm2api
git pull

# 2. 重新构建镜像
docker compose build

# 3. 重启服务
docker compose up -d

# 4. 查看日志确认
docker compose logs -f
```

### 备份和恢复

```bash
# 备份密钥和配置
tar -czf megallm-backup-$(date +%Y%m%d).tar.gz \
  data/keys.txt .env

# 恢复
tar -xzf megallm-backup-20250123.tar.gz
```

### 日志管理

```bash
# 查看日志文件大小
du -sh logs/

# 清理旧日志（保留最近 7 天）
find logs/ -name "*.log" -mtime +7 -delete

# 配置日志轮转
cat > /etc/logrotate.d/megallm-proxy << 'EOF'
/opt/megallm2api/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 appuser appuser
}
EOF
```

### 监控

```bash
# 查看容器资源使用
docker stats megallm-proxy

# 查看详细信息
docker inspect megallm-proxy

# 健康检查
watch -n 5 'curl -s http://localhost:8000/health | jq'
```

---

## 故障排查

### 1. 容器无法启动

```bash
# 查看详细错误
docker compose logs

# 检查配置文件
docker compose config

# 检查端口占用
sudo lsof -i:8000

# 检查磁盘空间
df -h

# 检查 Docker 状态
sudo systemctl status docker
```

### 2. 无法访问服务

```bash
# 检查容器是否运行
docker compose ps

# 检查端口映射
docker port megallm-proxy

# 检查防火墙
sudo ufw status
sudo firewall-cmd --list-all

# 测试本地连接
curl http://localhost:8000/health

# 测试外部连接
curl http://your-server-ip:8000/health
```

### 3. 密钥错误

```bash
# 检查密钥文件
cat data/keys.txt

# 重新加载密钥（无需重启）
curl -X POST http://localhost:8000/admin/reload-keys

# 重置失败的密钥
curl -X POST http://localhost:8000/admin/reset-failed-keys
```

### 4. 性能问题

```bash
# 增加 worker 数量
# 编辑 Dockerfile，修改启动命令:
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "8"]

# 重新构建
docker compose build
docker compose up -d

# 调整资源限制
# 编辑 docker-compose.yml 中的 deploy.resources 部分
```

### 5. 查看详细日志

```bash
# 进入容器查看
docker compose exec megallm-proxy bash

# 查看应用日志
tail -f /app/logs/app.log

# 退出容器
exit
```

---

## 安全建议

1. **密钥文件权限**
```bash
chmod 600 data/keys.txt
```

2. **使用环境变量而非硬编码**
```bash
# 不要在代码中硬编码密钥
# 使用环境变量或密钥文件
```

3. **限制访问IP（可选）**
```nginx
# 在 Nginx 配置中
allow 192.168.1.0/24;
deny all;
```

4. **启用速率限制**
```nginx
# 在 Nginx 配置中
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
limit_req zone=api_limit burst=20;
```

5. **定期更新**
```bash
# 更新系统包
sudo apt-get update && sudo apt-get upgrade -y

# 更新 Docker
sudo apt-get install -y docker-ce docker-ce-cli containerd.io
```

---

## 性能优化

### 1. 调整 Worker 数量

根据 CPU 核心数调整：

```dockerfile
# Dockerfile 中
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "8"]

# 推荐公式: workers = (2 * CPU_CORES) + 1
```

### 2. 配置连接池

在代码中已优化，可在 `.env` 中调整：

```bash
# HTTP 连接池设置（如需要可添加）
HTTP_POOL_CONNECTIONS=100
HTTP_POOL_MAXSIZE=100
```

### 3. 启用缓存（如适用）

可以在 Nginx 层面添加缓存：

```nginx
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m max_size=1g;

location / {
    proxy_cache api_cache;
    proxy_cache_valid 200 1m;
    proxy_cache_key "$scheme$request_method$host$request_uri";
}
```

---

## 总结

这个部署方案提供了：

- ✅ 完整的 Docker 容器化部署
- ✅ 生产级别的配置（非 root 用户、资源限制）
- ✅ 健康检查和自动重启
- ✅ Nginx 反向代理配置
- ✅ HTTPS 支持
- ✅ 日志管理和监控
- ✅ 故障排查指南

根据实际需求选择部署方式，建议生产环境使用 Nginx + Docker Compose 方案。
