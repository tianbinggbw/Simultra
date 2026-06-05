#!/bin/bash
# Simultra - 启动脚本
# 用于 Mac 上启动 Simultra 服务

set -e

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_DIR="$(dirname "$SCRIPT_DIR")"

echo "=========================================="
echo "  Simultra - AI 同声传译"
echo "=========================================="
echo ""

# 检查 Ollama
check_ollama() {
    if ! command -v ollama &> /dev/null; then
        echo "❌ Ollama 未安装"
        echo ""
        echo "请先安装 Ollama:"
        echo "  brew install ollama"
        echo "  ollama pull llama3.2:3b"
        echo ""
        exit 1
    fi

    if ! pgrep -x "ollama" > /dev/null; then
        echo "⚠️  Ollama 未运行，正在启动..."
        nohup ollama serve > /tmp/ollama.log 2>&1 &
        sleep 3
    fi

    echo "✅ Ollama 已就绪"
}

# 检查 Python 依赖
check_python_deps() {
    echo ""
    echo "检查 Python 依赖..."

    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 未安装"
        echo ""
        echo "请安装 Python 3.10+"
        exit 1
    fi

    # 检查必要的包
    MISSING_DEPS=()
    for pkg in fastapi uvicorn funasr sounddevice; do
        if ! python3 -c "import $pkg" 2>/dev/null; then
            MISSING_DEPS+=($pkg)
        fi
    done

    if [ ${#MISSING_DEPS[@]} -ne 0 ]; then
        echo "❌ 缺少 Python 包: ${MISSING_DEPS[*]}"
        echo ""
        echo "请安装依赖:"
        echo "  cd $APP_DIR/python"
        echo "  pip install -r requirements.txt"
        echo ""
        exit 1
    fi

    echo "✅ Python 依赖已就绪"
}

# 启动后端服务
start_backend() {
    echo ""
    echo "启动后端服务..."

    # 杀掉旧的进程
    pkill -f "uvicorn main:app" 2>/dev/null || true

    # 启动新的后端
    cd "$APP_DIR/python"
    nohup python3 -m uvicorn main:app --host 127.0.0.1 --port 7860 > /tmp/simultra_backend.log 2>&1 &
    sleep 2

    # 检查是否启动成功
    if curl -s http://127.0.0.1:7860/health > /dev/null 2>&1; then
        echo "✅ 后端服务已启动 (http://127.0.0.1:7860)"
    else
        echo "❌ 后端服务启动失败，请查看日志:"
        echo "  tail -f /tmp/simultra_backend.log"
        exit 1
    fi
}

# 主流程
main() {
    check_ollama
    check_python_deps
    start_backend

    echo ""
    echo "=========================================="
    echo "  ✅ Simultra 已准备就绪！"
    echo ""
    echo "  后端: http://127.0.0.1:7860"
    echo "  前端: 打开 Simultra 应用"
    echo ""
    echo "  停止服务: ./stop.sh"
    echo "=========================================="
}

main "$@"