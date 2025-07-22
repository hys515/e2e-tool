import socket
import threading
import errno
import os
import json
from gmssl import sm2, func
import gmalg

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 50000

def ensure_sm2_keypair(username):
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

def get_session_key_path(me, peer):
    base_dir = os.path.join(os.path.dirname(__file__), '..', 'session_keys')
    os.makedirs(base_dir, exist_ok=True)
    users = sorted([me, peer])
    return os.path.join(base_dir, f"{users[0]}_{users[1]}_session.key")

def save_session_key(me, peer, session_key):
    path = get_session_key_path(me, peer)
    try:
        with open(path, 'w') as f:
            f.write(session_key)
        print(f"[系统] 会话密钥已保存到 {path}")
        print(f"[系统] 会话密钥内容: {session_key}")
    except Exception as e:
        print(f"[错误] 保存会话密钥失败: {e}")

def load_session_key(me, peer):
    path = get_session_key_path(me, peer)
    if os.path.exists(path):
        with open(path, 'r') as f:
            session_key = f.read()
        print(f"[系统] 已加载会话密钥: {path}")
        print(f"[系统] 会话密钥内容: {session_key}")
        return session_key
    return None

def zuc_keystream(zuc, length):
    stream = b''
    while len(stream) < length:
        stream += zuc.generate()
    return stream[:length]

def encrypt_message(session_key, plaintext):
    key = bytes.fromhex(session_key[:32])  # 16字节
    iv = os.urandom(16)
    zuc = gmalg.ZUC(key, iv)
    pt_bytes = plaintext.encode()
    keystream = zuc_keystream(zuc, len(pt_bytes))
    ciphertext = bytes([a ^ b for a, b in zip(pt_bytes, keystream)])
    return iv.hex() + ':' + ciphertext.hex()

def decrypt_message(session_key, msg):
    key = bytes.fromhex(session_key[:32])  # 16字节
    iv_hex, ct_hex = msg.split(':', 1)
    iv = bytes.fromhex(iv_hex)
    ciphertext = bytes.fromhex(ct_hex)
    zuc = gmalg.ZUC(key, iv)
    keystream = zuc_keystream(zuc, len(ciphertext))
    plaintext = bytes([a ^ b for a, b in zip(ciphertext, keystream)])
    return plaintext.decode()

def recv_thread(sock, username, state):
    buffer = ""
    while True:
        try:
            data = sock.recv(4096)
            if not data:
                print("[系统] 服务器断开连接")
                break
            buffer += data.decode()
            while '\n' in buffer:
                line, buffer = buffer.split('\n', 1)
                msg = line.strip()
                if msg.startswith("[KEYEXCHANGE]"):
                    _, peer, peer_pub = msg.split(":", 2)
                    priv, pub = ensure_sm2_keypair(username)
                    sm2_crypt = sm2.CryptSM2(public_key=peer_pub, private_key=priv)
                    session_key = sm2_crypt._kg(int(priv, 16), peer_pub)[:32]
                    save_session_key(username, peer, session_key)
                    print(f"[系统] 与 {peer} 的密钥交换完成，可以安全通信。")
                    state['session_peer'] = peer
                elif msg.startswith("[PEER_PUBKEY]"):
                    _, peer = msg.split(":", 1)
                    priv, pub = ensure_sm2_keypair(username)
                    sock.sendall(f"[PUBKEY]{username}:{pub}\n".encode())
                elif msg.startswith("[SESSION_READY]"):
                    _, peer = msg.split(":", 1)
                    print(f"[系统] 已与 {peer} 建立会话，可以开始通信。")
                    state['session_peer'] = peer
                elif msg.startswith("[INFO]"):
                    print(msg[6:])
                elif msg.startswith("[系统]"):
                    print(msg)
                elif msg:
                    print(msg)
                elif msg.startswith("{") and msg.endswith("}"):
                    try:
                        msg_obj = json.loads(msg)
                        if msg_obj.get('type') == 'msg':
                            peer = msg_obj['from']
                            session_key = load_session_key(username, peer)
                            try:
                                plaintext = decrypt_message(session_key, msg_obj['content'])
                                print(f"[{peer}] {plaintext}")
                            except Exception as e:
                                print(f"[系统] 解密失败: {e}")
                    except Exception:
                        print(f"[系统] 无法解析JSON消息: {msg}")
        except OSError as e:
            if e.errno == errno.EBADF:
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
            msg = input()
            if msg in ("quit", "exit"):
                print("[系统] 退出客户端")
                sock.close()
                break
            if state['session_peer']:
                session_key = load_session_key(username, state['session_peer'])
                encrypted = encrypt_message(session_key, msg)
                msg_obj = {
                    "type": "msg",
                    "to": state['session_peer'],
                    "from": username,
                    "content": encrypted
                }
                sock.sendall((json.dumps(msg_obj) + '\n').encode())

if __name__ == "__main__":
    main()