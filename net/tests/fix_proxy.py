 #!/usr/bin/env python3
"""
修复代理问题的脚本
"""

import os
import sys

def check_proxy_settings():
    """检查代理设置"""
    print("🔍 检查代理设置...")
    
    proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']
    found_proxies = []
    
    for var in proxy_vars:
        value = os.environ.get(var)
        if value:
            found_proxies.append((var, value))
            print(f"❌ 发现代理设置: {var} = {value}")
    
    if not found_proxies:
        print("✅ 未发现代理设置")
        return False
    
    return True

def fix_proxy_issue():
    """修复代理问题"""
    print("\n🔧 修复代理问题...")
    
    # 方法1: 临时取消代理设置
    print("\n方法1: 临时取消代理设置")
    print("运行以下命令：")
    print("unset HTTP_PROXY HTTPS_PROXY http_proxy https_proxy")
    print("python3 net/websocket_client.py")
    
    # 方法2: 安装python-socks
    print("\n方法2: 安装python-socks")
    print("运行以下命令：")
    print("pip install python-socks")
    print("python3 net/websocket_client.py")
    
    # 方法3: 使用本地连接
    print("\n方法3: 使用本地连接")
    print("确保服务器运行在本地：")
    print("python3 net/websocket_server.py")
    print("然后在另一个终端运行：")
    print("python3 net/local_client.py")

def create_local_client():
    """创建本地客户端脚本"""
    script_content = '''#!/usr/bin/env python3
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
'''
    
    with open('net/local_client.py', 'w') as f:
        f.write(script_content)
    
    print("\n✅ 已创建本地客户端脚本: net/local_client.py")
    print("使用方法: python3 net/local_client.py")

def main():
    """主函数"""
    print("🔧 WebSocket代理问题修复工具")
    print("=" * 40)
    
    # 检查代理设置
    has_proxy = check_proxy_settings()
    
    if has_proxy:
        print("\n⚠️  检测到代理设置，这可能导致连接问题")
        fix_proxy_issue()
        create_local_client()
    else:
        print("\n✅ 代理设置正常，可以直接运行客户端")
        print("python3 net/websocket_client.py")

if __name__ == "__main__":
    main()