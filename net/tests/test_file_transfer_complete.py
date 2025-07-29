#!/usr/bin/env python3
"""
完整的文件传输测试
模拟两个客户端之间的隐写文件传输
"""

import asyncio
import json
import websockets
import os
import sys
import time

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

class TestClient:
    def __init__(self, username, server_url="ws://localhost:8765"):
        self.username = username
        self.server_url = server_url
        self.websocket = None
        self.session_peer = None
        self.received_files = []
        
    async def connect(self):
        """连接到服务器"""
        try:
            print(f"[{self.username}] 🔗 连接到服务器...")
            self.websocket = await websockets.connect(self.server_url)
            print(f"[{self.username}] ✅ 连接成功")
            
            # 发送登录消息
            await self.websocket.send(json.dumps({
                "type": "login",
                "username": self.username
            }))
            print(f"[{self.username}] 📤 发送登录消息")
            
            # 发送公钥
            await self.websocket.send(json.dumps({
                "type": "pubkey",
                "username": self.username,
                "pubkey": f"pubkey_{self.username}"
            }))
            print(f"[{self.username}] 📤 发送公钥")
            
            return True
        except Exception as e:
            print(f"[{self.username}] ❌ 连接失败: {e}")
            return False
    
    async def receive_messages(self, duration=10):
        """接收消息"""
        print(f"[{self.username}] 👂 开始接收消息...")
        start_time = time.time()
        
        try:
            while time.time() - start_time < duration:
                try:
                    message = await asyncio.wait_for(self.websocket.recv(), timeout=1.0)
                    data = json.loads(message)
                    print(f"[{self.username}] 📥 收到消息: {data}")
                    
                    if data.get('type') == 'session_ready':
                        self.session_peer = data['peer']
                        print(f"[{self.username}] ✅ 会话已建立，对端: {self.session_peer}")
                        
                    elif data.get('type') == 'file':
                        print(f"[{self.username}] 📁 收到文件: {data['filename']}")
                        self.received_files.append(data)
                        
                        # 模拟文件保存
                        file_data = bytes.fromhex(data['data'])
                        save_path = f"received_files/{data['filename']}"
                        os.makedirs("received_files", exist_ok=True)
                        
                        with open(save_path, 'wb') as f:
                            f.write(file_data)
                        print(f"[{self.username}] 💾 文件已保存: {save_path}")
                        
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    print(f"[{self.username}] ❌ 接收消息失败: {e}")
                    break
                    
        except Exception as e:
            print(f"[{self.username}] ❌ 接收循环失败: {e}")
    
    async def send_file(self, filename, filetype, file_data):
        """发送文件"""
        if not self.session_peer:
            print(f"[{self.username}] ❌ 未建立会话")
            return False
            
        try:
            file_message = {
                "type": "file",
                "from": self.username,
                "to": self.session_peer,
                "filename": filename,
                "filetype": filetype,
                "data": file_data.hex()
            }
            
            await self.websocket.send(json.dumps(file_message))
            print(f"[{self.username}] 📤 文件已发送: {filename}")
            return True
            
        except Exception as e:
            print(f"[{self.username}] ❌ 发送文件失败: {e}")
            return False
    
    async def close(self):
        """关闭连接"""
        if self.websocket:
            await self.websocket.close()
            print(f"[{self.username}] 🔌 连接已关闭")

async def test_file_transfer():
    """测试文件传输"""
    print("🚀 开始文件传输测试")
    print("=" * 60)
    
    # 创建两个客户端
    client1 = TestClient("alice")
    client2 = TestClient("bob")
    
    try:
        # 连接两个客户端
        print("📡 连接客户端...")
        if not await client1.connect():
            return
        if not await client2.connect():
            return
        
        print("✅ 两个客户端都已连接")
        
        # 启动接收任务
        print("👂 启动消息接收...")
        receive_task1 = asyncio.create_task(client1.receive_messages(15))
        receive_task2 = asyncio.create_task(client2.receive_messages(15))
        
        # 等待会话建立
        print("⏳ 等待会话建立...")
        await asyncio.sleep(3)
        
        # 发送测试文件
        print("📁 发送测试文件...")
        test_data = b"This is a test file content for steganography testing"
        success = await client1.send_file("test_stego.png", "image", test_data)
        
        if success:
            print("✅ 文件发送成功")
        else:
            print("❌ 文件发送失败")
        
        # 等待接收完成
        print("⏳ 等待接收完成...")
        await asyncio.sleep(5)
        
        # 取消接收任务
        receive_task1.cancel()
        receive_task2.cancel()
        
        # 显示结果
        print("\n" + "=" * 60)
        print("📊 测试结果:")
        print(f"Alice 收到的文件数: {len(client1.received_files)}")
        print(f"Bob 收到的文件数: {len(client2.received_files)}")
        
        if client1.received_files:
            print("Alice 收到的文件:")
            for file in client1.received_files:
                print(f"  - {file['filename']} (来自: {file['from']})")
                
        if client2.received_files:
            print("Bob 收到的文件:")
            for file in client2.received_files:
                print(f"  - {file['filename']} (来自: {file['from']})")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # 关闭连接
        await client1.close()
        await client2.close()
        print("🏁 测试完成")

async def main():
    """主函数"""
    await test_file_transfer()

if __name__ == "__main__":
    asyncio.run(main()) 