import os
from PyPDF2 import PdfReader, PdfWriter
import binascii
import zlib
import hashlib

def calculate_size_limit(original_size, tolerance=0.05):
    """计算允许的最大嵌入数据量（±tolerance）"""
    return original_size * tolerance

def embed_binary_in_pdf(input_pdf, binary_data, output_pdf, metadata_key="/HiddenData"):
    """
    将二进制数据嵌入PDF，确保大小变化不超过±tolerance%
    :param input_pdf: 原始PDF路径
    :param binary_data: 要嵌入的二进制数据
    :param output_pdf: 输出PDF路径
    :param metadata_key: 元数据键名
    """
    # 获取原始文件大小
    original_size = os.path.getsize(input_pdf)
    max_allowed = calculate_size_limit(original_size)
    
    # 检查数据大小
    if len(binary_data) > max_allowed:
        compressed = zlib.compress(binary_data)
        if len(compressed) > max_allowed:
            raise ValueError(
                f"数据过大！原始大小: {len(binary_data):,} 字节，"
                f"压缩后: {len(compressed):,} 字节，"
                f"允许最大值: {max_allowed:,.0f} 字节"
            )
        binary_data = compressed
        print(f"数据已压缩: {len(binary_data):,} 字节")

    # 读取和准备PDF
    reader = PdfReader(input_pdf)
    writer = PdfWriter()
    
    # 复制所有页面（优化对象流以减少体积）
    for page in reader.pages:
        writer.add_page(page)
    
    # 使用更高效的存储方式
    hex_data = binascii.hexlify(binary_data).decode('ascii')
    writer.add_metadata({metadata_key: hex_data})

    # 写入临时文件检查大小
    temp_path = output_pdf + ".tmp"
    with open(temp_path, 'wb') as f:
        writer.write(f)
    
    # 验证大小变化
    new_size = os.path.getsize(temp_path)
    size_change = (new_size - original_size) / original_size
    
    if abs(size_change) > 0.05:  # 超过5%
        os.remove(temp_path)
        raise ValueError(
            f"大小变化超标: {size_change:.2%} (允许±5%)\n"
            f"原始大小: {original_size:,} 字节\n"
            f"新大小: {new_size:,} 字节"
        )
    
    # 验证通过，重命名文件
    os.replace(temp_path, output_pdf)
    
    print(f"\n嵌入成功！大小变化: {size_change:.2%}")
    print(f"原始文件: {original_size:,} 字节")
    print(f"新文件: {new_size:,} 字节")
    print(f"嵌入数据: {len(binary_data):,} 字节")

def extract_binary_from_pdf(input_pdf, metadata_key="/HiddenData"):
    """从PDF提取二进制数据（自动处理压缩）"""
    reader = PdfReader(input_pdf)
    if metadata_key not in reader.metadata:
        raise ValueError(f"未找到元数据键: {metadata_key}")
    
    hex_data = reader.metadata[metadata_key]
    binary_data = binascii.unhexlify(hex_data)
    
    try:
        # 尝试解压（如果是压缩数据）
        return zlib.decompress(binary_data)
    except zlib.error:
        return binary_data

def calculate_sha256(data):
    """计算数据的 SHA-256 哈希值"""
    sha256_hash = hashlib.sha256()
    sha256_hash.update(data)
    return sha256_hash.hexdigest()

# 示例用法
if __name__ == "__main__":
     # 配置路径
    original_pdf = "/Users/tangtang/Documents/ZUC端到端加密隐藏部分/hide/original_1-2.pdf"
    output_pdf = "/Users/tangtang/Documents/ZUC端到端加密隐藏部分/hide/embedded.pdf"
    binary_file = "/Users/tangtang/Documents/ZUC端到端加密隐藏部分/hide/cipher_128.bin"  # 要隐藏的二进制文件
    extracted_file = "hide/extracted/pdfs/extracted_data_from_embedded.pdf.bin"

    try:
        # 1. 读取二进制文件
        with open(binary_file, 'rb') as f:
            binary_data = f.read()
        print(f"要嵌入的文件: {binary_file} ({len(binary_data):,} 字节)")

        # 2. 嵌入到PDF（自动控制大小）
        embed_binary_in_pdf(original_pdf, binary_data, output_pdf)

        # 3. 提取验证
        extracted_data = extract_binary_from_pdf(output_pdf)
        with open(extracted_file, 'wb') as f:
            f.write(extracted_data)
        
        print(f"\n验证结果:")
        print(f"原始数据 SHA-256: {calculate_sha256(binary_data)}")
        print(f"提取数据 SHA-256: {calculate_sha256(extracted_data)}")
        print("数据一致:", binary_data == extracted_data)

    except Exception as e:
        print(f"\n错误: {str(e)}")