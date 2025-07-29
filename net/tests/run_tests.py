#!/usr/bin/env python3
"""
测试运行脚本
提供快速运行常用测试的功能
"""

import os
import sys
import subprocess
import argparse

def run_test(test_name, description=""):
    """运行单个测试"""
    print(f"\n{'='*60}")
    print(f"🧪 运行测试: {test_name}")
    if description:
        print(f"📝 描述: {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run([sys.executable, test_name], 
                              capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ 测试通过")
            if result.stdout:
                print("📤 输出:")
                print(result.stdout)
        else:
            print("❌ 测试失败")
            if result.stderr:
                print("📤 错误:")
                print(result.stderr)
            if result.stdout:
                print("📤 输出:")
                print(result.stdout)
                
    except subprocess.TimeoutExpired:
        print("⏰ 测试超时")
    except Exception as e:
        print(f"❌ 运行测试失败: {e}")

def run_basic_tests():
    """运行基础功能测试"""
    print("\n🚀 运行基础功能测试")
    
    tests = [
        ("test_imports.py", "测试模块导入和基本功能"),
        ("test_connection.py", "测试基本连接功能"),
        ("test_features.py", "测试完整功能特性")
    ]
    
    for test_file, description in tests:
        if os.path.exists(test_file):
            run_test(test_file, description)
        else:
            print(f"⚠️  测试文件不存在: {test_file}")

def run_steg_tests():
    """运行隐写术测试"""
    print("\n🎭 运行隐写术测试")
    
    tests = [
        ("test_steg.py", "测试所有隐写功能"),
        ("test_video_fix.py", "测试视频隐写修复")
    ]
    
    for test_file, description in tests:
        if os.path.exists(test_file):
            run_test(test_file, description)
        else:
            print(f"⚠️  测试文件不存在: {test_file}")

def run_transfer_tests():
    """运行文件传输测试"""
    print("\n📁 运行文件传输测试")
    
    tests = [
        ("test_chunked_transfer.py", "测试分块文件传输"),
        ("test_file_transfer_complete.py", "测试完整文件传输")
    ]
    
    for test_file, description in tests:
        if os.path.exists(test_file):
            run_test(test_file, description)
        else:
            print(f"⚠️  测试文件不存在: {test_file}")

def run_stability_tests():
    """运行稳定性测试"""
    print("\n💓 运行稳定性测试")
    
    tests = [
        ("test_heartbeat_fix.py", "测试心跳机制和连接稳定性"),
        ("test_connection_stability.py", "测试连接稳定性和大文件传输")
    ]
    
    for test_file, description in tests:
        if os.path.exists(test_file):
            run_test(test_file, description)
        else:
            print(f"⚠️  测试文件不存在: {test_file}")

def run_all_tests():
    """运行所有测试"""
    print("\n🎯 运行所有测试")
    
    run_basic_tests()
    run_steg_tests()
    run_transfer_tests()
    run_stability_tests()

def create_test_files():
    """创建测试文件"""
    print("\n🛠️  创建测试文件")
    
    files = [
        ("create_test_image.py", "创建测试图片"),
        ("create_test_pdf.py", "创建测试PDF")
    ]
    
    for test_file, description in files:
        if os.path.exists(test_file):
            print(f"📝 {description}")
            run_test(test_file, description)
        else:
            print(f"⚠️  文件不存在: {test_file}")

def show_menu():
    """显示菜单"""
    print("\n" + "="*60)
    print("🧪 E2E工具测试菜单")
    print("="*60)
    print("1. 基础功能测试")
    print("2. 隐写术测试")
    print("3. 文件传输测试")
    print("4. 稳定性测试")
    print("5. 创建测试文件")
    print("6. 运行所有测试")
    print("0. 退出")
    print("="*60)

def interactive_menu():
    """交互式菜单"""
    while True:
        show_menu()
        try:
            choice = input("\n请选择 (0-6): ").strip()
            
            if choice == "0":
                print("👋 退出测试")
                break
            elif choice == "1":
                run_basic_tests()
            elif choice == "2":
                run_steg_tests()
            elif choice == "3":
                run_transfer_tests()
            elif choice == "4":
                run_stability_tests()
            elif choice == "5":
                create_test_files()
            elif choice == "6":
                run_all_tests()
            else:
                print("❌ 无效选择，请输入 0-6")
                
        except KeyboardInterrupt:
            print("\n👋 用户退出")
            break
        except Exception as e:
            print(f"❌ 错误: {e}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="E2E工具测试运行器")
    parser.add_argument("--basic", action="store_true", help="运行基础功能测试")
    parser.add_argument("--steg", action="store_true", help="运行隐写术测试")
    parser.add_argument("--transfer", action="store_true", help="运行文件传输测试")
    parser.add_argument("--stability", action="store_true", help="运行稳定性测试")
    parser.add_argument("--create-files", action="store_true", help="创建测试文件")
    parser.add_argument("--all", action="store_true", help="运行所有测试")
    parser.add_argument("--interactive", action="store_true", help="交互式菜单")
    
    args = parser.parse_args()
    
    # 切换到测试目录
    test_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(test_dir)
    
    if args.basic:
        run_basic_tests()
    elif args.steg:
        run_steg_tests()
    elif args.transfer:
        run_transfer_tests()
    elif args.stability:
        run_stability_tests()
    elif args.create_files:
        create_test_files()
    elif args.all:
        run_all_tests()
    elif args.interactive:
        interactive_menu()
    else:
        # 默认显示交互式菜单
        interactive_menu()

if __name__ == "__main__":
    main() 