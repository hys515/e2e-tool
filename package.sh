#!/bin/bash

set -e

# 配置
OUTPUT_NAME="e2e-tool-package"
ZIP_NAME="${OUTPUT_NAME}.zip"
DIST_DIR="./$OUTPUT_NAME"

# 1. 清理旧构建
echo "[*] Cleaning old build and output..."
make clean > /dev/null 2>&1 || true
rm -rf "$DIST_DIR" "$ZIP_NAME"

# 2. 编译程序
echo "[*] Building e2e-tool (static)..."
make

# 3. 创建打包目录
echo "[*] Creating package directory..."
mkdir -p "$DIST_DIR"

# 4. 拷贝文件（只包含最终用户需要的内容）
cp ./e2e-tool "$DIST_DIR/"
cp ./README.md "$DIST_DIR/"
cp ./test_perf.py "$DIST_DIR/"

# 5. 打包为 zip
echo "[*] Creating zip archive..."
zip -rq "$ZIP_NAME" "$OUTPUT_NAME"

# 6. 完成提示
echo "[✓] 打包完成：$ZIP_NAME"
echo "    包含文件："
ls -1 "$DIST_DIR"
