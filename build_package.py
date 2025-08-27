#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
理想论坛自动签到程序打包脚本
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
    ║      理想论坛自动签到程序打包工具     ║
    ║     Ideal Forum Sign-in Bot Packager ║
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

def create_spec_file():
    """创建PyInstaller规范文件"""
    print("📝 创建打包规范文件...")
    
    spec_content = """# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# GUI应用程序
gui_a = Analysis(
    ['gui_main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config.ini', '.'),
        ('README.md', '.'),
        ('requirements.txt', '.'),
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtWidgets', 
        'PyQt6.QtGui',
        'selenium',
        'webdriver_manager',
        'loguru',
        'schedule',
        'configparser',
        'email.mime.text',
        'email.mime.multipart',
        'smtplib',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PyQt5', 'PySide2', 'PySide6', 'tkinter'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

gui_pyz = PYZ(gui_a.pure, gui_a.zipped_data, cipher=block_cipher)

gui_exe = EXE(
    gui_pyz,
    gui_a.scripts,
    [],
    exclude_binaries=True,
    name='理想论坛自动签到程序',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

# 命令行应用程序  
cli_a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config.ini', '.'),
        ('README.md', '.'),
        ('requirements.txt', '.'),
    ],
    hiddenimports=[
        'selenium',
        'webdriver_manager',
        'loguru',
        'schedule',
        'configparser',
        'email.mime.text',
        'email.mime.multipart',
        'smtplib',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PyQt5', 'PyQt6', 'PySide2', 'PySide6', 'tkinter'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

cli_pyz = PYZ(cli_a.pure, cli_a.zipped_data, cipher=block_cipher)

cli_exe = EXE(
    cli_pyz,
    cli_a.scripts,
    [],
    exclude_binaries=True,
    name='理想论坛签到器命令行版',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# 打包目录
coll = COLLECT(
    gui_exe,
    gui_a.binaries,
    gui_a.zipfiles,
    gui_a.datas,
    cli_exe,
    cli_a.binaries,
    cli_a.zipfiles,
    cli_a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='理想论坛自动签到程序'
)
"""
    
    with open('app.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ 规范文件创建成功: app.spec")

def build_executable():
    """构建可执行文件"""
    print("🔨 开始构建可执行文件...")
    
    try:
        # 使用spec文件构建
        cmd = [sys.executable, "-m", "PyInstaller", "app.spec", "--clean"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 可执行文件构建成功")
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
    
    dist_dir = Path("dist/理想论坛自动签到程序")
    if not dist_dir.exists():
        print("❌ 构建目录不存在")
        return False
    
    # 创建便携版目录
    portable_dir = Path("便携版")
    if portable_dir.exists():
        shutil.rmtree(portable_dir)
    
    portable_dir.mkdir()
    
    # 复制程序文件
    shutil.copytree(dist_dir, portable_dir / "程序文件")
    
    # 创建启动脚本
    start_gui_bat = """@echo off
chcp 65001 >nul
title 理想论坛自动签到程序
cd /d "%~dp0程序文件"
start "" "理想论坛自动签到程序.exe"
"""
    
    start_cli_bat = """@echo off
chcp 65001 >nul
title 理想论坛签到器命令行版
cd /d "%~dp0程序文件"
"理想论坛签到器命令行版.exe"
pause
"""
    
    with open(portable_dir / "启动GUI版本.bat", 'w', encoding='gbk') as f:
        f.write(start_gui_bat)
    
    with open(portable_dir / "启动命令行版本.bat", 'w', encoding='gbk') as f:
        f.write(start_cli_bat)
    
    # 复制说明文件
    files_to_copy = ['config.ini', 'README.md', 'requirements.txt']
    for file in files_to_copy:
        if Path(file).exists():
            shutil.copy2(file, portable_dir)
    
    print("✅ 便携版本创建成功: 便携版/")
    return True

def create_installer():
    """创建安装包脚本"""
    print("📝 创建安装包脚本...")
    
    nsis_script = f"""
; 理想论坛自动签到程序安装脚本
!include "MUI2.nsh"

; 程序信息
Name "理想论坛自动签到程序"
OutFile "理想论坛自动签到程序安装包.exe"
InstallDir "$PROGRAMFILES\\理想论坛自动签到程序"
RequestExecutionLevel admin

; 界面设置
!define MUI_ABORTWARNING
!define MUI_ICON "${{NSISDIR}}\\Contrib\\Graphics\\Icons\\modern-install.ico"

; 安装页面
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; 卸载页面
!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; 语言
!insertmacro MUI_LANGUAGE "SimpChinese"

; 安装部分
Section "主程序" SecMain
    SetOutPath "$INSTDIR"
    File /r "dist\\理想论坛自动签到程序\\*.*"
    
    ; 创建快捷方式
    CreateDirectory "$SMPROGRAMS\\理想论坛自动签到程序"
    CreateShortcut "$SMPROGRAMS\\理想论坛自动签到程序\\理想论坛自动签到程序.lnk" "$INSTDIR\\理想论坛自动签到程序.exe"
    CreateShortcut "$SMPROGRAMS\\理想论坛自动签到程序\\命令行版本.lnk" "$INSTDIR\\理想论坛签到器命令行版.exe"
    CreateShortcut "$SMPROGRAMS\\理想论坛自动签到程序\\卸载.lnk" "$INSTDIR\\uninstall.exe"
    
    CreateShortcut "$DESKTOP\\理想论坛自动签到程序.lnk" "$INSTDIR\\理想论坛自动签到程序.exe"
    
    ; 写入卸载信息
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\理想论坛自动签到程序" "DisplayName" "理想论坛自动签到程序"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\理想论坛自动签到程序" "UninstallString" "$INSTDIR\\uninstall.exe"
    WriteUninstaller "$INSTDIR\\uninstall.exe"
SectionEnd

; 卸载部分
Section "Uninstall"
    Delete "$INSTDIR\\*.*"
    RMDir /r "$INSTDIR"
    
    Delete "$SMPROGRAMS\\理想论坛自动签到程序\\*.*"
    RMDir "$SMPROGRAMS\\理想论坛自动签到程序"
    
    Delete "$DESKTOP\\理想论坛自动签到程序.lnk"
    
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\理想论坛自动签到程序"
SectionEnd
"""
    
    with open('installer.nsi', 'w', encoding='utf-8') as f:
        f.write(nsis_script)
    
    print("✅ 安装包脚本创建成功: installer.nsi")
    print("💡 如需创建安装包，请安装NSIS并运行: makensis installer.nsi")

def main():
    """主函数"""
    print_banner()
    
    print("🚀 开始打包理想论坛自动签到程序...")
    print(f"📅 打包时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 1. 检查依赖
    if not check_dependencies():
        print("❌ 依赖检查失败，退出打包")
        return False
    
    # 2. 创建规范文件
    create_spec_file()
    
    # 3. 构建可执行文件
    if not build_executable():
        print("❌ 可执行文件构建失败，退出打包")
        return False
    
    # 4. 创建便携版本
    if not create_portable_package():
        print("❌ 便携版本创建失败")
        return False
    
    # 5. 创建安装包脚本
    create_installer()
    
    print()
    print("🎉 打包完成！生成的文件:")
    print("  📁 dist/理想论坛自动签到程序/  - 程序文件目录")
    print("  📁 便携版/                    - 便携版本")
    print("  📄 installer.nsi             - 安装包脚本")
    print()
    print("💡 使用说明:")
    print("  1. 便携版本：解压后直接运行启动脚本")
    print("  2. 安装版本：使用NSIS编译installer.nsi")
    print("  3. 配置文件：首次运行需要编辑config.ini")
    
    return True

if __name__ == "__main__":
    success = main()
    input("\\n按回车键退出...")
    sys.exit(0 if success else 1)
