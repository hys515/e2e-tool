#!/usr/bin/env python3
"""
最基本的WebSocket服务器
"""

import asyncio
import websockets
import json
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def handle_client(websocket, path):
    """处理客户端连接"""
    try:
        logger.info(f"新连接: {websocket.remote_address}")
        
        # 简单的消息回显
        async for message in websocket:
            try:
                logger.info(f"收到消息: {message}")
                
                # 回显消息
                response = {
                    "type": "echo",
                    "message": message
                }
                await websocket.send(json.dumps(response))
                logger.info(f"发送回显: {response}")
                
            except Exception as e:
                logger.error(f"处理消息失败: {e}")
                
    except websockets.exceptions.ConnectionClosed:
        logger.info("连接关闭")
    except Exception as e:
        logger.error(f"客户端异常: {e}")

async def main():
    """主函数"""
    logger.info("启动基本WebSocket服务器: localhost:8765")
    
    try:
        async with websockets.serve(handle_client, "localhost", 8765):
            logger.info("服务器已启动，等待连接...")
            await asyncio.Future()  # 保持运行
    except Exception as e:
        logger.error(f"服务器启动失败: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("收到退出信号，正在关闭服务器...")
    except Exception as e:
        logger.error(f"服务器异常: {e}")