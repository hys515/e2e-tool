#!/usr/bin/env python3
"""
E2E工具功能测试脚本
"""

import asyncio
import websockets
import json
import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

async def test_websocket_features():
    """测试WebSocket功能"""
    uri = "ws://localhost:8765"
    print("🧪 开始测试WebSocket功能")
    print("=" * 50)
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ 连接成功")
            
            # 测试登录
            login_msg = {"type": "login", "username": "test_user"}
            await websocket.send(json.dumps(login_msg))
            print(f"📤 发送登录消息: {login_msg}")
            
            # 等待响应
            response = await websocket.recv()
            data = json.loads(response)
            print(f"📥 收到响应: {data}")
            
            if data.get('type') == 'session_ready':
                print("✅ 会话建立成功")
                
                # 测试发送消息
                msg = {"type": "msg", "from": "test_user", "to": "peer", "content": "Hello, E2E!"}
                await websocket.send(json.dumps(msg))
                print(f"📤 发送消息: {msg}")
                
            elif data.get('type') == 'error':
                print(f"❌ 登录失败: {data.get('message')}")
                
    except Exception as e:
        print(f"❌ 测试失败: {e}")

async def test_steganography():
    """测试隐写功能"""
    print("\n🧪 开始测试隐写功能")
    print("=" * 50)
    
    try:
        # 测试图片隐写
        from hide.steg import embed_message, extract_message
        
        # 创建测试图片
        test_image_path = "test/test_image.png"
        if not os.path.exists(test_image_path):
            print(f"⚠️  测试图片不存在: {test_image_path}")
            return
            
        # 测试嵌入消息
        message = "这是一条测试隐写消息"
        output_path = "test/output_steg.png"
        
        print(f"📝 测试消息: {message}")
        print(f"🖼️  载体图片: {test_image_path}")
        print(f"💾 输出文件: {output_path}")
        
        embed_message(test_image_path, message, output_path, "image")
        print("✅ 消息嵌入成功")
        
        # 测试提取消息
        extracted = extract_message(output_path, "image")
        print(f"📖 提取的消息: {extracted}")
        
        if extracted == message:
            print("✅ 隐写功能测试通过")
        else:
            print("❌ 隐写功能测试失败")
            
    except ImportError as e:
        print(f"❌ 导入隐写模块失败: {e}")
    except Exception as e:
        print(f"❌ 隐写测试失败: {e}")

async def test_encryption():
    """测试加密功能"""
    print("\n🧪 开始测试加密功能")
    print("=" * 50)
    
    try:
        from gmssl import sm2, func
        import gmalg
        
        # 生成密钥对
        private_key = '00B9AB0B828FF68872F21A837FC303668428DEA11DCD1B24429D0C99E24EED83D5'
        public_key = 'B9C9A6E04E9C91F7BA880429273747D7EF5DDEB0BB2FF6317EB00BEF331A83081A6994B8993F3F5D6EADDDB81872266C87C018FB4162F5AF347B483E24620207'
        
        sm2_crypt = sm2.CryptSM2(
            public_key=public_key, private_key=private_key
        )
        
        # 测试加密
        message = "Hello, SM2!"
        encrypted = sm2_crypt.encrypt(message.encode())
        print(f"🔐 加密成功: {len(encrypted)} bytes")
        
        # 测试解密
        decrypted = sm2_crypt.decrypt(encrypted)
        decrypted_text = decrypted.decode()
        print(f"🔓 解密成功: {decrypted_text}")
        
        if decrypted_text == message:
            print("✅ 加密功能测试通过")
        else:
            print("❌ 加密功能测试失败")
            
    except ImportError as e:
        print(f"❌ 导入加密模块失败: {e}")
    except Exception as e:
        print(f"❌ 加密测试失败: {e}")

def test_file_operations():
    """测试文件操作"""
    print("\n🧪 开始测试文件操作")
    print("=" * 50)
    
    # 测试目录结构
    directories = [
        "session_keys",
        "keys", 
        "received_files",
        "test/data",
        "hide/output"
    ]
    
    for directory in directories:
        if os.path.exists(directory):
            print(f"✅ 目录存在: {directory}")
        else:
            print(f"❌ 目录不存在: {directory}")
            try:
                os.makedirs(directory, exist_ok=True)
                print(f"📁 创建目录: {directory}")
            except Exception as e:
                print(f"❌ 创建目录失败: {e}")

async def main():
    """主测试函数"""
    print("🚀 E2E工具功能测试")
    print("=" * 60)
    
    # 测试文件操作
    test_file_operations()
    
    # 测试加密功能
    await test_encryption()
    
    # 测试隐写功能
    await test_steganography()
    
    # 测试WebSocket功能
    await test_websocket_features()
    
    print("\n🎉 测试完成")

if __name__ == "__main__":
    asyncio.run(main()) 