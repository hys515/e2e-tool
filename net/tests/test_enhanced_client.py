#!/usr/bin/env python3
"""
测试增强的客户端功能
"""

import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def test_path_resolution():
    """测试路径解析功能"""
    print("🧪 测试路径解析功能")
    print("=" * 50)
    
    from net.websocket_client import WebSocketClient
    
    client = WebSocketClient()
    
    # 测试输入路径解析
    print("\n📁 测试输入路径解析:")
    test_inputs = [
        "test_image.png",  # 只有文件名
        "test/test_image.png",  # 相对路径
        "/Users/umiri/Projects/e2e_tool/test/test_image.png",  # 绝对路径
        "nonexistent.png",  # 不存在的文件
        ""  # 空输入
    ]
    
    for test_input in test_inputs:
        result = client.resolve_input_path(test_input)
        print(f"  输入: '{test_input}' -> 结果: {result}")
    
    # 测试输出路径解析
    print("\n📁 测试输出路径解析:")
    test_outputs = [
        ("", "image"),  # 空输入，生成默认名称
        ("my_output.png", "image"),  # 只有文件名
        ("/tmp/output.png", "image"),  # 完整路径
    ]
    
    for test_output, carrier_type in test_outputs:
        result = client.resolve_output_path(test_output, carrier_type)
        print(f"  输入: '{test_output}' (类型: {carrier_type}) -> 结果: {result}")
    
    # 测试文件列表功能
    print("\n📁 测试文件列表功能:")
    print("输入目录文件:")
    input_files = client.get_available_files(client.input_dir)
    for file in input_files:
        print(f"  - {file}")
    
    print("\n按类型分类:")
    extensions = {
        'image': ['.png', '.jpg', '.jpeg', '.bmp', '.tiff'],
        'pdf': ['.pdf'],
        'video': ['.mp4', '.avi', '.mov', '.mkv']
    }
    
    for file_type, exts in extensions.items():
        files = client.get_available_files(client.input_dir, exts)
        if files:
            print(f"  {file_type}: {', '.join(files)}")

def create_test_files():
    """创建测试文件"""
    print("\n📁 创建测试文件")
    print("=" * 30)
    
    test_dir = os.path.join(project_root, "test")
    os.makedirs(test_dir, exist_ok=True)
    
    # 创建测试图片
    test_image = os.path.join(test_dir, "test_image.png")
    if not os.path.exists(test_image):
        from PIL import Image, ImageDraw
        img = Image.new('RGB', (100, 100), color='white')
        draw = ImageDraw.Draw(img)
        draw.text((10, 10), "Test", fill='black')
        img.save(test_image)
        print(f"✅ 创建测试图片: {test_image}")
    
    # 创建测试PDF
    test_pdf = os.path.join(test_dir, "test_document.pdf")
    if not os.path.exists(test_pdf):
        try:
            from reportlab.pdfgen import canvas
            c = canvas.Canvas(test_pdf)
            c.drawString(100, 750, "Test Document")
            c.save()
            print(f"✅ 创建测试PDF: {test_pdf}")
        except ImportError:
            print("⚠️  无法创建PDF（需要reportlab）")
    
    # 创建测试文本文件
    test_txt = os.path.join(test_dir, "test.txt")
    if not os.path.exists(test_txt):
        with open(test_txt, 'w') as f:
            f.write("This is a test file for E2E tool.")
        print(f"✅ 创建测试文本: {test_txt}")

def main():
    """主函数"""
    print("🚀 增强客户端功能测试")
    print("=" * 60)
    
    # 创建测试文件
    create_test_files()
    
    # 测试路径解析
    test_path_resolution()
    
    print("\n🎉 测试完成")
    print("\n💡 使用提示:")
    print("1. 启动客户端: python3 net/websocket_client.py")
    print("2. 使用 'files' 命令查看可用文件")
    print("3. 使用 'sendmsg' 发送隐写消息（支持Tab自动补全）")
    print("4. 输入文件名时可以使用Tab键自动补全路径")

if __name__ == "__main__":
    main()