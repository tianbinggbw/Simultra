#!/bin/bash
# Simultra - 推送到 GitHub

echo "正在推送代码到 GitHub..."
echo "仓库地址: https://github.com/tianbinggbw/Simultra"

# 检查是否需要登录
echo ""
echo "请确保已安装 GitHub CLI (gh) 并登录:"
echo "  1. 安装: brew install gh (macOS)"
echo "  2. 登录: gh auth login"
echo ""

# 尝试使用 gh
if command -v gh &> /dev/null; then
    gh repo create Simultra --public --source=. --push
else
    echo "请手动执行以下命令:"
    echo "  1. 在 GitHub 网页创建仓库: https://github.com/new"
    echo "     - 仓库名: Simultra"
    echo "     - 不要勾选 Initialize repository"
    echo ""
    echo "  2. 推送代码:"
    echo "     git remote add origin https://github.com/tianbinggbw/Simultra.git"
    echo "     git push -u origin master"
fi