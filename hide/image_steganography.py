import cv2
import numpy as np
import os
from skimage.metrics import structural_similarity as ssim
def embed_data(image_path, data_bytes, output_path, n_bits=1):
    """
    将二进制数据嵌入到图片中
    :param image_path: 原始图片路径
    :param data_bytes: 要嵌入的二进制数据（bytes类型）
    :param output_path: 嵌入后图片保存路径
    :param n_bits: 每个像素嵌入的位数（1~8）
    """
    # 读取图片
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("无法读取图片，请检查路径是否正确")
    original_img = img.copy()
    # 将二进制数据转换为比特流
    bit_stream = ''.join([format(byte, '08b') for byte in data_bytes])
    data_len = len(bit_stream)

    # 计算图片可嵌入的最大比特数
    max_bits = img.shape[0] * img.shape[1] * 3 * n_bits  # 3通道
    if data_len > max_bits:
        raise ValueError(f"数据过大，无法嵌入。最大可嵌入 {max_bits} 位，当前数据 {data_len} 位")

    data_index = 0
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            for k in range(3):  # RGB三通道
                if data_index < data_len:
                    pixel = img[i, j, k]
                    # 清除最低n位
                    pixel = (pixel >> n_bits) << n_bits
                    # 提取n位数据
                    bits = bit_stream[data_index:data_index + n_bits]
                    # 嵌入数据
                    img[i, j, k] = pixel | int(bits, 2)
                    data_index += n_bits
                else:
                    break
            if data_index >= data_len:
                break
        if data_index >= data_len:
            break

    # 保存嵌入后的图片
    cv2.imwrite(output_path, img, [cv2.IMWRITE_PNG_COMPRESSION, 3])  # 启用压缩，默认级别为3，平衡速度和压缩率
    print(f"数据嵌入完成，保存为 {output_path}")
    # 计算质量指标
    embedded_img = cv2.imread(output_path)
    psnr = calculate_psnr(original_img, embedded_img)
    ssim_val = calculate_ssim(original_img, embedded_img)
    
    print(f"PSNR: {psnr:.2f} dB")
    print(f"SSIM: {ssim_val:.4f}")

    return psnr, ssim_val

def extract_data(image_path, data_length_bytes, n_bits=1):
    """
    从图片中提取嵌入的二进制数据
    :param image_path: 嵌入数据的图片路径
    :param data_length_bytes: 原始嵌入数据的字节长度
    :param n_bits: 每个像素嵌入的位数（与嵌入时一致）
    :return: 提取出的二进制数据（bytes类型）
    """
    # 读取图片
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("无法读取图片，请检查路径是否正确")

    # 计算需要提取的比特数
    total_bits = data_length_bytes * 8
    bit_stream = ''
    data_index = 0

    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            for k in range(3):  # RGB三通道
                if data_index < total_bits:
                    pixel = img[i, j, k]
                    # 提取最低n位
                    bits = format(pixel & ((1 << n_bits) - 1), f'0{n_bits}b')
                    bit_stream += bits
                    data_index += n_bits
                else:
                    break
            if data_index >= total_bits:
                break
        if data_index >= total_bits:
            break

    # 将比特流转换为字节数据
    data_bytes = bytearray()
    for i in range(0, len(bit_stream), 8):
        byte = bit_stream[i:i + 8]
        if len(byte) == 8:
            data_bytes.append(int(byte, 2))

    return bytes(data_bytes)
def print_file_size(file_path):
    """
    打印文件大小
    :param file_path: 文件路径
    """
    size = os.path.getsize(file_path)
    print(f"文件大小: {size} 字节")
def calculate_psnr(img1, img2):
    """计算两幅图像的PSNR值"""
    mse = np.mean((img1 - img2) ** 2)
    if mse == 0:
        return float('inf')
    max_pixel = 255.0
    psnr = 20 * np.log10(max_pixel / np.sqrt(mse))
    return psnr

def calculate_ssim(img1, img2):
    """计算两幅图像的SSIM值（多通道）"""
    # 转换为灰度图像计算SSIM（单通道）
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    return ssim (gray1, gray2, data_range=gray2.max() - gray2.min() )
if __name__ == "__main__":
    # 加密后的二进制数据
    bin_files = ['cipher_16384.bin']  # 数据列表

    # 使用绝对路径
    original_image_path = '/Users/tangtang/Documents/ZUC端到端加密隐藏部分/hide/original.png'
    embedded_image_path = '/Users/tangtang/Documents/ZUC端到端加密隐藏部分/hide/embedded.png'
    # 打印原始图像文件大小
    print("原始图像文件大小:")
    print_file_size(original_image_path)

    # 依次嵌入数据
    for bin_file in bin_files:
        bin_file_path = os.path.join(os.path.dirname(__file__), bin_file)
        with open(bin_file_path, 'rb') as f:
            encrypted_data = f.read()

        # 嵌入数据
        embed_data(original_image_path, encrypted_data, embedded_image_path, n_bits=1)
        # 嵌入数据并获取质量指标
        psnr, ssim_val = embed_data(original_image_path, encrypted_data, embedded_image_path, n_bits=1)
        # 打印嵌入后图像文件大小
        print("嵌入后图像文件大小:")
        print_file_size(embedded_image_path)

        # 提取数据（注意：提取时需要知道原始数据长度）
        extracted_data = extract_data(embedded_image_path, len(encrypted_data), n_bits=1)

        # 验证提取结果
        print("提取的数据:", extracted_data)
        print("数据是否一致:", extracted_data == encrypted_data)