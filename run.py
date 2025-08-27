#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
理想论坛自动签到程序 - 主启动脚本
提供用户友好的命令行界面
"""

import os
import sys
import argparse
from datetime import datetime


def print_banner():
    """打印程序横幅"""
    banner = """
    ╔═══════════════════════════════════════╗
    ║        理想论坛自动签到程序           ║
    ║     Ideal Forum Auto Sign-in Bot      ║
    ║                                       ║
    ║        Version: 1.0.0                 ║
    ║        Author: AI Assistant           ║
    ╚═══════════════════════════════════════╝
    """
    print(banner)


def check_config():
    """检查配置文件"""
    if not os.path.exists('config.ini'):
        print("❌ 未找到配置文件 config.ini")
        print("💡 请先复制并编辑 config.ini 文件，填入您的用户名和密码")
        return False
    return True


def show_help():
    """显示帮助信息"""
    help_text = """
🎯 使用方法:

基础功能：
  python run.py --test          立即测试签到功能
  python run.py --sign          立即执行一次签到
  python run.py --schedule      启动定时签到调度器
  python run.py --config        显示当前配置信息

高级功能：
  python run.py --full-test     运行完整功能测试
  python run.py --check         检查环境和依赖

📝 配置说明：
1. 编辑 config.ini 文件
2. 在 [LOGIN] 部分填入您的用户名和密码
3. 在 [SCHEDULE] 部分设置签到时间（24小时格式，如 09:00）

📊 文件说明：
  config.ini     - 配置文件（必须）
  sign_bot.py    - 核心签到逻辑
  scheduler.py   - 定时任务调度器
  test_sign.py   - 测试脚本
  run.py         - 主启动脚本

📞 支持：
如有问题，请检查日志文件 sign_log.txt 和 scheduler_log.txt
    """
    print(help_text)


def main():
    """主函数"""
    print_banner()
    
    parser = argparse.ArgumentParser(description='理想论坛自动签到程序', add_help=False)
    parser.add_argument('--test', action='store_true', help='运行基础环境测试')
    parser.add_argument('--sign', action='store_true', help='立即执行一次签到')
    parser.add_argument('--schedule', action='store_true', help='启动定时签到调度器')
    parser.add_argument('--config', action='store_true', help='显示配置信息')
    parser.add_argument('--full-test', action='store_true', help='运行完整功能测试（实际登录）')
    parser.add_argument('--check', action='store_true', help='检查环境和依赖')
    parser.add_argument('--help', action='store_true', help='显示帮助信息')
    
    args = parser.parse_args()
    
    # 如果没有参数或者要求显示帮助，显示帮助
    if not any(vars(args).values()) or args.help:
        show_help()
        return
    
    # 检查配置文件（除了check命令外都需要）
    if not args.check and not check_config():
        sys.exit(1)
    
    try:
        if args.check:
            # 检查环境
            print("🔍 检查环境和依赖...")
            os.system(f"{sys.executable} test_sign.py")
            
        elif args.test:
            # 运行基础测试
            print("🧪 运行基础环境测试...")
            os.system(f"{sys.executable} test_sign.py")
            
        elif args.sign:
            # 立即签到
            print("🚀 立即执行签到任务...")
            os.system(f"{sys.executable} sign_bot.py")
            
        elif args.schedule:
            # 启动调度器
            print("⏰ 启动定时签到调度器...")
            os.system(f"{sys.executable} scheduler.py --run")
            
        elif args.config:
            # 显示配置信息
            print("📋 显示配置信息...")
            os.system(f"{sys.executable} scheduler.py --info")
            
        elif args.full_test:
            # 完整功能测试
            print("🎯 运行完整功能测试...")
            os.system(f"{sys.executable} scheduler.py --test")
    
    except KeyboardInterrupt:
        print("\n⏹️  用户中断程序")
    except Exception as e:
        print(f"❌ 程序执行错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
