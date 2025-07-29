import cv2
import numpy as np
import subprocess
import os
import time
from hide.utils import get_video_path, get_output_video_path, get_extracted_video_path

# 固定路径配置
INPUT_VIDEO = get_video_path('input.mp4')
OUTPUT_VIDEO = get_output_video_path('output_with_hidden_data.avi')
DATA_FILE = get_output_video_path('secret.bin')
EXTRACTED_FILE = get_extracted_video_path('extracted_secret.bin')

def ffv1_embed(input_video, data_bytes, output_video):
    """使用FFV1编码的极速隐写方案，data_bytes为bytes"""
    # 1. 读取并处理第一帧
    start_time = time.time()
    cap = cv2.VideoCapture(input_video)
    ret, frame = cap.read()
    cap.release()
    if not ret:
        raise ValueError("无法读取视频第一帧")
    print(f"读取第一帧耗时: {time.time() - start_time:.2f} 秒")

    # 2. 嵌入数据到LSB
    start_time = time.time()
    data_bits = np.unpackbits(np.frombuffer(data_bytes, dtype=np.uint8))
    frame_flat = frame.flatten()
    bits_needed = min(len(data_bits), len(frame_flat))
    frame_flat[:bits_needed] = (frame_flat[:bits_needed] & 0xFE) | data_bits[:bits_needed]
    embedded_frame = frame_flat.reshape(frame.shape)
    # 计算嵌入速率
    data_size_bytes = len(data_bytes)
    embedding_time = time.time() - start_time
    embedding_rate = data_size_bytes / embedding_time
    print(f"嵌入数据到LSB耗时: {embedding_time:.2f} 秒")
    print(f"嵌入速率: {embedding_rate:.2f} 字节/秒")

    # 3. 使用FFV1编码
    start_time = time.time()
    height, width = frame.shape[:2]
    fourcc = cv2.VideoWriter_fourcc(*'FFV1')  # 修改为FFV1
    writer = cv2.VideoWriter('temp.avi', fourcc, 30, (width, height), isColor=True)
    if not writer.isOpened():
        raise RuntimeError("FFV1编码器初始化失败，请检查OpenCV支持")
    writer.write(embedded_frame)
    writer.release()
    print(f"使用FFV1编码耗时: {time.time() - start_time:.2f} 秒")

    # 4. 简化处理：直接使用嵌入的帧
    start_time = time.time()
    import shutil
    shutil.copy('temp.avi', output_video)
    os.remove('temp.avi')
    print(f"使用简化处理耗时: {time.time() - start_time:.2f} 秒")

    # 验证
    start_time = time.time()
    verify_embedding(input_video, output_video, data_bytes)
    print(f"验证数据完整性耗时: {time.time() - start_time:.2f} 秒")

def ffv1_extract(stego_video, data_length):
    """从视频第一帧提取指定长度的二进制数据"""
    cap = cv2.VideoCapture(stego_video)
    ret, frame = cap.read()
    cap.release()
    if not ret or frame is None:
        raise ValueError(f"无法读取视频第一帧: {stego_video}")
    bits_to_extract = data_length * 8
    extracted_bits = (frame.flatten() & 1)[:bits_to_extract]
    data_bytes = np.packbits(extracted_bits)
    return bytes(data_bytes[:data_length])

def embed_message(input_path, output_path, message: bytes):
    """
    统一接口：在视频 input_path 中嵌入 message，输出到 output_path
    自动在数据前加4字节长度头部
    """
    length_bytes = len(message).to_bytes(4, 'big')
    full_message = length_bytes + message
    return ffv1_embed(input_path, full_message, output_path)

def extract_message(stego_path) -> bytes:
    """
    统一接口：从视频 stego_path 中提取嵌入的消息
    自动解析前4字节长度
    """
    # 先提取前4字节长度
    length_bytes = ffv1_extract(stego_path, 4)
    data_length = int.from_bytes(length_bytes, 'big')
    # 再提取实际数据
    return ffv1_extract(stego_path, 4 + data_length)[4:]

def verify_embedding(original_video, embedded_video, data_bytes):
    """验证数据完整性"""
    # 提取第一帧
    start_time = time.time()
    cap = cv2.VideoCapture(embedded_video)
    ret, frame = cap.read()
    cap.release()
    
    # 检查视频读取是否成功
    if not ret or frame is None:
        print(f"⚠️  警告: 无法读取嵌入视频进行验证: {embedded_video}")
        print("⚠️  跳过数据完整性验证")
        return
    
    # 提取LSB
    extracted_bits = (frame.flatten() & 1)[:len(data_bytes)*8]
    # 对比原始数据
    original_bits = np.unpackbits(np.frombuffer(data_bytes, dtype=np.uint8))
    mismatch = np.sum(extracted_bits != original_bits)
    print(f"数据校验: {mismatch}位不匹配" if mismatch else "✅ 数据完全匹配")
    print(f"嵌入的bits: {original_bits[:32]}...")
    print(f"提取的bits: {extracted_bits[:32]}...")
    extraction_time = time.time() - start_time
    data_size_bytes = len(data_bytes)
    extraction_rate = data_size_bytes / extraction_time
    print(f"提取数据耗时: {extraction_time:.2f} 秒")
    print(f"提取速率: {extraction_rate:.2f} 字节/秒")

if __name__ == "__main__":
    start_time = time.time()
    with open(DATA_FILE, 'rb') as f:
        secret_data = f.read()
    embed_message(
        input_path=INPUT_VIDEO,
        output_path=OUTPUT_VIDEO,
        message=secret_data
    )
    extracted_data = extract_message(OUTPUT_VIDEO)
    with open(EXTRACTED_FILE, 'wb') as f:
        f.write(extracted_data)
    print("数据是否一致:", extracted_data == secret_data)
    print(f"总耗时: {time.time() - start_time:.2f} 秒")