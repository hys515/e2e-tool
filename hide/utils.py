import os

# 基础目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 资源目录
RESOURCES_DIR = os.path.join(BASE_DIR, 'hide', 'resources')
OUTPUT_DIR = os.path.join(BASE_DIR, 'hide', 'output')
EXTRACTED_DIR = os.path.join(BASE_DIR, 'hide', 'extracted')

# 图像相关
IMAGES_RESOURCES = os.path.join(RESOURCES_DIR, 'images')
IMAGES_OUTPUT = os.path.join(OUTPUT_DIR, 'images')
IMAGES_EXTRACTED = os.path.join(EXTRACTED_DIR, 'images')

def get_image_path(filename):
    """获取原始图片资源路径"""
    return os.path.join(IMAGES_RESOURCES, filename)

def get_output_image_path(filename):
    """获取嵌入后图片输出路径"""
    return os.path.join(IMAGES_OUTPUT, filename)

def get_extracted_image_path(filename):
    """获取提取验证图片路径"""
    return os.path.join(IMAGES_EXTRACTED, filename)

# PDF相关
def get_pdf_path(filename):
    return os.path.join(RESOURCES_DIR, 'pdfs', filename)

def get_output_pdf_path(filename):
    return os.path.join(OUTPUT_DIR, 'pdfs', filename)

def get_extracted_pdf_path(filename):
    return os.path.join(EXTRACTED_DIR, 'pdfs', filename)

# 视频相关
def get_video_path(filename):
    return os.path.join(RESOURCES_DIR, 'videos', filename)

def get_output_video_path(filename):
    return os.path.join(OUTPUT_DIR, 'videos', filename)

def get_extracted_video_path(filename):
    return os.path.join(EXTRACTED_DIR, 'videos', filename)

# 通用二进制文件（如密文）
def get_output_bin_path(filename):
    return os.path.join(OUTPUT_DIR, filename)

def get_extracted_bin_path(filename):
    return os.path.join(EXTRACTED_DIR, filename) 