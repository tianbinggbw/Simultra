#!/bin/bash
# Simultra - 停止脚本

pkill -f "uvicorn main:app" 2>/dev/null && echo "✅ 后端服务已停止" || echo "后端服务未运行"
pkill -f "ollama serve" 2>/dev/null && echo "✅ Ollama 已停止" || echo "Ollama 未运行"

echo "已清理 Simultra 相关进程"