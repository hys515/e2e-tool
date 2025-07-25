import os
from PyPDF2 import PdfReader, PdfWriter
import binascii
import zlib
import hashlib
from hide.utils import get_pdf_path, get_output_pdf_path, get_extracted_pdf_path

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

def embed_message(input_path, output_path, message: bytes):
    """
    统一接口：在PDF input_path 中嵌入 message，输出到 output_path
    自动在数据前加4字节长度头部
    """
    length_bytes = len(message).to_bytes(4, 'big')
    full_message = length_bytes + message
    return embed_binary_in_pdf(input_path, full_message, output_pdf=output_path)

def extract_message(stego_path) -> bytes:
    """
    统一接口：从PDF stego_path 中提取嵌入的消息
    自动解析前4字节长度
    """
    full_data = extract_binary_from_pdf(stego_path)
    if len(full_data) < 4:
        raise ValueError("提取数据长度不足4字节，无法解析长度头部")
    data_length = int.from_bytes(full_data[:4], 'big')
    return full_data[4:4+data_length]

def calculate_sha256(data):
    """计算数据的 SHA-256 哈希值"""
    sha256_hash = hashlib.sha256()
    sha256_hash.update(data)
    return sha256_hash.hexdigest()

if __name__ == "__main__":
    # 固定路径
    ORIGINAL_PDF = get_pdf_path("cover.pdf")
    BINARY_FILE = get_output_pdf_path("secret.bin")
    OUTPUT_PDF = get_output_pdf_path("cover_embedded.pdf")
    EXTRACTED_FILE = get_extracted_pdf_path("extracted_secret.bin")

    try:
        with open(BINARY_FILE, 'rb') as f:
            binary_data = f.read()
        print(f"要嵌入的文件: {BINARY_FILE} ({len(binary_data):,} 字节)")

        embed_message(ORIGINAL_PDF, OUTPUT_PDF, binary_data)
        extracted_data = extract_message(OUTPUT_PDF)
        with open(EXTRACTED_FILE, 'wb') as f:
            f.write(extracted_data)
        print(f"\n验证结果:")
        print(f"原始数据 SHA-256: {calculate_sha256(binary_data)}")
        print(f"提取数据 SHA-256: {calculate_sha256(extracted_data)}")
        print("数据是否一致:", binary_data == extracted_data)
    except Exception as e:
        print(f"\n错误: {str(e)}")