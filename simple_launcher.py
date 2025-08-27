#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化启动器 - 不依赖PyQt6
功能：基础功能启动，避免GUI依赖问题
"""

import os
import sys
import subprocess
from pathlib import Path
from loguru import logger


def print_banner():
    """打印程序横幅"""
    banner = """
    ╔═══════════════════════════════════════╗
    ║        理想论坛自动签到程序           ║
    ║     Ideal Forum Auto Sign-in Bot      ║
    ║                                       ║
    ║        Version: 1.0.0 (Simple)       ║
    ║        Author: AI Assistant           ║
    ╚═══════════════════════════════════════╝
    """
    print(banner)


def check_basic_environment():
    """检查基础环境"""
    logger.info("🔍 检查基础环境...")
    
    # 检查Python版本
    python_version = sys.version_info
    if python_version.major < 3 or python_version.minor < 7:
        logger.error(f"Python版本过低: {python_version.major}.{python_version.minor}")
        return False
    else:
        logger.info(f"✅ Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # 检查必要文件
    required_files = [
        "config.ini",
        "sign_bot.py",
        "run.py",
        "requirements.txt"
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        logger.error(f"缺少必要文件: {', '.join(missing_files)}")
        return False
    else:
        logger.info("✅ 必要文件检查通过")
    
    return True


def install_basic_requirements():
    """安装基础依赖包"""
    logger.info("📦 安装基础依赖包...")
    
    basic_packages = [
        "selenium",
        "configparser", 
        "schedule",
        "webdriver-manager",
        "loguru"
    ]
    
    for package in basic_packages:
        try:
            logger.info(f"安装 {package}...")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", package
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"✅ {package} 安装成功")
            else:
                logger.warning(f"⚠️ {package} 安装可能有问题: {result.stderr}")
        except Exception as e:
            logger.error(f"❌ 安装 {package} 失败: {e}")
    
    logger.info("✅ 基础依赖包安装完成")


def run_basic_test():
    """运行基础测试"""
    logger.info("🧪 运行基础功能测试...")
    
    try:
        result = subprocess.run([
            sys.executable, "test_sign.py"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.success("✅ 基础测试通过")
            print(result.stdout)
            return True
        else:
            logger.error("❌ 基础测试失败")
            print(result.stderr)
            return False
    except Exception as e:
        logger.error(f"❌ 运行测试时发生错误: {e}")
        return False


def run_sign_task():
    """运行签到任务"""
    logger.info("🚀 执行签到任务...")
    
    try:
        result = subprocess.run([
            sys.executable, "run.py", "--sign"
        ], capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        return result.returncode == 0
    except Exception as e:
        logger.error(f"❌ 执行签到任务时发生错误: {e}")
        return False


def run_schedule():
    """启动定时任务"""
    logger.info("⏰ 启动定时签到调度器...")
    
    try:
        # 直接启动调度器，不捕获输出，让用户看到实时信息
        subprocess.run([
            sys.executable, "run.py", "--schedule"
        ])
    except KeyboardInterrupt:
        logger.info("用户中断了定时任务")
    except Exception as e:
        logger.error(f"❌ 启动定时任务时发生错误: {e}")


def show_menu():
    """显示菜单"""
    print("\n🎯 请选择操作:")
    print("1. 环境检查和设置")
    print("2. 运行基础测试")
    print("3. 立即执行签到")
    print("4. 启动定时签到")
    print("5. 显示配置信息")
    print("6. 尝试启动GUI界面")
    print("0. 退出程序")
    print()


def main():
    """主函数"""
    print_banner()
    
    while True:
        show_menu()
        
        try:
            choice = input("请输入选择 (0-6): ").strip()
            
            if choice == "0":
                print("👋 谢谢使用！")
                break
            
            elif choice == "1":
                # 环境检查和设置
                print("\n🔧 环境检查和设置...")
                if check_basic_environment():
                    install_basic_requirements()
                    print("✅ 环境设置完成")
                else:
                    print("❌ 环境检查失败")
            
            elif choice == "2":
                # 运行基础测试
                print("\n🧪 运行基础测试...")
                run_basic_test()
            
            elif choice == "3":
                # 立即执行签到
                print("\n🚀 立即执行签到...")
                success = run_sign_task()
                if success:
                    print("✅ 签到任务完成")
                else:
                    print("❌ 签到任务失败")
            
            elif choice == "4":
                # 启动定时签到
                print("\n⏰ 启动定时签到...")
                print("💡 按 Ctrl+C 可以停止定时任务")
                run_schedule()
            
            elif choice == "5":
                # 显示配置信息
                print("\n📋 显示配置信息...")
                try:
                    result = subprocess.run([
                        sys.executable, "run.py", "--config"
                    ], capture_output=True, text=True)
                    print(result.stdout)
                except Exception as e:
                    print(f"❌ 获取配置信息失败: {e}")
            
            elif choice == "6":
                # 尝试启动GUI界面
                print("\n🎨 尝试启动GUI界面...")
                try:
                    # 先尝试安装PyQt6
                    print("📦 安装GUI依赖包...")
                    subprocess.run([
                        sys.executable, "-m", "pip", "install", "PyQt6"
                    ], check=True)
                    
                    # 启动GUI
                    subprocess.run([
                        sys.executable, "run.py", "--gui"
                    ])
                except subprocess.CalledProcessError:
                    print("❌ PyQt6安装失败")
                except Exception as e:
                    print(f"❌ GUI启动失败: {e}")
                    print("💡 建议使用命令行模式")
            
            else:
                print("❌ 无效选择，请重新输入")
            
            input("\n按回车键继续...")
            
        except KeyboardInterrupt:
            print("\n👋 用户中断，程序退出")
            break
        except Exception as e:
            print(f"❌ 发生错误: {e}")
            input("按回车键继续...")


if __name__ == "__main__":
    main()
