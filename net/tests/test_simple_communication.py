#!/usr/bin/env python3
"""
简单通信测试
"""

import asyncio
import websockets
import json

async def test_simple_communication():
    """简单通信测试"""
    print("🧪 简单通信测试")
    print("=" * 40)
    
    uri = "ws://localhost:8765"
    
    # 客户端1
    print("📱 客户端1 (alice)")
    async with websockets.connect(uri) as client1:
        print("✅ 客户端1连接成功")
        
        # 登录
        await client1.send(json.dumps({"type": "login", "username": "alice"}))
        response1 = await client1.recv()
        data1 = json.loads(response1)
        print(f"📥 客户端1收到: {data1}")
        
        if data1.get('type') == 'session_ready':
            print("✅ 客户端1会话建立")
            
            # 客户端2
            print("\n📱 客户端2 (bob)")
            async with websockets.connect(uri) as client2:
                print("✅ 客户端2连接成功")
                
                # 登录
                await client2.send(json.dumps({"type": "login", "username": "bob"}))
                response2 = await client2.recv()
                data2 = json.loads(response2)
                print(f"📥 客户端2收到: {data2}")
                
                if data2.get('type') == 'session_ready':
                    print("✅ 客户端2会话建立")
                    
                    # 发送测试消息
                    print("\n💬 发送测试消息")
                    test_msg = {
                        "type": "msg",
                        "from": "alice",
                        "to": "bob",
                        "content": "Hello from Alice!"
                    }
                    
                    await client1.send(json.dumps(test_msg))
                    print("📤 客户端1发送消息")
                    
                    # 等待接收
                    try:
                        msg_response = await asyncio.wait_for(client2.recv(), timeout=3.0)
                        msg_data = json.loads(msg_response)
                        print(f"📥 客户端2收到: {msg_data}")
                        
                        if msg_data.get('type') == 'msg':
                            print("✅ 消息传递成功")
                        else:
                            print("❌ 消息传递失败")
                            
                    except asyncio.TimeoutError:
                        print("❌ 消息接收超时")
                    
                    # 保持连接
                    print("\n⏳ 保持连接3秒...")
                    await asyncio.sleep(3)
                    
                else:
                    print(f"❌ 客户端2会话建立失败: {data2}")
        else:
            print(f"❌ 客户端1会话建立失败: {data1}")

if __name__ == "__main__":
    asyncio.run(test_simple_communication()) 