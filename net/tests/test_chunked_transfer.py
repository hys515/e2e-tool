#!/usr/bin/env python3
"""
测试分块文件传输功能
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

class TestChunkedClient:
    def __init__(self, username, server_url="ws://localhost:8765"):
        self.username = username
        self.server_url = server_url
        self.websocket = None
        self.session_peer = None
        self.file_receiving = {}
        
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
    
    async def receive_messages(self, duration=15):
        """接收消息"""
        print(f"[{self.username}] 👂 开始接收消息...")
        start_time = time.time()
        
        try:
            while time.time() - start_time < duration:
                try:
                    message = await asyncio.wait_for(self.websocket.recv(), timeout=1.0)
                    data = json.loads(message)
                    print(f"[{self.username}] 📥 收到消息类型: {data.get('type')}")
                    
                    if data.get('type') == 'session_ready':
                        self.session_peer = data['peer']
                        print(f"[{self.username}] ✅ 会话已建立，对端: {self.session_peer}")
                        
                    elif data.get('type') == 'file_start':
                        # 分块文件开始
                        peer = data['from']
                        filename = data['filename']
                        filetype = data['filetype']
                        filesize = data['filesize']
                        chunks = data['chunks']
                        print(f"[{self.username}] 📁 收到分块文件开始: {filename} ({filesize} bytes, {chunks} chunks)")
                        
                        self.file_receiving[filename] = {
                            'peer': peer,
                            'filetype': filetype,
                            'filesize': filesize,
                            'chunks': chunks,
                            'received_chunks': set(),
                            'data': b''
                        }
                        
                    elif data.get('type') == 'file_chunk':
                        # 分块文件数据
                        peer = data['from']
                        filename = data['filename']
                        chunk_index = data['chunk_index']
                        chunk_data = bytes.fromhex(data['chunk_data'])
                        
                        if filename in self.file_receiving:
                            file_info = self.file_receiving[filename]
                            file_info['received_chunks'].add(chunk_index)
                            file_info['data'] += chunk_data
                            print(f"[{self.username}] 📦 收到文件块 {chunk_index + 1}: {len(chunk_data)} bytes")
                            
                    elif data.get('type') == 'file_end':
                        # 分块文件结束
                        peer = data['from']
                        filename = data['filename']
                        
                        if filename in self.file_receiving:
                            file_info = self.file_receiving[filename]
                            expected_chunks = file_info['chunks']
                            received_chunks = len(file_info['received_chunks'])
                            
                            print(f"[{self.username}] ✅ 文件传输完成: {filename} ({received_chunks}/{expected_chunks} chunks)")
                            
                            if received_chunks == expected_chunks:
                                # 保存完整文件
                                save_dir = os.path.join(project_root, "received_files")
                                os.makedirs(save_dir, exist_ok=True)
                                save_path = os.path.join(save_dir, filename)
                                
                                with open(save_path, 'wb') as f:
                                    f.write(file_info['data'])
                                
                                print(f"[{self.username}] 💾 分块文件已保存: {save_path}")
                                print(f"[{self.username}] 📊 文件大小: {len(file_info['data'])} bytes")
                            else:
                                print(f"[{self.username}] ❌ 文件传输不完整: {received_chunks}/{expected_chunks} chunks")
                            
                            # 清理接收状态
                            del self.file_receiving[filename]
                        
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    print(f"[{self.username}] ❌ 接收消息失败: {e}")
                    break
                    
        except Exception as e:
            print(f"[{self.username}] ❌ 接收循环失败: {e}")
    
    async def send_large_file(self, filepath, filetype):
        """发送大文件（测试分块传输）"""
        if not self.session_peer:
            print(f"[{self.username}] ❌ 未建立会话")
            return False
            
        try:
            filesize = os.path.getsize(filepath)
            filename = os.path.basename(filepath)
            
            print(f"[{self.username}] 📁 准备发送大文件: {filename} ({filesize} bytes)")
            
            # 使用分块传输
            CHUNK_SIZE = 64 * 1024  # 64KB per chunk
            
            # 发送文件开始消息
            start_msg = {
                "type": "file_start",
                "filename": filename,
                "filetype": filetype,
                "filesize": filesize,
                "chunks": (filesize + CHUNK_SIZE - 1) // CHUNK_SIZE,
                "from": self.username,
                "to": self.session_peer
            }
            await self.websocket.send(json.dumps(start_msg))
            print(f"[{self.username}] 📤 发送文件开始消息")
            
            # 分块发送文件数据
            with open(filepath, 'rb') as f:
                chunk_index = 0
                while True:
                    chunk_data = f.read(CHUNK_SIZE)
                    if not chunk_data:
                        break
                    
                    chunk_msg = {
                        "type": "file_chunk",
                        "filename": filename,
                        "chunk_index": chunk_index,
                        "chunk_data": chunk_data.hex(),
                        "from": self.username,
                        "to": self.session_peer
                    }
                    await self.websocket.send(json.dumps(chunk_msg))
                    print(f"[{self.username}] 📤 发送块 {chunk_index + 1}: {len(chunk_data)} bytes")
                    chunk_index += 1
            
            # 发送文件结束消息
            end_msg = {
                "type": "file_end",
                "filename": filename,
                "from": self.username,
                "to": self.session_peer
            }
            await self.websocket.send(json.dumps(end_msg))
            print(f"[{self.username}] ✅ 文件传输完成")
            return True
            
        except Exception as e:
            print(f"[{self.username}] ❌ 发送大文件失败: {e}")
            return False
    
    async def close(self):
        """关闭连接"""
        if self.websocket:
            await self.websocket.close()
            print(f"[{self.username}] 🔌 连接已关闭")

async def test_chunked_transfer():
    """测试分块传输"""
    print("🚀 测试分块文件传输功能")
    print("=" * 60)
    
    # 创建两个客户端
    client1 = TestChunkedClient("alice")
    client2 = TestChunkedClient("bob")
    
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
        receive_task1 = asyncio.create_task(client1.receive_messages(20))
        receive_task2 = asyncio.create_task(client2.receive_messages(20))
        
        # 等待会话建立
        print("⏳ 等待会话建立...")
        await asyncio.sleep(3)
        
        # 发送大文件
        print("📁 发送大文件...")
        large_file_path = os.path.join(project_root, "hide", "output", "test_video_fix.mp4")
        if os.path.exists(large_file_path):
            success = await client1.send_large_file(large_file_path, "video")
            if success:
                print("✅ 大文件发送成功")
            else:
                print("❌ 大文件发送失败")
        else:
            print(f"❌ 大文件不存在: {large_file_path}")
        
        # 等待接收完成
        print("⏳ 等待接收完成...")
        await asyncio.sleep(10)
        
        # 取消接收任务
        receive_task1.cancel()
        receive_task2.cancel()
        
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
    await test_chunked_transfer()

if __name__ == "__main__":
    asyncio.run(main()) 