import firebase_admin
from firebase_admin import credentials, db, storage
import json
import os
import time
import threading
from gmssl import sm2, func
import gmalg
from hide.steg import embed_message, extract_message

class FirebaseClient:
    def __init__(self, config_path="firebase_config.json"):
        self.config_path = config_path
        self.username = None
        self.session_peer = None
        self.session_key = None
        self.db_ref = None
        self.storage_bucket = None
        self.listener = None
        
        # 初始化Firebase
        self._init_firebase()
        
    def _init_firebase(self):
        """初始化Firebase连接"""
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate(self.config_path)
                firebase_admin.initialize_app(cred, {
                    'databaseURL': 'https://your-project.firebaseio.com',
                    'storageBucket': 'your-project.appspot.com'
                })
            
            self.db_ref = db.reference()
            self.storage_bucket = storage.bucket()
            print("[系统] Firebase连接成功")
            
        except Exception as e:
            print(f"[错误] Firebase初始化失败: {e}")
            print("请确保firebase_config.json文件存在且配置正确")
    
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
    
    def on_message_received(self, event):
        """处理接收到的消息"""
        try:
            if event.data_type == 'put':
                data = event.data
                if data:
                    message_type = data.get('type')
                    
                    if message_type == 'msg':
                        # 加密消息
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
                            
                    elif message_type == 'file':
                        # 文件消息
                        peer = data['from']
                        filename = data['filename']
                        file_url = data['file_url']
                        
                        # 从Firebase Storage下载文件
                        self.download_file(file_url, filename)
                        print(f"[系统] 文件已下载: {filename}")
                        
                        # 如果是隐写文件，自动提取
                        filetype = data.get('filetype')
                        if filetype in ['image', 'pdf', 'video']:
                            try:
                                save_path = os.path.join(os.path.dirname(__file__), '..', 'received_files', filename)
                                extracted_data = extract_message(filetype, save_path)
                                session_key = self.load_session_key(self.username, peer)
                                if session_key:
                                    plaintext = self.decrypt_message(session_key, extracted_data.decode())
                                    print(f"[{peer}] (隐写消息) {plaintext}")
                            except Exception as e:
                                print(f"[系统] 隐写提取失败: {e}")
                                
                    elif message_type == 'key_exchange':
                        # 密钥交换
                        peer = data['peer']
                        peer_pub = data['peer_pub']
                        
                        priv, pub = self.ensure_sm2_keypair(self.username)
                        sm2_crypt = sm2.CryptSM2(public_key=peer_pub, private_key=priv)
                        session_key = sm2_crypt._kg(int(priv, 16), peer_pub)[:32]
                        
                        self.save_session_key(self.username, peer, session_key)
                        print(f"[系统] 与 {peer} 的密钥交换完成")
                        
                    elif message_type == 'session_ready':
                        # 会话建立
                        peer = data['peer']
                        self.session_peer = peer
                        print(f"[系统] 已与 {peer} 建立会话")
                        
        except Exception as e:
            print(f"[错误] 处理消息失败: {e}")
    
    def start_listening(self):
        """开始监听消息"""
        try:
            # 监听用户消息
            messages_ref = self.db_ref.child('messages').child(self.username)
            self.listener = messages_ref.listen(self.on_message_received)
            print(f"[系统] 开始监听消息: {self.username}")
            
        except Exception as e:
            print(f"[错误] 启动监听失败: {e}")
    
    def stop_listening(self):
        """停止监听"""
        if self.listener:
            self.listener.close()
            print("[系统] 已停止监听")
    
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
                "type": "msg",
                "to": self.session_peer,
                "from": self.username,
                "content": encrypted,
                "timestamp": time.time()
            }
            
            # 发送到Firebase
            self.db_ref.child('messages').child(self.session_peer).push(message)
            print(f"[我] {text}")
            
        except Exception as e:
            print(f"[错误] 发送消息失败: {e}")
    
    def upload_file(self, filepath, filetype):
        """上传文件到Firebase Storage"""
        try:
            filename = os.path.basename(filepath)
            blob = self.storage_bucket.blob(f"files/{filename}")
            
            with open(filepath, 'rb') as f:
                blob.upload_from_file(f)
            
            # 生成下载URL
            blob.make_public()
            file_url = blob.public_url
            
            return file_url
            
        except Exception as e:
            print(f"[错误] 上传文件失败: {e}")
            return None
    
    def download_file(self, file_url, filename):
        """从Firebase Storage下载文件"""
        try:
            save_dir = os.path.join(os.path.dirname(__file__), '..', 'received_files')
            os.makedirs(save_dir, exist_ok=True)
            save_path = os.path.join(save_dir, filename)
            
            blob = self.storage_bucket.blob(f"files/{filename}")
            blob.download_to_filename(save_path)
            
            return save_path
            
        except Exception as e:
            print(f"[错误] 下载文件失败: {e}")
            return None
    
    def send_file(self, filepath, filetype):
        """发送文件"""
        try:
            # 上传文件
            file_url = self.upload_file(filepath, filetype)
            if not file_url:
                return
                
            filename = os.path.basename(filepath)
            filesize = os.path.getsize(filepath)
            
            file_message = {
                "type": "file",
                "filename": filename,
                "filetype": filetype,
                "filesize": filesize,
                "from": self.username,
                "to": self.session_peer,
                "file_url": file_url,
                "timestamp": time.time()
            }
            
            # 发送文件消息
            self.db_ref.child('messages').child(self.session_peer).push(file_message)
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
    
    def login(self, username):
        """用户登录"""
        self.username = username
        
        # 确保密钥对存在
        priv, pub = self.ensure_sm2_keypair(username)
        
        # 更新用户状态
        self.db_ref.child('users').child(username).set({
            'online': True,
            'pubkey': pub,
            'last_seen': time.time()
        })
        
        # 检查是否有其他在线用户
        users = self.db_ref.child('users').get()
        online_users = []
        for user, data in users.items():
            if user != username and data.get('online'):
                online_users.append(user)
        
        if online_users:
            peer = online_users[0]
            self.session_peer = peer
            
            # 通知对方会话建立
            self.db_ref.child('messages').child(peer).push({
                "type": "session_ready",
                "peer": username,
                "timestamp": time.time()
            })
            
            # 开始密钥交换
            self.db_ref.child('messages').child(peer).push({
                "type": "key_exchange",
                "peer": username,
                "peer_pub": pub,
                "timestamp": time.time()
            })
            
            print(f"[系统] 已与 {peer} 建立会话")
        
        # 开始监听消息
        self.start_listening()
    
    def logout(self):
        """用户登出"""
        if self.username:
            # 更新用户状态
            self.db_ref.child('users').child(self.username).update({
                'online': False,
                'last_seen': time.time()
            })
            
            # 停止监听
            self.stop_listening()
            
            print(f"[系统] 用户 {self.username} 已登出")
    
    def run(self):
        """运行客户端"""
        try:
            username = input("请输入用户名: ").strip()
            if not username:
                print("[错误] 用户名不能为空")
                return
                
            self.login(username)
            
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
            self.logout()

if __name__ == "__main__":
    client = FirebaseClient()
    client.run() 