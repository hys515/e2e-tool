#!/usr/bin/env python3
"""
ZUC 文件转换工具
将 ZUC 格式的加密文件转换为标准二进制文件，并提供分析功能
"""

import os
import sys
import argparse
import hashlib
from pathlib import Path
import math


def analyze_file(file_path):
    """分析文件的基本信息"""
    if not os.path.exists(file_path):
        print(f"[错误] 文件不存在: {file_path}")
        return None
    
    file_size = os.path.getsize(file_path)
    
    # 读取文件内容
    with open(file_path, 'rb') as f:
        content = f.read()
    
    # 计算 MD5 和 SHA256
    md5_hash = hashlib.md5(content).hexdigest()
    sha256_hash = hashlib.sha256(content).hexdigest()
    
    # 分析字节分布
    byte_counts = {}
    for byte in content:
        byte_counts[byte] = byte_counts.get(byte, 0) + 1
    
    # 计算熵（随机性指标）
    total_bytes = len(content)
    entropy = 0
    for count in byte_counts.values():
        p = count / total_bytes
        if p > 0:
            entropy -= p * math.log2(p)
    
    return {
        'size': file_size,
        'md5': md5_hash,
        'sha256': sha256_hash,
        'entropy': entropy,
        'byte_distribution': byte_counts,
        'content': content
    }


def convert_zuc_to_bin(input_file, output_file=None, analyze=True):
    """将 ZUC 文件转换为二进制文件"""
    
    # 分析输入文件
    if analyze:
        print(f"=== 分析文件: {input_file} ===")
        info = analyze_file(input_file)
        if info is None:
            return False
        
        print(f"文件大小: {info['size']} 字节")
        print(f"MD5: {info['md5']}")
        print(f"SHA256: {info['sha256']}")
        print(f"熵值: {info['entropy']:.2f} (0-8, 越高越随机)")
        
        # 显示字节分布
        print("\n字节分布 (前10个最常见的字节):")
        sorted_bytes = sorted(info['byte_distribution'].items(), 
                            key=lambda x: x[1], reverse=True)
        for byte_val, count in sorted_bytes[:10]:
            percentage = (count / info['size']) * 100
            print(f"  0x{byte_val:02x}: {count} 次 ({percentage:.1f}%)")
    
    # 确定输出文件名
    if output_file is None:
        input_path = Path(input_file)
        output_file = input_path.with_suffix('.bin')
    
    # 复制文件内容
    try:
        with open(input_file, 'rb') as f_in:
            with open(output_file, 'wb') as f_out:
                f_out.write(f_in.read())
        
        print(f"\n[✓] 转换完成: {input_file} → {output_file}")
        
        # 验证转换结果
        if os.path.exists(output_file):
            original_size = os.path.getsize(input_file)
            converted_size = os.path.getsize(output_file)
            if original_size == converted_size:
                print(f"[✓] 文件大小验证通过: {converted_size} 字节")
            else:
                print(f"[⚠] 文件大小不匹配: 原始 {original_size}, 转换后 {converted_size}")
        
        return True
        
    except Exception as e:
        print(f"[错误] 转换失败: {e}")
        return False


def batch_convert(input_dir, output_dir=None, pattern="*.zuc"):
    """批量转换目录中的所有 ZUC 文件"""
    
    if not os.path.isdir(input_dir):
        print(f"[错误] 目录不存在: {input_dir}")
        return False
    
    # 确定输出目录
    if output_dir is None:
        output_dir = os.path.join(input_dir, "bin_output")
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 查找所有 ZUC 文件
    input_path = Path(input_dir)
    zuc_files = list(input_path.glob(pattern))
    
    if not zuc_files:
        print(f"[警告] 在 {input_dir} 中未找到 {pattern} 文件")
        return False
    
    print(f"=== 批量转换: 找到 {len(zuc_files)} 个 ZUC 文件 ===")
    
    success_count = 0
    for zuc_file in zuc_files:
        output_file = Path(output_dir) / f"{zuc_file.stem}.bin"
        
        print(f"\n处理: {zuc_file.name}")
        if convert_zuc_to_bin(str(zuc_file), str(output_file), analyze=False):
            success_count += 1
    
    print(f"\n=== 批量转换完成 ===")
    print(f"成功转换: {success_count}/{len(zuc_files)} 个文件")
    print(f"输出目录: {output_dir}")
    
    return success_count == len(zuc_files)


def main():
    parser = argparse.ArgumentParser(
        description="ZUC 文件转换工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  %(prog)s input.zuc                    # 转换单个文件
  %(prog)s input.zuc -o output.bin      # 指定输出文件名
  %(prog)s input.zuc --no-analyze       # 不显示分析信息
  %(prog)s perf_test/ --batch           # 批量转换目录
  %(prog)s perf_test/ --batch --output bin_files  # 指定输出目录
        """
    )
    
    parser.add_argument('input', help='输入文件或目录')
    parser.add_argument('-o', '--output', help='输出文件或目录')
    parser.add_argument('--no-analyze', action='store_true', 
                       help='不显示文件分析信息')
    parser.add_argument('--batch', action='store_true',
                       help='批量转换模式（输入为目录）')
    parser.add_argument('--pattern', default='*.zuc',
                       help='批量转换时的文件模式 (默认: *.zuc)')
    
    args = parser.parse_args()
    
    if args.batch:
        # 批量转换模式
        success = batch_convert(args.input, args.output, args.pattern)
        sys.exit(0 if success else 1)
    else:
        # 单个文件转换模式
        success = convert_zuc_to_bin(args.input, args.output, not args.no_analyze)
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main() 