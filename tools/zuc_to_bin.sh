#!/bin/bash

# ZUC 文件转换脚本
# 将 ZUC 格式的加密文件转换为标准二进制文件

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[信息]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[成功]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[警告]${NC} $1"
}

print_error() {
    echo -e "${RED}[错误]${NC} $1"
}

# 显示帮助信息
show_help() {
    cat << EOF
ZUC 文件转换工具

用法:
    $0 <输入文件> [输出文件]
    $0 --batch <目录> [输出目录]

选项:
    --batch    批量转换模式
    --help     显示此帮助信息

示例:
    $0 perf_test/cipher_16.zuc
    $0 perf_test/cipher_16.zuc output.bin
    $0 --batch perf_test/
    $0 --batch perf_test/ bin_output/

EOF
}

# 转换单个文件
convert_single() {
    local input_file="$1"
    local output_file="$2"
    
    # 检查输入文件
    if [[ ! -f "$input_file" ]]; then
        print_error "输入文件不存在: $input_file"
        return 1
    fi
    
    # 确定输出文件名
    if [[ -z "$output_file" ]]; then
        output_file="${input_file%.zuc}.bin"
    fi
    
    # 显示文件信息
    local file_size=$(stat -f%z "$input_file" 2>/dev/null || stat -c%s "$input_file" 2>/dev/null)
    print_info "转换文件: $input_file (${file_size} 字节)"
    
    # 复制文件
    cp "$input_file" "$output_file"
    
    # 验证结果
    if [[ -f "$output_file" ]]; then
        local new_size=$(stat -f%z "$output_file" 2>/dev/null || stat -c%s "$output_file" 2>/dev/null)
        if [[ "$file_size" -eq "$new_size" ]]; then
            print_success "转换完成: $output_file (${new_size} 字节)"
            return 0
        else
            print_error "文件大小不匹配: 原始 ${file_size}, 转换后 ${new_size}"
            return 1
        fi
    else
        print_error "输出文件创建失败: $output_file"
        return 1
    fi
}

# 批量转换
batch_convert() {
    local input_dir="$1"
    local output_dir="$2"
    
    # 检查输入目录
    if [[ ! -d "$input_dir" ]]; then
        print_error "输入目录不存在: $input_dir"
        return 1
    fi
    
    # 确定输出目录
    if [[ -z "$output_dir" ]]; then
        output_dir="${input_dir}/bin_output"
    fi
    
    # 创建输出目录
    mkdir -p "$output_dir"
    
    # 查找所有 ZUC 文件
    local zuc_files=($(find "$input_dir" -name "*.zuc" -type f))
    
    if [[ ${#zuc_files[@]} -eq 0 ]]; then
        print_warning "在 $input_dir 中未找到 .zuc 文件"
        return 0
    fi
    
    print_info "找到 ${#zuc_files[@]} 个 ZUC 文件，开始批量转换..."
    
    local success_count=0
    for file in "${zuc_files[@]}"; do
        local filename=$(basename "$file")
        local output_file="${output_dir}/${filename%.zuc}.bin"
        
        if convert_single "$file" "$output_file"; then
            ((success_count++))
        fi
    done
    
    print_success "批量转换完成: ${success_count}/${#zuc_files[@]} 个文件成功"
    print_info "输出目录: $output_dir"
    
    return $(( ${#zuc_files[@]} - success_count ))
}

# 主函数
main() {
    # 检查参数
    if [[ $# -eq 0 ]] || [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
        show_help
        exit 0
    fi
    
    # 批量转换模式
    if [[ "$1" == "--batch" ]]; then
        if [[ $# -lt 2 ]]; then
            print_error "批量转换模式需要指定输入目录"
            exit 1
        fi
        
        local input_dir="$2"
        local output_dir="$3"
        
        batch_convert "$input_dir" "$output_dir"
        exit $?
    fi
    
    # 单个文件转换模式
    local input_file="$1"
    local output_file="$2"
    
    convert_single "$input_file" "$output_file"
    exit $?
}

# 运行主函数
main "$@" 