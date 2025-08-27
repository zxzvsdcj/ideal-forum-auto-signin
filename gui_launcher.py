#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
理想论坛自动签到程序 - GUI专用启动器
功能：直接启动GUI界面，无需命令行参数
"""

import os
import sys
from pathlib import Path

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """主函数 - 直接启动GUI"""
    try:
        # 检查配置文件
        config_file = Path("config.ini")
        if not config_file.exists():
            # 如果配置文件不存在，创建默认配置
            default_config = """[LOGIN]
username = your_username_here
password = your_password_here

[SCHEDULE]
enable_schedule = true
sign_time = 09:00

[SETTINGS]
headless = true
login_timeout = 10
retry_count = 3
page_load_timeout = 5

[EMAIL]
enable_email = false
smtp_server = smtp.qq.com
smtp_port = 465
sender_email = your_email@qq.com
sender_password = your_auth_code
receiver_email = your_email@qq.com
email_subject = 理想论坛签到通知
notify_on_success = true
notify_on_failure = true

[BROWSER]
user_agent = Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36
window_size = 1920,1080

[LOGGING]
log_level = INFO
log_file = sign_log.txt
max_log_size = 10MB
backup_count = 5
"""
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(default_config)
        
        # 尝试启动GUI
        try:
            from gui_main import main as gui_main
            gui_main()
        except ImportError:
            print("❌ GUI模块未找到，启动命令行版本...")
            from run import main as cli_main
            # 模拟 --gui 参数
            sys.argv = ['run.py', '--gui']
            cli_main()
            
    except Exception as e:
        import tkinter as tk
        from tkinter import messagebox
        
        # 如果GUI启动失败，显示错误消息
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        
        error_msg = f"""理想论坛签到程序启动失败！

错误信息：{str(e)}

可能的解决方案：
1. 确保已安装 PyQt6：pip install PyQt6
2. 检查 config.ini 配置文件
3. 尝试以管理员身份运行

程序将退出，请检查后重试。"""
        
        messagebox.showerror("启动失败", error_msg)
        root.destroy()
        sys.exit(1)

if __name__ == '__main__':
    main()
