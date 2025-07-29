import asyncio
import websockets
import json
import logging
import functools

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebSocketServer:
    def __init__(self, host="0.0.0.0", port=8765):
        self.host = host
        self.port = port
        self.clients = {}  # username -> websocket
        self.pubkeys = {}  # username -> pubkey
        self.lock = asyncio.Lock()
        
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
                            
                        async with self.lock:
                            if username in self.clients:
                                logger.info(f"用户名已存在: {username}")
                                await websocket.send(json.dumps({
                                    "type": "error",
                                    "message": "用户名已存在"
                                }))
                                return
                                
                            if len(self.clients) >= 2:
                                logger.info(f"已有两人在线，拒绝 {username}")
                                await websocket.send(json.dumps({
                                    "type": "error",
                                    "message": "只允许两人在线"
                                }))
                                return
                                
                            self.clients[username] = websocket
                            
                        logger.info(f"用户 {username} 已上线")
                        
                        # 通知双方会话已建立
                        async with self.lock:
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
                                    
                                # 主动向双方索要公钥
                                for user in users:
                                    peer = users[1] if user == users[0] else users[0]
                                    try:
                                        await self.clients[user].send(json.dumps({
                                            "type": "request_pubkey",
                                            "peer": peer
                                        }))
                                        logger.info(f"发送request_pubkey给 {user}")
                                    except Exception as e:
                                        logger.error(f"发送request_pubkey失败: {e}")
                        break
                        
                except json.JSONDecodeError as e:
                    logger.warning(f"收到非JSON消息: {message}, 错误: {e}")
                except Exception as e:
                    logger.error(f"客户端异常: {e}", exc_info=True)
                    break
                    
            # 主消息循环
            async for message in websocket:
                try:
                    data = json.loads(message)
                    logger.info(f"收到消息: {data}")
                    
                    if data.get('type') == 'pubkey':
                        # 处理公钥上报
                        user = data['username']
                        pubkey = data['pubkey']
                        
                        async with self.lock:
                            self.pubkeys[user] = pubkey
                            logger.info(f"收到 {user} 的公钥上报")
                            
                            if len(self.pubkeys) == 2:
                                users = list(self.pubkeys.keys())
                                for u in users:
                                    peer = users[1] if u == users[0] else users[0]
                                    peer_pub = self.pubkeys[peer]
                                    
                                    try:
                                        await self.clients[u].send(json.dumps({
                                            "type": "key_exchange",
                                            "peer": peer,
                                            "peer_pub": peer_pub
                                        }))
                                        logger.info(f"发送key_exchange给 {u}")
                                    except Exception as e:
                                        logger.error(f"发送key_exchange失败: {e}")
                                    
                    elif data.get('type') == 'msg':
                        # 转发加密消息
                        target = data['to']
                        async with self.lock:
                            if target in self.clients:
                                try:
                                    await self.clients[target].send(json.dumps(data))
                                    logger.info(f"转发加密消息: {data['from']} -> {target}")
                                except Exception as e:
                                    logger.error(f"转发消息失败: {e}")
                                
                    elif data.get('type') == 'file':
                        # 转发文件
                        target = data['to']
                        async with self.lock:
                            if target in self.clients:
                                try:
                                    await self.clients[target].send(json.dumps(data))
                                    logger.info(f"转发文件: {data['from']} -> {target}, 文件: {data['filename']}")
                                except Exception as e:
                                    logger.error(f"转发文件失败: {e}")
                                    
                    elif data.get('type') in ['file_start', 'file_chunk', 'file_end']:
                        # 转发分块文件消息
                        target = data['to']
                        async with self.lock:
                            if target in self.clients:
                                try:
                                    await self.clients[target].send(json.dumps(data))
                                    if data.get('type') == 'file_start':
                                        logger.info(f"转发文件开始: {data['from']} -> {target}, 文件: {data['filename']}")
                                    elif data.get('type') == 'file_chunk':
                                        logger.info(f"转发文件块: {data['from']} -> {target}, 文件: {data['filename']}, 块: {data['chunk_index']}")
                                    elif data.get('type') == 'file_end':
                                        logger.info(f"转发文件结束: {data['from']} -> {target}, 文件: {data['filename']}")
                                except Exception as e:
                                    logger.error(f"转发分块文件消息失败: {e}")
                    elif data.get('type') == 'heartbeat':
                        # 处理心跳消息
                        logger.debug(f"收到心跳: {data['from']}")
                        # 可以在这里添加心跳响应逻辑
                                
                    elif data.get('type') == 'user_list':
                        # 返回用户列表
                        async with self.lock:
                            users = list(self.clients.keys())
                            try:
                                await websocket.send(json.dumps({
                                    "type": "user_list",
                                    "users": users
                                }))
                                logger.info(f"发送用户列表给 {username}")
                            except Exception as e:
                                logger.error(f"发送用户列表失败: {e}")
                            
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
            try:
                async with self.lock:
                    if username and username in self.clients:
                        del self.clients[username]
                    if username and username in self.pubkeys:
                        del self.pubkeys[username]
                        
                    # 通知其他用户下线
                    for user, ws in self.clients.items():
                        try:
                            await ws.send(json.dumps({
                                "type": "user_offline",
                                "username": username
                            }))
                        except:
                            pass
                            
                logger.info(f"用户 {username} 下线")
            except Exception as e:
                logger.error(f"清理连接失败: {e}")
    
    async def start(self):
        logger.info(f"启动WebSocket服务器: {self.host}:{self.port}")
        try:
            async with websockets.serve(
                functools.partial(self.handle_client), 
                self.host, 
                self.port,
                ping_interval=20,  # 20秒ping间隔
                ping_timeout=10,   # 10秒ping超时
                close_timeout=10   # 10秒关闭超时
            ):
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
    server = WebSocketServer()
    server.run()