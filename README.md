# 🔐 E2E隐写通信系统：端到端加密信息隐藏工具

**E2E隐写通信系统** 是一个基于国密算法的端到端加密信息隐藏通信平台，支持在图像、PDF、视频等载体文件中隐藏加密消息，实现隐蔽的安全通信。

## 🌟 项目特色

- **🔒 端到端加密**：基于SM2+ZUC国密算法，确保通信安全
- **🎭 信息隐藏**：支持图像、PDF、视频三种载体的隐写术
- **🌐 实时通信**：基于WebSocket的实时消息传输
- **📦 大文件支持**：智能分块传输，支持任意大小文件
- **💓 连接稳定**：心跳机制保证长时间连接稳定性
- **🔧 模块化设计**：清晰的架构，易于扩展和维护

---

## 📁 项目结构

```
e2e_tool/
├── cli/                    # C语言命令行工具
│   └── main.c             # 主程序入口
├── crypto/                 # 加密模块
│   ├── __init__.py
│   └── zuc_ctypes.py      # ZUC流密码实现
├── hide/                   # 信息隐藏模块
│   ├── __init__.py
│   ├── steg.py            # 隐写术统一接口
│   ├── image_steganography.py    # 图像隐写
│   ├── pdf_steganography.py      # PDF隐写
│   ├── video_steganography.py    # 视频隐写
│   ├── utils.py           # 工具函数
│   ├── resources/         # 载体文件资源
│   ├── output/           # 隐写输出文件
│   └── extracted/        # 提取的文件
├── net/                   # 网络通信模块
│   ├── websocket_server.py       # WebSocket服务器
│   ├── websocket_client.py       # WebSocket客户端
│   ├── client_factory.py         # 客户端工厂
│   ├── firebase_client.py        # Firebase客户端
│   ├── socketio_client.py        # Socket.IO客户端
│   ├── server.py                 # 原始Socket服务器
│   ├── client.py                 # 原始Socket客户端
│   ├── quick_start.py            # 快速启动脚本
│   ├── run_client.py             # 客户端运行脚本
│   ├── tests/                    # 测试脚本目录
│   │   ├── README.md             # 测试脚本说明
│   │   ├── test_*.py             # 功能测试脚本
│   │   ├── debug_*.py            # 调试脚本
│   │   └── create_test_*.py      # 测试文件创建脚本
│   ├── USAGE.md                  # 使用指南
│   ├── USAGE_ENHANCED.md         # 增强使用指南
│   └── README_IM.md              # 即时通信指南
├── src/                   # C语言源码
│   └── sm2_ecdh.c        # SM2 ECDH实现
├── include/               # 头文件
│   └── sm2_ecdh.h        # SM2 ECDH接口
├── test/                  # 测试文件
│   ├── data/             # 测试数据
│   ├── test_*.py         # Python测试
│   └── test_sm2_ecdh.c   # C语言测试
├── keys/                  # 密钥存储
├── session_keys/          # 会话密钥
├── received_files/        # 接收的文件
├── requirements.txt       # Python依赖
├── Makefile              # 构建配置
├── CMakeLists.txt        # CMake配置
└── README.md             # 项目文档
```

---

## 🚀 核心功能

### 1. 端到端加密通信
- **SM2密钥生成**：基于椭圆曲线的非对称加密
- **ECDH密钥协商**：安全的会话密钥生成
- **ZUC流加密**：国密流密码算法加密消息
- **密钥管理**：自动化的密钥生成、存储和加载

### 2. 信息隐藏技术
- **图像隐写**：LSB隐写术，支持PNG、JPG等格式
- **PDF隐写**：元数据隐写，保持文档完整性
- **视频隐写**：首帧LSB隐写，支持MP4、AVI等格式
- **容量优化**：智能选择最佳隐写方案

### 3. 网络通信
- **WebSocket服务器**：实时双向通信
- **多客户端支持**：WebSocket、Firebase、Socket.IO
- **分块传输**：大文件智能分块，避免超时
- **心跳机制**：保持连接稳定性
- **自动重连**：网络异常时自动恢复

### 4. 用户体验
- **交互式界面**：友好的命令行交互
- **路径自动补全**：Tab键自动补全文件路径
- **文件管理**：自动分类和管理文件
- **错误处理**：完善的异常处理和提示

---

## 🛠️ 技术架构

### 加密层
```
明文消息 → ZUC加密 → 密文 → 隐写嵌入 → 载体文件
```

### 通信层
```
客户端A ←→ WebSocket服务器 ←→ 客户端B
```

### 隐写层
```
载体文件 + 密文数据 → 隐写算法 → 隐写文件
```

---

## 📦 安装与配置

### 环境要求
- Python 3.8+
- FFmpeg（视频隐写需要）
- GmSSL（C语言工具需要）

### 快速安装

```bash
# 1. 克隆项目
git clone <repository-url>
cd e2e_tool

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 编译C语言工具（可选）
make
```

### 依赖说明

```bash
# 核心依赖
websockets>=10.0        # WebSocket通信
opencv-python>=4.5      # 图像处理
PyPDF2>=3.0            # PDF处理
numpy>=1.21             # 数值计算
Pillow>=8.0             # 图像处理

# 可选依赖
firebase-admin>=5.0     # Firebase支持
python-socketio>=5.0    # Socket.IO支持
```

---

## 🚀 使用方法

### 1. 启动服务器

```bash
# 启动WebSocket服务器
python net/websocket_server.py
```

### 2. 启动客户端

```bash
# 启动WebSocket客户端
python net/websocket_client.py
```

### 3. 基本操作

```bash
# 连接到服务器后，输入用户名
请输入用户名: alice

# 可用命令
sendmsg          # 发送隐写消息
sendfile <文件> <类型>  # 发送文件
files            # 显示可用文件
extractmsg       # 提取隐写消息
quit/exit        # 退出
```

### 4. 发送隐写消息

```bash
> sendmsg

=== 发送隐写消息 ===
请选择隐写类型（image/pdf/video）: image
请输入载体文件名: test_image.png
请输入输出文件名: stego_image.png
请输入要发送的明文消息: Hello, this is a secret message!

[系统] 开始发送隐写消息...
[系统] 加密消息...
[系统] 执行隐写处理...
[系统] 发送隐写文件...
[系统] 隐写消息已发送
```

### 5. 接收和提取

```bash
# 接收方自动处理
[系统] 收到来自 alice 的文件: stego_image.png (类型: image)
[系统] 检测到隐写文件，开始提取...
[系统] 隐写提取成功，数据大小: 128 bytes
[bob] (隐写消息) Hello, this is a secret message!
```

---

## 🧪 测试验证

### 功能测试

```bash
# 测试隐写功能
python test/test_steg.py

# 测试网络通信
python net/test_features.py

# 测试分块传输
python net/test_chunked_transfer.py

# 测试心跳机制
python net/test_heartbeat_fix.py
```

### 性能测试

```bash
# 测试加密性能
python test/test_perf.py

# 测试隐写容量
python test/test_image_steg.py
python test/test_pdf_steg.py
python test/test_video_steg.py
```

---

## 🔧 高级功能

### 1. 多客户端支持

```python
# Firebase客户端
python net/firebase_client.py

# Socket.IO客户端
python net/socketio_client.py

# 客户端工厂
python net/client_factory.py
```

### 2. 自定义隐写参数

```python
# 图像隐写 - 自定义LSB位数
embed_message('image', input_path, output_path, message, n_bits=2)

# PDF隐写 - 自定义元数据键
embed_message('pdf', input_path, output_path, message, metadata_key="/CustomData")

# 视频隐写 - 自定义编码器
embed_message('video', input_path, output_path, message, codec='libx264')
```

### 3. 批量处理

```python
# 批量隐写处理
for file in image_files:
    embed_message('image', file, f"stego_{file}", message)

# 批量提取
for file in stego_files:
    data = extract_message('image', file)
    print(f"从 {file} 提取: {data}")
```

---

## 📊 性能指标

### 隐写容量
- **图像**：每像素1-3位，取决于图像大小
- **PDF**：受文件大小限制，通常几KB到几MB
- **视频**：首帧容量，通常几KB

### 传输性能
- **小文件**：直接传输，延迟<100ms
- **大文件**：分块传输，64KB/块，支持任意大小
- **连接稳定性**：心跳机制，支持长时间连接

### 加密性能
- **SM2密钥生成**：<10ms
- **ECDH密钥协商**：<5ms
- **ZUC加密/解密**：>1MB/s

---

## 🔒 安全特性

### 加密算法
- **SM2**：国密椭圆曲线公钥密码算法
- **ECDH**：椭圆曲线Diffie-Hellman密钥协商
- **ZUC**：国密流密码算法

### 安全机制
- **端到端加密**：消息在传输前加密
- **前向安全性**：每次会话使用新密钥
- **密钥隔离**：不同用户间密钥完全隔离
- **隐写隐蔽性**：载体文件视觉无变化

---

## 🐛 故障排除

### 常见问题

1. **连接失败**
   ```bash
   # 检查服务器状态
   ps aux | grep websocket_server
   
   # 重启服务器
   python net/websocket_server.py
   ```

2. **隐写失败**
   ```bash
   # 检查载体文件
   ls -la test/
   
   # 检查FFmpeg（视频隐写）
   ffmpeg -version
   ```

3. **文件传输超时**
   ```bash
   # 检查网络连接
   ping localhost
   
   # 检查防火墙设置
   ```

### 调试模式

```bash
# 启用详细日志
export PYTHONPATH=.
python -u net/websocket_client.py

# 使用调试脚本
python net/debug_communication.py
```

---

## 🤝 贡献指南

### 开发环境

```bash
# 设置开发环境
git clone <repository-url>
cd e2e_tool
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements_dev.txt  # 开发依赖
```

### 代码规范
- 遵循PEP 8 Python代码规范
- 使用类型注解
- 编写单元测试
- 添加文档字符串

### 提交规范
- feat: 新功能
- fix: 修复bug
- docs: 文档更新
- style: 代码格式
- refactor: 重构
- test: 测试相关

---

## 📄 许可证

本项目采用MIT许可证，详见LICENSE文件。

---

## 🙏 致谢

- **GmSSL**：国密算法库
- **OpenCV**：图像处理库
- **WebSockets**：网络通信库
- **FFmpeg**：视频处理工具

---

## 📞 联系方式

- **项目主页**：<repository-url>
- **问题反馈**：Issues页面
- **功能建议**：Discussions页面

---

## 📈 更新日志

### v1.0.0 (2024-07-29)
- ✅ 实现端到端加密通信
- ✅ 支持图像、PDF、视频隐写
- ✅ 实现WebSocket实时通信
- ✅ 添加分块传输和心跳机制
- ✅ 完善错误处理和用户体验

---

**🎉 开始使用E2E隐写通信系统，体验安全隐蔽的通信方式！**

