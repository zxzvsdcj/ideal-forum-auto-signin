#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
理想论坛自动签到程序打包脚本（仅命令行版本）
功能：将程序打包成可执行文件
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

def print_banner():
    """打印横幅"""
    banner = """
    ╔═══════════════════════════════════════╗
    ║    理想论坛自动签到程序打包工具       ║
    ║       (命令行版本)                    ║
    ║                                       ║
    ║        Version: 1.0.0                 ║
    ╚═══════════════════════════════════════╝
    """
    print(banner)

def check_dependencies():
    """检查打包依赖"""
    print("🔍 检查打包依赖...")
    
    try:
        import PyInstaller
        print(f"✅ PyInstaller已安装: {PyInstaller.__version__}")
        return True
    except ImportError:
        print("❌ PyInstaller未安装")
        print("📦 正在安装PyInstaller...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
            print("✅ PyInstaller安装成功")
            return True
        except subprocess.CalledProcessError:
            print("❌ PyInstaller安装失败")
            return False

def build_cli_executable():
    """构建命令行可执行文件"""
    print("🔨 开始构建命令行可执行文件...")
    
    try:
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",  # 打包成单个文件
            "--console",  # 控制台程序
            "--name=理想论坛签到器",
            "--add-data=config.ini;.",
            "--add-data=requirements.txt;.",
            "--exclude-module=PyQt6",
            "--exclude-module=PyQt5", 
            "--exclude-module=tkinter",
            "--exclude-module=matplotlib",
            "--exclude-module=numpy",
            "--exclude-module=pandas",
            "--hidden-import=selenium",
            "--hidden-import=webdriver_manager",
            "--hidden-import=loguru",
            "--hidden-import=schedule",
            "--hidden-import=configparser",
            "--hidden-import=email.mime.text",
            "--hidden-import=email.mime.multipart",
            "--hidden-import=smtplib",
            "run.py"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 命令行可执行文件构建成功")
            return True
        else:
            print("❌ 构建失败:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ 构建过程中发生错误: {e}")
        return False

def create_portable_package():
    """创建便携版本"""
    print("📦 创建便携版本...")
    
    exe_file = Path("dist/理想论坛签到器.exe")
    if not exe_file.exists():
        print("❌ 可执行文件不存在")
        return False
    
    # 创建便携版目录
    portable_dir = Path("理想论坛签到器便携版")
    if portable_dir.exists():
        shutil.rmtree(portable_dir)
    
    portable_dir.mkdir()
    
    # 复制可执行文件
    shutil.copy2(exe_file, portable_dir / "理想论坛签到器.exe")
    
    # 复制配置文件
    shutil.copy2("config.ini", portable_dir / "config.ini")
    
    # 创建启动脚本
    start_bat = """@echo off
chcp 65001 >nul
title 理想论坛自动签到程序
echo.
echo ╔═══════════════════════════════════════╗
echo ║        理想论坛自动签到程序           ║
echo ║     Ideal Forum Auto Sign-in Bot      ║
echo ║                                       ║
echo ║        便携版 v1.0.0                  ║
echo ╚═══════════════════════════════════════╝
echo.
echo 使用说明：
echo    1. 首次运行前请编辑 config.ini 配置文件
echo    2. 填入您的用户名和密码
echo    3. 可配置邮件通知功能
echo.
echo 启动程序...
echo.
"理想论坛签到器.exe"
echo.
echo 程序已结束，按任意键退出...
pause >nul
"""
    
    quick_sign_bat = """@echo off
chcp 65001 >nul
title 理想论坛快速签到
echo 正在执行快速签到...
"理想论坛签到器.exe" --sign
echo.
echo 签到完成，5秒后自动关闭...
timeout /t 5 >nul
"""
    
    schedule_bat = """@echo off
chcp 65001 >nul
title 理想论坛定时签到
echo 正在启动定时签到...
echo 按 Ctrl+C 可以停止定时任务
"理想论坛签到器.exe" --schedule
"""
    
    with open(portable_dir / "启动程序.bat", 'w', encoding='gbk') as f:
        f.write(start_bat)
    
    with open(portable_dir / "快速签到.bat", 'w', encoding='gbk') as f:
        f.write(quick_sign_bat)
    
    with open(portable_dir / "定时签到.bat", 'w', encoding='gbk') as f:
        f.write(schedule_bat)
    
    # 创建使用说明
    readme_content = """理想论坛自动签到程序 - 便携版
=====================================

📋 文件说明：
- 理想论坛签到器.exe     主程序
- config.ini            配置文件
- 启动程序.bat          带菜单启动
- 快速签到.bat          直接执行签到
- 定时签到.bat          启动定时任务

🔧 首次使用：
1. 编辑 config.ini 文件
2. 修改 [LOGIN] 部分的用户名和密码
3. 运行 启动程序.bat

📧 邮件通知配置：
1. 在 config.ini 中设置 enable_email = true
2. 配置 QQ 邮箱 SMTP 信息
3. 获取 QQ 邮箱授权码填入 sender_password

⏰ 定时签到：
- 默认每天 09:00 自动签到
- 可在 config.ini 中修改 sign_time

💡 命令行参数：
--test      运行测试
--sign      立即签到  
--schedule  定时签到
--config    显示配置
--help      显示帮助

❓ 问题解决：
1. 首次运行可能需要下载 Chrome 驱动
2. 如遇到验证码，程序会等待手动处理
3. 查看日志文件了解详细运行情况

版本：v1.0.0
更新：2025-08-27
"""
    
    with open(portable_dir / "使用说明.txt", 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("✅ 便携版本创建成功: 理想论坛签到器便携版/")
    return True

def main():
    """主函数"""
    print_banner()
    
    print("🚀 开始打包理想论坛自动签到程序（命令行版本）...")
    print(f"📅 打包时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 1. 检查依赖
    if not check_dependencies():
        print("❌ 依赖检查失败，退出打包")
        return False
    
    # 2. 构建可执行文件
    if not build_cli_executable():
        print("❌ 可执行文件构建失败，退出打包")
        return False
    
    # 3. 创建便携版本
    if not create_portable_package():
        print("❌ 便携版本创建失败")
        return False
    
    print()
    print("🎉 打包完成！生成的文件:")
    print("  📁 理想论坛签到器便携版/        - 便携版本")
    print("  📄 理想论坛签到器.exe           - 单文件可执行程序")
    print("  📄 启动程序.bat                - 带菜单启动脚本")
    print("  📄 快速签到.bat                - 快速签到脚本")
    print("  📄 定时签到.bat                - 定时签到脚本")
    print()
    print("💡 使用说明:")
    print("  1. 首次使用：编辑 config.ini 配置用户名密码")
    print("  2. 快速签到：双击 快速签到.bat")
    print("  3. 定时签到：双击 定时签到.bat")
    print("  4. 程序菜单：双击 启动程序.bat")
    
    return True

if __name__ == "__main__":
    success = main()
    input("\\n按回车键退出...")
    sys.exit(0 if success else 1)
