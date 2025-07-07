#!/bin/bash

echo "🔍 Git 与 VS Code 环境诊断工具"
echo "================================="

# 检查 Git 是否安装
if command -v git >/dev/null 2>&1; then
    GIT_PATH=$(command -v git)
    GIT_VER=$(git --version)
    echo "✅ 检测到 Git：$GIT_VER"
    echo "   路径：$GIT_PATH"
else
    echo "❌ 未检测到 git 命令，请先安装 Git（如：brew install git）"
    exit 1
fi

echo ""

# 检查当前是否在 Git 仓库中
if [ -d ".git" ]; then
    echo "✅ 当前目录是 Git 仓库"
else
    echo "⚠️  当前目录不是 Git 仓库，是否忘记运行 git init？"
fi

echo ""

# 检查 code 命令是否存在
if command -v code >/dev/null 2>&1; then
    CODE_PATH=$(command -v code)
    CODE_VER=$(code --version | head -n 1)
    echo "✅ 检测到 VS Code CLI（code）：$CODE_VER"
    echo "   路径：$CODE_PATH"
else
    echo "❌ 未检测到 VS Code CLI 命令（code）"
    echo "   ▶ 你可能使用的是 Cursor，或者没有安装 'Shell Command: Install code in PATH'"
fi

echo ""

# 检查是否使用 Cursor.app
if pgrep -xq "Cursor"; then
    echo "⚠️  检测到你正在使用 Cursor.app（非官方 VS Code）"
    echo "   Cursor 默认不带 Git 图形界面（Source Control 面板）"
else
    echo "✅ 未检测到 Cursor，可能正在使用官方 VS Code"
fi

echo ""

# 检查 VS Code 的用户设置中是否设置了 git.path
USER_SETTINGS="$HOME/Library/Application Support/Code/User/settings.json"
if [ -f "$USER_SETTINGS" ]; then
    if grep -q '"git.path"' "$USER_SETTINGS"; then
        echo "✅ VS Code 用户设置中指定了 git.path："
        grep '"git.path"' "$USER_SETTINGS"
    else
        echo "ℹ️  VS Code 用户设置中未指定 git.path（通常不需要）"
    fi
else
    echo "⚠️  VS Code 用户配置文件不存在，可能未使用官方 VS Code"
fi

echo ""
echo "✅ 诊断完毕。如你使用 Cursor，可考虑安装原版 VS Code 获取完整 Git 支持。"
