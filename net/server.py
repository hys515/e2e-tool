import socket
import threading

HOST = '0.0.0.0'
PORT = 50000

clients = {}  # username -> (conn, addr)
pubkeys = {}  # username -> pubkey
lock = threading.Lock()

def handle_client(conn, addr):
    username = None
    try:
        print(f"[调试] 新连接: {addr}")
        conn.sendall('请输入用户名: '.encode('utf-8'))
        username = conn.recv(1024).decode().strip()
        print(f"[调试] 用户 {username} 尝试上线")
        if not username:
            conn.close()
            return
        with lock:
            if username in clients:
                print(f"[调试] 用户名已存在: {username}")
                conn.sendall('用户名已存在，连接断开\n'.encode('utf-8'))
                conn.close()
                return
            if len(clients) >= 2:
                print(f"[调试] 已有两人在线，拒绝 {username}")
                conn.sendall('只允许两人在线，连接断开\n'.encode('utf-8'))
                conn.close()
                return
            clients[username] = (conn, addr)
        print(f"[调试] 用户 {username} 已上线: {addr}")
        # 通知双方会话已建立
        with lock:
            if len(clients) == 2:
                users = list(clients.keys())
                for user in users:
                    c, _ = clients[user]
                    peer = users[1] if user == users[0] else users[0]
                    print(f"[调试] 通知 {user} 会话已建立，对方为 {peer}")
                    c.sendall(f"[SESSION_READY]:{peer}\n".encode())
                # 主动向双方索要公钥
                for user in users:
                    c, _ = clients[user]
                    peer = users[1] if user == users[0] else users[0]
                    print(f"[调试] 向 {user} 索要公钥，对方为 {peer}")
                    c.sendall(f"[PEER_PUBKEY]:{peer}\n".encode())
        # 主消息循环
        while True:
            data = conn.recv(4096)
            if not data:
                break
            msg = data.decode().strip()
            if msg.startswith("[PUBKEY]"):
                # [PUBKEY]username:pubkey
                _, rest = msg.split("]", 1)
                user, pub = rest.split(":", 1)
                print(f"[调试] 收到 {user} 的公钥上报: {pub[:6]}...")
                with lock:
                    pubkeys[user] = pub
                    print(f"[调试] 当前已上报公钥用户: {[u[:6] for u in pubkeys.keys()]}")
                    # 如果两人都已上报公钥，通知双方进行密钥交换
                    if len(pubkeys) == 2:
                        users = list(pubkeys.keys())
                        for u in users:
                            c, _ = clients[u]
                            peer = users[1] if u == users[0] else users[0]
                            peer_pub = pubkeys[peer]
                            print(f"[调试] 向 {u} 发送 [KEYEXCHANGE]，peer={peer[:6]}, peer_pub={peer_pub[:6]}...")
                            c.sendall(f"[KEYEXCHANGE]:{peer}:{peer_pub}\n".encode())
            else:
                # 普通消息转发
                with lock:
                    for user, (c, _) in clients.items():
                        if user != username:
                            print(f"[调试] 转发消息 [{username[:6]}] -> [{user[:6]}]: {msg}")
                            c.sendall(f"[{username}] {msg}\n".encode())
    except Exception as e:
        print(f"[调试] 用户 {username} 异常: {e}")
    finally:
        with lock:
            if username and username in clients:
                del clients[username]
            if username and username in pubkeys:
                del pubkeys[username]
            # 通知对方下线
            for user, (c, _) in clients.items():
                print(f"[调试] 通知 {user}，{username} 已下线")
                c.sendall(f"[系统] {username} 已下线，会话结束。\n".encode('utf-8'))
        print(f"[调试] 用户 {username} 下线")
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
            print("\n[Server] 收到退出信号，正在优雅关闭...")
        finally:
            s.close()
            print("[Server] 已关闭 socket，退出。")

if __name__ == "__main__":
    main()