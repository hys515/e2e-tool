#!/usr/bin/env python3
"""
完整的E2E通信测试脚本
"""

import asyncio
import websockets
import json
import os
import sys
import time

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

async def test_full_communication():
    """测试完整的通信功能"""
    print("🧪 完整通信功能测试")
    print("=" * 60)
    
    # 测试两个客户端之间的通信
    uri = "ws://localhost:8765"
    
    # 客户端1
    print("📱 启动客户端1 (alice)")
    try:
        async with websockets.connect(uri) as client1:
            print("✅ 客户端1连接成功")
            
            # 登录
            login_msg = {"type": "login", "username": "alice"}
            await client1.send(json.dumps(login_msg))
            print("📤 客户端1发送登录消息")
            
            # 等待会话建立
            response = await client1.recv()
            data = json.loads(response)
            print(f"📥 客户端1收到响应: {data}")
            
            if data.get('type') == 'session_ready':
                print("✅ 客户端1会话建立成功")
                
                # 客户端2
                print("\n📱 启动客户端2 (bob)")
                async with websockets.connect(uri) as client2:
                    print("✅ 客户端2连接成功")
                    
                    # 登录
                    login_msg2 = {"type": "login", "username": "bob"}
                    await client2.send(json.dumps(login_msg2))
                    print("📤 客户端2发送登录消息")
                    
                    # 等待会话建立
                    response2 = await client2.recv()
                    data2 = json.loads(response2)
                    print(f"📥 客户端2收到响应: {data2}")
                    
                    if data2.get('type') == 'session_ready':
                        print("✅ 客户端2会话建立成功")
                        
                        # 测试消息发送
                        print("\n💬 测试消息发送")
                        test_msg = {
                            "type": "msg",
                            "from": "alice",
                            "to": "bob",
                            "content": "Hello from Alice!"
                        }
                        await client1.send(json.dumps(test_msg))
                        print("📤 客户端1发送消息")
                        
                        # 等待消息接收
                        try:
                            msg_response = await asyncio.wait_for(client2.recv(), timeout=5.0)
                            msg_data = json.loads(msg_response)
                            print(f"📥 客户端2收到消息: {msg_data}")
                            
                            if msg_data.get('type') == 'msg':
                                print("✅ 消息传递成功")
                            else:
                                print("❌ 消息传递失败")
                                
                        except asyncio.TimeoutError:
                            print("❌ 消息接收超时")
                        
                        # 测试文件发送
                        print("\n📁 测试文件发送")
                        file_msg = {
                            "type": "file",
                            "from": "bob",
                            "to": "alice",
                            "filename": "test.txt",
                            "content": "This is a test file content"
                        }
                        await client2.send(json.dumps(file_msg))
                        print("📤 客户端2发送文件")
                        
                        # 等待文件接收
                        try:
                            file_response = await asyncio.wait_for(client1.recv(), timeout=5.0)
                            file_data = json.loads(file_response)
                            print(f"📥 客户端1收到文件: {file_data}")
                            
                            if file_data.get('type') == 'file':
                                print("✅ 文件传递成功")
                            else:
                                print("❌ 文件传递失败")
                                
                        except asyncio.TimeoutError:
                            print("❌ 文件接收超时")
                            
                    else:
                        print(f"❌ 客户端2会话建立失败: {data2}")
                        
            else:
                print(f"❌ 客户端1会话建立失败: {data}")
                
    except Exception as e:
        print(f"❌ 通信测试失败: {e}")

async def test_key_exchange():
    """测试密钥交换功能"""
    print("\n🔑 密钥交换功能测试")
    print("=" * 40)
    
    uri = "ws://localhost:8765"
    
    try:
        async with websockets.connect(uri) as client1:
            print("✅ 客户端1连接成功")
            
            # 登录
            login_msg = {"type": "login", "username": "test_user1"}
            await client1.send(json.dumps(login_msg))
            
            response = await client1.recv()
            data = json.loads(response)
            
            if data.get('type') == 'session_ready':
                print("✅ 会话建立成功")
                
                # 发送公钥
                pubkey_msg = {
                    "type": "pubkey",
                    "username": "test_user1",
                    "pubkey": "test_public_key_data"
                }
                await client1.send(json.dumps(pubkey_msg))
                print("📤 发送公钥")
                
                # 等待密钥交换
                try:
                    key_response = await asyncio.wait_for(client1.recv(), timeout=5.0)
                    key_data = json.loads(key_response)
                    print(f"📥 收到密钥交换消息: {key_data}")
                    
                    if key_data.get('type') == 'key_exchange':
                        print("✅ 密钥交换成功")
                    else:
                        print("❌ 密钥交换失败")
                        
                except asyncio.TimeoutError:
                    print("❌ 密钥交换超时")
                    
    except Exception as e:
        print(f"❌ 密钥交换测试失败: {e}")

async def main():
    """主测试函数"""
    print("🚀 E2E完整功能测试")
    print("=" * 80)
    
    # 测试完整通信
    await test_full_communication()
    
    # 测试密钥交换
    await test_key_exchange()
    
    print("\n🎉 完整功能测试完成")

if __name__ == "__main__":
    asyncio.run(main()) 