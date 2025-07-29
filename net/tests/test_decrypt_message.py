#!/usr/bin/env python3
"""
测试解密接收到的隐写消息
"""

import os
import sys

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from hide.steg import extract_message
from net.websocket_client import WebSocketClient

def test_decrypt_message():
    """测试解密隐写消息"""
    print("🔐 测试解密隐写消息")
    print("=" * 50)
    
    # 创建客户端实例来使用解密功能
    client = WebSocketClient()
    
    # 提取隐写数据
    stego_file = os.path.join(project_root, "received_files", "takianon.png")
    if not os.path.exists(stego_file):
        print("❌ 隐写文件不存在")
        return
    
    try:
        print(f"📁 从文件提取隐写数据: {stego_file}")
        extracted_data = extract_message("image", stego_file)
        print(f"✅ 提取成功！数据大小: {len(extracted_data)} bytes")
        print(f"📄 提取的数据: {extracted_data}")
        
        # 尝试解码为字符串
        try:
            ciphertext = extracted_data.decode('utf-8')
            print(f"📝 密文: {ciphertext}")
        except UnicodeDecodeError:
            print("❌ 无法解码为UTF-8")
            return
        
        # 尝试解密（需要会话密钥）
        print("\n🔑 尝试解密...")
        
        # 检查会话密钥文件
        session_key_path = os.path.join(project_root, "session_keys", "taki_anon_session.key")
        if os.path.exists(session_key_path):
            print(f"✅ 找到会话密钥文件: {session_key_path}")
            
            # 加载会话密钥
            session_key = client.load_session_key("taki", "anon")
            if session_key:
                print("✅ 会话密钥加载成功")
                
                # 尝试解密
                try:
                    plaintext = client.decrypt_message(session_key, ciphertext)
                    print(f"🎉 解密成功！")
                    print(f"📝 明文消息: {plaintext}")
                except Exception as e:
                    print(f"❌ 解密失败: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print("❌ 会话密钥加载失败")
        else:
            print(f"❌ 会话密钥文件不存在: {session_key_path}")
            
            # 列出所有会话密钥文件
            session_keys_dir = os.path.join(project_root, "session_keys")
            if os.path.exists(session_keys_dir):
                keys = os.listdir(session_keys_dir)
                print(f"📁 现有的会话密钥文件: {keys}")
                
                # 尝试使用anon_taki的密钥
                alt_key_path = os.path.join(session_keys_dir, "anon_taki_session.key")
                if os.path.exists(alt_key_path):
                    print(f"🔄 尝试使用反向密钥: {alt_key_path}")
                    session_key = client.load_session_key("anon", "taki")
                    if session_key:
                        print("✅ 反向会话密钥加载成功")
                        try:
                            plaintext = client.decrypt_message(session_key, ciphertext)
                            print(f"🎉 解密成功！")
                            print(f"📝 明文消息: {plaintext}")
                        except Exception as e:
                            print(f"❌ 解密失败: {e}")
                            import traceback
                            traceback.print_exc()
                    else:
                        print("❌ 反向会话密钥加载失败")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_decrypt_message() 