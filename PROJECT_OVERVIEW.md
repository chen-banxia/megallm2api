# 项目总览

## 项目信息

- **项目名称**: MegaLLM API 代理服务
- **版本**: 1.0.0
- **Python 版本**: 3.8+ (推荐 3.11+, 开发测试 3.12)
- **框架**: FastAPI 0.109.0
- **许可证**: MIT

## 项目简介

高可用的 MegaLLM API 代理服务，提供多密钥轮询、自动重试、故障转移和上下文管理功能。完全兼容 OpenAI API 格式。

## 核心特性

### 1. 多密钥管理
- ✅ Round-Robin 轮询算法
- ✅ 自动故障隔离
- ✅ 密钥状态监控
- ✅ 热重载密钥（无需重启）

### 2. 高可用性
- ✅ 自动重试机制（指数退避）
- ✅ 故障转移（密钥切换）
- ✅ 健康检查端点
- ✅ 完善的错误处理

### 3. 上下文管理
- ✅ 12+ 模型上下文限制配置
- ✅ 智能 token 估算
- ✅ 超限友好提示
- ✅ 多轮对话支持

### 4. 流式响应
- ✅ SSE (Server-Sent Events) 支持
- ✅ 实时流式输出
- ✅ 完整的错误处理

### 5. 生产就绪
- ✅ Docker 容器化
- ✅ 多 worker 模式
- ✅ 结构化日志
- ✅ 性能监控

## 技术栈

### 核心依赖

| 层次 | 技术 | 版本 | 说明 |
|------|------|------|------|
| **Web 框架** | FastAPI | 0.109.0 | 高性能异步框架 |
| **ASGI 服务器** | Uvicorn | 0.27.0 | 支持 HTTP/2 |
| **数据验证** | Pydantic | 2.5.3 | Rust 核心，高性能 |
| **HTTP 客户端** | httpx | 0.26.0 | 异步 HTTP/2 |
| **重试机制** | tenacity | 8.2.3 | 智能重试 |
| **日志系统** | loguru | 0.7.2 | 简洁强大 |

### 依赖统计

- **核心包数量**: 8个
- **总依赖包数**: 约 40个
- **总大小**: 约 50MB
- **Docker 镜像**: 约 200MB

## 项目结构

```
megallm2api/
├── api/                    # API 路由
│   ├── __init__.py
│   └── routes.py          # 主要路由定义
├── config/                # 配置管理
│   ├── __init__.py
│   ├── settings.py        # 环境变量配置
│   └── model_config.py    # 模型上下文配置
├── core/                  # 核心模块
│   ├── __init__.py
│   ├── key_manager.py     # 密钥管理（轮询）
│   ├── http_client.py     # HTTP 客户端（重试）
│   └── proxy.py           # 代理逻辑
├── models/                # 数据模型
│   ├── __init__.py
│   └── schemas.py         # Pydantic 模型
├── utils/                 # 工具函数
│   ├── __init__.py
│   └── logger.py          # 日志配置
├── scripts/               # 脚本工具
│   ├── setup.sh          # Linux/Mac 安装脚本
│   ├── setup.bat         # Windows 安装脚本
│   ├── deploy.sh         # Docker 部署脚本
│   ├── test_api.py       # API 测试
│   ├── test_stream.py    # 流式测试
│   └── test_context_limit.py  # 上下文测试
├── tests/                 # 单元测试
│   ├── __init__.py
│   └── test_key_manager.py
├── data/                  # 数据文件
│   └── keys.txt          # API 密钥（gitignore）
├── logs/                  # 日志目录
├── docs/                  # 文档目录
│   └── 设计文档.md
├── main.py               # 主程序入口
├── Dockerfile            # Docker 镜像定义
├── docker-compose.yml    # Docker Compose 配置
├── requirements.txt      # 生产依赖
├── requirements-dev.txt  # 开发依赖
├── .env.example          # 环境变量示例
├── .dockerignore         # Docker 忽略文件
├── .gitignore           # Git 忽略文件
├── .python-version      # Python 版本标识
├── README.md            # 项目说明
├── QUICKSTART.md        # 快速开始
├── DOCKER_DEPLOY.md     # Docker 部署指南
├── DEPENDENCIES.md      # 依赖说明
└── PROJECT_OVERVIEW.md  # 本文件
```

## API 端点

### 聊天接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/v1/chat/completions` | 聊天补全（兼容 OpenAI） |

### 管理接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/v1/models` | 获取模型列表（带上下文信息） |
| GET | `/v1/models/{model_id}/info` | 获取指定模型信息 |
| GET | `/health` | 健康检查 |
| POST | `/admin/reload-keys` | 重新加载密钥 |
| POST | `/admin/reset-failed-keys` | 重置失败密钥 |

### 文档接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/docs` | Swagger UI |
| GET | `/redoc` | ReDoc 文档 |

## 支持的模型

| 模型 | 上下文长度 | 说明 |
|------|-----------|------|
| qwen/qwen3-next-80b-a3b-instruct | 262,000 | 最大上下文 |
| moonshotai/kimi-k2-instruct-0905 | 256,000 | 长上下文 |
| deepseek-ai/deepseek-v3.1-terminus | 164,000 | 高性能 |
| llama3.3-70b-instruct | 131,000 | 开源大模型 |
| alibaba-qwen3-32b | 131,000 | 阿里巴巴 |
| openai-gpt-oss-120b | 128,000 | 默认模型 |
| openai-gpt-oss-20b | 128,000 | 轻量模型 |
| deepseek-r1-distill-llama-70b | 128,000 | 蒸馏模型 |
| deepseek-ai/deepseek-v3.1 | 128,000 | DeepSeek V3 |
| mistralai/mistral-nemotron | 128,000 | Mistral |
| minimaxai/minimax-m2 | 128,000 | MiniMax |
| llama3-8b-instruct | 8,000 | 小型模型 |

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `MEGALLM_BASE_URL` | https://ai.megallm.io/v1 | MegaLLM API 地址 |
| `MEGALLM_TIMEOUT` | 120.0 | 请求超时（秒） |
| `MEGALLM_MAX_RETRIES` | 3 | 单密钥最大重试 |
| `MAX_KEY_RETRIES` | 3 | 最大密钥切换 |
| `HOST` | 0.0.0.0 | 监听地址 |
| `PORT` | 8000 | 监听端口 |
| `LOG_LEVEL` | INFO | 日志级别 |

## 部署方式

### 1. 本地开发

```bash
# 安装依赖
pip install -r requirements.txt

# 配置密钥
echo "sk-your-key" > data/keys.txt

# 启动服务
python main.py
```

### 2. Docker Compose（推荐）

```bash
# 配置密钥
echo "sk-your-key" > data/keys.txt

# 启动服务
docker compose up -d

# 查看日志
docker compose logs -f
```

### 3. Docker 手动部署

```bash
# 构建镜像
docker build -t megallm-proxy:latest .

# 运行容器
docker run -d \
  --name megallm-proxy \
  -p 8000:8000 \
  -v $(pwd)/data/keys.txt:/app/data/keys.txt:ro \
  megallm-proxy:latest
```

### 4. 生产部署（Nginx + Docker）

参考 [DOCKER_DEPLOY.md](DOCKER_DEPLOY.md) 获取完整部署指南。

## 性能指标

### 延迟

- **本地代理开销**: < 10ms
- **总延迟**: 主要取决于 MegaLLM API 响应时间
- **并发支持**: 4 workers × 20 连接 = 80+ 并发

### 资源使用

- **内存**: 约 500MB - 1GB（4 workers）
- **CPU**: 0.5 - 2 核（取决于负载）
- **磁盘**: < 1GB（包括日志）

### 推荐配置

**小型部署 (< 100 req/min):**
- CPU: 1 核
- 内存: 512MB
- Workers: 2

**中型部署 (< 1000 req/min):**
- CPU: 2 核
- 内存: 2GB
- Workers: 4

**大型部署 (> 1000 req/min):**
- CPU: 4 核
- 内存: 4GB
- Workers: 8

## 监控和日志

### 日志级别

- `DEBUG`: 详细调试信息
- `INFO`: 常规信息（默认）
- `WARNING`: 警告信息
- `ERROR`: 错误信息

### 日志位置

- 文件: `logs/app.log`
- 控制台: 彩色输出

### 监控指标

- 密钥使用统计
- 请求成功/失败率
- 上下文使用率
- 响应时间

## 安全建议

1. **密钥安全**
   - ✅ 使用 `chmod 600 data/keys.txt`
   - ✅ 不要提交密钥到 Git
   - ✅ 定期轮换密钥

2. **网络安全**
   - ✅ 使用 HTTPS (Nginx + Let's Encrypt)
   - ✅ 限制访问 IP
   - ✅ 配置防火墙

3. **应用安全**
   - ✅ 非 root 用户运行
   - ✅ 资源限制
   - ✅ 速率限制

## 故障排查

### 常见问题

1. **所有密钥失败**: 调用 `/admin/reset-failed-keys`
2. **请求超时**: 增加 `MEGALLM_TIMEOUT`
3. **上下文超限**: 减少消息数量或使用更大上下文模型
4. **端口占用**: 修改 `PORT` 环境变量

### 调试步骤

1. 查看日志: `docker compose logs -f`
2. 检查健康: `curl http://localhost:8000/health`
3. 测试 API: `curl -X POST http://localhost:8000/v1/chat/completions ...`

## 开发指南

### 添加新功能

1. 在相应模块添加代码
2. 编写单元测试
3. 更新文档
4. 提交 PR

### 运行测试

```bash
# 单元测试
pytest

# 覆盖率
pytest --cov=core --cov=api

# API 测试
python scripts/test_api.py
python scripts/test_stream.py
python scripts/test_context_limit.py
```

### 代码质量

```bash
# 格式化
black .

# 检查
flake8 .

# 类型检查
mypy .
```

## 文档索引

- [README.md](README.md) - 项目说明和完整文档
- [QUICKSTART.md](QUICKSTART.md) - 5分钟快速开始
- [DOCKER_DEPLOY.md](DOCKER_DEPLOY.md) - Docker 部署指南
- [DEPENDENCIES.md](DEPENDENCIES.md) - 依赖详细说明
- [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) - 本文件

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 联系方式

如有问题，请提交 GitHub Issue。

---

**最后更新**: 2025-01-23
**文档版本**: 1.0.0
