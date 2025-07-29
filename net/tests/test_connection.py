#!/usr/bin/env python3
"""
简化的WebSocket连接测试
"""

import asyncio
import websockets
import json
import os
import sys

# 临时取消代理设置
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)

async def test_connection():
    """测试WebSocket连接"""
    try:
        print("🔍 测试WebSocket连接...")
        
        # 连接到服务器
        uri = "ws://localhost:8765"
        print(f"连接到: {uri}")
        
        async with websockets.connect(uri) as websocket:
            print("✅ 连接成功")
            
            # 发送测试消息
            test_message = {
                "type": "login",
                "username": "test_user"
            }
            
            print(f"发送消息: {test_message}")
            await websocket.send(json.dumps(test_message))
            
            # 等待响应
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"收到响应: {response}")
            except asyncio.TimeoutError:
                print("⚠️  等待响应超时")
            
            print("✅ 测试完成")
            
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        print(f"错误类型: {type(e).__name__}")

def main():
    """主函数"""
    print("🧪 WebSocket连接测试")
    print("=" * 30)
    
    # 检查服务器是否运行
    import subprocess
    try:
        result = subprocess.run(['netstat', '-an'], capture_output=True, text=True)
        if '8765' in result.stdout:
            print("✅ 端口8765正在监听")
        else:
            print("❌ 端口8765未监听")
            print("请先启动服务器: python3 net/websocket_server.py")
            return
    except Exception as e:
        print(f"⚠️  无法检查端口状态: {e}")
    
    # 运行测试
    asyncio.run(test_connection())

if __name__ == "__main__":
    main()