#!/usr/bin/env python3
"""
测试实际客户端代码
"""

import asyncio
import os
import sys
import time

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from net.websocket_client import WebSocketClient

async def test_real_client():
    """测试实际客户端"""
    print("🚀 测试实际客户端代码")
    print("=" * 50)
    
    # 创建客户端
    client = WebSocketClient()
    client.username = "test_user"  # 设置用户名
    
    try:
        # 启动客户端
        print("🔗 启动客户端...")
        
        # 创建一个任务来运行客户端
        client_task = asyncio.create_task(client._run_async())
        
        # 等待连接建立
        print("⏳ 等待连接建立...")
        await asyncio.sleep(5)
        
        # 检查连接状态
        if hasattr(client, 'websocket') and client.websocket:
            print("✅ 客户端已连接")
            
            # 检查会话状态
            if client.session_peer:
                print(f"✅ 会话已建立，对端: {client.session_peer}")
                
                # 测试发送隐写消息
                print("\n📁 测试发送隐写消息...")
                
                # 确保测试文件存在
                test_image_path = os.path.join(project_root, "test", "test_image.png")
                if not os.path.exists(test_image_path):
                    print(f"❌ 测试图片不存在: {test_image_path}")
                    print("请先运行: python net/create_test_image.py")
                    return
                
                # 发送隐写消息
                await client.send_stego_message(
                    carrier_type="image",
                    input_path=test_image_path,
                    output_path=os.path.join(project_root, "hide", "output", "test_debug.png"),
                    plaintext="Hello, this is a test message from real client!"
                )
                
                print("✅ 隐写消息发送完成")
                
            else:
                print("❌ 会话未建立")
        else:
            print("❌ 客户端未连接")
        
        # 等待一段时间
        print("⏳ 等待处理完成...")
        await asyncio.sleep(5)
        
        # 取消客户端任务
        client_task.cancel()
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("🏁 测试完成")

async def main():
    """主函数"""
    await test_real_client()

if __name__ == "__main__":
    asyncio.run(main()) 