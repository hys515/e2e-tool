#!/usr/bin/env python3
"""
快速启动脚本 - 优先使用WebSocket方案
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def check_websocket():
    """检查WebSocket依赖"""
    try:
        import websockets
        return True
    except ImportError:
        return False

def check_hide_module():
    """检查hide模块是否可用"""
    try:
        import hide
        return True
    except ImportError:
        return False

def main():
    """主函数"""
    print("🔐 E2E-Tool 快速启动")
    print("=" * 30)
    
    # 检查WebSocket依赖
    if not check_websocket():
        print("❌ WebSocket 依赖未安装")
        print("请运行以下命令安装：")
        print("pip install websockets")
        print("\n或者激活虚拟环境后安装：")
        print("source venv/bin/activate")
        print("pip install websockets")
        return
    
    print("✅ WebSocket 依赖已安装")
    
    # 检查hide模块
    if not check_hide_module():
        print("❌ hide 模块未找到")
        print("请确保在项目根目录下运行此脚本")
        print("当前工作目录:", os.getcwd())
        print("项目根目录:", project_root)
        return
    
    print("✅ hide 模块可用")
    
    # 尝试导入WebSocket客户端
    try:
        from net.websocket_client import WebSocketClient
        print("✅ WebSocket 客户端导入成功")
    except ImportError as e:
        print(f"❌ WebSocket 客户端导入失败: {e}")
        print("请检查文件路径和依赖")
        return
    
    # 启动客户端
    print("\n🚀 启动 WebSocket 客户端...")
    client = WebSocketClient()
    
    try:
        client.run()
    except KeyboardInterrupt:
        print("\n👋 用户退出")
    except Exception as e:
        print(f"\n❌ 客户端运行错误: {e}")

if __name__ == "__main__":
    main() 