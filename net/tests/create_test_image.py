#!/usr/bin/env python3
"""
创建测试图片用于隐写测试
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_test_image():
    """创建一个测试图片"""
    # 创建目录
    os.makedirs("test", exist_ok=True)
    
    # 创建一个简单的测试图片
    width, height = 400, 300
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # 添加一些文字
    try:
        # 尝试使用系统字体
        font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
    except:
        # 使用默认字体
        font = ImageFont.load_default()
    
    text = "E2E Tool Test Image"
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    draw.text((x, y), text, fill='black', font=font)
    
    # 添加一些图形
    draw.rectangle([50, 50, 150, 100], outline='blue', width=2)
    draw.ellipse([200, 150, 300, 250], fill='red')
    
    # 保存图片
    output_path = "test/test_image.png"
    image.save(output_path)
    print(f"✅ 测试图片已创建: {output_path}")
    print(f"📏 图片尺寸: {width}x{height}")
    
    return output_path

if __name__ == "__main__":
    create_test_image() 