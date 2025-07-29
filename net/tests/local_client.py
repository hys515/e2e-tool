#!/usr/bin/env python3
"""
本地WebSocket客户端 - 避免代理问题
"""

import os
import sys

# 临时取消代理设置
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 导入并运行客户端
from net.websocket_client import WebSocketClient

if __name__ == "__main__":
    print("🔐 E2E-Tool 本地客户端")
    print("=" * 30)
    print("已禁用代理设置，使用本地连接")
    print()
    
    client = WebSocketClient("ws://localhost:8765")
    client.run()