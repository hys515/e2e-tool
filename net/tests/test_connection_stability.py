#!/usr/bin/env python3
"""
连接稳定性测试脚本
测试大文件传输和心跳机制
"""

import asyncio
import os
import sys
import time

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from net.websocket_client import WebSocketClient

async def test_connection_stability():
    """测试连接稳定性"""
    print("🧪 开始连接稳定性测试")
    
    # 创建客户端
    client = WebSocketClient()
    
    try:
        # 连接到服务器
        await client.connect()
        print("✅ 连接成功")
        
        # 等待会话建立
        print("⏳ 等待会话建立...")
        await asyncio.sleep(2)
        
        if not client.session_peer:
            print("❌ 会话未建立，无法进行测试")
            return
        
        print(f"✅ 会话已建立，对方: {client.session_peer}")
        
        # 测试心跳机制
        print("\n💓 测试心跳机制...")
        for i in range(5):
            await client.send_heartbeat()
            await asyncio.sleep(1)
        print("✅ 心跳测试完成")
        
        # 测试大文件传输（模拟）
        print("\n📁 测试大文件传输稳定性...")
        
        # 创建一个测试文件
        test_file = "test_large_file.bin"
        file_size = 2 * 1024 * 1024  # 2MB
        
        print(f"📝 创建测试文件: {test_file} ({file_size} bytes)")
        with open(test_file, 'wb') as f:
            # 写入一些测试数据
            for i in range(file_size // 1024):
                f.write(f"chunk_{i:06d}".encode().ljust(1024, b'0'))
        
        try:
            # 发送文件
            print("📤 开始发送文件...")
            start_time = time.time()
            
            await client.send_file(test_file, "binary")
            
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"✅ 文件发送完成，耗时: {duration:.2f} 秒")
            print(f"📊 传输速率: {file_size / duration / 1024 / 1024:.2f} MB/s")
            
        except Exception as e:
            print(f"❌ 文件传输失败: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            # 清理测试文件
            if os.path.exists(test_file):
                os.remove(test_file)
                print(f"🧹 清理测试文件: {test_file}")
        
        print("\n✅ 连接稳定性测试完成")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 关闭连接
        if client.websocket and not client.websocket.closed:
            await client.websocket.close()
            print("🔌 连接已关闭")

async def test_video_stego_stability():
    """测试视频隐写稳定性"""
    print("\n🎭 开始视频隐写稳定性测试")
    
    # 创建客户端
    client = WebSocketClient()
    
    try:
        # 连接到服务器
        await client.connect()
        print("✅ 连接成功")
        
        # 等待会话建立
        print("⏳ 等待会话建立...")
        await asyncio.sleep(2)
        
        if not client.session_peer:
            print("❌ 会话未建立，无法进行测试")
            return
        
        print(f"✅ 会话已建立，对方: {client.session_peer}")
        
        # 测试视频隐写
        print("\n📹 测试视频隐写...")
        
        # 检查测试视频文件
        test_video = "hide/resources/videos/input.mp4"
        if not os.path.exists(test_video):
            print(f"❌ 测试视频文件不存在: {test_video}")
            return
        
        # 准备测试消息
        test_message = "这是一个测试消息，用于验证视频隐写的稳定性。" * 10
        
        try:
            # 发送隐写消息
            print("📤 开始发送隐写消息...")
            start_time = time.time()
            
            await client.send_stego_message(
                carrier_type="video",
                input_path=test_video,
                output_path="test_stability_output.mp4",
                plaintext=test_message
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"✅ 隐写消息发送完成，耗时: {duration:.2f} 秒")
            
        except Exception as e:
            print(f"❌ 隐写消息发送失败: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n✅ 视频隐写稳定性测试完成")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 关闭连接
        if client.websocket and not client.websocket.closed:
            await client.websocket.close()
            print("🔌 连接已关闭")

async def main():
    """主函数"""
    print("🚀 开始连接稳定性测试套件")
    print("=" * 60)
    
    # 测试1: 连接稳定性
    await test_connection_stability()
    
    # 等待一下
    await asyncio.sleep(2)
    
    # 测试2: 视频隐写稳定性
    await test_video_stego_stability()
    
    print("\n" + "=" * 60)
    print("🎉 所有测试完成")

if __name__ == "__main__":
    asyncio.run(main()) 