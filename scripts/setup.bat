@echo off
REM Windows 快速设置脚本

echo ===== MegaLLM Proxy Setup =====

REM 创建必要的目录
if not exist data mkdir data
if not exist logs mkdir logs

REM 复制配置文件
if not exist .env (
    echo 创建 .env 配置文件...
    copy .env.example .env
)

if not exist data\keys.txt (
    echo 创建 keys.txt 密钥文件...
    copy data\keys.txt.example data\keys.txt
    echo 请编辑 data\keys.txt 添加您的 API 密钥
)

REM 创建虚拟环境
if not exist .venv (
    echo 创建虚拟环境...
    python -m venv .venv
)

REM 激活虚拟环境并安装依赖
echo 安装依赖...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo ===== 设置完成 =====
echo.
echo 下一步操作：
echo 1. 编辑 data\keys.txt 添加您的 API 密钥（每行一个）
echo 2. （可选）编辑 .env 修改配置
echo 3. 启动服务：
echo    .venv\Scripts\activate.bat
echo    python main.py
echo.
pause
