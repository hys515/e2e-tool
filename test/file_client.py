import socket
import os
import json

def send_file(sock, filepath):
    filesize = os.path.getsize(filepath)
    filename = os.path.basename(filepath)
    fileinfo = {
        "type": "file",
        "filename": filename,
        "filetype": "test",  # 可自定义
        "filesize": filesize,
        "from": "test_client",
        "to": "test_server"
    }
    sock.sendall((json.dumps(fileinfo) + '\n').encode())
    with open(filepath, 'rb') as f:
        while True:
            chunk = f.read(4096)
            if not chunk:
                break
            sock.sendall(chunk)
    print(f"[系统] 文件已发送: {filename}")

def main():
    SERVER_HOST = '127.0.0.1'
    SERVER_PORT = 50001
    filepath = input("请输入要发送的文件路径: ").strip()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((SERVER_HOST, SERVER_PORT))
        send_file(sock, filepath)
        print("[Client] 传输完成，关闭连接。")

if __name__ == "__main__":
    main()