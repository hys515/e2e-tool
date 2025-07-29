#!/usr/bin/env python3
"""
统一的即时通信客户端启动脚本
支持条件导入和依赖检查
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_dependencies():
    """检查各种即时通信方案的依赖"""
    dependencies = {
        'websocket': False,
        'socketio': False,
        'firebase': False
    }
    
    # 检查 WebSocket
    try:
        import websockets
        dependencies['websocket'] = True
        print("✅ WebSocket 依赖已安装")
    except ImportError:
        print("❌ WebSocket 依赖未安装，运行: pip install websockets")
    
    # 检查 Socket.IO
    try:
        import socketio
        dependencies['socketio'] = True
        print("✅ Socket.IO 依赖已安装")
    except ImportError:
        print("❌ Socket.IO 依赖未安装，运行: pip install python-socketio python-engineio")
    
    # 检查 Firebase
    try:
        import firebase_admin
        dependencies['firebase'] = True
        print("✅ Firebase 依赖已安装")
    except ImportError:
        print("❌ Firebase 依赖未安装，运行: pip install firebase-admin")
    
    return dependencies

def create_client(client_type):
    """创建指定类型的客户端"""
    deps = check_dependencies()
    
    if client_type == 'websocket' and deps['websocket']:
        try:
            from websocket_client import WebSocketClient
            return WebSocketClient()
        except ImportError as e:
            print(f"❌ WebSocket 客户端导入失败: {e}")
            return None
    
    elif client_type == 'socketio' and deps['socketio']:
        try:
            from socketio_client import SocketIOClient
            return SocketIOClient()
        except ImportError as e:
            print(f"❌ Socket.IO 客户端导入失败: {e}")
            return None
    
    elif client_type == 'firebase' and deps['firebase']:
        try:
            from firebase_client import FirebaseClient
            return FirebaseClient()
        except ImportError as e:
            print(f"❌ Firebase 客户端导入失败: {e}")
            return None
    
    else:
        print(f"❌ 不支持的客户端类型: {client_type}")
        return None

def show_available_options():
    """显示可用的客户端选项"""
    print("\n=== 可用的即时通信方案 ===")
    
    deps = check_dependencies()
    
    if deps['websocket']:
        print("1. WebSocket - 轻量级，适合局域网")
    if deps['socketio']:
        print("2. Socket.IO - 功能丰富，适合生产环境")
    if deps['firebase']:
        print("3. Firebase - 云端托管，适合商业应用")
    
    if not any(deps.values()):
        print("\n❌ 没有可用的客户端，请先安装依赖：")
        print("pip install websockets python-socketio firebase-admin")
    
    return deps

def interactive_client_selection():
    """交互式客户端选择"""
    deps = check_dependencies()
    available = []
    
    if deps['websocket']:
        available.append('websocket')
    if deps['socketio']:
        available.append('socketio')
    if deps['firebase']:
        available.append('firebase')
    
    if not available:
        print("\n❌ 没有可用的客户端，请先安装依赖")
        print("推荐安装 WebSocket（最轻量）：")
        print("pip install websockets")
        return None
    
    print("\n=== 选择即时通信方案 ===")
    options = []
    
    if 'websocket' in available:
        options.append(('websocket', 'WebSocket - 轻量级，适合局域网'))
    if 'socketio' in available:
        options.append(('socketio', 'Socket.IO - 功能丰富，适合生产环境'))
    if 'firebase' in available:
        options.append(('firebase', 'Firebase - 云端托管，适合商业应用'))
    
    for i, (client_type, description) in enumerate(options, 1):
        print(f"{i}. {description}")
    
    while True:
        try:
            choice = input(f"\n请选择 (1-{len(options)}): ").strip()
            choice_idx = int(choice) - 1
            
            if 0 <= choice_idx < len(options):
                selected_type = options[choice_idx][0]
                print(f"\n✅ 已选择: {options[choice_idx][1]}")
                return create_client(selected_type)
            else:
                print(f"❌ 请输入 1-{len(options)} 之间的数字")
        except ValueError:
            print("❌ 请输入有效的数字")
        except KeyboardInterrupt:
            print("\n👋 退出选择")
            return None

def main():
    """主函数"""
    print("🔐 E2E-Tool 即时通信客户端")
    print("=" * 40)
    
    # 显示可用选项
    show_available_options()
    
    # 交互式选择
    client = interactive_client_selection()
    
    if client:
        print(f"\n🚀 启动 {type(client).__name__}")
        try:
            client.run()
        except KeyboardInterrupt:
            print("\n👋 用户退出")
        except Exception as e:
            print(f"\n❌ 客户端运行错误: {e}")
    else:
        print("\n❌ 无法启动客户端")

if __name__ == "__main__":
    main() 