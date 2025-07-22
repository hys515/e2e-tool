import socket
import threading
import json

HOST = '0.0.0.0'
PORT = 50000

clients = {}  # username -> (conn, addr)
lock = threading.Lock()

def broadcast_user_list():
    with lock:
        user_list = list(clients.keys())
        msg = json.dumps({"type": "user_list", "users": user_list})
        for conn, _ in clients.values():
            try:
                conn.sendall(msg.encode() + b'\n')
            except:
                pass

def handle_client(conn, addr):
    username = None
    try:
        conn.sendall('请输入用户名: '.encode('utf-8'))
        username = conn.recv(1024).decode().strip()
        if not username:
            conn.close()
            return
        with lock:
            if username in clients:
                conn.sendall('用户名已存在，连接断开\n'.encode('utf-8'))
                conn.close()
                return
            clients[username] = (conn, addr)
        print(f"[+] 用户上线: {username} @ {addr}")
        broadcast_user_list()
        welcome_msg = '欢迎，当前在线用户: ' + ', '.join(clients.keys()) + '\n'
        conn.sendall(welcome_msg.encode('utf-8'))
        while True:
            data = conn.recv(4096)
            if not data:
                break
            for line in data.split(b'\n'):
                if not line.strip():
                    continue
                try:
                    msg = json.loads(line.decode())
                    if msg.get('type') == 'list':
                        # 只回复请求者
                        user_list = list(clients.keys())
                        conn.sendall(json.dumps({"type": "user_list", "users": user_list}).encode() + b'\n')
                    elif msg.get('type') == 'key_exchange_request':
                        to_user = msg.get('to')
                        from_user = msg.get('from')
                        pubkey = msg.get('pubkey')
                        with lock:
                            if to_user in clients:
                                to_conn, _ = clients[to_user]
                                # 通知对方有密钥交换请求
                                to_conn.sendall(json.dumps({
                                    "type": "key_exchange_request",
                                    "from": from_user,
                                    "pubkey": pubkey
                                }).encode() + b'\n')
                            else:
                                conn.sendall('目标用户不在线\n'.encode('utf-8'))
                    elif msg.get('type') == 'key_exchange_response':
                        to_user = msg.get('to')
                        from_user = username
                        pubkey = msg.get('pubkey')
                        with lock:
                            if to_user in clients:
                                to_conn, _ = clients[to_user]
                                # 通知发起方密钥交换完成
                                to_conn.sendall(json.dumps({
                                    "type": "key_exchange_response",
                                    "from": from_user,
                                    "pubkey": pubkey
                                }).encode() + b'\n')
                                # 也通知被邀请方
                                conn.sendall(json.dumps({
                                    "type": "key_exchange_done",
                                    "from": to_user,
                                    "pubkey": pubkey
                                }).encode() + b'\n')
                            else:
                                conn.sendall('目标用户不在线\n'.encode('utf-8'))
                    elif msg.get('type') == 'msg':
                        to_user = msg.get('to')
                        content = msg.get('content')
                        with lock:
                            if to_user in clients:
                                to_conn, _ = clients[to_user]
                                to_conn.sendall(json.dumps({
                                    'type': 'msg',
                                    'from': username,
                                    'content': content
                                }).encode() + b'\n')
                            else:
                                conn.sendall('目标用户不在线\n'.encode('utf-8'))
                    else:
                        conn.sendall('未知消息类型\n'.encode('utf-8'))
                except Exception as e:
                    conn.sendall(f'消息解析错误: {e}\n'.encode('utf-8'))
    except Exception as e:
        print(f"[-] 用户 {username} 异常: {e}")
    finally:
        with lock:
            if username and username in clients:
                del clients[username]
        print(f"[-] 用户下线: {username}")
        broadcast_user_list()
        conn.close()

def main():
    print(f"[Server] 启动，监听 {HOST}:{PORT}")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        try:
            while True:
                conn, addr = s.accept()
                threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
        except KeyboardInterrupt:
            print("\n[Server] 收到退出信号，正在关闭...")
        finally:
            s.close()
            print("[Server] 已关闭 socket，退出。")

if __name__ == "__main__":
    main()