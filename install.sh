#!/bin/bash
# Simultra - 安装脚本
# 在 Mac 上首次运行时执行

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=========================================="
echo "  Simultra 安装程序"
echo "=========================================="
echo ""

# 检查系统
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "⚠️  警告: 此脚本应在 macOS 上运行"
fi

# 安装 Homebrew 如果没有
if ! command -v brew &> /dev/null; then
    echo "安装 Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# 安装 Python
if ! command -v python3 &> /dev/null; then
    echo "安装 Python 3.11..."
    brew install python@3.11
fi

# 安装 Rust (Tauri 需要)
if ! command -v cargo &> /dev/null; then
    echo "安装 Rust..."
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    source "$HOME/.cargo/env"
fi

# 检查 Ollama
if ! command -v ollama &> /dev/null; then
    echo "安装 Ollama..."
    brew install ollama

    echo "下载翻译模型 (llama3.2:3b)..."
    ollama pull llama3.2:3b

    echo "下载中文模型 (qwen2.5:7b)..."
    ollama pull qwen2.5:7b
fi

# 安装 Python 依赖
echo ""
echo "安装 Python 依赖..."
cd "$SCRIPT_DIR/python"
pip3 install -r requirements.txt

echo ""
echo "=========================================="
echo "  ✅ 安装完成！"
echo ""
echo "  启动 Simultra:"
echo "    ./start.sh"
echo ""
echo "  或手动启动后端:"
echo "    cd python && python3 -m uvicorn main:app --port 7860"
echo "=========================================="