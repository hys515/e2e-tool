# 🔐 E2E-Tool：基于 GmSSL 的国密加密工具

**E2E-Tool** 是一个基于 GmSSL 实现的命令行加密工具，支持国密 ZUC 流加密、SM2 密钥对生成、SM2 ECDH 会话密钥协商等功能。项目采用模块化设计，测试代码与产物集中管理，便于维护和自动化测试。

本工具适用于构建端到端加密（E2EE）系统的"加解密模块"，输出为纯粹的二进制密文，便于与信息隐藏模块对接。

---

## 📁 项目目录结构

```
e2e_tool/
├── cli/                    # 命令行主程序源码
│   └── main.c             # 主程序入口，包含所有命令处理逻辑
├── include/               # 头文件
│   └── sm2_ecdh.h        # SM2 ECDH 功能接口声明
├── src/                   # 库实现源码
│   └── sm2_ecdh.c        # SM2 密钥生成和 ECDH 协商实现
├── test/                  # 测试相关内容
│   ├── test_sm2_ecdh.c   # 单元/集成测试代码
│   ├── test_perf.py      # 性能测试脚本
│   ├── test_sm2_ecdh     # 测试可执行文件
│   └── data/             # 测试过程中产生的所有临时文件
│       └── .gitkeep      # 保持空目录可提交
├── .vscode/              # VSCode 配置
│   └── tasks.json        # 构建任务配置
├── e2e-tool              # 主可执行文件（静态链接 GmSSL）
├── Makefile              # Linux/macOS 构建配置
├── Makefile.windows      # Windows 构建配置
├── CMakeLists.txt        # 跨平台 CMake 构建配置
├── build.bat             # Windows 便捷构建脚本
├── package.sh            # 打包脚本
├── README.md             # 项目文档
└── .gitignore           # Git 忽略配置
```

**特点：**
- 所有测试产物（如 .pem/.key/.zuc/.txt）都集中在 `test/data/` 目录下
- 静态链接 GmSSL，无需用户单独安装依赖
- 模块化设计，便于维护和扩展

---

## 🛠️ 构建方法

### 环境要求
- **macOS/Linux**: GCC 编译器
- **Windows**: MinGW-w64 或 Visual Studio
- Python 3（仅性能测试需要）
- GmSSL 库（需要预先安装）

### 编译步骤

#### macOS/Linux 环境

```bash
# 1. 编译主程序
make

# 2. 编译测试程序
make test

# 3. 清理编译产物
make clean

# 4. 打包分发
./package.sh
```

#### Windows 环境

**方法一：使用 MinGW-w64**
```cmd
# 1. 安装 MinGW-w64 和 Make
# 2. 编译主程序
mingw32-make -f Makefile.windows

# 3. 编译测试程序
mingw32-make -f Makefile.windows test

# 4. 清理编译产物
mingw32-make -f Makefile.windows clean
```

**方法二：使用 CMake（推荐）**
```cmd
# 1. 创建构建目录
mkdir build
cd build

# 2. 配置项目
cmake ..

# 3. 编译
cmake --build .

# 4. 运行测试
ctest
```

**方法三：使用 Visual Studio**
```cmd
# 1. 打开 Developer Command Prompt
# 2. 使用 CMake 生成 Visual Studio 项目
cmake -G "Visual Studio 16 2019" -A x64 ..

# 3. 编译
cmake --build . --config Release
```

#### VSCode 集成

项目包含 VSCode 任务配置，支持以下快捷操作：

- `Ctrl+Shift+P` → `Tasks: Run Task` → `build`：编译主程序
- `Ctrl+Shift+P` → `Tasks: Run Task` → `build-test`：编译测试程序
- `Ctrl+Shift+P` → `Tasks: Run Task` → `run-test`：运行测试
- `Ctrl+Shift+P` → `Tasks: Run Task` → `cmake-compile`：使用 CMake 编译

### Makefile 目标说明

| 目标 | 说明 |
|------|------|
| `make` | 编译主程序 `e2e-tool` |
| `make test` | 编译测试程序 `test/test_sm2_ecdh` |
| `make clean` | 清理所有编译产物 |
| `make all` | 编译主程序和测试程序 |

---

## 🚀 功能与使用方法

### 1. 生成 SM2 密钥对

**命令格式：**
```bash
./e2e-tool gen-keys -priv <私钥文件> -pub <公钥文件>
```

**示例：**
```bash
# 生成 Alice 的密钥对
./e2e-tool gen-keys -priv test/data/alice.pem -pub test/data/alice_pub.pem

# 生成 Bob 的密钥对
./e2e-tool gen-keys -priv test/data/bob.pem -pub test/data/bob_pub.pem
```

**输出：**
```
[+] SM2 keypair generated:
    Private: test/data/alice.pem
    Public : test/data/alice_pub.pem
```

### 2. SM2 ECDH 会话密钥协商

**命令格式：**
```bash
./e2e-tool key-exchange -priv <我的私钥> -peer <对方公钥> -out <会话密钥文件>
```

**示例：**
```bash
# Alice 与 Bob 的公钥协商会话密钥
./e2e-tool key-exchange -priv test/data/alice.pem -peer test/data/bob_pub.pem -out test/data/alice_session.key

# Bob 与 Alice 的公钥协商会话密钥
./e2e-tool key-exchange -priv test/data/bob.pem -peer test/data/alice_pub.pem -out test/data/bob_session.key
```

**验证 ECDH 正确性：**
```bash
# 两个会话密钥应该完全相同
diff test/data/alice_session.key test/data/bob_session.key
```

### 3. ZUC 加密

**命令格式：**
```bash
./e2e-tool encrypt -in <明文文件> -out <密文文件>
```

**示例：**
```bash
# 创建测试文件
echo "Hello, World!" > test/data/plain.txt

# 加密
./e2e-tool encrypt -in test/data/plain.txt -out test/data/cipher.zuc
```

**输出：**
```
[+] Encryption successful
[+] Encrypted file: test/data/cipher.zuc
[+] Key saved to: zuc.key
```

### 4. ZUC 解密

**命令格式：**
```bash
./e2e-tool decrypt -in <密文文件> -out <明文文件> -key <密钥文件>
```

**示例：**
```bash
# 解密
./e2e-tool decrypt -in test/data/cipher.zuc -out test/data/recovered.txt -key zuc.key

# 验证解密结果
diff test/data/plain.txt test/data/recovered.txt
```

**输出：**
```
[+] Decryption successful
[+] Decrypted file: test/data/recovered.txt
[+] Preview:
Hello, World!
```

### 5. 查看帮助

```bash
./e2e-tool
```

**输出：**
```
Usage:
  ./e2e-tool encrypt -in <input.txt> -out <output.zuc>
  ./e2e-tool decrypt -in <input.zuc> -out <output.txt> -key <zuc.key>
  ./e2e-tool gen-keys -priv <priv.pem> -pub <pub.pem>
  ./e2e-tool key-exchange -priv <my.pem> -peer <peer_pub.pem> -out <session.key>
```

---

## 🧪 测试方法

### 1. 自动化单元/集成测试

```bash
# 编译测试程序
make test

# 运行测试
./test/test_sm2_ecdh
```

**测试内容：**
- SM2 密钥生成测试
- SM2 ECDH 密钥协商测试
- ZUC 加密解密测试
- 文件加密解密测试
- 端到端集成测试

**输出示例：**
```
=== SM2 ECDH + ZUC 加密测试程序 ===
测试时间: 2025-07-07

=== SM2 密钥生成测试 ===
[✓] SM2 密钥生成 PASSED

=== SM2 ECDH 密钥协商测试 ===
[✓] ECDH 密钥协商正确性 PASSED

=== ZUC 加密解密测试 ===
[✓] ZUC 加密解密 PASSED

=== 文件加密解密测试 ===
[✓] 文件加密解密 PASSED

=== 端到端测试 ===
[✓] 端到端加密解密 PASSED

=== 测试统计 ===
总测试数: 5
通过: 5
失败: 0
成功率: 100.0%
```

### 2. 性能测试

```bash
python3 test/test_perf.py
```

**输出示例：**
```
   Size (bytes) |  Enc Time (ms) |  Dec Time (ms) | OK?
-------------------------------------------------------
           128 |          0.25  |         0.21   | ✅
           256 |          0.31  |         0.28   | ✅
           512 |          0.45  |         0.42   | ✅
          1024 |          0.78  |         0.75   | ✅
          2048 |          1.23  |         1.19   | ✅
          4096 |          2.34  |         2.28   | ✅
          8192 |          4.56  |         4.48   | ✅
         16384 |          8.91  |         8.76   | ✅
         32768 |         17.23  |        16.98   | ✅
         65536 |         33.45  |        32.89   | ✅
```

---

## 🧹 清理方法

### 清理编译产物
```bash
make clean
```

### 清理测试产物
```bash
rm -rf test/data/*
```

### 清理所有临时文件
```bash
make clean
rm -rf test/data/*
rm -f *.pem *.key *.zuc *.txt
```

---

## 📦 打包分发

```bash
./package.sh
```

生成 `e2e-tool-package.zip`，包含：
- `e2e-tool`（静态链接的可执行文件）
- `README.md`
- `test_perf.py`

---

## 🔧 技术特性

### 加密算法
- **SM2**：国密椭圆曲线公钥密码算法
- **ZUC**：国密流密码算法
- **ECDH**：椭圆曲线 Diffie-Hellman 密钥协商

### 安全特性
- 静态链接 GmSSL，无动态库依赖
- 使用系统安全随机数源生成密钥
- 支持 PEM 格式密钥文件
- 64 字节（512 位）会话密钥输出

### 跨平台支持
- **macOS**: 原生支持，使用 Security Framework
- **Linux**: 标准 POSIX 接口
- **Windows**: 支持 MinGW-w64、MSVC、CMake 构建
- **IDE 集成**: VSCode 任务配置，支持一键编译测试

### 性能特性
- 支持大文件加密（测试到 4MB）
- 流式加密，内存占用恒定
- 加密解密性能对称

---

## 🚀 快速开始

### Windows 用户
```cmd
# 1. 双击运行构建脚本
build.bat

# 2. 或使用 CMake
mkdir build && cd build
cmake ..
cmake --build .
```

### macOS/Linux 用户
```bash
# 1. 编译
make

# 2. 测试
make test && ./test/test_sm2_ecdh

# 3. 使用
./e2e-tool gen-keys -priv key.pem -pub key_pub.pem
```

### VSCode 用户
1. 打开项目文件夹
2. `Ctrl+Shift+P` → `Tasks: Run Task` → `build`
3. `Ctrl+Shift+P` → `Tasks: Run Task` → `run-test`

---

## 📜 License

本项目为研究用途构建，使用 GmSSL 项目作为底层加密引擎。请遵循 GmSSL 的使用与分发许可。

