# 依赖说明文档

本文档详细说明项目的所有依赖及其用途。

## 生产环境依赖 (requirements.txt)

### Web 框架

| 包名 | 版本 | 用途 |
|------|------|------|
| **fastapi** | 0.109.0 | 现代化的 Web 框架，提供自动 API 文档、数据验证等功能 |
| **uvicorn[standard]** | 0.27.0 | ASGI 服务器，支持 HTTP/2、WebSocket，高性能异步处理 |

**为什么选择 FastAPI？**
- 自动生成 OpenAPI (Swagger) 文档
- 基于 Pydantic 的数据验证
- 原生异步支持
- 类型提示和 IDE 支持

### 数据验证

| 包名 | 版本 | 用途 |
|------|------|------|
| **pydantic** | 2.5.3 | 强大的数据验证库，使用 Python 类型提示 |
| **pydantic-settings** | 2.1.0 | 环境变量和配置管理 |

**关键功能：**
- 请求/响应数据自动验证
- 类型转换和错误提示
- 环境变量自动加载

### HTTP 客户端

| 包名 | 版本 | 用途 |
|------|------|------|
| **httpx** | 0.26.0 | 现代异步 HTTP 客户端 |
| **tenacity** | 8.2.3 | 智能重试机制库 |

**httpx 特性：**
- 支持 HTTP/1.1 和 HTTP/2
- 异步和同步 API
- 连接池管理
- 超时控制

**tenacity 特性：**
- 指数退避重试
- 自定义重试条件
- 重试统计和日志

### 日志系统

| 包名 | 版本 | 用途 |
|------|------|------|
| **loguru** | 0.7.2 | 简单强大的日志库 |

**优势：**
- 简洁的 API
- 彩色输出
- 异步日志写入
- 自动日志轮转

### 其他

| 包名 | 版本 | 用途 |
|------|------|------|
| **python-multipart** | 0.0.6 | 处理表单数据和文件上传 |

## 开发环境依赖 (requirements-dev.txt)

### 测试工具

| 包名 | 版本 | 用途 |
|------|------|------|
| **pytest** | 8.0.0 | Python 测试框架 |
| **pytest-asyncio** | 0.23.4 | 异步测试支持 |
| **pytest-cov** | 4.1.0 | 测试覆盖率报告 |
| **pytest-mock** | 3.12.0 | Mock 对象支持 |

**使用示例：**
```bash
# 运行所有测试
pytest

# 查看覆盖率
pytest --cov=core --cov=api --cov-report=html
```

### 代码质量工具

| 包名 | 版本 | 用途 |
|------|------|------|
| **black** | 24.1.1 | 代码格式化工具 |
| **flake8** | 7.0.0 | 代码风格检查 |
| **isort** | 5.13.2 | import 语句排序 |
| **mypy** | 1.8.0 | 静态类型检查 |

**使用示例：**
```bash
# 格式化代码
black .

# 检查代码风格
flake8 .

# 排序 imports
isort .

# 类型检查
mypy .
```

### API 测试客户端

| 包名 | 版本 | 用途 |
|------|------|------|
| **requests** | 2.31.0 | 用于测试脚本和示例代码 |
| **openai** | 1.12.0 | OpenAI SDK，用于兼容性测试 |

### 开发辅助工具

| 包名 | 版本 | 用途 |
|------|------|------|
| **ipython** | 8.21.0 | 增强的 Python REPL |
| **ipdb** | 0.13.13 | IPython debugger |
| **python-dotenv** | 1.0.1 | 本地 .env 文件支持 |

## 版本兼容性

### Python 版本要求

- **最低版本**: Python 3.8
- **推荐版本**: Python 3.11+
- **开发测试版本**: Python 3.12
- **支持版本**: 3.8, 3.9, 3.10, 3.11, 3.12

### 操作系统支持

- ✅ Windows 10/11
- ✅ Linux (Ubuntu 20.04+, CentOS 7+, Debian 10+)
- ✅ macOS 11+

## 安装指南

### 生产环境

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 开发环境

```bash
# 先安装生产依赖
pip install -r requirements.txt

# 再安装开发依赖
pip install -r requirements-dev.txt
```

### Docker 环境

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# 仅安装生产依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**说明**: Docker 镜像使用 Python 3.12，与开发环境版本一致，确保最佳兼容性。

## 依赖更新策略

### 安全更新

定期检查安全漏洞：

```bash
# 安装安全检查工具
pip install safety

# 检查已知漏洞
safety check

# 或使用 pip-audit
pip install pip-audit
pip-audit
```

### 版本升级

```bash
# 查看过时的包
pip list --outdated

# 升级所有包（谨慎！）
pip install --upgrade -r requirements.txt

# 更新 requirements.txt
pip freeze > requirements.txt
```

### 依赖锁定

建议使用 `pip-tools` 锁定依赖版本：

```bash
# 安装 pip-tools
pip install pip-tools

# 编译依赖（生成 requirements.txt）
pip-compile requirements.in

# 同步环境
pip-sync requirements.txt
```

## 常见问题

### Q1: 为什么使用 httpx 而不是 requests？

**A:** httpx 支持异步 I/O 和 HTTP/2，性能更好，更适合高并发场景。

### Q2: tenacity 的重试策略是什么？

**A:**
- 最大重试次数: 3 次
- 等待策略: 指数退避 (1s, 2s, 4s, ...)
- 重试条件: 仅网络错误和超时

### Q3: 为什么需要 pydantic-settings？

**A:** 它提供了更好的环境变量管理，支持类型验证和默认值。

### Q4: 开发依赖是必需的吗？

**A:** 不是。生产环境只需要 `requirements.txt` 中的依赖。

## 许可证信息

所有依赖均为开源软件，主要许可证包括：

- **MIT License**: FastAPI, httpx, loguru, pytest
- **BSD License**: pydantic, uvicorn
- **Apache 2.0**: tenacity

详细许可证信息请查看各包的官方文档。

## 相关链接

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [httpx 官方文档](https://www.python-httpx.org/)
- [Pydantic 官方文档](https://docs.pydantic.dev/)
- [pytest 官方文档](https://docs.pytest.org/)
- [loguru 官方文档](https://loguru.readthedocs.io/)
