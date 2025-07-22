import socket
import threading
import json
import os
from gmssl import sm2, func
import errno

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 50000

def ensure_sm2_keypair(username):
    key_dir = os.path.join(os.path.dirname(__file__), '..', 'keys')
    os.makedirs(key_dir, exist_ok=True)
    priv_path = os.path.join(key_dir, f"{username}_priv.hex")
    pub_path = os.path.join(key_dir, f"{username}_pub.hex")
    if not (os.path.exists(priv_path) and os.path.exists(pub_path)):
        print(f"[系统] 为用户 {username} 生成SM2密钥对...")
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
    return priv, pub

def get_session_key_path(me, peer):
    base_dir = os.path.join(os.path.dirname(__file__), '..', 'session_keys')
    os.makedirs(base_dir, exist_ok=True)
    return os.path.join(base_dir, f"{me}_{peer}_session.key")

def save_session_key(me, peer, session_key):
    path = get_session_key_path(me, peer)
    with open(path, 'w') as f:
        f.write(session_key)

def load_session_key(me, peer):
    path = get_session_key_path(me, peer)
    if os.path.exists(path):
        with open(path, 'r') as f:
            return f.read()
    return None

def recv_thread(sock, username, state):
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
                except Exception:
                    # 跳过非JSON行
                    continue
                if msg.get('type') == 'user_list':
                    print(f"[系统] 在线用户: {', '.join(msg['users'])}")
                elif msg.get('type') == 'key_exchange_request':
                    peer = msg['from']
                    print(f"[系统] 收到来自 {peer} 的密钥交换请求，正在协商...")
                    priv, pub = ensure_sm2_keypair(username)
                    resp = {
                        "type": "key_exchange_response",
                        "to": peer,
                        "pubkey": pub
                    }
                    sock.sendall((json.dumps(resp) + '\n').encode())
                    state['session_peer'] = peer
                elif msg.get('type') == 'key_exchange_response':
                    peer = msg['from']
                    peer_pub = msg['pubkey']
                    priv, pub = ensure_sm2_keypair(username)
                    sm2_crypt = sm2.CryptSM2(public_key=peer_pub, private_key=priv)
                    session_key = sm2_crypt._kg(int(priv, 16), peer_pub)[:32]
                    save_session_key(username, peer, session_key)
                    print(f"[系统] 与 {peer} 的会话密钥协商完成，可以通话了。")
                    state['session_peer'] = peer
                elif msg.get('type') == 'msg':
                    print(f"[{msg['from']}] {msg['content']}")
                else:
                    print(f"[系统] {msg}")
        except OSError as e:
            if e.errno == errno.EBADF:  # 9
                # socket 已关闭，属于正常退出
                break
            print(f"[错误] 接收消息异常: {e}")
            break
        except Exception as e:
            print(f"[错误] 接收消息异常: {e}")
            break

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((SERVER_HOST, SERVER_PORT))
        prompt = sock.recv(1024).decode()
        username = input(prompt)
        sock.sendall((username + '\n').encode())
        priv, pub = ensure_sm2_keypair(username)
        state = {'session_peer': None}
        threading.Thread(target=recv_thread, args=(sock, username, state), daemon=True).start()
        while True:
            cmd = input("> ").strip()
            if cmd == "list":
                sock.sendall((json.dumps({"type": "list"}) + '\n').encode())
            elif cmd.startswith("connect "):
                peer = cmd.split(" ", 1)[1]
                if peer == username:
                    print("[系统] 不能和自己建立会话")
                    continue
                session_key = load_session_key(username, peer)
                if session_key:
                    print(f"[系统] 加载已有的会话密钥，可以直接通话。")
                else:
                    msg = {"type": "key_exchange_request", "to": peer, "from": username, "pubkey": pub}
                    sock.sendall((json.dumps(msg) + '\n').encode())
                    print(f"[系统] 已向 {peer} 发起密钥交换请求。")
                state['session_peer'] = peer
            elif cmd == "leave":
                if state['session_peer']:
                    print(f"[系统] 已退出与 {state['session_peer']} 的会话")
                    state['session_peer'] = None
                else:
                    print("[系统] 当前未处于会话中")
            elif cmd in ("quit", "logout"):
                print("[系统] 退出客户端")
                sock.close()
                break
            elif state['session_peer']:
                msg = {
                    "type": "msg",
                    "to": state['session_peer'],
                    "from": username,
                    "content": cmd
                }
                sock.sendall((json.dumps(msg) + '\n').encode())
            else:
                print("[系统] 请输入 'list' 查看在线用户，或 'connect <用户名>' 建立会话，'leave' 退出会话，'quit' 退出客户端")

if __name__ == "__main__":
    main() 