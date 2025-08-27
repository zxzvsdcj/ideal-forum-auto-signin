#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能启动器
功能：自动检查和管理虚拟环境，然后启动应用程序
"""

import os
import sys
import subprocess
from pathlib import Path
from venv_manager import VirtualEnvironmentManager
from git_manager import GitManager
from loguru import logger


class SmartLauncher:
    """智能启动器"""
    
    def __init__(self):
        """初始化启动器"""
        self.project_dir = Path.cwd()
        self.venv_manager = VirtualEnvironmentManager(self.project_dir)
        self.git_manager = GitManager(self.project_dir)
        
        logger.info("智能启动器初始化完成")
    
    def check_and_setup_environment(self):
        """检查并设置环境"""
        logger.info("🔧 检查和设置运行环境...")
        
        # 1. 检查虚拟环境
        if not self.venv_manager.check_venv_exists():
            logger.warning("虚拟环境不存在，开始创建...")
            if not self.venv_manager.setup_project_venv():
                logger.error("虚拟环境设置失败")
                return False
        else:
            logger.info("✅ 虚拟环境已存在")
        
        # 2. 检查是否在虚拟环境中运行
        if not self.venv_manager.is_venv_active():
            logger.warning("当前不在虚拟环境中运行")
            logger.info("尝试在虚拟环境中重新启动...")
            return self.restart_in_venv()
        else:
            logger.info("✅ 当前在虚拟环境中运行")
        
        # 3. 验证环境配置
        validation = self.venv_manager.validate_environment()
        if validation['issues']:
            logger.warning("环境验证发现问题:")
            for issue in validation['issues']:
                logger.warning(f"  - {issue}")
            
            # 尝试修复
            if not validation['requirements_installed']:
                logger.info("尝试安装缺失的依赖包...")
                self.venv_manager.install_requirements()
        
        return True
    
    def restart_in_venv(self):
        """在虚拟环境中重新启动"""
        if not self.venv_manager.check_venv_exists():
            logger.error("虚拟环境不存在，无法重新启动")
            return False
        
        try:
            # 构建在虚拟环境中运行的命令
            current_script = sys.argv[0]
            script_args = sys.argv[1:]
            
            if sys.platform == "win32":
                # Windows
                activate_script = self.venv_manager.venv_dir / "Scripts" / "activate.bat"
                command = f'"{activate_script}" && python "{current_script}" {" ".join(script_args)}'
                
                logger.info("在虚拟环境中重新启动程序...")
                subprocess.run(command, shell=True)
            else:
                # Unix/Linux/macOS
                activate_script = self.venv_manager.venv_dir / "bin" / "activate"
                command = f'source "{activate_script}" && python "{current_script}" {" ".join(script_args)}'
                
                logger.info("在虚拟环境中重新启动程序...")
                subprocess.run(command, shell=True, executable='/bin/bash')
            
            return False  # 返回False表示已重新启动，当前进程应退出
            
        except Exception as e:
            logger.error(f"在虚拟环境中重新启动失败: {e}")
            return False
    
    def auto_git_commit(self):
        """自动Git提交"""
        try:
            logger.info("🔄 检查Git状态...")
            
            if not self.git_manager.is_git_repo():
                logger.info("初始化Git仓库...")
                self.git_manager.init_git_repo()
            
            status = self.git_manager.get_status()
            if not status.get("clean", True):
                logger.info("发现未提交的更改，执行自动提交...")
                success = self.git_manager.commit_changes()
                
                if success:
                    logger.success("✅ 自动Git提交完成")
                    
                    # 尝试推送到远程（如果配置了）
                    remote_info = self.git_manager.get_remote_info()
                    if not remote_info.get("error") and remote_info.get("remotes"):
                        logger.info("推送到远程仓库...")
                        self.git_manager.push_to_remote()
                else:
                    logger.warning("自动Git提交失败")
            else:
                logger.info("Git仓库状态干净，无需提交")
                
        except Exception as e:
            logger.warning(f"自动Git提交时发生错误: {e}")
    
    def launch_application(self, app_type="gui"):
        """启动应用程序"""
        logger.info(f"🚀 启动应用程序: {app_type}")
        
        try:
            if app_type == "gui":
                # 启动GUI界面
                from gui_main import main as gui_main
                gui_main()
            
            elif app_type == "cli":
                # 启动命令行界面
                from run import main as cli_main
                cli_main()
            
            elif app_type == "sign":
                # 直接执行签到
                from sign_bot import main as sign_main
                sign_main()
            
            elif app_type == "schedule":
                # 启动调度器
                from scheduler import main as scheduler_main
                scheduler_main()
            
            else:
                logger.error(f"未知的应用程序类型: {app_type}")
                return False
            
            return True
            
        except ImportError as e:
            logger.error(f"导入应用程序模块失败: {e}")
            logger.info("可能需要安装依赖包，尝试安装...")
            
            if self.venv_manager.install_requirements():
                logger.info("依赖包安装完成，请重新运行程序")
            
            return False
        except Exception as e:
            logger.error(f"启动应用程序失败: {e}")
            return False
    
    def smart_launch(self, app_type="gui", auto_commit=True):
        """智能启动流程"""
        logger.info("🎯 理想论坛自动签到程序 - 智能启动器")
        logger.info("=" * 50)
        
        # 1. 检查和设置环境
        if not self.check_and_setup_environment():
            logger.error("环境设置失败，程序退出")
            return False
        
        # 2. 自动Git提交（可选）
        if auto_commit:
            self.auto_git_commit()
        
        # 3. 启动应用程序
        success = self.launch_application(app_type)
        
        if success:
            logger.success("✅ 程序启动成功")
        else:
            logger.error("❌ 程序启动失败")
        
        return success


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='理想论坛自动签到程序 - 智能启动器')
    parser.add_argument('--app', choices=['gui', 'cli', 'sign', 'schedule'], 
                       default='gui', help='选择启动的应用程序类型')
    parser.add_argument('--no-commit', action='store_true', help='跳过自动Git提交')
    parser.add_argument('--setup-only', action='store_true', help='仅设置环境，不启动应用')
    parser.add_argument('--check-env', action='store_true', help='检查环境状态')
    
    args = parser.parse_args()
    
    # 创建智能启动器
    launcher = SmartLauncher()
    
    if args.check_env:
        # 检查环境状态
        print("🔍 检查环境状态...")
        
        # 检查虚拟环境
        venv_info = launcher.venv_manager.get_venv_info()
        print(f"虚拟环境存在: {'✅' if venv_info['exists'] else '❌'}")
        print(f"虚拟环境激活: {'✅' if venv_info['active'] else '❌'}")
        
        if venv_info['exists']:
            print(f"Python版本: {venv_info.get('python_version', '未知')}")
            print(f"已安装包数: {len(venv_info.get('installed_packages', []))}")
        
        # 检查Git状态
        git_status = launcher.git_manager.get_status()
        if not git_status.get('error'):
            print(f"Git仓库状态: {'✅ 干净' if git_status.get('clean') else '⚠️ 有更改'}")
            print(f"未提交更改: {git_status.get('total_changes', 0)}个")
        
        return
    
    elif args.setup_only:
        # 仅设置环境
        print("🔧 设置运行环境...")
        success = launcher.check_and_setup_environment()
        sys.exit(0 if success else 1)
    
    else:
        # 智能启动
        success = launcher.smart_launch(
            app_type=args.app,
            auto_commit=not args.no_commit
        )
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
