# MegaLLM API 代理服务

高可用的 MegaLLM API 代理服务，支持多密钥轮询、自动重试和故障转移。

## 特性

- **多密钥轮询**: 支持多个 API 密钥轮询使用，提高可用性和并发能力
- **自动重试**: 内置智能重试机制，自动处理临时故障
- **故障转移**: 密钥失败时自动切换到下一个可用密钥
- **健康检查**: 实时监控服务和密钥状态
- **OpenAI 兼容**: 完全兼容 OpenAI API 格式
- **高性能**: 基于 FastAPI 和 httpx 的异步架构
- **完善的日志**: 使用 loguru 提供结构化日志

## 系统架构

```
megallm2api/
├── api/              # API路由
├── config/           # 配置管理
├── core/             # 核心模块
│   ├── key_manager.py    # 密钥管理(轮询)
│   ├── http_client.py    # HTTP客户端(重试)
│   └── proxy.py          # 代理逻辑
├── models/           # 数据模型
├── utils/            # 工具函数
├── tests/            # 单元测试
├── data/             # 数据文件
│   └── keys.txt      # API密钥
└── main.py           # 主程序入口
```

## 快速开始

### 1. 环境准备

**Python 版本要求:**
- 最小版本: Python 3.8+
- 推荐版本: Python 3.11+
- 开发测试版本: Python 3.12

```bash
# 克隆项目
git clone <your-repo-url>
cd megallm2api

# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 安装生产依赖
pip install -r requirements.txt

# 如果是开发环境，还需要安装开发工具
pip install -r requirements-dev.txt
```

### 2. 配置

#### 配置密钥文件

```bash
# 复制示例文件
cp data/keys.txt.example data/keys.txt

# 编辑 data/keys.txt，每行添加一个 API 密钥
# sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# sk-yyyyyyyyyyyyyyyyyyyyyyyyyyyyyy
```

#### 配置环境变量（可选）

```bash
# 复制示例文件
cp .env.example .env

# 根据需要修改配置
```

主要配置项：

- `MEGALLM_BASE_URL`: MegaLLM API 地址（默认: https://ai.megallm.io/v1）
- `MEGALLM_TIMEOUT`: 请求超时时间（默认: 120秒）
- `MEGALLM_MAX_RETRIES`: 单个密钥最大重试次数（默认: 3）
- `MAX_KEY_RETRIES`: 密钥失败后最大切换次数（默认: 3）
- `HOST`: 服务监听地址（默认: 0.0.0.0）
- `PORT`: 服务端口（默认: 8000）

### 3. 运行服务

```bash
# 开发模式（自动重载）
python main.py

# 或使用 uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 生产模式
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

服务启动后访问：

- API 文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

## API 使用

### 聊天补全

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "你好！"}
    ]
  }'
```

**注意**:
- `model` 参数是可选的,不传则默认使用 `openai-gpt-oss-120b`
- 其他参数(如 `temperature`、`max_tokens` 等)由后端自动设置默认值

### Python 示例

```python
import requests

# 最简示例 - 使用默认模型
response = requests.post(
    "http://localhost:8000/v1/chat/completions",
    json={
        "messages": [
            {"role": "user", "content": "介绍一下Python"}
        ]
    }
)

result = response.json()
print(result['choices'][0]['message']['content'])

# 指定模型
response = requests.post(
    "http://localhost:8000/v1/chat/completions",
    json={
        "model": "gpt-4",
        "messages": [
            {"role": "system", "content": "你是一个有用的助手"},
            {"role": "user", "content": "介绍一下Python"}
        ]
    }
)
```

### 使用 OpenAI SDK

```python
from openai import OpenAI

# 指向本地代理服务
client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="dummy"  # 代理服务会自动管理真实密钥
)

# 不指定 model,使用默认模型 openai-gpt-oss-120b
response = client.chat.completions.create(
    messages=[
        {"role": "user", "content": "Hello!"}
    ]
)

print(response.choices[0].message.content)

# 或指定具体模型
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "Hello!"}
    ]
)
```

## 管理端点

### 健康检查

```bash
curl http://localhost:8000/health
```

返回示例：

```json
{
  "status": "healthy",
  "key_stats": {
    "total": 3,
    "available": 3,
    "failed": 0,
    "current_index": 1
  },
  "version": "1.0.0"
}
```

### 重新加载密钥

```bash
curl -X POST http://localhost:8000/admin/reload-keys
```

### 重置失败的密钥

```bash
curl -X POST http://localhost:8000/admin/reset-failed-keys
```

### 获取模型列表

```bash
curl http://localhost:8000/v1/models
```

## 高可用特性详解

### 1. 密钥轮询机制

- **Round-Robin 算法**: 自动轮换使用多个密钥，均衡负载
- **故障隔离**: 失败的密钥自动标记并跳过
- **自动恢复**: 支持手动重置失败密钥

### 2. 自动重试机制

- **指数退避**: 使用 tenacity 库实现智能重试
- **重试条件**: 仅对超时和网络错误重试
- **快速失败**: 4xx 客户端错误不重试，直接返回

### 3. 故障转移

```
请求 -> 密钥1(失败) -> 密钥2(失败) -> 密钥3(成功)
      ↓             ↓
   标记失败      标记失败
```

### 4. 监控和日志

- 每个请求的详细日志
- 密钥使用统计
- 失败原因追踪
- 性能指标记录

## 测试

```bash
# 确保已安装开发依赖
pip install -r requirements-dev.txt

# 运行单元测试
pytest

# 查看测试覆盖率
pytest --cov=core --cov=api --cov-report=html

# 运行特定测试
pytest tests/test_key_manager.py -v

# 测试 API 功能
python scripts/test_api.py

# 测试流式响应
python scripts/test_stream.py
```

## 部署建议

### Docker 部署

创建 `Dockerfile`:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

构建和运行:

```bash
docker build -t megallm-proxy .
docker run -d -p 8000:8000 \
  -v $(pwd)/data/keys.txt:/app/data/keys.txt \
  -v $(pwd)/logs:/app/logs \
  megallm-proxy
```

### Systemd 服务

创建 `/etc/systemd/system/megallm-proxy.service`:

```ini
[Unit]
Description=MegaLLM Proxy Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/megallm2api
Environment="PATH=/opt/megallm2api/.venv/bin"
ExecStart=/opt/megallm2api/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务:

```bash
sudo systemctl daemon-reload
sudo systemctl enable megallm-proxy
sudo systemctl start megallm-proxy
```

### Nginx 反向代理

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 180s;
    }
}
```

## 性能优化

1. **使用多个 worker**: `uvicorn main:app --workers 4`
2. **启用 HTTP/2**: 已在 httpx 客户端中启用
3. **连接池**: 配置了合理的连接池大小
4. **异步日志**: loguru 使用 enqueue=True 异步写入

## 常见问题

### Q: 所有密钥都失败怎么办？

A: 服务会返回 503 错误。可以通过 `/admin/reset-failed-keys` 端点重置失败的密钥。

### Q: 如何添加新密钥？

A: 编辑 `data/keys.txt` 文件添加新密钥，然后调用 `/admin/reload-keys` 端点重新加载。

### Q: 支持流式响应吗？

A: 当前版本支持 `stream` 参数，但需要确保上游 API 支持。

### Q: 如何限制速率？

A: 可以在 Nginx 层面添加限流，或使用 FastAPI 的限流中间件。

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

如有问题，请提交 GitHub Issue。
