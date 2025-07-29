import asyncio
import websockets

async def handle_client(websocket, path):
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

async def main():
    print("启动WebSocket服务器: localhost:8766")
    async with websockets.serve(handle_client, "localhost", 8766):
        print("服务器已启动，等待连接...")
        await asyncio.Future()  # 保持运行

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("收到退出信号，正在关闭服务器...")
    except Exception as e:
        print(f"服务器异常: {e}") 