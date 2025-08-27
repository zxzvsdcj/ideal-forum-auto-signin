#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
理想论坛自动签到程序GUI版本打包脚本
功能：将程序打包成带GUI界面的可执行文件
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
    ║    理想论坛自动签到程序GUI版本打包     ║
    ║       Ideal Forum GUI Packager       ║
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
    except ImportError:
        print("❌ PyInstaller未安装")
        print("📦 正在安装PyInstaller...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
            print("✅ PyInstaller安装成功")
        except subprocess.CalledProcessError:
            print("❌ PyInstaller安装失败")
            return False
    
    # 检查图标文件
    if not Path("app_icon.ico").exists():
        print("⚠️ 图标文件不存在，创建默认图标...")
        try:
            subprocess.run([sys.executable, "create_icon.py"], check=True)
        except:
            print("❌ 无法创建图标文件")
    
    return True

def build_gui_executable():
    """构建GUI可执行文件"""
    print("🔨 开始构建GUI可执行文件...")
    
    try:
        # 构建命令
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",                    # 打包成单文件
            "--windowed",                   # 窗口程序（无控制台）
            "--name=理想论坛签到器",          # 程序名称
            "--icon=app_icon.ico",          # 图标文件
            "--add-data=config.ini;.",      # 添加配置文件
            "--add-data=app_icon.ico;.",    # 添加图标文件
            
            # 排除不需要的模块
            "--exclude-module=PyQt5",
            "--exclude-module=PySide2",
            "--exclude-module=PySide6",
            "--exclude-module=tkinter",
            "--exclude-module=matplotlib",
            "--exclude-module=numpy",
            "--exclude-module=pandas",
            
            # 隐式导入
            "--hidden-import=selenium",
            "--hidden-import=webdriver_manager",
            "--hidden-import=loguru",
            "--hidden-import=schedule",
            "--hidden-import=configparser",
            "--hidden-import=PyQt6",
            "--hidden-import=PyQt6.QtCore",
            "--hidden-import=PyQt6.QtWidgets",
            "--hidden-import=PyQt6.QtGui",
            
            # 启动文件
            "gui_launcher.py"
        ]
        
        print("⚙️ 执行打包命令...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ GUI可执行文件构建成功")
            return True
        else:
            print("❌ 构建失败:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ 构建过程中发生错误: {e}")
        return False

def create_gui_portable_package():
    """创建GUI便携版本"""
    print("📦 创建GUI便携版本...")
    
    exe_file = Path("dist/理想论坛签到器.exe")
    if not exe_file.exists():
        print("❌ GUI可执行文件不存在")
        return False
    
    # 创建便携版目录
    portable_dir = Path("理想论坛签到器GUI便携版")
    if portable_dir.exists():
        shutil.rmtree(portable_dir)
    
    portable_dir.mkdir()
    
    # 复制可执行文件
    shutil.copy2(exe_file, portable_dir / "理想论坛签到器.exe")
    
    # 复制配置文件
    shutil.copy2("config.ini", portable_dir / "config.ini")
    
    # 复制图标文件
    if Path("app_icon.ico").exists():
        shutil.copy2("app_icon.ico", portable_dir / "app_icon.ico")
    if Path("app_icon.png").exists():
        shutil.copy2("app_icon.png", portable_dir / "app_icon.png")
    
    # 创建启动脚本
    start_gui_bat = """@echo off
chcp 65001 >nul
title 理想论坛自动签到程序
echo.
echo ╔═══════════════════════════════════════╗
echo ║        理想论坛自动签到程序           ║
echo ║     Ideal Forum Auto Sign-in Bot      ║
echo ║                                       ║
echo ║        GUI版本 v1.0.0                 ║
echo ╚═══════════════════════════════════════╝
echo.
echo 正在启动GUI界面...
echo.
start "" "理想论坛签到器.exe"
echo.
echo GUI界面已启动，如需帮助请查看使用说明文档。
timeout /t 3 >nul
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
    
    config_bat = """@echo off
chcp 65001 >nul
title 编辑配置文件
echo 正在打开配置文件编辑器...
notepad.exe config.ini
"""
    
    # 写入批处理文件
    with open(portable_dir / "启动GUI界面.bat", 'w', encoding='gbk') as f:
        f.write(start_gui_bat)
    
    with open(portable_dir / "快速签到.bat", 'w', encoding='gbk') as f:
        f.write(quick_sign_bat)
    
    with open(portable_dir / "编辑配置.bat", 'w', encoding='gbk') as f:
        f.write(config_bat)
    
    # 创建使用说明
    readme_content = """理想论坛自动签到程序 - GUI便携版
====================================

🖥️ GUI版本特性：
- 炫酷的图形界面，操作简单直观
- 实时状态显示和日志查看
- 可视化配置管理
- 一键签到和定时任务设置

📁 文件说明：
- 理想论坛签到器.exe     主程序（GUI版本）
- config.ini            配置文件
- app_icon.ico          程序图标
- 启动GUI界面.bat       启动图形界面
- 快速签到.bat          命令行快速签到
- 编辑配置.bat          编辑配置文件

🚀 使用方法：
1. 首次使用：双击"编辑配置.bat"修改用户名和密码
2. 启动GUI：双击"启动GUI界面.bat"
3. 快速签到：双击"快速签到.bat"

💡 GUI界面功能：
- 登录测试：验证账号密码
- 立即签到：执行一次签到
- 定时任务：设置每日自动签到
- 邮件配置：设置签到结果通知
- 日志查看：查看详细运行日志

⚙️ 配置说明：
在config.ini中设置：
- [LOGIN] 部分：用户名和密码
- [SCHEDULE] 部分：签到时间设置
- [EMAIL] 部分：邮件通知配置

🔧 故障排除：
1. 程序启动失败：检查是否安装了必要的运行库
2. 登录失败：确认用户名密码正确
3. GUI无响应：尝试以管理员身份运行

版本：v1.0.0 GUI版
更新：2025-08-27
特色：炫酷GUI界面 + 智能签到 + 邮件通知
"""
    
    with open(portable_dir / "使用说明.txt", 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("✅ GUI便携版本创建成功: 理想论坛签到器GUI便携版/")
    return True

def main():
    """主函数"""
    print_banner()
    
    print("🚀 开始打包理想论坛自动签到程序GUI版本...")
    print(f"📅 打包时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 1. 检查依赖
    if not check_dependencies():
        print("❌ 依赖检查失败，退出打包")
        return False
    
    # 2. 构建GUI可执行文件
    if not build_gui_executable():
        print("❌ GUI可执行文件构建失败，退出打包")
        return False
    
    # 3. 创建便携版本
    if not create_gui_portable_package():
        print("❌ GUI便携版本创建失败")
        return False
    
    print()
    print("🎉 GUI版本打包完成！生成的文件:")
    print("  📁 理想论坛签到器GUI便携版/       - 完整GUI便携版")
    print("  🖥️ 理想论坛签到器.exe            - GUI主程序")
    print("  🎨 app_icon.ico                 - 炫酷程序图标")
    print("  📋 启动GUI界面.bat              - GUI启动脚本")
    print("  ⚡ 快速签到.bat                 - 快速签到脚本")
    print("  ⚙️ 编辑配置.bat                 - 配置编辑脚本")
    print()
    print("💡 使用说明:")
    print("  1. 首次使用：双击 编辑配置.bat 设置用户名密码")
    print("  2. 启动GUI：双击 启动GUI界面.bat")
    print("  3. 程序特色：炫酷GUI界面 + 程序图标 + 智能签到")
    print("  4. 直接运行：双击 理想论坛签到器.exe")
    
    return True

if __name__ == "__main__":
    success = main()
    input("\n按回车键退出...")
    sys.exit(0 if success else 1)
