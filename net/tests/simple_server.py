#!/usr/bin/env python3
"""
简化的WebSocket服务器
"""

import asyncio
import websockets
import json
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleWebSocketServer:
    def __init__(self, host="0.0.0.0", port=8765):
        self.host = host
        self.port = port
        self.clients = {}  # username -> websocket
        
    async def handle_client(self, websocket, path):
        """处理客户端连接"""
        username = None
        try:
            logger.info(f"新连接: {websocket.remote_address}")
            
            # 等待客户端发送用户名
            async for message in websocket:
                try:
                    data = json.loads(message)
                    logger.info(f"收到消息: {data}")
                    
                    if data.get('type') == 'login':
                        username = data['username']
                        logger.info(f"用户 {username} 尝试上线")
                        
                        if not username:
                            await websocket.send(json.dumps({
                                "type": "error",
                                "message": "用户名不能为空"
                            }))
                            return
                            
                        if username in self.clients:
                            logger.info(f"用户名已存在: {username}")
                            await websocket.send(json.dumps({
                                "type": "error",
                                "message": "用户名已存在"
                            }))
                            return
                            
                        self.clients[username] = websocket
                        logger.info(f"用户 {username} 已上线")
                        
                        # 通知双方会话已建立
                        if len(self.clients) == 2:
                            users = list(self.clients.keys())
                            logger.info(f"会话建立: {users[0]} <-> {users[1]}")
                            
                            for user in users:
                                peer = users[1] if user == users[0] else users[0]
                                try:
                                    await self.clients[user].send(json.dumps({
                                        "type": "session_ready",
                                        "peer": peer
                                    }))
                                    logger.info(f"发送session_ready给 {user}")
                                except Exception as e:
                                    logger.error(f"发送session_ready失败: {e}")
                        break
                        
                except json.JSONDecodeError as e:
                    logger.warning(f"收到非JSON消息: {message}, 错误: {e}")
                except Exception as e:
                    logger.error(f"处理登录消息失败: {e}")
                    break
                    
            # 主消息循环
            async for message in websocket:
                try:
                    data = json.loads(message)
                    logger.info(f"收到消息: {data}")
                    
                    if data.get('type') == 'msg':
                        # 转发消息
                        target = data['to']
                        if target in self.clients:
                            try:
                                await self.clients[target].send(json.dumps(data))
                                logger.info(f"转发消息: {data['from']} -> {target}")
                            except Exception as e:
                                logger.error(f"转发消息失败: {e}")
                                
                    elif data.get('type') == 'file':
                        # 转发文件
                        target = data['to']
                        if target in self.clients:
                            try:
                                await self.clients[target].send(json.dumps(data))
                                logger.info(f"转发文件: {data['from']} -> {target}")
                            except Exception as e:
                                logger.error(f"转发文件失败: {e}")
                            
                except json.JSONDecodeError as e:
                    logger.warning(f"收到非JSON消息: {message}, 错误: {e}")
                except Exception as e:
                    logger.error(f"处理消息失败: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"连接关闭: {username}")
        except Exception as e:
            logger.error(f"客户端异常: {e}")
        finally:
            # 清理连接
            if username and username in self.clients:
                del self.clients[username]
                logger.info(f"用户 {username} 下线")
    
    async def start(self):
        """启动服务器"""
        logger.info(f"启动WebSocket服务器: {self.host}:{self.port}")
        
        try:
            async with websockets.serve(self.handle_client, self.host, self.port):
                logger.info("服务器已启动，等待连接...")
                await asyncio.Future()  # 保持运行
        except Exception as e:
            logger.error(f"服务器启动失败: {e}")
    
    def run(self):
        """运行服务器"""
        try:
            asyncio.run(self.start())
        except KeyboardInterrupt:
            logger.info("收到退出信号，正在关闭服务器...")
        except Exception as e:
            logger.error(f"服务器异常: {e}")

if __name__ == "__main__":
    server = SimpleWebSocketServer()
    server.run()