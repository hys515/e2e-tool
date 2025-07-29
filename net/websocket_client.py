import json
import os
import sys
import threading
import asyncio
import readline  # 用于自动补全
import glob
import websockets
import time

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from gmssl import sm2, func
import gmalg
from hide.steg import embed_message, extract_message

class PathCompleter:
    """路径自动补全器"""
    def __init__(self):
        self.current_dir = os.getcwd()
        
    def complete(self, text, state):
        """自动补全函数"""
        if state == 0:
            # 第一次调用，生成补全列表
            self.matches = []
            
            # 获取当前输入的部分路径
            if text.startswith('/'):
                # 绝对路径
                base_path = text
            else:
                # 相对路径
                base_path = os.path.join(self.current_dir, text)
            
            # 获取目录部分
            dir_path = os.path.dirname(base_path)
            if not dir_path:
                dir_path = '.'
            
            # 获取文件名部分
            file_pattern = os.path.basename(base_path) + '*'
            
            try:
                # 查找匹配的文件和目录
                matches = glob.glob(os.path.join(dir_path, file_pattern))
                
                # 过滤并格式化结果
                for match in matches:
                    if os.path.isdir(match):
                        # 目录添加斜杠
                        rel_path = os.path.relpath(match, self.current_dir)
                        if not rel_path.startswith('.'):
                            self.matches.append(rel_path + '/')
                    else:
                        # 文件
                        rel_path = os.path.relpath(match, self.current_dir)
                        if not rel_path.startswith('.'):
                            self.matches.append(rel_path)
                            
            except Exception:
                pass
                
        # 返回匹配项
        if state < len(self.matches):
            return self.matches[state]
        else:
            return None

class WebSocketClient:
    def __init__(self, server_url="ws://localhost:8765"):
        self.server_url = server_url
        self.websocket = None
        self.username = None
        self.session_peer = None
        
        # 设置固定路径
        self.input_dir = os.path.join(project_root, "test")  # 输入文件目录
        self.output_dir = os.path.join(project_root, "hide", "output")  # 输出文件目录
        self.received_dir = os.path.join(project_root, "received_files")  # 接收文件目录
        
        # 确保目录存在
        os.makedirs(self.input_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.received_dir, exist_ok=True)
        
        # 设置自动补全
        self.completer = PathCompleter()
        readline.set_completer(self.completer.complete)
        readline.parse_and_bind("tab: complete")
        
    def get_available_files(self, directory, extensions=None):
        """获取指定目录下的可用文件"""
        files = []
        try:
            for file in os.listdir(directory):
                file_path = os.path.join(directory, file)
                if os.path.isfile(file_path):
                    if extensions is None or any(file.lower().endswith(ext) for ext in extensions):
                        files.append(file)
        except Exception:
            pass
        return sorted(files)
    
    def resolve_input_path(self, user_input):
        """解析输入路径"""
        if not user_input:
            return None
            
        # 如果用户输入的是文件名，自动添加输入目录
        if not os.path.dirname(user_input):
            # 只有文件名，在输入目录中查找
            input_path = os.path.join(self.input_dir, user_input)
            if os.path.exists(input_path):
                return input_path
            else:
                # 显示可用文件
                available_files = self.get_available_files(self.input_dir)
                if available_files:
                    print(f"📁 可用文件: {', '.join(available_files)}")
                return None
        else:
            # 完整路径
            if os.path.exists(user_input):
                return user_input
            else:
                print(f"❌ 文件不存在: {user_input}")
                return None
    
    def resolve_output_path(self, user_input, carrier_type):
        """解析输出路径"""
        if not user_input:
            # 生成默认文件名
            timestamp = int(time.time())
            default_name = f"stego_{carrier_type}_{timestamp}"
            
            if carrier_type == 'image':
                return os.path.join(self.output_dir, f"{default_name}.png")
            elif carrier_type == 'pdf':
                return os.path.join(self.output_dir, f"{default_name}.pdf")
            elif carrier_type == 'video':
                return os.path.join(self.output_dir, f"{default_name}.mp4")
            else:
                return os.path.join(self.output_dir, f"{default_name}.bin")
        else:
            # 用户指定了文件名
            if not os.path.dirname(user_input):
                # 只有文件名，添加到输出目录
                return os.path.join(self.output_dir, user_input)
            else:
                # 完整路径
                return user_input
        
    def ensure_sm2_keypair(self, username):
        """确保SM2密钥对存在"""
        key_dir = os.path.join(os.path.dirname(__file__), '..', 'keys')
        os.makedirs(key_dir, exist_ok=True)
        priv_path = os.path.join(key_dir, f"{username}_priv.hex")
        pub_path = os.path.join(key_dir, f"{username}_pub.hex")
        
        if not (os.path.exists(priv_path) and os.path.exists(pub_path)):
            private_key = func.random_hex(64)
            sm2_crypt = sm2.CryptSM2(public_key='', private_key=private_key)
            public_key = sm2_crypt._kg(int(private_key, 16), sm2.default_ecc_table['g'])
            with open(priv_path, 'w') as f:
                f.write(private_key)
            with open(pub_path, 'w') as f:
                f.write(public_key)
            print(f"[系统] 已为 {username} 生成SM2密钥对")
        else:
            print(f"[系统] 已加载 {username} 的SM2密钥对")
            
        with open(priv_path, 'r') as f:
            priv = f.read()
        with open(pub_path, 'r') as f:
            pub = f.read()
        return priv, pub
    
    def get_session_key_path(self, me, peer):
        base_dir = os.path.join(os.path.dirname(__file__), '..', 'session_keys')
        os.makedirs(base_dir, exist_ok=True)
        users = sorted([me, peer])
        return os.path.join(base_dir, f"{users[0]}_{users[1]}_session.key")
    
    def save_session_key(self, me, peer, session_key):
        path = self.get_session_key_path(me, peer)
        try:
            with open(path, 'w') as f:
                f.write(session_key)
            print(f"[系统] 会话密钥已保存到 {path}")
        except Exception as e:
            print(f"[错误] 保存会话密钥失败: {e}")
    
    def load_session_key(self, me, peer):
        path = self.get_session_key_path(me, peer)
        if os.path.exists(path):
            with open(path, 'r') as f:
                session_key = f.read()
            print(f"[系统] 已加载会话密钥: {path}")
            return session_key
        return None
    
    def zuc_keystream(self, zuc, length):
        stream = b''
        while len(stream) < length:
            stream += zuc.generate()
        return stream[:length]
    
    def encrypt_message(self, session_key, plaintext):
        """使用ZUC加密消息"""
        key = bytes.fromhex(session_key[:32])  # 16字节
        iv = os.urandom(16)
        zuc = gmalg.ZUC(key, iv)
        pt_bytes = plaintext.encode()
        keystream = self.zuc_keystream(zuc, len(pt_bytes))
        ciphertext = bytes([a ^ b for a, b in zip(pt_bytes, keystream)])
        return iv.hex() + ':' + ciphertext.hex()
    
    def decrypt_message(self, session_key, msg):
        """使用ZUC解密消息"""
        key = bytes.fromhex(session_key[:32])  # 16字节
        iv_hex, ct_hex = msg.split(':', 1)
        iv = bytes.fromhex(iv_hex)
        ciphertext = bytes.fromhex(ct_hex)
        zuc = gmalg.ZUC(key, iv)
        keystream = self.zuc_keystream(zuc, len(ciphertext))
        plaintext = bytes([a ^ b for a, b in zip(ciphertext, keystream)])
        return plaintext.decode()
    
    async def send_stego_message(self, carrier_type, input_path, output_path, plaintext):
        """发送隐写消息"""
        try:
            print(f"[系统] 开始发送隐写消息...")
            
            # 检查连接状态
            if not self.websocket or self.websocket.closed:
                print(f"[系统] 连接已断开，尝试重连...")
                await self.reconnect()
                if not self.session_peer:
                    print(f"[错误] 重连后会话未建立，无法发送消息")
                    return
            
            # 加密明文
            session_key = self.load_session_key(self.username, self.session_peer)
            if not session_key:
                print("[错误] 未找到会话密钥")
                return
                
            print(f"[系统] 加密消息...")
            ciphertext = self.encrypt_message(session_key, plaintext)
            
            # 隐写处理
            print(f"[系统] 执行隐写处理...")
            try:
                embed_message(carrier_type, input_path, output_path, ciphertext.encode())
            except Exception as stego_error:
                print(f"[错误] 隐写处理失败: {stego_error}")
                print("[系统] 隐写失败，但客户端将继续运行")
                return
            
            # 发送文件
            print(f"[系统] 发送隐写文件...")
            await self.send_file(output_path, carrier_type)
            print(f"[系统] 隐写消息已发送: {output_path}")
            
        except Exception as e:
            print(f"[错误] 发送隐写消息失败: {e}")
            print("[系统] 隐写消息发送失败，但客户端将继续运行")
            import traceback
            traceback.print_exc()
    
    async def send_file(self, filepath, filetype):
        """发送文件"""
        try:
            print(f"[系统] 准备发送文件: {filepath}")
            
            if not os.path.exists(filepath):
                print(f"[错误] 文件不存在: {filepath}")
                return
                
            filesize = os.path.getsize(filepath)
            filename = os.path.basename(filepath)
            
            print(f"[系统] 文件大小: {filesize} bytes")
            
            # 检查文件大小，如果超过1MB则分块传输
            MAX_CHUNK_SIZE = 1024 * 1024  # 1MB
            
            if filesize > MAX_CHUNK_SIZE:
                print(f"[系统] 文件过大，使用分块传输...")
                await self.send_file_chunked(filepath, filetype, filename, filesize)
            else:
                print(f"[系统] 读取文件内容...")
                # 读取文件内容
                with open(filepath, 'rb') as f:
                    file_data = f.read()
                
                fileinfo = {
                    "type": "file",
                    "filename": filename,
                    "filetype": filetype,
                    "filesize": filesize,
                    "from": self.username,
                    "to": self.session_peer,
                    "data": file_data.hex()  # 转换为hex传输
                }
                
                print(f"[系统] 发送文件消息...")
                await self.websocket.send(json.dumps(fileinfo))
                print(f"[系统] 文件已发送: {filename}")
            
        except Exception as e:
            print(f"[错误] 发送文件失败: {e}")
            import traceback
            traceback.print_exc()
    
    async def send_file_chunked(self, filepath, filetype, filename, filesize):
        """分块发送大文件"""
        try:
            CHUNK_SIZE = 64 * 1024  # 64KB per chunk
            total_chunks = (filesize + CHUNK_SIZE - 1) // CHUNK_SIZE
            
            # 检查连接状态
            if not self.websocket or self.websocket.closed:
                print(f"[系统] 连接已断开，尝试重连...")
                if not await self.reconnect():
                    raise Exception("无法建立连接")
            
            # 发送文件开始消息
            start_msg = {
                "type": "file_start",
                "filename": filename,
                "filetype": filetype,
                "filesize": filesize,
                "chunks": total_chunks,
                "from": self.username,
                "to": self.session_peer
            }
            await self.websocket.send(json.dumps(start_msg))
            print(f"[系统] 发送文件开始消息: {filename} ({filesize} bytes, {total_chunks} chunks)")
            
            # 分块发送文件数据
            with open(filepath, 'rb') as f:
                chunk_index = 0
                while True:
                    chunk_data = f.read(CHUNK_SIZE)
                    if not chunk_data:
                        break
                    
                    # 发送心跳保持连接
                    if chunk_index % 3 == 0:  # 每3个块发送一次心跳
                        try:
                            await self.send_heartbeat()
                        except Exception as e:
                            print(f"[警告] 心跳发送失败: {e}")
                            # 如果心跳失败，检查连接状态
                            if self.websocket.closed:
                                print(f"[警告] 连接已断开，尝试重连...")
                                if not await self.reconnect():
                                    raise Exception("重连失败，无法继续传输")
                    
                    chunk_msg = {
                        "type": "file_chunk",
                        "filename": filename,
                        "chunk_index": chunk_index,
                        "chunk_data": chunk_data.hex(),
                        "from": self.username,
                        "to": self.session_peer
                    }
                    await self.websocket.send(json.dumps(chunk_msg))
                    print(f"[系统] 发送块 {chunk_index + 1}/{total_chunks}: {len(chunk_data)} bytes")
                    chunk_index += 1
                    
                    # 每发送几个块就发送心跳
                    if chunk_index % 3 == 0:  # 更频繁的心跳
                        await self.send_heartbeat()
                    
                    # 添加小延迟避免阻塞
                    await asyncio.sleep(0.01)  # 减少延迟
            
            # 发送文件结束消息
            end_msg = {
                "type": "file_end",
                "filename": filename,
                "from": self.username,
                "to": self.session_peer
            }
            await self.websocket.send(json.dumps(end_msg))
            print(f"[系统] 文件传输完成: {filename}")
            
        except Exception as e:
            print(f"[错误] 分块发送文件失败: {e}")
            import traceback
            traceback.print_exc()
            
            # 尝试重新发送
            print(f"[系统] 尝试重新发送文件...")
            try:
                await asyncio.sleep(1)  # 等待1秒
                if not self.websocket.closed:
                    await self.send_file_chunked(filepath, filetype, filename, filesize)
                else:
                    print(f"[错误] 连接已断开，无法重新发送")
            except Exception as retry_e:
                print(f"[错误] 重新发送也失败: {retry_e}")
    
    async def handle_message(self, message):
        """处理接收到的消息"""
        try:
            data = json.loads(message)
            print(f"[系统] 收到消息类型: {data.get('type')}")
            
            if data.get('type') == 'msg':
                # 加密消息
                peer = data['from']
                print(f"[系统] 收到来自 {peer} 的消息")
                session_key = self.load_session_key(self.username, peer)
                if session_key:
                    try:
                        plaintext = self.decrypt_message(session_key, data['content'])
                        print(f"[{peer}] {plaintext}")
                    except Exception as e:
                        print(f"[系统] 解密失败: {e}")
                else:
                    print(f"[系统] 未找到与 {peer} 的会话密钥")
                    
            elif data.get('type') == 'file':
                # 文件消息
                peer = data['from']
                filename = data['filename']
                filetype = data['filetype']
                print(f"[系统] 收到来自 {peer} 的文件: {filename} (类型: {filetype})")
                
                try:
                    file_data = bytes.fromhex(data['data'])
                    print(f"[系统] 文件数据大小: {len(file_data)} bytes")
                    
                    # 保存文件
                    save_dir = os.path.join(os.path.dirname(__file__), '..', 'received_files')
                    os.makedirs(save_dir, exist_ok=True)
                    save_path = os.path.join(save_dir, filename)
                    
                    with open(save_path, 'wb') as f:
                        f.write(file_data)
                    
                    print(f"[系统] 文件已保存: {save_path}")
                    
                    # 如果是隐写文件，自动提取
                    if filetype in ['image', 'pdf', 'video']:
                        print(f"[系统] 检测到隐写文件，开始提取...")
                        try:
                            extracted_data = extract_message(filetype, save_path)
                            print(f"[系统] 隐写提取成功，数据大小: {len(extracted_data)} bytes")
                            
                            session_key = self.load_session_key(self.username, peer)
                            if session_key:
                                plaintext = self.decrypt_message(session_key, extracted_data.decode())
                                print(f"[{peer}] (隐写消息) {plaintext}")
                            else:
                                print(f"[系统] 未找到与 {peer} 的会话密钥")
                        except Exception as e:
                            print(f"[系统] 隐写提取失败: {e}")
                            import traceback
                            traceback.print_exc()
                except Exception as e:
                    print(f"[系统] 处理文件失败: {e}")
                    import traceback
                    traceback.print_exc()
                    
            elif data.get('type') == 'file_start':
                # 分块文件开始
                peer = data['from']
                filename = data['filename']
                filetype = data['filetype']
                filesize = data['filesize']
                chunks = data['chunks']
                print(f"[系统] 收到来自 {peer} 的分块文件开始: {filename} ({filesize} bytes, {chunks} chunks)")
                
                # 初始化文件接收状态
                if not hasattr(self, 'file_receiving'):
                    self.file_receiving = {}
                
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
                    print(f"[系统] 收到文件块 {chunk_index + 1}: {len(chunk_data)} bytes")
                    
            elif data.get('type') == 'file_end':
                # 分块文件结束
                peer = data['from']
                filename = data['filename']
                
                if filename in self.file_receiving:
                    file_info = self.file_receiving[filename]
                    expected_chunks = file_info['chunks']
                    received_chunks = len(file_info['received_chunks'])
                    
                    print(f"[系统] 文件传输完成: {filename} ({received_chunks}/{expected_chunks} chunks)")
                    
                    if received_chunks == expected_chunks:
                        # 保存完整文件
                        save_dir = os.path.join(os.path.dirname(__file__), '..', 'received_files')
                        os.makedirs(save_dir, exist_ok=True)
                        save_path = os.path.join(save_dir, filename)
                        
                        with open(save_path, 'wb') as f:
                            f.write(file_info['data'])
                        
                        print(f"[系统] 分块文件已保存: {save_path}")
                        
                        # 如果是隐写文件，自动提取
                        if file_info['filetype'] in ['image', 'pdf', 'video']:
                            print(f"[系统] 检测到隐写文件，开始提取...")
                            try:
                                extracted_data = extract_message(file_info['filetype'], save_path)
                                print(f"[系统] 隐写提取成功，数据大小: {len(extracted_data)} bytes")
                                
                                session_key = self.load_session_key(self.username, peer)
                                if session_key:
                                    plaintext = self.decrypt_message(session_key, extracted_data.decode())
                                    print(f"[{peer}] (隐写消息) {plaintext}")
                                else:
                                    print(f"[系统] 未找到与 {peer} 的会话密钥")
                            except Exception as e:
                                print(f"[系统] 隐写提取失败: {e}")
                                import traceback
                                traceback.print_exc()
                    else:
                        print(f"[错误] 文件传输不完整: {received_chunks}/{expected_chunks} chunks")
                    
                    # 清理接收状态
                    del self.file_receiving[filename]
                        
            elif data.get('type') == 'key_exchange':
                # 密钥交换
                peer = data['peer']
                peer_pub = data['peer_pub']
                
                priv, pub = self.ensure_sm2_keypair(self.username)
                sm2_crypt = sm2.CryptSM2(public_key=peer_pub, private_key=priv)
                session_key = sm2_crypt._kg(int(priv, 16), peer_pub)[:32]
                
                self.save_session_key(self.username, peer, session_key)
                print(f"[系统] 与 {peer} 的密钥交换完成")
                
            elif data.get('type') == 'session_ready':
                # 会话建立
                peer = data['peer']
                self.session_peer = peer
                print(f"[系统] 已与 {peer} 建立会话")
                
            elif data.get('type') == 'user_list':
                print(f"[系统] 在线用户: {', '.join(data['users'])}")
                
        except json.JSONDecodeError:
            print(f"[系统] 收到非JSON消息: {message}")
        except Exception as e:
            print(f"[错误] 处理消息失败: {e}")
    
    async def connect(self):
        """连接到WebSocket服务器"""
        try:
            self.websocket = await websockets.connect(
                self.server_url,
                ping_interval=20,  # 20秒ping间隔
                ping_timeout=10,   # 10秒ping超时
                close_timeout=10   # 10秒关闭超时
            )
            print(f"[系统] 已连接到服务器: {self.server_url}")
            
            # 发送用户名
            await self.websocket.send(json.dumps({
                "type": "login",
                "username": self.username
            }))
            
            # 发送公钥
            priv, pub = self.ensure_sm2_keypair(self.username)
            await self.websocket.send(json.dumps({
                "type": "pubkey",
                "username": self.username,
                "pubkey": pub
            }))
            
            # 开始接收消息
            async for message in self.websocket:
                await self.handle_message(message)
                
        except Exception as e:
            print(f"[错误] 连接失败: {e}")
    
    async def send_heartbeat(self):
        """发送心跳消息"""
        try:
            if not self.websocket.closed:
                heartbeat_msg = {
                    "type": "heartbeat",
                    "from": self.username,
                    "timestamp": asyncio.get_event_loop().time()
                }
                await self.websocket.send(json.dumps(heartbeat_msg))
                print(f"[心跳] 发送心跳消息")
            else:
                print(f"[警告] 连接已关闭，无法发送心跳")
        except websockets.exceptions.ConnectionClosed:
            print(f"[警告] 连接已关闭，尝试重连...")
            await self.reconnect()
        except Exception as e:
            print(f"[警告] 心跳发送失败: {e}")
            # 检查连接状态，如果断开则重连
            if self.websocket.closed:
                print(f"[系统] 检测到连接断开，尝试重连...")
                await self.reconnect()
    
    async def reconnect(self):
        """重新连接"""
        try:
            print(f"[系统] 尝试重新连接...")
            if self.websocket and not self.websocket.closed:
                await self.websocket.close()
            
            # 重新建立连接
            self.websocket = await websockets.connect(
                self.server_url,
                ping_interval=20,  # 20秒ping间隔
                ping_timeout=10,   # 10秒ping超时
                close_timeout=10   # 10秒关闭超时
            )
            
            # 重新登录
            await self.websocket.send(json.dumps({
                "type": "login",
                "username": self.username
            }))
            
            print(f"[系统] 重连成功")
            return True
        except Exception as e:
            print(f"[错误] 重连失败: {e}")
            return False
    
    async def send_text_message(self, text):
        """发送文本消息"""
        if not self.session_peer:
            print("[错误] 未建立会话")
            return
            
        try:
            session_key = self.load_session_key(self.username, self.session_peer)
            if not session_key:
                print("[错误] 未找到会话密钥")
                return
                
            encrypted = self.encrypt_message(session_key, text)
            
            message = {
                "type": "msg",
                "to": self.session_peer,
                "from": self.username,
                "content": encrypted
            }
            
            await self.websocket.send(json.dumps(message))
            print(f"[我] {text}")
            
        except Exception as e:
            print(f"[错误] 发送消息失败: {e}")
    
    def start_input_loop(self):
        """启动输入循环"""
        async def input_loop():
            while True:
                try:
                    user_input = await asyncio.get_event_loop().run_in_executor(
                        None, input, "> "
                    )
                    
                    if user_input.strip() in ("quit", "exit"):
                        print("[系统] 退出客户端")
                        break
                    elif user_input.startswith("sendfile "):
                        # 发送文件
                        print("\n=== 发送文件 ===")
                        try:
                            parts = user_input.split()
                            if len(parts) >= 3:
                                filepath = parts[1]
                                filetype = parts[2]
                                
                                # 解析文件路径
                                resolved_path = self.resolve_input_path(filepath)
                                if resolved_path:
                                    await self.send_file(resolved_path, filetype)
                                else:
                                    print("❌ 文件不存在")
                            else:
                                print("❌ 用法: sendfile <文件名> <文件类型>")
                        except Exception as e:
                            print(f"[系统] 发送文件失败: {e}")
                    elif user_input == "sendmsg":
                        # 发送隐写消息
                        print("\n=== 发送隐写消息 ===")
                        
                        # 选择隐写类型
                        carrier_type = input("请选择隐写类型（image/pdf/video）: ").strip().lower()
                        if carrier_type not in ['image', 'pdf', 'video']:
                            print("❌ 不支持的隐写类型")
                            continue
                        
                        # 显示可用文件
                        extensions = {
                            'image': ['.png', '.jpg', '.jpeg', '.bmp', '.tiff'],
                            'pdf': ['.pdf'],
                            'video': ['.mp4', '.avi', '.mov', '.mkv']
                        }
                        
                        available_files = self.get_available_files(self.input_dir, extensions[carrier_type])
                        if available_files:
                            print(f"📁 可用的{carrier_type}文件: {', '.join(available_files)}")
                        else:
                            print(f"⚠️  在 {self.input_dir} 中没有找到{carrier_type}文件")
                        
                        # 输入载体文件
                        input_file = input(f"请输入载体文件名（或完整路径）: ").strip()
                        input_path = self.resolve_input_path(input_file)
                        if not input_path:
                            print("❌ 无法找到载体文件")
                            continue
                        
                        # 输入输出文件名
                        output_file = input(f"请输入输出文件名（留空使用默认名称）: ").strip()
                        output_path = self.resolve_output_path(output_file, carrier_type)
                        print(f"📁 输出路径: {output_path}")
                        
                        # 输入消息
                        plaintext = input("请输入要发送的明文消息: ").strip()
                        if not plaintext:
                            print("❌ 消息不能为空")
                            continue
                        
                        await self.send_stego_message(carrier_type, input_path, output_path, plaintext)
                    elif user_input == "files":
                        # 显示可用文件
                        print("\n=== 可用文件 ===")
                        print(f"📁 输入目录: {self.input_dir}")
                        
                        all_files = self.get_available_files(self.input_dir)
                        if all_files:
                            print("📄 所有文件:")
                            for file in all_files:
                                print(f"  - {file}")
                        else:
                            print("⚠️  没有找到文件")
                        
                        # 按类型分类显示
                        extensions = {
                            'image': ['.png', '.jpg', '.jpeg', '.bmp', '.tiff'],
                            'pdf': ['.pdf'],
                            'video': ['.mp4', '.avi', '.mov', '.mkv']
                        }
                        
                        for file_type, exts in extensions.items():
                            files = self.get_available_files(self.input_dir, exts)
                            if files:
                                print(f"\n🖼️  {file_type}文件:")
                                for file in files:
                                    print(f"  - {file}")
                    elif user_input == "extractmsg":
                        # 提取隐写消息
                        print("\n=== 提取隐写消息 ===")
                        carrier_type = input("请选择隐写类型（image/pdf/video）: ").strip().lower()
                        if carrier_type not in ['image', 'pdf', 'video']:
                            print("❌ 不支持的隐写类型")
                            continue
                        
                        # 显示可用文件
                        extensions = {
                            'image': ['.png', '.jpg', '.jpeg', '.bmp', '.tiff'],
                            'pdf': ['.pdf'],
                            'video': ['.mp4', '.avi', '.mov', '.mkv']
                        }
                        
                        available_files = self.get_available_files(self.output_dir, extensions[carrier_type])
                        if available_files:
                            print(f"📁 可用的{carrier_type}文件: {', '.join(available_files)}")
                        
                        stego_file = input("请输入隐写文件名（或完整路径）: ").strip()
                        stego_path = self.resolve_input_path(stego_file)
                        if not stego_path:
                            # 尝试在输出目录中查找
                            stego_path = os.path.join(self.output_dir, stego_file)
                            if not os.path.exists(stego_path):
                                print("❌ 无法找到隐写文件")
                                continue
                        
                        try:
                            extracted_data = extract_message(carrier_type, stego_path)
                            session_key = self.load_session_key(self.username, self.session_peer)
                            if session_key:
                                plaintext = self.decrypt_message(session_key, extracted_data.decode())
                                print(f"[系统] 解密得到明文: {plaintext}")
                            else:
                                print("[系统] 未找到会话密钥")
                        except Exception as e:
                            print(f"[错误] 提取隐写消息失败: {e}")
                            import traceback
                            traceback.print_exc()
                    else:
                        # 发送普通消息
                        await self.send_text_message(user_input)
                        
                except EOFError:
                    break
                except Exception as e:
                    print(f"[错误] 输入处理失败: {e}")
        
        asyncio.create_task(input_loop())

    def run(self):
        """运行客户端（同步接口）"""
        try:
            self.username = input("请输入用户名: ").strip()
            if not self.username:
                print("[错误] 用户名不能为空")
                return
                
            print("\n=== 命令说明 ===")
            print("sendmsg - 发送隐写消息")
            print("sendfile <文件名> <文件类型> - 发送文件")
            print("files - 显示可用文件")
            print("extractmsg - 提取隐写消息")
            print("quit/exit - 退出")
            print("================\n")
            
            # 启动异步事件循环
            asyncio.run(self._run_async())
            
        except KeyboardInterrupt:
            print("\n👋 用户退出")
        except Exception as e:
            print(f"\n❌ 客户端运行错误: {e}")
    
    async def _run_async(self):
        """异步运行客户端"""
        # 启动输入循环
        self.start_input_loop()
        
        # 连接到服务器
        await self.connect()

async def main():
    client = WebSocketClient()
    client.username = input("请输入用户名: ").strip()
    
    # 启动输入循环
    client.start_input_loop()
    
    # 连接到服务器
    await client.connect()

if __name__ == "__main__":
    asyncio.run(main()) 
import json
import os
import sys
import threading
import asyncio
import readline  # 用于自动补全
import glob
import websockets
import time

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from gmssl import sm2, func
import gmalg
from hide.steg import embed_message, extract_message

class PathCompleter:
    """路径自动补全器"""
    def __init__(self):
        self.current_dir = os.getcwd()
        
    def complete(self, text, state):
        """自动补全函数"""
        if state == 0:
            # 第一次调用，生成补全列表
            self.matches = []
            
            # 获取当前输入的部分路径
            if text.startswith('/'):
                # 绝对路径
                base_path = text
            else:
                # 相对路径
                base_path = os.path.join(self.current_dir, text)
            
            # 获取目录部分
            dir_path = os.path.dirname(base_path)
            if not dir_path:
                dir_path = '.'
            
            # 获取文件名部分
            file_pattern = os.path.basename(base_path) + '*'
            
            try:
                # 查找匹配的文件和目录
                matches = glob.glob(os.path.join(dir_path, file_pattern))
                
                # 过滤并格式化结果
                for match in matches:
                    if os.path.isdir(match):
                        # 目录添加斜杠
                        rel_path = os.path.relpath(match, self.current_dir)
                        if not rel_path.startswith('.'):
                            self.matches.append(rel_path + '/')
                    else:
                        # 文件
                        rel_path = os.path.relpath(match, self.current_dir)
                        if not rel_path.startswith('.'):
                            self.matches.append(rel_path)
                            
            except Exception:
                pass
                
        # 返回匹配项
        if state < len(self.matches):
            return self.matches[state]
        else:
            return None

class WebSocketClient:
    def __init__(self, server_url="ws://localhost:8765"):
        self.server_url = server_url
        self.websocket = None
        self.username = None
        self.session_peer = None
        
        # 设置固定路径
        self.input_dir = os.path.join(project_root, "test")  # 输入文件目录
        self.output_dir = os.path.join(project_root, "hide", "output")  # 输出文件目录
        self.received_dir = os.path.join(project_root, "received_files")  # 接收文件目录
        
        # 确保目录存在
        os.makedirs(self.input_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.received_dir, exist_ok=True)
        
        # 设置自动补全
        self.completer = PathCompleter()
        readline.set_completer(self.completer.complete)
        readline.parse_and_bind("tab: complete")
        
    def get_available_files(self, directory, extensions=None):
        """获取指定目录下的可用文件"""
        files = []
        try:
            for file in os.listdir(directory):
                file_path = os.path.join(directory, file)
                if os.path.isfile(file_path):
                    if extensions is None or any(file.lower().endswith(ext) for ext in extensions):
                        files.append(file)
        except Exception:
            pass
        return sorted(files)
    
    def resolve_input_path(self, user_input):
        """解析输入路径"""
        if not user_input:
            return None
            
        # 如果用户输入的是文件名，自动添加输入目录
        if not os.path.dirname(user_input):
            # 只有文件名，在输入目录中查找
            input_path = os.path.join(self.input_dir, user_input)
            if os.path.exists(input_path):
                return input_path
            else:
                # 显示可用文件
                available_files = self.get_available_files(self.input_dir)
                if available_files:
                    print(f"📁 可用文件: {', '.join(available_files)}")
                return None
        else:
            # 完整路径
            if os.path.exists(user_input):
                return user_input
            else:
                print(f"❌ 文件不存在: {user_input}")
                return None
    
    def resolve_output_path(self, user_input, carrier_type):
        """解析输出路径"""
        if not user_input:
            # 生成默认文件名
            timestamp = int(time.time())
            default_name = f"stego_{carrier_type}_{timestamp}"
            
            if carrier_type == 'image':
                return os.path.join(self.output_dir, f"{default_name}.png")
            elif carrier_type == 'pdf':
                return os.path.join(self.output_dir, f"{default_name}.pdf")
            elif carrier_type == 'video':
                return os.path.join(self.output_dir, f"{default_name}.mp4")
            else:
                return os.path.join(self.output_dir, f"{default_name}.bin")
        else:
            # 用户指定了文件名
            if not os.path.dirname(user_input):
                # 只有文件名，添加到输出目录
                return os.path.join(self.output_dir, user_input)
            else:
                # 完整路径
                return user_input
        
    def ensure_sm2_keypair(self, username):
        """确保SM2密钥对存在"""
        key_dir = os.path.join(os.path.dirname(__file__), '..', 'keys')
        os.makedirs(key_dir, exist_ok=True)
        priv_path = os.path.join(key_dir, f"{username}_priv.hex")
        pub_path = os.path.join(key_dir, f"{username}_pub.hex")
        
        if not (os.path.exists(priv_path) and os.path.exists(pub_path)):
            private_key = func.random_hex(64)
            sm2_crypt = sm2.CryptSM2(public_key='', private_key=private_key)
            public_key = sm2_crypt._kg(int(private_key, 16), sm2.default_ecc_table['g'])
            with open(priv_path, 'w') as f:
                f.write(private_key)
            with open(pub_path, 'w') as f:
                f.write(public_key)
            print(f"[系统] 已为 {username} 生成SM2密钥对")
        else:
            print(f"[系统] 已加载 {username} 的SM2密钥对")
            
        with open(priv_path, 'r') as f:
            priv = f.read()
        with open(pub_path, 'r') as f:
            pub = f.read()
        return priv, pub
    
    def get_session_key_path(self, me, peer):
        base_dir = os.path.join(os.path.dirname(__file__), '..', 'session_keys')
        os.makedirs(base_dir, exist_ok=True)
        users = sorted([me, peer])
        return os.path.join(base_dir, f"{users[0]}_{users[1]}_session.key")
    
    def save_session_key(self, me, peer, session_key):
        path = self.get_session_key_path(me, peer)
        try:
            with open(path, 'w') as f:
                f.write(session_key)
            print(f"[系统] 会话密钥已保存到 {path}")
        except Exception as e:
            print(f"[错误] 保存会话密钥失败: {e}")
    
    def load_session_key(self, me, peer):
        path = self.get_session_key_path(me, peer)
        if os.path.exists(path):
            with open(path, 'r') as f:
                session_key = f.read()
            print(f"[系统] 已加载会话密钥: {path}")
            return session_key
        return None
    
    def zuc_keystream(self, zuc, length):
        stream = b''
        while len(stream) < length:
            stream += zuc.generate()
        return stream[:length]
    
    def encrypt_message(self, session_key, plaintext):
        """使用ZUC加密消息"""
        key = bytes.fromhex(session_key[:32])  # 16字节
        iv = os.urandom(16)
        zuc = gmalg.ZUC(key, iv)
        pt_bytes = plaintext.encode()
        keystream = self.zuc_keystream(zuc, len(pt_bytes))
        ciphertext = bytes([a ^ b for a, b in zip(pt_bytes, keystream)])
        return iv.hex() + ':' + ciphertext.hex()
    
    def decrypt_message(self, session_key, msg):
        """使用ZUC解密消息"""
        key = bytes.fromhex(session_key[:32])  # 16字节
        iv_hex, ct_hex = msg.split(':', 1)
        iv = bytes.fromhex(iv_hex)
        ciphertext = bytes.fromhex(ct_hex)
        zuc = gmalg.ZUC(key, iv)
        keystream = self.zuc_keystream(zuc, len(ciphertext))
        plaintext = bytes([a ^ b for a, b in zip(ciphertext, keystream)])
        return plaintext.decode()
    
    async def send_stego_message(self, carrier_type, input_path, output_path, plaintext):
        """发送隐写消息"""
        try:
            print(f"[系统] 开始发送隐写消息...")
            
            # 加密明文
            session_key = self.load_session_key(self.username, self.session_peer)
            if not session_key:
                print("[错误] 未找到会话密钥")
                return
                
            print(f"[系统] 加密消息...")
            ciphertext = self.encrypt_message(session_key, plaintext)
            
            # 隐写处理
            print(f"[系统] 执行隐写处理...")
            try:
                embed_message(carrier_type, input_path, output_path, ciphertext.encode())
            except Exception as stego_error:
                print(f"[错误] 隐写处理失败: {stego_error}")
                print("[系统] 隐写失败，但客户端将继续运行")
                return
            
            # 发送文件
            print(f"[系统] 发送隐写文件...")
            await self.send_file(output_path, carrier_type)
            print(f"[系统] 隐写消息已发送: {output_path}")
            
        except Exception as e:
            print(f"[错误] 发送隐写消息失败: {e}")
            print("[系统] 隐写消息发送失败，但客户端将继续运行")
            import traceback
            traceback.print_exc()
    
    async def send_file(self, filepath, filetype):
        """发送文件"""
        try:
            print(f"[系统] 准备发送文件: {filepath}")
            
            if not os.path.exists(filepath):
                print(f"[错误] 文件不存在: {filepath}")
                return
                
            filesize = os.path.getsize(filepath)
            filename = os.path.basename(filepath)
            
            print(f"[系统] 文件大小: {filesize} bytes")
            
            # 检查文件大小，如果超过1MB则分块传输
            MAX_CHUNK_SIZE = 1024 * 1024  # 1MB
            
            if filesize > MAX_CHUNK_SIZE:
                print(f"[系统] 文件过大，使用分块传输...")
                await self.send_file_chunked(filepath, filetype, filename, filesize)
            else:
                print(f"[系统] 读取文件内容...")
                # 读取文件内容
                with open(filepath, 'rb') as f:
                    file_data = f.read()
                
                fileinfo = {
                    "type": "file",
                    "filename": filename,
                    "filetype": filetype,
                    "filesize": filesize,
                    "from": self.username,
                    "to": self.session_peer,
                    "data": file_data.hex()  # 转换为hex传输
                }
                
                print(f"[系统] 发送文件消息...")
                await self.websocket.send(json.dumps(fileinfo))
                print(f"[系统] 文件已发送: {filename}")
            
        except Exception as e:
            print(f"[错误] 发送文件失败: {e}")
            import traceback
            traceback.print_exc()
    
    async def send_file_chunked(self, filepath, filetype, filename, filesize):
        """分块发送大文件"""
        try:
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
            print(f"[系统] 发送文件开始消息: {filename} ({filesize} bytes, {(filesize + CHUNK_SIZE - 1) // CHUNK_SIZE} chunks)")
            
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
                    print(f"[系统] 发送块 {chunk_index + 1}: {len(chunk_data)} bytes")
                    chunk_index += 1
            
            # 发送文件结束消息
            end_msg = {
                "type": "file_end",
                "filename": filename,
                "from": self.username,
                "to": self.session_peer
            }
            await self.websocket.send(json.dumps(end_msg))
            print(f"[系统] 文件传输完成: {filename}")
            
        except Exception as e:
            print(f"[错误] 分块发送文件失败: {e}")
            import traceback
            traceback.print_exc()
    
    async def handle_message(self, message):
        """处理接收到的消息"""
        try:
            data = json.loads(message)
            print(f"[系统] 收到消息类型: {data.get('type')}")
            
            if data.get('type') == 'msg':
                # 加密消息
                peer = data['from']
                print(f"[系统] 收到来自 {peer} 的消息")
                session_key = self.load_session_key(self.username, peer)
                if session_key:
                    try:
                        plaintext = self.decrypt_message(session_key, data['content'])
                        print(f"[{peer}] {plaintext}")
                    except Exception as e:
                        print(f"[系统] 解密失败: {e}")
                else:
                    print(f"[系统] 未找到与 {peer} 的会话密钥")
                    
            elif data.get('type') == 'file':
                # 文件消息
                peer = data['from']
                filename = data['filename']
                filetype = data['filetype']
                print(f"[系统] 收到来自 {peer} 的文件: {filename} (类型: {filetype})")
                
                try:
                    file_data = bytes.fromhex(data['data'])
                    print(f"[系统] 文件数据大小: {len(file_data)} bytes")
                    
                    # 保存文件
                    save_dir = os.path.join(os.path.dirname(__file__), '..', 'received_files')
                    os.makedirs(save_dir, exist_ok=True)
                    save_path = os.path.join(save_dir, filename)
                    
                    with open(save_path, 'wb') as f:
                        f.write(file_data)
                    
                    print(f"[系统] 文件已保存: {save_path}")
                    
                    # 如果是隐写文件，自动提取
                    if filetype in ['image', 'pdf', 'video']:
                        print(f"[系统] 检测到隐写文件，开始提取...")
                        try:
                            extracted_data = extract_message(filetype, save_path)
                            print(f"[系统] 隐写提取成功，数据大小: {len(extracted_data)} bytes")
                            
                            session_key = self.load_session_key(self.username, peer)
                            if session_key:
                                plaintext = self.decrypt_message(session_key, extracted_data.decode())
                                print(f"[{peer}] (隐写消息) {plaintext}")
                            else:
                                print(f"[系统] 未找到与 {peer} 的会话密钥")
                        except Exception as e:
                            print(f"[系统] 隐写提取失败: {e}")
                            import traceback
                            traceback.print_exc()
                except Exception as e:
                    print(f"[系统] 处理文件失败: {e}")
                    import traceback
                    traceback.print_exc()
                    
            elif data.get('type') == 'file_start':
                # 分块文件开始
                peer = data['from']
                filename = data['filename']
                filetype = data['filetype']
                filesize = data['filesize']
                chunks = data['chunks']
                print(f"[系统] 收到来自 {peer} 的分块文件开始: {filename} ({filesize} bytes, {chunks} chunks)")
                
                # 初始化文件接收状态
                if not hasattr(self, 'file_receiving'):
                    self.file_receiving = {}
                
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
                    print(f"[系统] 收到文件块 {chunk_index + 1}: {len(chunk_data)} bytes")
                    
            elif data.get('type') == 'file_end':
                # 分块文件结束
                peer = data['from']
                filename = data['filename']
                
                if filename in self.file_receiving:
                    file_info = self.file_receiving[filename]
                    expected_chunks = file_info['chunks']
                    received_chunks = len(file_info['received_chunks'])
                    
                    print(f"[系统] 文件传输完成: {filename} ({received_chunks}/{expected_chunks} chunks)")
                    
                    if received_chunks == expected_chunks:
                        # 保存完整文件
                        save_dir = os.path.join(os.path.dirname(__file__), '..', 'received_files')
                        os.makedirs(save_dir, exist_ok=True)
                        save_path = os.path.join(save_dir, filename)
                        
                        with open(save_path, 'wb') as f:
                            f.write(file_info['data'])
                        
                        print(f"[系统] 分块文件已保存: {save_path}")
                        
                        # 如果是隐写文件，自动提取
                        if file_info['filetype'] in ['image', 'pdf', 'video']:
                            print(f"[系统] 检测到隐写文件，开始提取...")
                            try:
                                extracted_data = extract_message(file_info['filetype'], save_path)
                                print(f"[系统] 隐写提取成功，数据大小: {len(extracted_data)} bytes")
                                
                                session_key = self.load_session_key(self.username, peer)
                                if session_key:
                                    plaintext = self.decrypt_message(session_key, extracted_data.decode())
                                    print(f"[{peer}] (隐写消息) {plaintext}")
                                else:
                                    print(f"[系统] 未找到与 {peer} 的会话密钥")
                            except Exception as e:
                                print(f"[系统] 隐写提取失败: {e}")
                                import traceback
                                traceback.print_exc()
                    else:
                        print(f"[错误] 文件传输不完整: {received_chunks}/{expected_chunks} chunks")
                    
                    # 清理接收状态
                    del self.file_receiving[filename]
                        
            elif data.get('type') == 'key_exchange':
                # 密钥交换
                peer = data['peer']
                peer_pub = data['peer_pub']
                
                priv, pub = self.ensure_sm2_keypair(self.username)
                sm2_crypt = sm2.CryptSM2(public_key=peer_pub, private_key=priv)
                session_key = sm2_crypt._kg(int(priv, 16), peer_pub)[:32]
                
                self.save_session_key(self.username, peer, session_key)
                print(f"[系统] 与 {peer} 的密钥交换完成")
                
            elif data.get('type') == 'session_ready':
                # 会话建立
                peer = data['peer']
                self.session_peer = peer
                print(f"[系统] 已与 {peer} 建立会话")
                
            elif data.get('type') == 'user_list':
                print(f"[系统] 在线用户: {', '.join(data['users'])}")
                
        except json.JSONDecodeError:
            print(f"[系统] 收到非JSON消息: {message}")
        except Exception as e:
            print(f"[错误] 处理消息失败: {e}")
    
    async def connect(self):
        """连接到WebSocket服务器"""
        try:
            self.websocket = await websockets.connect(self.server_url)
            print(f"[系统] 已连接到服务器: {self.server_url}")
            
            # 发送用户名
            await self.websocket.send(json.dumps({
                "type": "login",
                "username": self.username
            }))
            
            # 发送公钥
            priv, pub = self.ensure_sm2_keypair(self.username)
            await self.websocket.send(json.dumps({
                "type": "pubkey",
                "username": self.username,
                "pubkey": pub
            }))
            
            # 开始接收消息
            async for message in self.websocket:
                await self.handle_message(message)
                
        except Exception as e:
            print(f"[错误] 连接失败: {e}")
    
    async def send_text_message(self, text):
        """发送文本消息"""
        if not self.session_peer:
            print("[错误] 未建立会话")
            return
            
        try:
            session_key = self.load_session_key(self.username, self.session_peer)
            if not session_key:
                print("[错误] 未找到会话密钥")
                return
                
            encrypted = self.encrypt_message(session_key, text)
            
            message = {
                "type": "msg",
                "to": self.session_peer,
                "from": self.username,
                "content": encrypted
            }
            
            await self.websocket.send(json.dumps(message))
            print(f"[我] {text}")
            
        except Exception as e:
            print(f"[错误] 发送消息失败: {e}")
    
    def start_input_loop(self):
        """启动输入循环"""
        async def input_loop():
            while True:
                try:
                    user_input = await asyncio.get_event_loop().run_in_executor(
                        None, input, "> "
                    )
                    
                    if user_input.strip() in ("quit", "exit"):
                        print("[系统] 退出客户端")
                        break
                    elif user_input.startswith("sendfile "):
                        # 发送文件
                        print("\n=== 发送文件 ===")
                        try:
                            parts = user_input.split()
                            if len(parts) >= 3:
                                filepath = parts[1]
                                filetype = parts[2]
                                
                                # 解析文件路径
                                resolved_path = self.resolve_input_path(filepath)
                                if resolved_path:
                                    await self.send_file(resolved_path, filetype)
                                else:
                                    print("❌ 文件不存在")
                            else:
                                print("❌ 用法: sendfile <文件名> <文件类型>")
                        except Exception as e:
                            print(f"[系统] 发送文件失败: {e}")
                    elif user_input == "sendmsg":
                        # 发送隐写消息
                        print("\n=== 发送隐写消息 ===")
                        
                        # 选择隐写类型
                        carrier_type = input("请选择隐写类型（image/pdf/video）: ").strip().lower()
                        if carrier_type not in ['image', 'pdf', 'video']:
                            print("❌ 不支持的隐写类型")
                            continue
                        
                        # 显示可用文件
                        extensions = {
                            'image': ['.png', '.jpg', '.jpeg', '.bmp', '.tiff'],
                            'pdf': ['.pdf'],
                            'video': ['.mp4', '.avi', '.mov', '.mkv']
                        }
                        
                        available_files = self.get_available_files(self.input_dir, extensions[carrier_type])
                        if available_files:
                            print(f"📁 可用的{carrier_type}文件: {', '.join(available_files)}")
                        else:
                            print(f"⚠️  在 {self.input_dir} 中没有找到{carrier_type}文件")
                        
                        # 输入载体文件
                        input_file = input(f"请输入载体文件名（或完整路径）: ").strip()
                        input_path = self.resolve_input_path(input_file)
                        if not input_path:
                            print("❌ 无法找到载体文件")
                            continue
                        
                        # 输入输出文件名
                        output_file = input(f"请输入输出文件名（留空使用默认名称）: ").strip()
                        output_path = self.resolve_output_path(output_file, carrier_type)
                        print(f"📁 输出路径: {output_path}")
                        
                        # 输入消息
                        plaintext = input("请输入要发送的明文消息: ").strip()
                        if not plaintext:
                            print("❌ 消息不能为空")
                            continue
                        
                        await self.send_stego_message(carrier_type, input_path, output_path, plaintext)
                    elif user_input == "files":
                        # 显示可用文件
                        print("\n=== 可用文件 ===")
                        print(f"📁 输入目录: {self.input_dir}")
                        
                        all_files = self.get_available_files(self.input_dir)
                        if all_files:
                            print("📄 所有文件:")
                            for file in all_files:
                                print(f"  - {file}")
                        else:
                            print("⚠️  没有找到文件")
                        
                        # 按类型分类显示
                        extensions = {
                            'image': ['.png', '.jpg', '.jpeg', '.bmp', '.tiff'],
                            'pdf': ['.pdf'],
                            'video': ['.mp4', '.avi', '.mov', '.mkv']
                        }
                        
                        for file_type, exts in extensions.items():
                            files = self.get_available_files(self.input_dir, exts)
                            if files:
                                print(f"\n🖼️  {file_type}文件:")
                                for file in files:
                                    print(f"  - {file}")
                    elif user_input == "extractmsg":
                        # 提取隐写消息
                        print("\n=== 提取隐写消息 ===")
                        carrier_type = input("请选择隐写类型（image/pdf/video）: ").strip().lower()
                        if carrier_type not in ['image', 'pdf', 'video']:
                            print("❌ 不支持的隐写类型")
                            continue
                        
                        # 显示可用文件
                        extensions = {
                            'image': ['.png', '.jpg', '.jpeg', '.bmp', '.tiff'],
                            'pdf': ['.pdf'],
                            'video': ['.mp4', '.avi', '.mov', '.mkv']
                        }
                        
                        available_files = self.get_available_files(self.output_dir, extensions[carrier_type])
                        if available_files:
                            print(f"📁 可用的{carrier_type}文件: {', '.join(available_files)}")
                        
                        stego_file = input("请输入隐写文件名（或完整路径）: ").strip()
                        stego_path = self.resolve_input_path(stego_file)
                        if not stego_path:
                            # 尝试在输出目录中查找
                            stego_path = os.path.join(self.output_dir, stego_file)
                            if not os.path.exists(stego_path):
                                print("❌ 无法找到隐写文件")
                                continue
                        
                        try:
                            extracted_data = extract_message(carrier_type, stego_path)
                            session_key = self.load_session_key(self.username, self.session_peer)
                            if session_key:
                                plaintext = self.decrypt_message(session_key, extracted_data.decode())
                                print(f"[系统] 解密得到明文: {plaintext}")
                            else:
                                print("[系统] 未找到会话密钥")
                        except Exception as e:
                            print(f"[错误] 提取隐写消息失败: {e}")
                            import traceback
                            traceback.print_exc()
                    else:
                        # 发送普通消息
                        await self.send_text_message(user_input)
                        
                except EOFError:
                    break
                except Exception as e:
                    print(f"[错误] 输入处理失败: {e}")
        
        asyncio.create_task(input_loop())

    def run(self):
        """运行客户端（同步接口）"""
        try:
            self.username = input("请输入用户名: ").strip()
            if not self.username:
                print("[错误] 用户名不能为空")
                return
                
            print("\n=== 命令说明 ===")
            print("sendmsg - 发送隐写消息")
            print("sendfile <文件名> <文件类型> - 发送文件")
            print("files - 显示可用文件")
            print("extractmsg - 提取隐写消息")
            print("quit/exit - 退出")
            print("================\n")
            
            # 启动异步事件循环
            asyncio.run(self._run_async())
            
        except KeyboardInterrupt:
            print("\n👋 用户退出")
        except Exception as e:
            print(f"\n❌ 客户端运行错误: {e}")
    
    async def _run_async(self):
        """异步运行客户端"""
        # 启动输入循环
        self.start_input_loop()
        
        # 连接到服务器
        await self.connect()

async def main():
    client = WebSocketClient()
    client.username = input("请输入用户名: ").strip()
    
    # 启动输入循环
    client.start_input_loop()
    
    # 连接到服务器
    await client.connect()

if __name__ == "__main__":
    asyncio.run(main()) 