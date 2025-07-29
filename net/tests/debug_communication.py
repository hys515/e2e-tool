#!/usr/bin/env python3
"""
调试通信问题
"""

import asyncio
import websockets
import json
import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

async def debug_communication():
    """调试通信问题"""
    print("🔍 调试通信问题")
    print("=" * 50)
    
    uri = "ws://localhost:8765"
    
    # 客户端1 (sender)
    print("📱 启动发送方客户端 (alice)")
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
                
                # 发送公钥
                pubkey_msg = {
                    "type": "pubkey",
                    "username": "alice",
                    "pubkey": "test_pubkey_alice"
                }
                await client1.send(json.dumps(pubkey_msg))
                print("📤 客户端1发送公钥")
                
                # 客户端2 (receiver)
                print("\n📱 启动接收方客户端 (bob)")
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
                        
                        # 发送公钥
                        pubkey_msg2 = {
                            "type": "pubkey",
                            "username": "bob",
                            "pubkey": "test_pubkey_bob"
                        }
                        await client2.send(json.dumps(pubkey_msg2))
                        print("📤 客户端2发送公钥")
                        
                        # 等待密钥交换
                        await asyncio.sleep(1)
                        
                        # 测试发送文件
                        print("\n📁 测试发送文件")
                        file_msg = {
                            "type": "file",
                            "filename": "test.txt",
                            "filetype": "image",
                            "filesize": 100,
                            "from": "alice",
                            "to": "bob",
                            "data": "68656c6c6f"  # "hello" in hex
                        }
                        
                        print(f"📤 客户端1发送文件消息: {file_msg}")
                        await client1.send(json.dumps(file_msg))
                        
                        # 等待文件接收
                        try:
                            print("⏳ 等待客户端2接收文件...")
                            file_response = await asyncio.wait_for(client2.recv(), timeout=5.0)
                            file_data = json.loads(file_response)
                            print(f"📥 客户端2收到文件: {file_data}")
                            
                            if file_data.get('type') == 'file':
                                print("✅ 文件传递成功")
                            else:
                                print("❌ 文件传递失败")
                                
                        except asyncio.TimeoutError:
                            print("❌ 文件接收超时")
                            
                        # 测试发送文本消息
                        print("\n💬 测试发送文本消息")
                        text_msg = {
                            "type": "msg",
                            "from": "alice",
                            "to": "bob",
                            "content": "Hello from Alice!"
                        }
                        
                        print(f"📤 客户端1发送文本消息: {text_msg}")
                        await client1.send(json.dumps(text_msg))
                        
                        # 等待消息接收
                        try:
                            print("⏳ 等待客户端2接收消息...")
                            msg_response = await asyncio.wait_for(client2.recv(), timeout=5.0)
                            msg_data = json.loads(msg_response)
                            print(f"📥 客户端2收到消息: {msg_data}")
                            
                            if msg_data.get('type') == 'msg':
                                print("✅ 消息传递成功")
                            else:
                                print("❌ 消息传递失败")
                                
                        except asyncio.TimeoutError:
                            print("❌ 消息接收超时")
                            
                        # 保持连接一段时间
                        print("\n⏳ 保持连接5秒...")
                        await asyncio.sleep(5)
                        
                    else:
                        print(f"❌ 客户端2会话建立失败: {data2}")
                        
            else:
                print(f"❌ 客户端1会话建立失败: {data}")
                
    except Exception as e:
        print(f"❌ 调试失败: {e}")

async def main():
    """主函数"""
    await debug_communication()

if __name__ == "__main__":
    asyncio.run(main())