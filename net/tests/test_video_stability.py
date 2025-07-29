#!/usr/bin/env python3
"""
视频隐写稳定性测试
测试连续发送视频隐写消息的稳定性
"""

import asyncio
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from net.websocket_client import WebSocketClient

async def test_video_stability():
    """测试视频隐写稳定性"""
    print("🎭 开始视频隐写稳定性测试")
    
    # 创建客户端
    client = WebSocketClient()
    client.username = "test_user"
    
    try:
        # 连接到服务器
        await client.connect()
        print("✅ 连接成功")
        
        # 等待会话建立
        print("⏳ 等待会话建立...")
        await asyncio.sleep(3)
        
        if not client.session_peer:
            print("❌ 会话未建立，无法进行测试")
            return
        
        print(f"✅ 会话已建立，对方: {client.session_peer}")
        
        # 检查测试视频文件
        test_video = "hide/resources/videos/input.mp4"
        if not os.path.exists(test_video):
            print(f"❌ 测试视频文件不存在: {test_video}")
            return
        
        # 测试多次发送
        for i in range(3):
            print(f"\n📹 测试第 {i+1} 次视频隐写...")
            
            # 准备测试消息
            test_message = f"这是第 {i+1} 次测试消息，用于验证视频隐写的稳定性。"
            
            try:
                # 发送隐写消息
                await client.send_stego_message(
                    carrier_type="video",
                    input_path=test_video,
                    output_path=f"test_stability_{i+1}.mp4",
                    plaintext=test_message
                )
                
                print(f"✅ 第 {i+1} 次测试成功")
                
                # 等待一下再进行下一次测试
                await asyncio.sleep(2)
                
            except Exception as e:
                print(f"❌ 第 {i+1} 次测试失败: {e}")
                import traceback
                traceback.print_exc()
        
        print("\n🎉 视频隐写稳定性测试完成")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 关闭连接
        if client.websocket and not client.websocket.closed:
            await client.websocket.close()
            print("🔌 连接已关闭")

if __name__ == "__main__":
    asyncio.run(test_video_stability())