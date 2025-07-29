# 🔄 即时通信API集成指南

本项目提供了多种即时通信API选择，可以根据需求选择合适的方案。

## 📋 方案对比

| 方案 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| **WebSocket** | 轻量级、实时性好、支持二进制 | 需要自建服务器 | 局域网、小规模应用 |
| **Socket.IO** | 自动重连、跨平台、功能丰富 | 依赖第三方库 | 生产环境、大规模应用 |
| **Firebase** | 云端托管、自动扩展、跨设备 | 需要Google账号、有费用 | 商业应用、多设备同步 |

## 🚀 快速开始

### 1. WebSocket方案（推荐入门）

**安装依赖：**
```bash
pip install websockets
```

**启动服务器：**
```bash
python net/websocket_server.py
```

**启动客户端：**
```bash
python net/websocket_client.py
```

### 2. Socket.IO方案（推荐生产）

**安装依赖：**
```bash
pip install python-socketio python-engineio
```

**启动服务器：**
```bash
# 需要先安装Flask-SocketIO
pip install flask-socketio
python net/socketio_server.py
```

**启动客户端：**
```bash
python net/socketio_client.py
```

### 3. Firebase方案（推荐商业）

**安装依赖：**
```bash
pip install firebase-admin
```

**配置Firebase：**
1. 在[Firebase Console](https://console.firebase.google.com/)创建项目
2. 下载`firebase_config.json`配置文件
3. 将配置文件放在项目根目录

**启动客户端：**
```bash
python net/firebase_client.py
```

## 🔧 功能特性

### 保持现有功能
- ✅ SM2密钥生成和ECDH协商
- ✅ ZUC加密解密
- ✅ 隐写术（图片/PDF/视频）
- ✅ 端到端加密

### 新增功能
- ✅ 实时消息传递
- ✅ 文件传输
- ✅ 自动重连
- ✅ 跨平台支持
- ✅ 云端同步（Firebase）

## 📝 使用示例

### 基本消息发送
```
> Hello, World!
[我] Hello, World!
[Alice] Hi there!
```

### 发送隐写消息
```
> sendmsg
请选择隐写类型（image/pdf/video）: image
请输入原始载体文件路径: hide/resources/images/cover.png
请输入隐写输出文件路径: hide/output/images/secret.png
请输入要发送的明文消息: This is a secret message
[系统] 隐写消息已发送: hide/output/images/secret.png
```

### 发送文件
```
> sendfile test.txt text
[系统] 文件已发送: test.txt
```

## 🔒 安全特性

### 端到端加密
- 使用SM2 ECDH进行密钥协商
- 使用ZUC流密码加密消息
- 服务器无法解密消息内容

### 隐写术
- 支持图片、PDF、视频载体
- 自动提取隐写消息
- 保持载体文件完整性

## 🛠️ 自定义配置

### WebSocket配置
```python
# 修改服务器地址
client = WebSocketClient("ws://your-server:8765")
```

### Socket.IO配置
```python
# 修改服务器地址
client = SocketIOClient("http://your-server:5000")
```

### Firebase配置
```python
# 修改Firebase项目配置
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://your-project.firebaseio.com',
    'storageBucket': 'your-project.appspot.com'
})
```

## 📊 性能对比

| 指标 | WebSocket | Socket.IO | Firebase |
|------|-----------|-----------|----------|
| 延迟 | ~10ms | ~15ms | ~50ms |
| 带宽 | 低 | 中 | 高 |
| 可靠性 | 中 | 高 | 很高 |
| 扩展性 | 低 | 中 | 高 |

## 🔧 故障排除

### 常见问题

**1. 连接失败**
```bash
# 检查服务器是否运行
netstat -an | grep 8765  # WebSocket
netstat -an | grep 5000  # Socket.IO
```

**2. 消息发送失败**
```bash
# 检查会话密钥
ls -la session_keys/
```

**3. 隐写提取失败**
```bash
# 检查文件路径
ls -la hide/output/images/
```

### 调试模式
```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📈 扩展建议

### 1. 添加群聊功能
- 修改服务器支持多用户会话
- 实现消息广播机制

### 2. 添加离线消息
- 使用数据库存储离线消息
- 实现消息队列机制

### 3. 添加文件压缩
- 对大文件进行压缩
- 减少传输时间和带宽

### 4. 添加消息加密
- 实现消息签名验证
- 添加防重放攻击机制

## 📞 技术支持

如有问题，请检查：
1. 依赖是否正确安装
2. 网络连接是否正常
3. 配置文件是否正确
4. 防火墙是否阻止连接

---

**选择建议：**
- **学习/测试**：使用WebSocket
- **生产环境**：使用Socket.IO
- **商业应用**：使用Firebase 