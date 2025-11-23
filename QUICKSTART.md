# 快速上手指南

## 5分钟快速开始

### 步骤 1: 安装依赖

**Windows:**
```bash
# 双击运行或命令行执行
scripts\setup.bat
```

**Linux/Mac:**
```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### 步骤 2: 配置 API 密钥

编辑 `data/keys.txt` 文件，每行添加一个 MegaLLM API 密钥:

```
sk-your-first-api-key-here
sk-your-second-api-key-here
sk-your-third-api-key-here
```

至少需要添加 **1个** 密钥才能启动服务。

### 步骤 3: 启动服务

**Windows:**
```bash
.venv\Scripts\activate
python main.py
```

**Linux/Mac:**
```bash
source .venv/bin/activate
python main.py
```

看到以下信息表示启动成功:
```
INFO: Started server process
INFO: Uvicorn running on http://0.0.0.0:8000
```

### 步骤 4: 测试服务

打开新的终端窗口，运行测试脚本:

```bash
python scripts/test_api.py
```

或访问 API 文档:
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/health (健康检查)

## 基本使用

### Python 调用示例

```python
import requests

# 最简示例 - 使用默认模型 openai-gpt-oss-120b
response = requests.post(
    "http://localhost:8000/v1/chat/completions",
    json={
        "messages": [
            {"role": "user", "content": "你好"}
        ]
    }
)

print(response.json()['choices'][0]['message']['content'])

# 或指定具体模型
response = requests.post(
    "http://localhost:8000/v1/chat/completions",
    json={
        "model": "gpt-4",
        "messages": [
            {"role": "user", "content": "你好"}
        ]
    }
)
```

### 使用 OpenAI SDK

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="dummy"  # 任意值，服务会自动使用配置的密钥
)

# 不指定 model,使用默认模型 openai-gpt-oss-120b
response = client.chat.completions.create(
    messages=[{"role": "user", "content": "Hello!"}]
)

print(response.choices[0].message.content)
```

### cURL 调用

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "你好"}]
  }'
```

**提示**: `model` 参数可选,不传则使用默认模型 `openai-gpt-oss-120b`

## 支持的模型

可以在请求中使用以下模型:

- openai-gpt-oss-20b
- llama3.3-70b-instruct
- deepseek-r1-distill-llama-70b
- alibaba-qwen3-32b
- openai-gpt-oss-120b
- llama3-8b-instruct
- moonshotai/kimi-k2-instruct-0905
- deepseek-ai/deepseek-v3.1-terminus
- qwen/qwen3-next-80b-a3b-instruct
- deepseek-ai/deepseek-v3.1
- mistralai/mistral-nemotron
- minimaxai/minimax-m2
- 以及 MegaLLM 支持的其他模型

## 管理功能

### 查看服务状态

```bash
curl http://localhost:8000/health
```

### 重新加载密钥（无需重启服务）

```bash
curl -X POST http://localhost:8000/admin/reload-keys
```

### 重置失败的密钥

```bash
curl -X POST http://localhost:8000/admin/reset-failed-keys
```

## 常见问题

### 1. 启动失败：找不到密钥文件

**错误:** `FileNotFoundError: 密钥文件不存在`

**解决:** 确保 `data/keys.txt` 文件存在并包含至少一个密钥

### 2. 所有密钥都失败

**错误:** `503 Service Unavailable`

**解决:**
1. 检查密钥是否有效
2. 调用重置端点: `curl -X POST http://localhost:8000/admin/reset-failed-keys`

### 3. 请求超时

**解决:** 在 `.env` 文件中增加超时时间:
```
MEGALLM_TIMEOUT=180.0
```

## Docker 快速部署

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 下一步

- 查看完整文档: [README.md](README.md)
- 自定义配置: [.env.example](.env.example)
- 添加更多密钥以提高并发能力
- 使用 Nginx 做反向代理
- 部署到生产环境

## 获取帮助

如遇问题，请查看:
1. 日志文件: `logs/app.log`
2. API 文档: http://localhost:8000/docs
3. 项目 README: [README.md](README.md)
