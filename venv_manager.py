#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
虚拟环境管理器
功能：检查、创建和管理项目虚拟环境
"""

import os
import sys
import subprocess
import venv
from pathlib import Path
from loguru import logger


class VirtualEnvironmentManager:
    """虚拟环境管理器"""
    
    def __init__(self, project_dir=None):
        """
        初始化虚拟环境管理器
        
        Args:
            project_dir: 项目目录路径，默认为当前目录
        """
        self.project_dir = Path(project_dir) if project_dir else Path.cwd()
        self.venv_dir = self.project_dir / ".venv"
        self.venv_name = ".venv"
        
        # 虚拟环境中的Python路径
        if sys.platform == "win32":
            self.venv_python = self.venv_dir / "Scripts" / "python.exe"
            self.venv_pip = self.venv_dir / "Scripts" / "pip.exe"
            self.activate_script = self.venv_dir / "Scripts" / "activate.bat"
        else:
            self.venv_python = self.venv_dir / "bin" / "python"
            self.venv_pip = self.venv_dir / "bin" / "pip"
            self.activate_script = self.venv_dir / "bin" / "activate"
        
        logger.info(f"虚拟环境管理器初始化完成，项目目录: {self.project_dir}")
    
    def check_venv_exists(self):
        """
        检查虚拟环境是否存在
        
        Returns:
            bool: 虚拟环境是否存在
        """
        venv_exists = self.venv_dir.exists() and self.venv_python.exists()
        
        if venv_exists:
            logger.info("✅ 虚拟环境已存在")
        else:
            logger.warning("❌ 虚拟环境不存在")
        
        return venv_exists
    
    def is_venv_active(self):
        """
        检查是否在虚拟环境中运行
        
        Returns:
            bool: 是否在虚拟环境中
        """
        # 检查VIRTUAL_ENV环境变量
        virtual_env = os.environ.get('VIRTUAL_ENV')
        if virtual_env:
            active_venv = Path(virtual_env)
            if active_venv == self.venv_dir:
                logger.info("✅ 当前在项目虚拟环境中运行")
                return True
            else:
                logger.warning(f"⚠️ 当前在其他虚拟环境中运行: {virtual_env}")
                return False
        
        # 检查sys.prefix和sys.base_prefix
        if sys.prefix != sys.base_prefix:
            logger.warning("⚠️ 当前在虚拟环境中，但不是项目虚拟环境")
            return False
        
        logger.warning("❌ 当前不在虚拟环境中")
        return False
    
    def create_venv(self):
        """
        创建虚拟环境
        
        Returns:
            bool: 创建是否成功
        """
        try:
            logger.info("🔧 开始创建虚拟环境...")
            
            # 如果虚拟环境已存在，先删除
            if self.venv_dir.exists():
                logger.info("删除现有虚拟环境...")
                import shutil
                shutil.rmtree(self.venv_dir)
            
            # 创建虚拟环境
            logger.info(f"创建虚拟环境: {self.venv_dir}")
            venv.create(self.venv_dir, with_pip=True, clear=True)
            
            # 验证创建结果
            if self.check_venv_exists():
                logger.success("✅ 虚拟环境创建成功")
                return True
            else:
                logger.error("❌ 虚拟环境创建失败")
                return False
                
        except Exception as e:
            logger.error(f"❌ 创建虚拟环境时发生错误: {e}")
            return False
    
    def install_requirements(self, requirements_file="requirements.txt"):
        """
        在虚拟环境中安装依赖包
        
        Args:
            requirements_file: 依赖文件路径
            
        Returns:
            bool: 安装是否成功
        """
        requirements_path = self.project_dir / requirements_file
        
        if not requirements_path.exists():
            logger.error(f"❌ 依赖文件不存在: {requirements_path}")
            return False
        
        if not self.check_venv_exists():
            logger.error("❌ 虚拟环境不存在，无法安装依赖")
            return False
        
        try:
            logger.info("📦 开始安装依赖包...")
            
            # 升级pip
            logger.info("升级pip...")
            subprocess.run([
                str(self.venv_python), "-m", "pip", "install", "--upgrade", "pip"
            ], check=True, capture_output=True, text=True)
            
            # 安装依赖
            logger.info(f"安装依赖文件: {requirements_file}")
            result = subprocess.run([
                str(self.venv_python), "-m", "pip", "install", "-r", str(requirements_path)
            ], check=True, capture_output=True, text=True)
            
            logger.success("✅ 依赖包安装成功")
            logger.info(f"安装日志:\n{result.stdout}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ 安装依赖包失败: {e}")
            logger.error(f"错误输出: {e.stderr}")
            return False
        except Exception as e:
            logger.error(f"❌ 安装依赖包时发生未知错误: {e}")
            return False
    
    def get_activate_command(self):
        """
        获取激活虚拟环境的命令
        
        Returns:
            str: 激活命令
        """
        if sys.platform == "win32":
            return f"{self.activate_script}"
        else:
            return f"source {self.activate_script}"
    
    def run_in_venv(self, command, shell=False):
        """
        在虚拟环境中运行命令
        
        Args:
            command: 要运行的命令（列表或字符串）
            shell: 是否使用shell运行
            
        Returns:
            subprocess.CompletedProcess: 运行结果
        """
        if not self.check_venv_exists():
            raise RuntimeError("虚拟环境不存在")
        
        if isinstance(command, str):
            if sys.platform == "win32":
                # Windows下需要特殊处理
                full_command = f'"{self.activate_script}" && {command}'
                return subprocess.run(full_command, shell=True, capture_output=True, text=True)
            else:
                full_command = f"source {self.activate_script} && {command}"
                return subprocess.run(full_command, shell=True, capture_output=True, text=True)
        else:
            # 列表形式的命令，直接使用虚拟环境的Python
            if command[0] == "python":
                command[0] = str(self.venv_python)
            elif command[0] == "pip":
                command = [str(self.venv_python), "-m", "pip"] + command[1:]
            
            return subprocess.run(command, shell=shell, capture_output=True, text=True)
    
    def get_venv_info(self):
        """
        获取虚拟环境信息
        
        Returns:
            dict: 虚拟环境信息
        """
        info = {
            "exists": self.check_venv_exists(),
            "active": self.is_venv_active(),
            "path": str(self.venv_dir),
            "python_path": str(self.venv_python),
            "pip_path": str(self.venv_pip),
            "activate_command": self.get_activate_command()
        }
        
        if info["exists"]:
            try:
                # 获取Python版本
                result = subprocess.run([
                    str(self.venv_python), "--version"
                ], capture_output=True, text=True)
                info["python_version"] = result.stdout.strip()
                
                # 获取pip版本
                result = subprocess.run([
                    str(self.venv_python), "-m", "pip", "--version"
                ], capture_output=True, text=True)
                info["pip_version"] = result.stdout.strip()
                
                # 获取已安装的包列表
                result = subprocess.run([
                    str(self.venv_python), "-m", "pip", "list", "--format=freeze"
                ], capture_output=True, text=True)
                info["installed_packages"] = result.stdout.strip().split('\n')
                
            except Exception as e:
                logger.warning(f"获取虚拟环境详细信息时发生错误: {e}")
        
        return info
    
    def setup_project_venv(self, force_recreate=False):
        """
        设置项目虚拟环境（完整流程）
        
        Args:
            force_recreate: 是否强制重新创建虚拟环境
            
        Returns:
            bool: 设置是否成功
        """
        logger.info("🚀 开始设置项目虚拟环境...")
        
        # 检查是否需要创建虚拟环境
        if force_recreate or not self.check_venv_exists():
            if not self.create_venv():
                return False
        
        # 安装依赖包
        if not self.install_requirements():
            return False
        
        # 显示虚拟环境信息
        info = self.get_venv_info()
        logger.info("📋 虚拟环境信息:")
        logger.info(f"  路径: {info['path']}")
        logger.info(f"  Python版本: {info.get('python_version', '未知')}")
        logger.info(f"  激活命令: {info['activate_command']}")
        
        if not self.is_venv_active():
            logger.warning("⚠️ 当前不在虚拟环境中运行")
            logger.info("💡 请使用以下命令激活虚拟环境:")
            logger.info(f"  {info['activate_command']}")
        
        logger.success("✅ 虚拟环境设置完成")
        return True
    
    def validate_environment(self):
        """
        验证环境配置
        
        Returns:
            dict: 验证结果
        """
        validation = {
            "venv_exists": False,
            "venv_active": False,
            "requirements_installed": False,
            "python_version_ok": False,
            "issues": [],
            "recommendations": []
        }
        
        # 检查虚拟环境是否存在
        validation["venv_exists"] = self.check_venv_exists()
        if not validation["venv_exists"]:
            validation["issues"].append("虚拟环境不存在")
            validation["recommendations"].append("运行 python venv_manager.py --setup 创建虚拟环境")
        
        # 检查是否在虚拟环境中运行
        validation["venv_active"] = self.is_venv_active()
        if not validation["venv_active"]:
            validation["issues"].append("当前不在虚拟环境中运行")
            validation["recommendations"].append(f"运行 {self.get_activate_command()}")
        
        # 检查Python版本
        try:
            if validation["venv_exists"]:
                result = subprocess.run([
                    str(self.venv_python), "-c", 
                    "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
                ], capture_output=True, text=True)
                
                python_version = result.stdout.strip()
                major, minor = map(int, python_version.split('.'))
                validation["python_version_ok"] = major >= 3 and minor >= 7
                
                if not validation["python_version_ok"]:
                    validation["issues"].append(f"Python版本过低: {python_version}")
                    validation["recommendations"].append("升级到Python 3.7+")
        except:
            validation["issues"].append("无法检查Python版本")
        
        # 检查依赖包是否安装
        requirements_file = self.project_dir / "requirements.txt"
        if requirements_file.exists() and validation["venv_exists"]:
            try:
                with open(requirements_file, 'r', encoding='utf-8') as f:
                    required_packages = [line.strip().split('==')[0] for line in f 
                                       if line.strip() and not line.startswith('#')]
                
                result = subprocess.run([
                    str(self.venv_python), "-m", "pip", "list", "--format=freeze"
                ], capture_output=True, text=True)
                
                installed_packages = [line.split('==')[0] for line in result.stdout.strip().split('\n')]
                
                missing_packages = [pkg for pkg in required_packages if pkg not in installed_packages]
                validation["requirements_installed"] = len(missing_packages) == 0
                
                if missing_packages:
                    validation["issues"].append(f"缺少依赖包: {', '.join(missing_packages)}")
                    validation["recommendations"].append("运行 pip install -r requirements.txt")
                
            except Exception as e:
                validation["issues"].append(f"检查依赖包时发生错误: {e}")
        
        return validation


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='虚拟环境管理器')
    parser.add_argument('--setup', action='store_true', help='设置项目虚拟环境')
    parser.add_argument('--check', action='store_true', help='检查虚拟环境状态')
    parser.add_argument('--validate', action='store_true', help='验证环境配置')
    parser.add_argument('--info', action='store_true', help='显示虚拟环境信息')
    parser.add_argument('--force', action='store_true', help='强制重新创建虚拟环境')
    
    args = parser.parse_args()
    
    # 创建虚拟环境管理器
    venv_manager = VirtualEnvironmentManager()
    
    if args.setup:
        # 设置虚拟环境
        print("🔧 设置项目虚拟环境...")
        success = venv_manager.setup_project_venv(force_recreate=args.force)
        sys.exit(0 if success else 1)
    
    elif args.check:
        # 检查虚拟环境状态
        print("🔍 检查虚拟环境状态...")
        exists = venv_manager.check_venv_exists()
        active = venv_manager.is_venv_active()
        
        print(f"虚拟环境存在: {'✅' if exists else '❌'}")
        print(f"虚拟环境激活: {'✅' if active else '❌'}")
        
        if not active and exists:
            print(f"💡 激活命令: {venv_manager.get_activate_command()}")
    
    elif args.validate:
        # 验证环境配置
        print("🧪 验证环境配置...")
        validation = venv_manager.validate_environment()
        
        print("\n📊 验证结果:")
        for key, value in validation.items():
            if key not in ['issues', 'recommendations']:
                status = "✅" if value else "❌"
                print(f"  {key}: {status}")
        
        if validation['issues']:
            print("\n⚠️ 发现问题:")
            for issue in validation['issues']:
                print(f"  - {issue}")
        
        if validation['recommendations']:
            print("\n💡 建议:")
            for rec in validation['recommendations']:
                print(f"  - {rec}")
    
    elif args.info:
        # 显示虚拟环境信息
        print("📋 虚拟环境信息:")
        info = venv_manager.get_venv_info()
        
        for key, value in info.items():
            if key == 'installed_packages':
                print(f"  {key}: {len(value)} 个包")
            elif isinstance(value, list):
                print(f"  {key}: {len(value)} 项")
            else:
                print(f"  {key}: {value}")
    
    else:
        # 默认显示帮助
        parser.print_help()
        print("\n💡 使用示例:")
        print("  python venv_manager.py --setup     # 设置虚拟环境")
        print("  python venv_manager.py --check     # 检查状态")
        print("  python venv_manager.py --validate  # 验证配置")
        print("  python venv_manager.py --info      # 显示信息")


if __name__ == "__main__":
    main()
