import socket
import os
import json

def recv_file(sock, save_dir):
    fileinfo_line = b''
    while not fileinfo_line.endswith(b'\n'):
        fileinfo_line += sock.recv(1)
    fileinfo = json.loads(fileinfo_line.decode())
    filesize = fileinfo['filesize']
    filename = fileinfo['filename']
    save_path = os.path.join(save_dir, filename)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, 'wb') as f:
        remaining = filesize
        while remaining > 0:
            chunk = sock.recv(min(4096, remaining))
            if not chunk:
                break
            f.write(chunk)
            remaining -= len(chunk)
    print(f"[系统] 文件已接收并保存为 {save_path}")

def main():
    HOST = '0.0.0.0'
    PORT = 50001
    SAVE_DIR = 'received_files'
    os.makedirs(SAVE_DIR, exist_ok=True)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(1)
        print(f"[Server] 等待连接 {HOST}:{PORT} ...")
        conn, addr = s.accept()
        print(f"[Server] 已连接: {addr}")
        recv_file(conn, SAVE_DIR)
        print("[Server] 传输完成，关闭连接。")

if __name__ == "__main__":
    main()