#!/usr/bin/env python3
"""
测试心跳机制和重连功能
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

class TestHeartbeatClient:
    def __init__(self, username, server_url="ws://localhost:8765"):
        self.username = username
        self.server_url = server_url
        self.websocket = None
        self.session_peer = None
        
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
            
            # 开始接收消息
            async for message in self.websocket:
                await self.handle_message(message)
                
        except Exception as e:
            print(f"[{self.username}] ❌ 连接失败: {e}")
    
    async def handle_message(self, message):
        """处理接收到的消息"""
        try:
            data = json.loads(message)
            print(f"[{self.username}] 📨 收到消息: {data.get('type')}")
            
            if data.get('type') == 'session_ready':
                print(f"[{self.username}] 🤝 会话已准备就绪")
                
            elif data.get('type') == 'request_pubkey':
                print(f"[{self.username}] 🔑 收到公钥请求")
                # 发送公钥（简化处理）
                await self.websocket.send(json.dumps({
                    "type": "pubkey",
                    "username": self.username,
                    "pubkey": "dummy_public_key"
                }))
                
            elif data.get('type') == 'key_exchange':
                print(f"[{self.username}] 🔄 收到密钥交换")
                self.session_peer = data['peer']
                print(f"[{self.username}] 🤝 建立会话: {self.session_peer}")
                
            elif data.get('type') == 'user_list':
                users = data['users']
                print(f"[{self.username}] 👥 在线用户: {users}")
                
                # 自动选择会话对象
                for user in users:
                    if user != self.username:
                        self.session_peer = user
                        print(f"[{self.username}] 🤝 建立会话: {self.session_peer}")
                        break
                        
        except Exception as e:
            print(f"[{self.username}] ❌ 处理消息失败: {e}")
    
    async def send_large_file(self):
        """发送大文件测试"""
        try:
            if not self.session_peer:
                print(f"[{self.username}] ❌ 未建立会话")
                return
            
            # 创建一个大文件用于测试
            test_file = f"test_large_file_{self.username}.bin"
            file_size = 2 * 1024 * 1024  # 2MB
            
            print(f"[{self.username}] 📁 创建测试文件: {test_file} ({file_size} bytes)")
            
            with open(test_file, 'wb') as f:
                f.write(b'0' * file_size)
            
            # 分块发送
            CHUNK_SIZE = 64 * 1024  # 64KB
            total_chunks = (file_size + CHUNK_SIZE - 1) // CHUNK_SIZE
            
            print(f"[{self.username}] 📤 开始分块发送: {total_chunks} chunks")
            
            # 发送文件开始消息
            start_msg = {
                "type": "file_start",
                "filename": test_file,
                "filetype": "test",
                "filesize": file_size,
                "chunks": total_chunks,
                "from": self.username,
                "to": self.session_peer
            }
            await self.websocket.send(json.dumps(start_msg))
            
            # 分块发送文件数据
            with open(test_file, 'rb') as f:
                chunk_index = 0
                while True:
                    chunk_data = f.read(CHUNK_SIZE)
                    if not chunk_data:
                        break
                    
                    chunk_msg = {
                        "type": "file_chunk",
                        "filename": test_file,
                        "chunk_index": chunk_index,
                        "chunk_data": chunk_data.hex(),
                        "from": self.username,
                        "to": self.session_peer
                    }
                    await self.websocket.send(json.dumps(chunk_msg))
                    print(f"[{self.username}] 📦 发送块 {chunk_index + 1}/{total_chunks}: {len(chunk_data)} bytes")
                    chunk_index += 1
                    
                    # 每发送几个块就发送心跳
                    if chunk_index % 10 == 0:
                        await self.send_heartbeat()
                        print(f"[{self.username}] 💓 发送心跳")
                    
                    # 添加延迟
                    await asyncio.sleep(0.01)
            
            # 发送文件结束消息
            end_msg = {
                "type": "file_end",
                "filename": test_file,
                "from": self.username,
                "to": self.session_peer
            }
            await self.websocket.send(json.dumps(end_msg))
            print(f"[{self.username}] ✅ 文件传输完成")
            
            # 清理测试文件
            os.remove(test_file)
            
        except Exception as e:
            print(f"[{self.username}] ❌ 发送文件失败: {e}")
    
    async def send_heartbeat(self):
        """发送心跳消息"""
        try:
            if not self.websocket.closed:
                heartbeat_msg = {
                    "type": "heartbeat",
                    "from": self.username
                }
                await self.websocket.send(json.dumps(heartbeat_msg))
        except Exception as e:
            print(f"[{self.username}] ⚠️ 心跳发送失败: {e}")

async def main():
    """主函数"""
    print("🧪 测试心跳机制和重连功能")
    print("=" * 50)
    
    # 创建两个客户端
    alice = TestHeartbeatClient("alice")
    bob = TestHeartbeatClient("bob")
    
    # 启动客户端
    alice_task = asyncio.create_task(alice.connect())
    bob_task = asyncio.create_task(bob.connect())
    
    # 等待连接建立
    await asyncio.sleep(3)
    
    # alice发送大文件
    await alice.send_large_file()
    
    # 等待传输完成
    await asyncio.sleep(5)
    
    print("✅ 测试完成")

if __name__ == "__main__":
    asyncio.run(main()) 