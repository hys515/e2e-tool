#!/usr/bin/env python3
"""
测试video隐写修复
"""

import os
import sys

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from hide.steg import embed_message, extract_message

def test_video_stego():
    """测试video隐写功能"""
    print("🎥 测试video隐写修复")
    print("=" * 50)
    
    # 检查输入视频是否存在
    input_video = os.path.join(project_root, "hide", "resources", "videos", "input.mp4")
    if not os.path.exists(input_video):
        print(f"❌ 输入视频不存在: {input_video}")
        return
    
    output_video = os.path.join(project_root, "hide", "output", "test_video_fix.mp4")
    test_message = b"Hello, this is a test video stego message!"
    
    try:
        print(f"📁 输入视频: {input_video}")
        print(f"📁 输出视频: {output_video}")
        print(f"📝 测试消息: {test_message}")
        
        # 测试嵌入
        print("\n🔧 测试嵌入...")
        try:
            embed_message("video", input_video, output_video, test_message)
            print("✅ 嵌入成功")
        except Exception as e:
            print(f"❌ 嵌入失败: {e}")
            return
        
        # 检查输出文件是否存在
        if not os.path.exists(output_video):
            print("❌ 输出文件未生成")
            return
        
        print(f"✅ 输出文件已生成: {output_video}")
        
        # 测试提取
        print("\n🔍 测试提取...")
        try:
            extracted = extract_message("video", output_video)
            print(f"✅ 提取成功: {extracted}")
            
            if extracted == test_message:
                print("🎉 测试完全成功！")
            else:
                print("❌ 提取的数据与原始数据不匹配")
                
        except Exception as e:
            print(f"❌ 提取失败: {e}")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_video_stego() 