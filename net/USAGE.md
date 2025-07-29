# 🚀 E2E-Tool 即时通信使用指南

## 快速开始

### 1. 启动服务器
```bash
# 在一个终端窗口中启动WebSocket服务器
python3 net/websocket_server.py
```

### 2. 启动客户端
```bash
# 在另一个终端窗口中启动客户端
python3 net/quick_start.py
```

### 3. 使用说明

#### 基本命令
- 直接输入文本：发送加密消息
- `sendmsg`：发送隐写消息
- `sendfile <文件路径> <文件类型>`：发送文件
- `extractmsg`：提取隐写消息
- `quit` 或 `exit`：退出

#### 隐写消息示例
```
> sendmsg
请选择隐写类型（image/pdf/video）: image
请输入原始载体文件路径: hide/resources/images/cover.png
请输入隐写输出文件路径: hide/output/images/secret.png
请输入要发送的明文消息: Hello, this is a secret message!
```

#### 文件发送示例
```
> sendfile test.txt text
[系统] 文件已发送: test.txt
```

## 功能特性

### 🔐 端到端加密
- 使用SM2 ECDH进行密钥协商
- 使用ZUC流密码加密消息
- 服务器无法解密消息内容

### 🎭 隐写术
- 支持图片、PDF、视频载体
- 自动提取隐写消息
- 保持载体文件完整性

### 📁 文件传输
- 支持任意类型文件
- 自动加密传输
- 支持隐写文件

## 故障排除

### 常见问题

**1. 连接失败**
```bash
# 检查服务器是否运行
netstat -an | grep 8765
```

**2. 模块导入错误**
```bash
# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install websockets
```

**3. 隐写提取失败**
```bash
# 检查文件路径
ls -la hide/output/images/
```

## 测试脚本

运行测试脚本检查所有功能：
```bash
python3 net/test_imports.py
```

## 高级用法

### 自定义服务器地址
```python
# 修改客户端连接地址
client = WebSocketClient("ws://your-server:8765")
```

### 批量测试
```bash
# 启动多个客户端进行测试
python3 net/quick_start.py  # 终端1
python3 net/quick_start.py  # 终端2
```

---

**提示：** 确保在项目根目录下运行所有命令！ 