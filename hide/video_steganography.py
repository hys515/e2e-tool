import cv2
import numpy as np
import subprocess
import os
import time

# 常量配置（修改为您的实际路径）
INPUT_VIDEO = '/Users/tangtang/Documents/ZUC/hide/input3.mp4'        # 输入视频路径
OUTPUT_VIDEO = '/Users/tangtang/Documents/ZUC/hide/output_with_hidden_data.avi'      # 输出视频路径
DATA_FILE = '/Users/tangtang/Documents/ZUC/hide/cipher_16384.bin'         # 要隐藏的二进制文件
EXTRACTED_FILE = '/Users/tangtang/Documents/ZUC/hide/extracted.bin' # 提取结果保存路径

def ffv1_embed(input_video, data_file, output_video):
    """使用FFV1编码的极速隐写方案"""
    
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
    with open(data_file, 'rb') as f:
        data_bits = np.unpackbits(np.frombuffer(f.read(), dtype=np.uint8))
    
    frame_flat = frame.flatten()
    bits_needed = min(len(data_bits), len(frame_flat))
    frame_flat[:bits_needed] = (frame_flat[:bits_needed] & 0xFE) | data_bits[:bits_needed]
    embedded_frame = frame_flat.reshape(frame.shape)
    # 计算嵌入速率
    data_size_bytes = os.path.getsize(data_file)
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

    # 4. 用FFmpeg拼接剩余帧（跳过原视频第一帧）
    start_time = time.time()
    cmd = [
        'ffmpeg',
        '-y',
        '-i', 'temp.avi',
        '-ss', '00:00:00.033',  # 精确跳过1帧（假设30fps）
        '-i', input_video,
        '-filter_complex', '[0][1]concat=n=2:v=1:a=0',
        '-c:v', 'ffv1',         # 强制使用FFV1
        '-an',
        output_video
    ]
    subprocess.run(cmd, stderr=subprocess.DEVNULL)
    os.remove('temp.avi')
    print(f"使用FFmpeg拼接剩余帧耗时: {time.time() - start_time:.2f} 秒")

    # 验证
    start_time = time.time()
    verify_embedding(input_video, output_video, data_file)
    print(f"验证数据完整性耗时: {time.time() - start_time:.2f} 秒")

def verify_embedding(original_video, embedded_video, data_file):
    """验证数据完整性"""
    # 提取第一帧
    start_time = time.time()
    cap = cv2.VideoCapture(embedded_video)
    ret, frame = cap.read()
    cap.release()
    
    # 提取LSB
    extracted_bits = (frame.flatten() & 1)[:os.path.getsize(data_file)*8]
    
    # 对比原始数据
    with open(data_file, 'rb') as f:
        original_bits = np.unpackbits(np.frombuffer(f.read(), dtype=np.uint8))
    
    mismatch = np.sum(extracted_bits != original_bits)
    print(f"数据校验: {mismatch}位不匹配" if mismatch else "✅ 数据完全匹配")
    
    # 输出嵌入的bits和提取出的bits
    print(f"嵌入的bits: {original_bits[:32]}...")  # 输出前32位用于调试
    print(f"提取的bits: {extracted_bits[:32]}...")  # 输出前32位用于调试
    
    # 计算提取时间
    extraction_time = time.time() - start_time
    #使用了嵌入数据文件大小
    data_size_bytes = os.path.getsize(data_file)
    extraction_rate = data_size_bytes / extraction_time
    
    print(f"提取数据耗时: {extraction_time:.2f} 秒")
    print(f"提取速率: {extraction_rate:.2f} 字节/秒")

if __name__ == "__main__":
    start_time = time.time()
    ffv1_embed(
        input_video=INPUT_VIDEO,
        data_file=DATA_FILE,
        output_video=OUTPUT_VIDEO
    )
    print(f"总耗时: {time.time() - start_time:.2f} 秒")