import asyncio
import websockets
import json
import functools

class SimpleWebSocketServer:
    def __init__(self, host="0.0.0.0", port=8765):
        self.host = host
        self.port = port
        
    async def handle_client(self, websocket, path):
        """处理客户端连接"""
        print(f"新连接: {websocket.remote_address}, path: {path}")
        try:
            async for message in websocket:
                print(f"收到消息: {message}")
                # 简单回显
                await websocket.send(f"服务器收到: {message}")
        except websockets.exceptions.ConnectionClosed:
            print("连接关闭")
        except Exception as e:
            print(f"异常: {e}")
    
    async def start(self):
        print(f"启动WebSocket服务器: {self.host}:{self.port}")
        try:
            async with websockets.serve(
                functools.partial(self.handle_client), self.host, self.port
            ):
                print("服务器已启动，等待连接...")
                await asyncio.Future()  # 保持运行
        except Exception as e:
            print(f"服务器启动失败: {e}")
    
    def run(self):
        """运行服务器"""
        try:
            asyncio.run(self.start())
        except KeyboardInterrupt:
            print("收到退出信号，正在关闭服务器...")
        except Exception as e:
            print(f"服务器异常: {e}")

if __name__ == "__main__":
    server = SimpleWebSocketServer()
    server.run() 