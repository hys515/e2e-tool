import asyncio
import websockets
import json

async def test_client():
    uri = "ws://localhost:8766"
    print(f"连接到: {uri}")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("连接成功！")
            
            # 发送测试消息
            test_message = "Hello, WebSocket!"
            await websocket.send(test_message)
            print(f"发送: {test_message}")
            
            # 接收响应
            response = await websocket.recv()
            print(f"收到: {response}")
            
    except Exception as e:
        print(f"连接失败: {e}")

if __name__ == "__main__":
    asyncio.run(test_client()) 