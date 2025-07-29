#!/usr/bin/env python3
"""
测试从received_files中提取隐写消息
"""

import os
import sys

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from hide.steg import extract_message

def test_extract_received():
    """测试提取接收到的隐写文件"""
    print("🔍 测试提取接收到的隐写文件")
    print("=" * 50)
    
    # 检查received_files目录
    received_dir = os.path.join(project_root, "received_files")
    if not os.path.exists(received_dir):
        print("❌ received_files目录不存在")
        return
    
    # 列出所有文件
    files = os.listdir(received_dir)
    print(f"📁 received_files目录中的文件: {files}")
    
    # 尝试提取每个文件
    for filename in files:
        if filename.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
            filepath = os.path.join(received_dir, filename)
            print(f"\n🖼️  尝试提取图片文件: {filename}")
            
            try:
                extracted_data = extract_message("image", filepath)
                print(f"✅ 提取成功！数据大小: {len(extracted_data)} bytes")
                print(f"📄 提取的数据: {extracted_data}")
                
                # 尝试解码
                try:
                    decoded = extracted_data.decode('utf-8')
                    print(f"📝 解码后的文本: {decoded}")
                except UnicodeDecodeError:
                    print("⚠️  数据不是UTF-8编码的文本")
                    
            except Exception as e:
                print(f"❌ 提取失败: {e}")
                
        elif filename.endswith('.pdf'):
            filepath = os.path.join(received_dir, filename)
            print(f"\n📄 尝试提取PDF文件: {filename}")
            
            try:
                extracted_data = extract_message("pdf", filepath)
                print(f"✅ 提取成功！数据大小: {len(extracted_data)} bytes")
                print(f"📄 提取的数据: {extracted_data}")
                
                # 尝试解码
                try:
                    decoded = extracted_data.decode('utf-8')
                    print(f"📝 解码后的文本: {decoded}")
                except UnicodeDecodeError:
                    print("⚠️  数据不是UTF-8编码的文本")
                    
            except Exception as e:
                print(f"❌ 提取失败: {e}")
                
        elif filename.endswith(('.mp4', '.avi', '.mov', '.mkv')):
            filepath = os.path.join(received_dir, filename)
            print(f"\n🎥 尝试提取视频文件: {filename}")
            
            try:
                extracted_data = extract_message("video", filepath)
                print(f"✅ 提取成功！数据大小: {len(extracted_data)} bytes")
                print(f"📄 提取的数据: {extracted_data}")
                
                # 尝试解码
                try:
                    decoded = extracted_data.decode('utf-8')
                    print(f"📝 解码后的文本: {decoded}")
                except UnicodeDecodeError:
                    print("⚠️  数据不是UTF-8编码的文本")
                    
            except Exception as e:
                print(f"❌ 提取失败: {e}")

if __name__ == "__main__":
    test_extract_received() 