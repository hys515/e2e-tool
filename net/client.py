import socket
import threading
import json
import sys

SERVER_HOST = '127.0.0.1'  # 服务器地址
SERVER_PORT = 50000        # 服务器端口


def recv_thread(sock):
    while True:
        try:
            data = sock.recv(4096)
            if not data:
                print("[系统] 服务器断开连接")
                sys.exit(0)
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
            print(f"[错误] 接收消息异常: {e}")
            break

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((SERVER_HOST, SERVER_PORT))
        # 注册用户名
        prompt = sock.recv(1024).decode()
        username = input(prompt)
        sock.sendall((username + '\n').encode())
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

if __name__ == "__main__":
    main() 