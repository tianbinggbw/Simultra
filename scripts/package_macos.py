#!/usr/bin/env python3
"""
Simultra - macOS DMG 打包脚本
在 macOS 12+ 上运行，生成 dmg 安装包

使用前提:
1. macOS 12.0+
2. Xcode CLI tools: xcode-select --install
3. Rust: curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
4. Node.js: brew install node
"""
import os
import sys
import subprocess
import shutil
import tempfile
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
PYTHON_DIR = PROJECT_ROOT / "python"
FRONTEND_DIR = PROJECT_ROOT / "src"
TAURI_DIR = PROJECT_ROOT / "src-tauri"
OUTPUT_DIR = PROJECT_ROOT / "dist"

# 版本信息
VERSION = "1.0.0"
APP_NAME = "Simultra"
BUNDLE_ID = "com.simultra.app"

def run_command(cmd, cwd=None, check=True):
    """执行命令"""
    print(f"  执行: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    result = subprocess.run(
        cmd,
        shell=isinstance(cmd, str),
        cwd=cwd or PROJECT_ROOT,
        capture_output=True,
        text=True
    )
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if check and result.returncode != 0:
        raise RuntimeError(f"命令执行失败: {cmd}")
    return result

def check_dependencies():
    """检查依赖"""
    print("\n检查 macOS 打包依赖...")

    checks = [
        ("node", "Node.js"),
        ("npm", "npm"),
        ("cargo", "Rust"),
        ("python3", "Python 3"),
    ]

    for cmd, name in checks:
        try:
            result = subprocess.run(
                cmd, "--version",
                capture_output=True,
                text=True
            )
            version = result.stdout.strip().split('\n')[0]
            print(f"  ✓ {name}: {version}")
        except Exception:
            print(f"  ✗ {name}: 未安装")
            print(f"    请安装: brew install {cmd}")
            return False

    return True

def install_frontend_deps():
    """安装前端依赖"""
    print("\n安装前端依赖...")

    # 安装 Node 依赖
    if (FRONTEND_DIR / "package.json").exists():
        run_command(["npm", "install"], cwd=FRONTEND_DIR)

    # 安装 Tauri CLI
    run_command(["npm", "install", "-D", "@tauri-apps/cli@^2"], cwd=PROJECT_ROOT)

def build_frontend():
    """构建前端"""
    print("\n构建前端 UI...")

    # 使用 Tauri 构建（包含前端）
    run_command(["npm", "run", "tauri", "build", "--verbose"], cwd=PROJECT_ROOT)

def create_dmg():
    """创建 DMG 安装包"""
    print("\n创建 DMG 安装包...")

    # Tauri 打包 dmg 会自动生成在 src-tauri/target/release/bundle/dmg/
    dmg_dir = TAURI_DIR / "target" / "release" / "bundle" / "dmg"

    if dmg_dir.exists():
        dmg_files = list(dmg_dir.glob("*.dmg"))
        if dmg_files:
            # 复制到 dist 目录
            OUTPUT_DIR.mkdir(exist_ok=True)
            for dmg in dmg_files:
                dest = OUTPUT_DIR / dmg.name
                shutil.copy2(dmg, dest)
                print(f"  ✓ DMG 已生成: {dest}")
                return

    print("  ✗ 未找到 DMG 文件，Tauri 打包可能失败")

def main():
    print("="*60)
    print(f"  Simultra DMG 打包脚本")
    print(f"  版本: {VERSION}")
    print("="*60)

    # 检查依赖
    if not check_dependencies():
        sys.exit(1)

    # 安装依赖
    install_frontend_deps()

    # 构建
    build_frontend()

    # 创建 DMG
    create_dmg()

    print("\n" + "="*60)
    print("  打包完成!")
    print("="*60)

if __name__ == "__main__":
    main()