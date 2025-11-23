#!/bin/bash

##############################################################################
# MegaLLM API 代理服务 - 快速部署脚本
#
# 用法:
#   chmod +x scripts/deploy.sh
#   ./scripts/deploy.sh
#
##############################################################################

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 打印函数
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo ""
    echo "========================================"
    echo " $1"
    echo "========================================"
    echo ""
}

# 检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 检查 Docker
check_docker() {
    print_header "检查 Docker 环境"

    if ! command_exists docker; then
        print_error "Docker 未安装，请先安装 Docker"
        echo ""
        echo "Ubuntu/Debian:"
        echo "  curl -fsSL https://get.docker.com | sh"
        echo ""
        echo "CentOS/RHEL:"
        echo "  sudo yum install -y docker-ce docker-ce-cli containerd.io"
        echo ""
        exit 1
    fi

    if ! command_exists docker compose 2>/dev/null && ! command_exists docker-compose; then
        print_error "Docker Compose 未安装"
        exit 1
    fi

    print_info "Docker: $(docker --version)"
    print_info "Docker Compose: $(docker compose version 2>/dev/null || docker-compose --version)"

    # 检查 Docker 服务状态
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker 服务未运行，请启动 Docker"
        echo "  sudo systemctl start docker"
        exit 1
    fi

    print_info "Docker 服务运行正常 ✓"
}

# 检查密钥文件
check_keys() {
    print_header "检查密钥文件"

    if [ ! -f "data/keys.txt" ]; then
        print_warn "密钥文件 data/keys.txt 不存在"

        # 创建目录
        mkdir -p data

        # 提示用户输入
        echo ""
        echo "请输入至少一个 MegaLLM API 密钥:"
        echo "(输入密钥后按 Enter，输入空行完成)"
        echo ""

        > data/keys.txt  # 清空文件

        while true; do
            read -r -p "密钥 (或直接 Enter 完成): " key
            if [ -z "$key" ]; then
                break
            fi
            echo "$key" >> data/keys.txt
        done

        # 检查是否至少有一个密钥
        if [ ! -s data/keys.txt ]; then
            print_error "至少需要一个密钥才能启动服务"
            rm -f data/keys.txt
            exit 1
        fi
    fi

    # 统计密钥数量
    key_count=$(grep -c ^ data/keys.txt || echo 0)
    print_info "找到 $key_count 个密钥 ✓"

    # 设置文件权限
    chmod 600 data/keys.txt
    print_info "密钥文件权限已设置 ✓"
}

# 创建环境变量文件
create_env() {
    print_header "配置环境变量"

    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_info "从 .env.example 创建 .env 文件 ✓"
        else
            # 创建基本的 .env 文件
            cat > .env << 'EOF'
# MegaLLM API 配置
MEGALLM_BASE_URL=https://ai.megallm.io/v1
MEGALLM_TIMEOUT=120.0
MEGALLM_MAX_RETRIES=3
MAX_KEY_RETRIES=3

# 服务配置
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
EOF
            print_info "创建默认 .env 文件 ✓"
        fi
    else
        print_info ".env 文件已存在 ✓"
    fi
}

# 创建必要的目录
create_directories() {
    print_header "创建目录"

    mkdir -p logs data
    chmod 755 logs data

    print_info "目录创建完成 ✓"
}

# 构建镜像
build_image() {
    print_header "构建 Docker 镜像"

    print_info "开始构建镜像..."

    if docker compose build; then
        print_info "镜像构建成功 ✓"
    else
        print_error "镜像构建失败"
        exit 1
    fi
}

# 启动服务
start_service() {
    print_header "启动服务"

    print_info "启动容器..."

    if docker compose up -d; then
        print_info "服务启动成功 ✓"
    else
        print_error "服务启动失败"
        exit 1
    fi

    # 等待服务启动
    print_info "等待服务就绪..."
    sleep 5
}

# 健康检查
health_check() {
    print_header "健康检查"

    max_attempts=10
    attempt=0

    while [ $attempt -lt $max_attempts ]; do
        if curl -f -s http://localhost:8000/health >/dev/null 2>&1; then
            print_info "服务健康检查通过 ✓"

            # 显示详细信息
            echo ""
            echo "服务状态:"
            curl -s http://localhost:8000/health | python3 -m json.tool 2>/dev/null || \
            curl -s http://localhost:8000/health

            return 0
        fi

        attempt=$((attempt + 1))
        print_warn "等待服务启动... ($attempt/$max_attempts)"
        sleep 3
    done

    print_error "健康检查失败，请查看日志"
    echo ""
    echo "查看日志:"
    echo "  docker compose logs -f"
    echo ""
    return 1
}

# 显示部署信息
show_info() {
    print_header "部署完成"

    # 获取服务器 IP
    server_ip=$(hostname -I | awk '{print $1}' || echo "localhost")

    echo ""
    echo "🎉 MegaLLM API 代理服务已成功部署！"
    echo ""
    echo "访问地址:"
    echo "  - 本地: http://localhost:8000"
    echo "  - 外部: http://$server_ip:8000"
    echo ""
    echo "API 文档:"
    echo "  - Swagger UI: http://$server_ip:8000/docs"
    echo "  - ReDoc: http://$server_ip:8000/redoc"
    echo ""
    echo "常用命令:"
    echo "  查看日志:    docker compose logs -f"
    echo "  查看状态:    docker compose ps"
    echo "  重启服务:    docker compose restart"
    echo "  停止服务:    docker compose stop"
    echo "  启动服务:    docker compose start"
    echo "  删除容器:    docker compose down"
    echo ""
    echo "测试命令:"
    echo "  curl http://localhost:8000/health"
    echo ""
    echo "  curl -X POST http://localhost:8000/v1/chat/completions \\"
    echo "    -H \"Content-Type: application/json\" \\"
    echo "    -d '{\"messages\":[{\"role\":\"user\",\"content\":\"你好\"}]}'"
    echo ""
}

# 主函数
main() {
    echo ""
    echo "=========================================="
    echo "  MegaLLM API 代理服务 - 部署脚本"
    echo "=========================================="
    echo ""

    # 检查是否在项目根目录
    if [ ! -f "Dockerfile" ] || [ ! -f "docker-compose.yml" ]; then
        print_error "请在项目根目录运行此脚本"
        exit 1
    fi

    # 执行部署步骤
    check_docker
    create_directories
    check_keys
    create_env
    build_image
    start_service

    # 健康检查
    if health_check; then
        show_info
        exit 0
    else
        print_error "部署失败，请查看日志排查问题"
        echo ""
        echo "查看日志:"
        echo "  docker compose logs"
        echo ""
        exit 1
    fi
}

# 运行主函数
main
