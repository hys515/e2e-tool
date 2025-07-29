#!/usr/bin/env python3
"""
调试文件传输功能
"""

import asyncio
import json
import websockets
import os
import sys

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

async def debug_file_transfer():
    """调试文件传输功能"""
    
    # 连接到服务器
    uri = "ws://localhost:8765"
    
    try:
        print("🔗 连接到服务器...")
        websocket = await websockets.connect(uri)
        print("✅ 连接成功")
        
        # 登录
        username = "debug_user"
        await websocket.send(json.dumps({
            "type": "login",
            "username": username
        }))
        print(f"📤 发送登录消息: {username}")
        
        # 发送公钥
        await websocket.send(json.dumps({
            "type": "pubkey",
            "username": username,
            "pubkey": "test_pubkey_123"
        }))
        print("📤 发送公钥")
        
        # 等待会话建立
        print("⏳ 等待会话建立...")
        session_ready = False
        while not session_ready:
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(message)
                print(f"📥 收到消息: {data}")
                
                if data.get('type') == 'session_ready':
                    session_ready = True
                    print("✅ 会话已建立")
                    break
                    
            except asyncio.TimeoutError:
                print("⏰ 等待超时，继续...")
                break
            except Exception as e:
                print(f"❌ 接收消息失败: {e}")
                break
        
        # 测试发送文件
        print("\n📁 测试发送文件...")
        test_file_data = b"This is a test file content for debugging"
        file_message = {
            "type": "file",
            "from": username,
            "to": "other_user",  # 假设有另一个用户
            "filename": "test_debug.txt",
            "filetype": "text",
            "data": test_file_data.hex()
        }
        
        await websocket.send(json.dumps(file_message))
        print("📤 文件消息已发送")
        print(f"📋 文件消息内容: {file_message}")
        
        # 等待一段时间看是否有响应
        print("\n⏳ 等待响应...")
        try:
            message = await asyncio.wait_for(websocket.recv(), timeout=3.0)
            data = json.loads(message)
            print(f"📥 收到响应: {data}")
        except asyncio.TimeoutError:
            print("⏰ 没有收到响应（这是正常的，因为没有其他用户）")
        except Exception as e:
            print(f"❌ 接收响应失败: {e}")
        
        # 关闭连接
        await websocket.close()
        print("🔌 连接已关闭")
        
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        import traceback
        traceback.print_exc()

async def test_server_status():
    """测试服务器状态"""
    print("🔍 检查服务器状态...")
    
    try:
        # 尝试连接
        uri = "ws://localhost:8765"
        websocket = await websockets.connect(uri)
        print("✅ 服务器正在运行")
        await websocket.close()
        return True
    except Exception as e:
        print(f"❌ 服务器未运行: {e}")
        return False

async def main():
    """主函数"""
    print("🚀 开始调试文件传输功能")
    print("=" * 50)
    
    # 检查服务器状态
    server_running = await test_server_status()
    if not server_running:
        print("❌ 请先启动服务器: python net/websocket_server.py")
        return
    
    print("\n" + "=" * 50)
    await debug_file_transfer()
    
    print("\n" + "=" * 50)
    print("🏁 调试完成")

if __name__ == "__main__":
    asyncio.run(main()) 