import socketio
import json
import os
import time
from gmssl import sm2, func
import gmalg
from hide.steg import embed_message, extract_message

class SocketIOClient:
    def __init__(self, server_url="http://localhost:5000"):
        self.server_url = server_url
        self.sio = socketio.Client()
        self.username = None
        self.session_peer = None
        self.session_key = None
        
        # 设置Socket.IO事件处理器
        self._setup_event_handlers()
        
    def _setup_event_handlers(self):
        """设置Socket.IO事件处理器"""
        
        @self.sio.event
        def connect():
            print(f"[系统] 已连接到服务器: {self.server_url}")
            
        @self.sio.event
        def disconnect():
            print("[系统] 与服务器断开连接")
            
        @self.sio.on('message')
        def on_message(data):
            self._handle_message(data)
            
        @self.sio.on('file')
        def on_file(data):
            self._handle_file(data)
            
        @self.sio.on('key_exchange')
        def on_key_exchange(data):
            self._handle_key_exchange(data)
            
        @self.sio.on('session_ready')
        def on_session_ready(data):
            self._handle_session_ready(data)
            
        @self.sio.on('user_list')
        def on_user_list(data):
            print(f"[系统] 在线用户: {', '.join(data['users'])}")
            
        @self.sio.on('error')
        def on_error(data):
            print(f"[错误] {data['message']}")
    
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
    
    def _handle_message(self, data):
        """处理接收到的消息"""
        try:
            peer = data['from']
            session_key = self.load_session_key(self.username, peer)
            if session_key:
                try:
                    plaintext = self.decrypt_message(session_key, data['content'])
                    print(f"[{peer}] {plaintext}")
                except Exception as e:
                    print(f"[系统] 解密失败: {e}")
            else:
                print(f"[系统] 未找到与 {peer} 的会话密钥")
        except Exception as e:
            print(f"[错误] 处理消息失败: {e}")
    
    def _handle_file(self, data):
        """处理接收到的文件"""
        try:
            peer = data['from']
            filename = data['filename']
            filetype = data['filetype']
            file_data = bytes.fromhex(data['data'])
            
            # 保存文件
            save_dir = os.path.join(os.path.dirname(__file__), '..', 'received_files')
            os.makedirs(save_dir, exist_ok=True)
            save_path = os.path.join(save_dir, filename)
            
            with open(save_path, 'wb') as f:
                f.write(file_data)
            
            print(f"[系统] 文件已接收: {save_path}")
            
            # 如果是隐写文件，自动提取
            if filetype in ['image', 'pdf', 'video']:
                try:
                    extracted_data = extract_message(filetype, save_path)
                    session_key = self.load_session_key(self.username, peer)
                    if session_key:
                        plaintext = self.decrypt_message(session_key, extracted_data.decode())
                        print(f"[{peer}] (隐写消息) {plaintext}")
                except Exception as e:
                    print(f"[系统] 隐写提取失败: {e}")
                    
        except Exception as e:
            print(f"[错误] 处理文件失败: {e}")
    
    def _handle_key_exchange(self, data):
        """处理密钥交换"""
        try:
            peer = data['peer']
            peer_pub = data['peer_pub']
            
            priv, pub = self.ensure_sm2_keypair(self.username)
            sm2_crypt = sm2.CryptSM2(public_key=peer_pub, private_key=priv)
            session_key = sm2_crypt._kg(int(priv, 16), peer_pub)[:32]
            
            self.save_session_key(self.username, peer, session_key)
            print(f"[系统] 与 {peer} 的密钥交换完成")
            
        except Exception as e:
            print(f"[错误] 密钥交换失败: {e}")
    
    def _handle_session_ready(self, data):
        """处理会话建立"""
        try:
            peer = data['peer']
            self.session_peer = peer
            print(f"[系统] 已与 {peer} 建立会话")
            
        except Exception as e:
            print(f"[错误] 处理会话建立失败: {e}")
    
    def connect(self, username):
        """连接到服务器"""
        try:
            self.username = username
            
            # 确保密钥对存在
            priv, pub = self.ensure_sm2_keypair(username)
            
            # 连接到服务器
            self.sio.connect(self.server_url)
            
            # 发送登录信息
            self.sio.emit('login', {
                'username': username,
                'pubkey': pub
            })
            
            print(f"[系统] 用户 {username} 已登录")
            
        except Exception as e:
            print(f"[错误] 连接失败: {e}")
    
    def disconnect(self):
        """断开连接"""
        if self.sio.connected:
            self.sio.disconnect()
        print(f"[系统] 用户 {self.username} 已登出")
    
    def send_message(self, text):
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
                "to": self.session_peer,
                "from": self.username,
                "content": encrypted
            }
            
            self.sio.emit('message', message)
            print(f"[我] {text}")
            
        except Exception as e:
            print(f"[错误] 发送消息失败: {e}")
    
    def send_file(self, filepath, filetype):
        """发送文件"""
        try:
            filesize = os.path.getsize(filepath)
            filename = os.path.basename(filepath)
            
            # 读取文件内容
            with open(filepath, 'rb') as f:
                file_data = f.read()
            
            fileinfo = {
                "filename": filename,
                "filetype": filetype,
                "filesize": filesize,
                "from": self.username,
                "to": self.session_peer,
                "data": file_data.hex()  # 转换为hex传输
            }
            
            self.sio.emit('file', fileinfo)
            print(f"[系统] 文件已发送: {filename}")
            
        except Exception as e:
            print(f"[错误] 发送文件失败: {e}")
    
    def send_stego_message(self, carrier_type, input_path, output_path, plaintext):
        """发送隐写消息"""
        try:
            # 加密明文
            session_key = self.load_session_key(self.username, self.session_peer)
            if not session_key:
                print("[错误] 未找到会话密钥")
                return
                
            ciphertext = self.encrypt_message(session_key, plaintext)
            
            # 隐写处理
            embed_message(carrier_type, input_path, output_path, ciphertext.encode())
            
            # 发送文件
            self.send_file(output_path, carrier_type)
            print(f"[系统] 隐写消息已发送: {output_path}")
            
        except Exception as e:
            print(f"[错误] 发送隐写消息失败: {e}")
    
    def run(self):
        """运行客户端"""
        try:
            username = input("请输入用户名: ").strip()
            if not username:
                print("[错误] 用户名不能为空")
                return
                
            self.connect(username)
            
            print("\n=== 命令说明 ===")
            print("sendmsg - 发送隐写消息")
            print("sendfile <filepath> <filetype> - 发送文件")
            print("extractmsg - 提取隐写消息")
            print("quit/exit - 退出")
            print("================\n")
            
            while True:
                try:
                    user_input = input("> ").strip()
                    
                    if user_input in ("quit", "exit"):
                        break
                    elif user_input.startswith("sendfile "):
                        try:
                            _, filepath, filetype = user_input.split()
                            self.send_file(filepath, filetype)
                        except Exception as e:
                            print(f"[系统] 用法: sendfile <filepath> <filetype>，错误: {e}")
                    elif user_input == "sendmsg":
                        carrier_type = input("请选择隐写类型（image/pdf/video）: ").strip()
                        input_path = input("请输入原始载体文件路径: ").strip()
                        output_path = input("请输入隐写输出文件路径: ").strip()
                        plaintext = input("请输入要发送的明文消息: ").strip()
                        self.send_stego_message(carrier_type, input_path, output_path, plaintext)
                    elif user_input == "extractmsg":
                        carrier_type = input("请选择隐写类型（image/pdf/video）: ").strip()
                        stego_path = input("请输入隐写文件路径: ").strip()
                        try:
                            extracted_data = extract_message(carrier_type, stego_path)
                            session_key = self.load_session_key(self.username, self.session_peer)
                            if session_key:
                                plaintext = self.decrypt_message(session_key, extracted_data.decode())
                                print(f"[系统] 解密得到明文: {plaintext}")
                        except Exception as e:
                            print(f"[错误] 提取隐写消息失败: {e}")
                    else:
                        self.send_message(user_input)
                        
                except EOFError:
                    break
                except Exception as e:
                    print(f"[错误] 输入处理失败: {e}")
                    
        except KeyboardInterrupt:
            print("\n[系统] 收到退出信号")
        finally:
            self.disconnect()

if __name__ == "__main__":
    client = SocketIOClient()
    client.run() 