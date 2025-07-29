# 🧪 网络通信测试脚本

本目录包含所有网络通信相关的测试脚本，用于验证各种功能模块的正确性。

## 📁 脚本分类

### 🔧 基础功能测试
- **`test_imports.py`** - 测试模块导入和基本功能
- **`test_connection.py`** - 测试基本连接功能
- **`test_features.py`** - 测试完整功能特性
- **`test_summary.py`** - 生成系统功能总结报告

### 🔐 加密通信测试
- **`test_decrypt_message.py`** - 测试消息解密功能
- **`test_full_communication.py`** - 测试完整通信流程
- **`test_simple_communication.py`** - 测试简单通信

### 📁 文件传输测试
- **`test_file_transfer_complete.py`** - 测试完整文件传输
- **`test_chunked_transfer.py`** - 测试分块文件传输
- **`debug_file_transfer.py`** - 调试文件传输问题

### 🎭 隐写术测试
- **`test_steg.py`** - 测试隐写术功能
- **`test_video_fix.py`** - 测试视频隐写修复
- **`test_extract_received.py`** - 测试接收文件隐写提取

### 💓 连接稳定性测试
- **`test_heartbeat_fix.py`** - 测试心跳机制和连接稳定性
- **`test_real_client.py`** - 测试真实客户端场景

### 🛠️ 服务器测试
- **`basic_server.py`** - 基础WebSocket服务器
- **`simple_server.py`** - 简单WebSocket服务器
- **`test_basic_server.py`** - 测试基础服务器
- **`test_simple_server.py`** - 测试简单服务器
- **`test_port_server.py`** - 测试端口服务器

### 🔌 客户端测试
- **`test_simple_client.py`** - 测试简单客户端
- **`test_port_client.py`** - 测试端口客户端
- **`test_enhanced_client.py`** - 测试增强客户端
- **`local_client.py`** - 本地客户端

### 🛠️ 工具脚本
- **`create_test_image.py`** - 创建测试图片
- **`create_test_pdf.py`** - 创建测试PDF
- **`fix_proxy.py`** - 修复代理问题

### 🐛 调试脚本
- **`debug_communication.py`** - 调试通信问题
- **`debug_file_transfer.py`** - 调试文件传输

### 📋 文档
- **`file_flow_diagram.md`** - 文件传输流程图

## 🚀 快速测试

### 使用测试运行脚本（推荐）
```bash
# 进入测试目录
cd net/tests

# 交互式菜单
python run_tests.py

# 或使用命令行参数
python run_tests.py --basic      # 基础功能测试
python run_tests.py --steg       # 隐写术测试
python run_tests.py --transfer   # 文件传输测试
python run_tests.py --stability  # 稳定性测试
python run_tests.py --all        # 运行所有测试
python run_tests.py --create-files  # 创建测试文件
```

### 手动运行测试

#### 1. 基础功能测试
```bash
# 测试模块导入
python net/tests/test_imports.py

# 测试基本连接
python net/tests/test_connection.py

# 生成功能总结
python net/tests/test_summary.py
```

### 2. 隐写术测试
```bash
# 测试所有隐写功能
python net/tests/test_steg.py

# 测试视频隐写修复
python net/tests/test_video_fix.py
```

### 3. 文件传输测试
```bash
# 测试分块传输
python net/tests/test_chunked_transfer.py

# 测试完整文件传输
python net/tests/test_file_transfer_complete.py
```

### 4. 连接稳定性测试
```bash
# 测试心跳机制
python net/tests/test_heartbeat_fix.py
```

## 🔧 调试指南

### 通信问题调试
```bash
# 调试通信问题
python net/tests/debug_communication.py

# 调试文件传输
python net/tests/debug_file_transfer.py
```

### 创建测试文件
```bash
# 创建测试图片
python net/tests/create_test_image.py

# 创建测试PDF
python net/tests/create_test_pdf.py
```

## 📊 测试覆盖范围

- ✅ **模块导入测试** - 验证所有依赖模块正确导入
- ✅ **连接测试** - 验证WebSocket连接建立
- ✅ **加密通信测试** - 验证SM2+ZUC加密解密
- ✅ **隐写术测试** - 验证图像、PDF、视频隐写
- ✅ **文件传输测试** - 验证小文件和大文件传输
- ✅ **分块传输测试** - 验证大文件分块传输
- ✅ **心跳机制测试** - 验证连接稳定性
- ✅ **错误处理测试** - 验证异常情况处理

## 🎯 使用建议

1. **开发阶段**：运行 `test_imports.py` 和 `test_features.py` 验证基本功能
2. **功能测试**：运行 `test_steg.py` 验证隐写术功能
3. **性能测试**：运行 `test_chunked_transfer.py` 测试大文件传输
4. **稳定性测试**：运行 `test_heartbeat_fix.py` 测试长时间连接
5. **问题调试**：使用 `debug_*.py` 脚本定位具体问题

## 📝 注意事项

- 运行测试前确保WebSocket服务器已启动
- 某些测试需要特定的测试文件，会自动创建
- 调试脚本会输出详细的日志信息
- 测试脚本可以独立运行，也可以组合使用

---

**💡 提示**：这些测试脚本保留了开发过程中的所有调试信息，对于理解系统工作原理和排查问题非常有帮助。 