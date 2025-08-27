#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能Git管理器
功能：自动Git提交和GitHub远程同步
"""

import os
import subprocess
import json
from datetime import datetime
from pathlib import Path
from loguru import logger
import configparser


class GitManager:
    """Git管理器"""
    
    def __init__(self, project_dir=None):
        """
        初始化Git管理器
        
        Args:
            project_dir: 项目目录路径，默认为当前目录
        """
        self.project_dir = Path(project_dir) if project_dir else Path.cwd()
        self.git_dir = self.project_dir / ".git"
        self.config_file = self.project_dir / "config.ini"
        
        logger.info(f"Git管理器初始化完成，项目目录: {self.project_dir}")
    
    def is_git_repo(self):
        """
        检查是否为Git仓库
        
        Returns:
            bool: 是否为Git仓库
        """
        is_repo = self.git_dir.exists() and self.git_dir.is_dir()
        
        if is_repo:
            logger.info("✅ 当前目录是Git仓库")
        else:
            logger.warning("❌ 当前目录不是Git仓库")
        
        return is_repo
    
    def init_git_repo(self):
        """
        初始化Git仓库
        
        Returns:
            bool: 初始化是否成功
        """
        try:
            if self.is_git_repo():
                logger.info("Git仓库已存在，跳过初始化")
                return True
            
            logger.info("🔧 初始化Git仓库...")
            result = subprocess.run(
                ["git", "init"], 
                cwd=self.project_dir, 
                capture_output=True, 
                text=True
            )
            
            if result.returncode == 0:
                logger.success("✅ Git仓库初始化成功")
                
                # 设置基本配置
                self._setup_git_config()
                
                # 创建.gitignore文件
                self._create_gitignore()
                
                return True
            else:
                logger.error(f"❌ Git仓库初始化失败: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 初始化Git仓库时发生错误: {e}")
            return False
    
    def _setup_git_config(self):
        """设置Git基本配置"""
        try:
            # 设置用户名和邮箱（如果未设置）
            result = subprocess.run(
                ["git", "config", "user.name"], 
                cwd=self.project_dir, 
                capture_output=True, 
                text=True
            )
            
            if result.returncode != 0:
                subprocess.run(
                    ["git", "config", "user.name", "Auto Commit Bot"],
                    cwd=self.project_dir,
                    check=True
                )
                logger.info("设置Git用户名: Auto Commit Bot")
            
            result = subprocess.run(
                ["git", "config", "user.email"], 
                cwd=self.project_dir, 
                capture_output=True, 
                text=True
            )
            
            if result.returncode != 0:
                subprocess.run(
                    ["git", "config", "user.email", "bot@autocommit.local"],
                    cwd=self.project_dir,
                    check=True
                )
                logger.info("设置Git邮箱: bot@autocommit.local")
                
        except Exception as e:
            logger.warning(f"设置Git配置时发生错误: {e}")
    
    def _create_gitignore(self):
        """创建.gitignore文件"""
        gitignore_path = self.project_dir / ".gitignore"
        
        if gitignore_path.exists():
            logger.info(".gitignore文件已存在")
            return
        
        gitignore_content = """# 日志文件
*.log
*.txt
sign_log.txt
scheduler_log.txt

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# 虚拟环境
.venv/
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# 系统文件
.DS_Store
Thumbs.db

# Chrome驱动
chromedriver*

# 临时文件
temp/
tmp/

# 敏感配置（用户可以选择是否提交config.ini）
# config.ini
"""
        
        try:
            with open(gitignore_path, 'w', encoding='utf-8') as f:
                f.write(gitignore_content)
            logger.info("✅ 创建.gitignore文件成功")
        except Exception as e:
            logger.warning(f"创建.gitignore文件失败: {e}")
    
    def get_status(self):
        """
        获取Git状态
        
        Returns:
            dict: Git状态信息
        """
        if not self.is_git_repo():
            return {"error": "不是Git仓库"}
        
        try:
            # 获取状态
            result = subprocess.run(
                ["git", "status", "--porcelain"], 
                cwd=self.project_dir, 
                capture_output=True, 
                text=True
            )
            
            if result.returncode == 0:
                status_lines = result.stdout.strip().split('\n') if result.stdout.strip() else []
                
                status_info = {
                    "clean": len(status_lines) == 0,
                    "modified_files": [],
                    "added_files": [],
                    "deleted_files": [],
                    "untracked_files": [],
                    "total_changes": len(status_lines)
                }
                
                for line in status_lines:
                    if len(line) >= 3:
                        status_code = line[:2]
                        filename = line[3:]
                        
                        if status_code.startswith('M'):
                            status_info["modified_files"].append(filename)
                        elif status_code.startswith('A'):
                            status_info["added_files"].append(filename)
                        elif status_code.startswith('D'):
                            status_info["deleted_files"].append(filename)
                        elif status_code.startswith('??'):
                            status_info["untracked_files"].append(filename)
                
                return status_info
            else:
                return {"error": f"获取状态失败: {result.stderr}"}
                
        except Exception as e:
            return {"error": f"获取Git状态时发生错误: {e}"}
    
    def add_all_changes(self):
        """
        添加所有更改到暂存区
        
        Returns:
            bool: 添加是否成功
        """
        try:
            logger.info("📝 添加所有更改到暂存区...")
            result = subprocess.run(
                ["git", "add", "."], 
                cwd=self.project_dir, 
                capture_output=True, 
                text=True
            )
            
            if result.returncode == 0:
                logger.success("✅ 所有更改已添加到暂存区")
                return True
            else:
                logger.error(f"❌ 添加更改失败: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 添加更改时发生错误: {e}")
            return False
    
    def generate_commit_message(self, changes_info=None):
        """
        生成智能提交信息
        
        Args:
            changes_info: 更改信息
            
        Returns:
            str: 提交信息
        """
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if not changes_info:
            changes_info = self.get_status()
        
        if changes_info.get("error"):
            return f"auto: 自动提交 ({current_time})"
        
        # 分析更改类型
        commit_type = "update"
        commit_scope = ""
        commit_description = ""
        
        total_changes = changes_info.get("total_changes", 0)
        modified_files = changes_info.get("modified_files", [])
        added_files = changes_info.get("added_files", [])
        deleted_files = changes_info.get("deleted_files", [])
        
        # 确定提交类型
        if len(added_files) > len(modified_files):
            commit_type = "feat"
            commit_description = "添加新功能和文件"
        elif len(deleted_files) > 0:
            commit_type = "refactor"
            commit_description = "重构代码和清理文件"
        elif any("config" in f.lower() for f in modified_files):
            commit_type = "config"
            commit_description = "更新配置文件"
        elif any(f.endswith(('.py', '.js', '.ts')) for f in modified_files):
            commit_type = "fix"
            commit_description = "修复代码和优化功能"
        elif any("README" in f or f.endswith('.md') for f in modified_files):
            commit_type = "docs"
            commit_description = "更新文档"
        
        # 确定作用域
        if any("gui" in f.lower() or "ui" in f.lower() for f in modified_files + added_files):
            commit_scope = "ui"
        elif any("email" in f.lower() or "mail" in f.lower() for f in modified_files + added_files):
            commit_scope = "email"
        elif any("sign" in f.lower() for f in modified_files + added_files):
            commit_scope = "sign"
        elif any("config" in f.lower() for f in modified_files + added_files):
            commit_scope = "config"
        elif any("test" in f.lower() for f in modified_files + added_files):
            commit_scope = "test"
        
        # 构建提交信息
        scope_part = f"({commit_scope})" if commit_scope else ""
        subject = f"{commit_type}{scope_part}: {commit_description}"
        
        # 添加详细信息
        details = []
        if added_files:
            details.append(f"新增文件: {len(added_files)}个")
        if modified_files:
            details.append(f"修改文件: {len(modified_files)}个")
        if deleted_files:
            details.append(f"删除文件: {len(deleted_files)}个")
        
        details_line = " | ".join(details)
        
        commit_message = f"{subject}\n\n{details_line}\n\n自动提交时间: {current_time}"
        
        return commit_message
    
    def commit_changes(self, message=None):
        """
        提交更改
        
        Args:
            message: 提交信息，如果为None则自动生成
            
        Returns:
            bool: 提交是否成功
        """
        try:
            # 检查是否有更改
            status = self.get_status()
            if status.get("clean", True):
                logger.info("没有更改需要提交")
                return True
            
            # 添加所有更改
            if not self.add_all_changes():
                return False
            
            # 生成提交信息
            if not message:
                message = self.generate_commit_message(status)
            
            logger.info("📝 提交更改...")
            logger.info(f"提交信息: {message.split(chr(10))[0]}")  # 只显示第一行
            
            result = subprocess.run(
                ["git", "commit", "-m", message], 
                cwd=self.project_dir, 
                capture_output=True, 
                text=True
            )
            
            if result.returncode == 0:
                logger.success("✅ 更改提交成功")
                return True
            else:
                logger.error(f"❌ 提交失败: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 提交更改时发生错误: {e}")
            return False
    
    def get_remote_info(self):
        """
        获取远程仓库信息
        
        Returns:
            dict: 远程仓库信息
        """
        try:
            result = subprocess.run(
                ["git", "remote", "-v"], 
                cwd=self.project_dir, 
                capture_output=True, 
                text=True
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n') if result.stdout.strip() else []
                remotes = {}
                
                for line in lines:
                    if line:
                        parts = line.split()
                        if len(parts) >= 2:
                            remote_name = parts[0]
                            remote_url = parts[1]
                            operation = parts[2] if len(parts) > 2 else ""
                            
                            if remote_name not in remotes:
                                remotes[remote_name] = {}
                            
                            if "(fetch)" in operation:
                                remotes[remote_name]["fetch"] = remote_url
                            elif "(push)" in operation:
                                remotes[remote_name]["push"] = remote_url
                
                return {"remotes": remotes}
            else:
                return {"error": f"获取远程信息失败: {result.stderr}"}
                
        except Exception as e:
            return {"error": f"获取远程仓库信息时发生错误: {e}"}
    
    def add_remote(self, remote_name, remote_url):
        """
        添加远程仓库
        
        Args:
            remote_name: 远程仓库名称
            remote_url: 远程仓库URL
            
        Returns:
            bool: 添加是否成功
        """
        try:
            logger.info(f"🔗 添加远程仓库: {remote_name} -> {remote_url}")
            result = subprocess.run(
                ["git", "remote", "add", remote_name, remote_url], 
                cwd=self.project_dir, 
                capture_output=True, 
                text=True
            )
            
            if result.returncode == 0:
                logger.success(f"✅ 远程仓库 {remote_name} 添加成功")
                return True
            else:
                logger.error(f"❌ 添加远程仓库失败: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 添加远程仓库时发生错误: {e}")
            return False
    
    def push_to_remote(self, remote_name="origin", branch_name="main"):
        """
        推送到远程仓库
        
        Args:
            remote_name: 远程仓库名称
            branch_name: 分支名称
            
        Returns:
            bool: 推送是否成功
        """
        try:
            logger.info(f"🚀 推送到远程仓库: {remote_name}/{branch_name}")
            
            # 首次推送可能需要设置上游分支
            result = subprocess.run(
                ["git", "push", "-u", remote_name, branch_name], 
                cwd=self.project_dir, 
                capture_output=True, 
                text=True
            )
            
            if result.returncode == 0:
                logger.success(f"✅ 推送到 {remote_name}/{branch_name} 成功")
                return True
            else:
                # 尝试普通推送
                result = subprocess.run(
                    ["git", "push", remote_name, branch_name], 
                    cwd=self.project_dir, 
                    capture_output=True, 
                    text=True
                )
                
                if result.returncode == 0:
                    logger.success(f"✅ 推送到 {remote_name}/{branch_name} 成功")
                    return True
                else:
                    logger.error(f"❌ 推送失败: {result.stderr}")
                    return False
                
        except Exception as e:
            logger.error(f"❌ 推送时发生错误: {e}")
            return False
    
    def pull_from_remote(self, remote_name="origin", branch_name="main"):
        """
        从远程仓库拉取
        
        Args:
            remote_name: 远程仓库名称
            branch_name: 分支名称
            
        Returns:
            bool: 拉取是否成功
        """
        try:
            logger.info(f"⬇️ 从远程仓库拉取: {remote_name}/{branch_name}")
            result = subprocess.run(
                ["git", "pull", remote_name, branch_name], 
                cwd=self.project_dir, 
                capture_output=True, 
                text=True
            )
            
            if result.returncode == 0:
                logger.success(f"✅ 从 {remote_name}/{branch_name} 拉取成功")
                return True
            else:
                logger.error(f"❌ 拉取失败: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 拉取时发生错误: {e}")
            return False
    
    def smart_sync(self, remote_url=None, remote_name="origin", branch_name="main"):
        """
        智能同步：自动提交并推送到远程仓库
        
        Args:
            remote_url: 远程仓库URL（首次设置）
            remote_name: 远程仓库名称
            branch_name: 分支名称
            
        Returns:
            bool: 同步是否成功
        """
        try:
            logger.info("🔄 开始智能Git同步...")
            
            # 确保是Git仓库
            if not self.is_git_repo():
                if not self.init_git_repo():
                    return False
            
            # 检查远程仓库
            remote_info = self.get_remote_info()
            if remote_info.get("error") or not remote_info.get("remotes"):
                if remote_url:
                    if not self.add_remote(remote_name, remote_url):
                        return False
                else:
                    logger.warning("未配置远程仓库，仅进行本地提交")
            
            # 提交本地更改
            if not self.commit_changes():
                return False
            
            # 推送到远程（如果有远程仓库）
            remote_info = self.get_remote_info()
            if not remote_info.get("error") and remote_info.get("remotes"):
                # 先尝试拉取（避免冲突）
                self.pull_from_remote(remote_name, branch_name)
                
                # 推送更改
                if not self.push_to_remote(remote_name, branch_name):
                    return False
            
            logger.success("✅ 智能Git同步完成")
            return True
            
        except Exception as e:
            logger.error(f"❌ 智能同步时发生错误: {e}")
            return False
    
    def get_commit_history(self, count=10):
        """
        获取提交历史
        
        Args:
            count: 获取的提交数量
            
        Returns:
            list: 提交历史列表
        """
        try:
            result = subprocess.run(
                ["git", "log", f"-{count}", "--oneline", "--decorate"], 
                cwd=self.project_dir, 
                capture_output=True, 
                text=True
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n') if result.stdout.strip() else []
                commits = []
                
                for line in lines:
                    if line:
                        parts = line.split(' ', 1)
                        if len(parts) >= 2:
                            commits.append({
                                "hash": parts[0],
                                "message": parts[1]
                            })
                
                return commits
            else:
                return []
                
        except Exception as e:
            logger.error(f"获取提交历史时发生错误: {e}")
            return []


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='智能Git管理器')
    parser.add_argument('--init', action='store_true', help='初始化Git仓库')
    parser.add_argument('--status', action='store_true', help='检查Git状态')
    parser.add_argument('--commit', action='store_true', help='提交更改')
    parser.add_argument('--sync', action='store_true', help='智能同步到远程')
    parser.add_argument('--remote', type=str, help='远程仓库URL')
    parser.add_argument('--message', '-m', type=str, help='自定义提交信息')
    parser.add_argument('--history', action='store_true', help='显示提交历史')
    
    args = parser.parse_args()
    
    # 创建Git管理器
    git_manager = GitManager()
    
    if args.init:
        # 初始化Git仓库
        print("🔧 初始化Git仓库...")
        success = git_manager.init_git_repo()
        sys.exit(0 if success else 1)
    
    elif args.status:
        # 检查Git状态
        print("🔍 检查Git状态...")
        status = git_manager.get_status()
        
        if status.get("error"):
            print(f"❌ {status['error']}")
        else:
            print(f"总更改数: {status['total_changes']}")
            print(f"仓库状态: {'✅ 干净' if status['clean'] else '⚠️ 有更改'}")
            
            if status['modified_files']:
                print(f"修改文件: {len(status['modified_files'])}个")
            if status['added_files']:
                print(f"新增文件: {len(status['added_files'])}个")
            if status['untracked_files']:
                print(f"未跟踪文件: {len(status['untracked_files'])}个")
    
    elif args.commit:
        # 提交更改
        print("📝 提交更改...")
        success = git_manager.commit_changes(args.message)
        sys.exit(0 if success else 1)
    
    elif args.sync:
        # 智能同步
        print("🔄 智能Git同步...")
        success = git_manager.smart_sync(remote_url=args.remote)
        sys.exit(0 if success else 1)
    
    elif args.history:
        # 显示提交历史
        print("📜 提交历史:")
        commits = git_manager.get_commit_history()
        
        if commits:
            for commit in commits:
                print(f"  {commit['hash']} {commit['message']}")
        else:
            print("  无提交记录")
    
    else:
        # 默认显示帮助
        parser.print_help()
        print("\n💡 使用示例:")
        print("  python git_manager.py --init                           # 初始化仓库")
        print("  python git_manager.py --status                         # 检查状态")
        print("  python git_manager.py --commit                         # 提交更改")
        print("  python git_manager.py --sync                           # 智能同步")
        print("  python git_manager.py --sync --remote <URL>            # 同步到指定远程")
        print("  python git_manager.py --commit --message '自定义信息'   # 自定义提交信息")


if __name__ == "__main__":
    main()
