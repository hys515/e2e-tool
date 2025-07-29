#!/usr/bin/env python3
"""
测试隐写功能
"""

import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def test_image_steganography():
    """测试图片隐写"""
    print("🧪 测试图片隐写功能")
    print("=" * 40)
    
    try:
        from hide.steg import embed_message, extract_message
        
        # 测试图片路径
        test_image_path = "test/test_image.png"
        output_path = "test/output_steg.png"
        
        if not os.path.exists(test_image_path):
            print(f"❌ 测试图片不存在: {test_image_path}")
            return False
            
        # 测试消息
        message = "这是一条测试隐写消息 - E2E Tool Test"
        print(f"📝 原始消息: {message}")
        print(f"🖼️  载体图片: {test_image_path}")
        
        # 嵌入消息
        embed_message("image", test_image_path, output_path, message.encode())
        print("✅ 消息嵌入成功")
        
        # 提取消息
        extracted = extract_message("image", output_path)
        print(f"📖 提取的消息: {extracted}")
        
        # 验证结果
        if extracted.decode() == message:
            print("✅ 图片隐写测试通过")
            return True
        else:
            print("❌ 图片隐写测试失败")
            print(f"期望: {message}")
            print(f"实际: {extracted.decode()}")
            return False
            
    except ImportError as e:
        print(f"❌ 导入隐写模块失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 图片隐写测试失败: {e}")
        return False

def test_pdf_steganography():
    """测试PDF隐写"""
    print("\n🧪 测试PDF隐写功能")
    print("=" * 40)
    
    try:
        from hide.steg import embed_message, extract_message
        
        # 创建测试PDF
        test_pdf_path = "test/test_document.pdf"
        output_path = "test/output_steg.pdf"
        
        # 简单的PDF创建（如果不存在）
        if not os.path.exists(test_pdf_path):
            print(f"⚠️  测试PDF不存在: {test_pdf_path}")
            print("跳过PDF隐写测试")
            return True
            
        # 测试消息
        message = "PDF隐写测试消息"
        print(f"📝 原始消息: {message}")
        print(f"📄 载体PDF: {test_pdf_path}")
        
        # 嵌入消息
        embed_message("pdf", test_pdf_path, output_path, message.encode())
        print("✅ PDF消息嵌入成功")
        
        # 提取消息
        extracted = extract_message("pdf", output_path)
        print(f"📖 提取的消息: {extracted}")
        
        # 验证结果
        if extracted.decode() == message:
            print("✅ PDF隐写测试通过")
            return True
        else:
            print("❌ PDF隐写测试失败")
            return False
            
    except ImportError as e:
        print(f"❌ 导入隐写模块失败: {e}")
        return False
    except Exception as e:
        print(f"❌ PDF隐写测试失败: {e}")
        return False

def test_video_steganography():
    """测试视频隐写"""
    print("\n🧪 测试视频隐写功能")
    print("=" * 40)
    
    try:
        from hide.steg import embed_message, extract_message
        
        # 测试视频路径
        test_video_path = "test/test_video.mp4"
        output_path = "test/output_steg.mp4"
        
        if not os.path.exists(test_video_path):
            print(f"⚠️  测试视频不存在: {test_video_path}")
            print("跳过视频隐写测试")
            return True
            
        # 测试消息
        message = "视频隐写测试消息"
        print(f"📝 原始消息: {message}")
        print(f"🎥 载体视频: {test_video_path}")
        
        # 嵌入消息
        embed_message("video", test_video_path, output_path, message.encode())
        print("✅ 视频消息嵌入成功")
        
        # 提取消息
        extracted = extract_message("video", output_path)
        print(f"📖 提取的消息: {extracted}")
        
        # 验证结果
        if extracted.decode() == message:
            print("✅ 视频隐写测试通过")
            return True
        else:
            print("❌ 视频隐写测试失败")
            return False
            
    except ImportError as e:
        print(f"❌ 导入隐写模块失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 视频隐写测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 隐写功能测试")
    print("=" * 60)
    
    results = []
    
    # 测试图片隐写
    results.append(test_image_steganography())
    
    # 测试PDF隐写
    results.append(test_pdf_steganography())
    
    # 测试视频隐写
    results.append(test_video_steganography())
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 测试结果总结:")
    passed = sum(results)
    total = len(results)
    print(f"✅ 通过: {passed}/{total}")
    print(f"❌ 失败: {total - passed}/{total}")
    
    if passed == total:
        print("🎉 所有隐写功能测试通过！")
    else:
        print("⚠️  部分功能需要进一步测试")

if __name__ == "__main__":
    main() 