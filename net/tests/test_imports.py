#!/usr/bin/env python3
"""
测试导入脚本 - 验证所有模块是否能正常导入
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def test_imports():
    """测试所有必要的导入"""
    print("🔍 测试模块导入...")
    print("=" * 40)
    
    # 测试基础模块
    try:
        import json
        print("✅ json 模块")
    except ImportError as e:
        print(f"❌ json 模块: {e}")
    
    try:
        import asyncio
        print("✅ asyncio 模块")
    except ImportError as e:
        print(f"❌ asyncio 模块: {e}")
    
    # 测试WebSocket
    try:
        import websockets
        print("✅ websockets 模块")
    except ImportError as e:
        print(f"❌ websockets 模块: {e}")
    
    # 测试加密模块
    try:
        from gmssl import sm2, func
        print("✅ gmssl 模块")
    except ImportError as e:
        print(f"❌ gmssl 模块: {e}")
    
    try:
        import gmalg
        print("✅ gmalg 模块")
    except ImportError as e:
        print(f"❌ gmalg 模块: {e}")
    
    # 测试隐写模块
    try:
        import hide
        print("✅ hide 模块")
    except ImportError as e:
        print(f"❌ hide 模块: {e}")
    
    try:
        from hide.steg import embed_message, extract_message
        print("✅ hide.steg 模块")
    except ImportError as e:
        print(f"❌ hide.steg 模块: {e}")
    
    # 测试客户端模块
    try:
        from net.websocket_client import WebSocketClient
        print("✅ WebSocketClient 类")
    except ImportError as e:
        print(f"❌ WebSocketClient 类: {e}")
    
    try:
        from net.websocket_server import WebSocketServer
        print("✅ WebSocketServer 类")
    except ImportError as e:
        print(f"❌ WebSocketServer 类: {e}")
    
    print("\n" + "=" * 40)
    print("📊 导入测试完成")

def test_basic_functionality():
    """测试基本功能"""
    print("\n🧪 测试基本功能...")
    print("=" * 40)
    
    try:
        # 测试WebSocket客户端创建
        from net.websocket_client import WebSocketClient
        client = WebSocketClient()
        print("✅ WebSocketClient 创建成功")
        
        # 测试WebSocket服务器创建
        from net.websocket_server import WebSocketServer
        server = WebSocketServer()
        print("✅ WebSocketServer 创建成功")
        
        print("✅ 基本功能测试通过")
        
    except Exception as e:
        print(f"❌ 基本功能测试失败: {e}")

def main():
    """主函数"""
    print("🔐 E2E-Tool 导入测试")
    print("=" * 40)
    
    # 显示当前路径信息
    print(f"当前工作目录: {os.getcwd()}")
    print(f"项目根目录: {project_root}")
    print(f"Python路径: {sys.path[:3]}...")
    print()
    
    # 测试导入
    test_imports()
    
    # 测试基本功能
    test_basic_functionality()
    
    print("\n🎉 测试完成！")

if __name__ == "__main__":
    main() 