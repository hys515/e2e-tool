import socket
import threading
import json
import sys
import time
from gmssl import sm2, func
import os

SERVER_HOST = '127.0.0.1'  # 服务器地址
SERVER_PORT = 50000        # 服务器端口


def recv_thread(sock):
    while True:
        try:
            data = sock.recv(4096)
            if not data:
                print("[系统] 服务器断开连接")
                break
            for line in data.split(b'\n'):
                if not line.strip():
                    continue
                try:
                    msg = json.loads(line.decode())
                    if msg.get('type') == 'user_list':
                        print(f"[系统] 在线用户: {', '.join(msg['users'])}")
                    elif msg.get('type') == 'msg':
                        print(f"[消息] 来自 {msg['from']}: {msg['content']}")
                    else:
                        print(f"[系统] {msg}")
                except Exception:
                    print("[系统] ", line.decode(errors='ignore'))
        except Exception as e:
            if isinstance(e, OSError) and e.errno == 9:
                # 文件描述符关闭，属于正常退出
                break
            print(f"[错误] 接收消息异常: {e}")
            break

def ensure_sm2_keypair(username):
    key_dir = os.path.join(os.path.dirname(__file__), '..', 'keys')
    os.makedirs(key_dir, exist_ok=True)
    priv_path = os.path.join(key_dir, f"{username}_priv.hex")
    pub_path = os.path.join(key_dir, f"{username}_pub.hex")
    if not (os.path.exists(priv_path) and os.path.exists(pub_path)):
        print(f"[系统] 为用户 {username} 生成SM2密钥对...")
        # 生成私钥（64位16进制字符串，32字节）
        private_key = func.random_hex(64)
        sm2_crypt = sm2.CryptSM2(public_key='', private_key=private_key)
        public_key = sm2_crypt._kg(int(private_key, 16), sm2.default_ecc_table['g'])
        with open(priv_path, 'w') as f:
            f.write(private_key)
        with open(pub_path, 'w') as f:
            f.write(public_key)
        print(f"[系统] 已为 {username} 生成SM2密钥对")
    with open(priv_path, 'r') as f:
        priv = f.read()
    with open(pub_path, 'r') as f:
        pub = f.read()
    print(f"[系统] 你的SM2私钥（hex，32字节）:\n{priv}")
    print(f"[系统] 你的SM2公钥（hex，64字节）:\n{pub}")
    return priv_path, pub_path

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((SERVER_HOST, SERVER_PORT))
        # 注册用户名
        prompt = sock.recv(1024).decode()
        username = input(prompt)
        sock.sendall((username + '\n').encode())
        ensure_sm2_keypair(username)
        # 启动接收线程
        threading.Thread(target=recv_thread, args=(sock,), daemon=True).start()
        # 主循环
        while True:
            try:
                cmd = input("[你] > ").strip()
                if cmd == 'exit':
                    print("[系统] 退出客户端")
                    break
                elif cmd == 'list':
                    # 服务器会自动推送在线用户列表
                    continue
                elif cmd.startswith('msg '):
                    # 发送消息: msg <用户名> <内容>
                    parts = cmd.split(' ', 2)
                    if len(parts) < 3:
                        print("用法: msg <用户名> <内容>")
                        continue
                    to_user, content = parts[1], parts[2]
                    msg = json.dumps({'type': 'msg', 'to': to_user, 'content': content})
                    sock.sendall(msg.encode())
                else:
                    print("[系统] 支持命令: list, msg <用户名> <内容>, exit")
            except Exception as e:
                print(f"[错误] {e}")
                break
    sock.close()
    time.sleep(0.1)  # 给接收线程一点时间退出

if __name__ == "__main__":
    main() 