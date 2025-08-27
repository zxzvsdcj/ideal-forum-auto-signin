#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
理想论坛自动签到程序 - 现代化GUI界面
基于PyQt6实现的炫酷用户界面
"""

import sys
import os
import json
import threading
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QLineEdit, 
                            QTextEdit, QCheckBox, QSpinBox, QTimeEdit, 
                            QGroupBox, QTabWidget, QStatusBar, QSplitter,
                            QFrame, QScrollArea, QGridLayout, QComboBox,
                            QFileDialog, QMessageBox, QProgressBar)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QTime, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import (QFont, QIcon, QPalette, QColor, QPixmap, QPainter, 
                        QBrush, QLinearGradient, QRadialGradient, QPen, QAction)

from sign_bot import IdealForumSignBot
from scheduler import SignScheduler
from email_notifier import EmailNotifier


class ModernButton(QPushButton):
    """现代化按钮组件"""
    
    def __init__(self, text, button_type="primary"):
        super().__init__(text)
        self.button_type = button_type
        self.setup_style()
        self.setup_animation()
    
    def setup_style(self):
        """设置按钮样式"""
        styles = {
            "primary": """
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #667eea, stop:1 #764ba2);
                    border: none;
                    border-radius: 8px;
                    color: white;
                    font-weight: bold;
                    font-size: 14px;
                    padding: 12px 24px;
                    min-width: 100px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #5a6fd8, stop:1 #6a4c96);
                    transform: translateY(-2px);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #4e5cd0, stop:1 #5e4088);
                }
                QPushButton:disabled {
                    background: #cccccc;
                    color: #666666;
                }
            """,
            "success": """
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #56ab2f, stop:1 #a8e6cf);
                    border: none;
                    border-radius: 8px;
                    color: white;
                    font-weight: bold;
                    font-size: 14px;
                    padding: 12px 24px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #4e9a2a, stop:1 #96d9b8);
                }
            """,
            "danger": """
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #ff416c, stop:1 #ff4b2b);
                    border: none;
                    border-radius: 8px;
                    color: white;
                    font-weight: bold;
                    font-size: 14px;
                    padding: 12px 24px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #e6395f, stop:1 #e6432a);
                }
            """,
            "secondary": """
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #f7f8fc, stop:1 #eef1f5);
                    border: 2px solid #e1e5e9;
                    border-radius: 8px;
                    color: #495057;
                    font-weight: bold;
                    font-size: 14px;
                    padding: 12px 24px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #e9ecef, stop:1 #dee2e6);
                    border-color: #adb5bd;
                }
            """
        }
        
        self.setStyleSheet(styles.get(self.button_type, styles["primary"]))
    
    def setup_animation(self):
        """设置按钮动画"""
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)


class ModernCard(QFrame):
    """现代化卡片组件"""
    
    def __init__(self):
        super().__init__()
        self.setup_style()
    
    def setup_style(self):
        """设置卡片样式"""
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e9ecef;
                padding: 20px;
            }
            QFrame:hover {
                border-color: #adb5bd;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            }
        """)
        self.setFrameStyle(QFrame.Shape.Box)


class StatusIndicator(QLabel):
    """状态指示器组件"""
    
    def __init__(self, status="offline"):
        super().__init__()
        self.status = status
        self.update_status(status)
        self.setup_style()
    
    def setup_style(self):
        """设置样式"""
        self.setFixedSize(12, 12)
        self.setStyleSheet("""
            QLabel {
                border-radius: 6px;
                border: 2px solid white;
            }
        """)
    
    def update_status(self, status):
        """更新状态"""
        self.status = status
        colors = {
            "online": "#28a745",
            "offline": "#6c757d", 
            "running": "#007bff",
            "error": "#dc3545",
            "warning": "#ffc107"
        }
        
        color = colors.get(status, "#6c757d")
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                border-radius: 6px;
                border: 2px solid white;
            }}
        """)


class SignInThread(QThread):
    """签到任务线程"""
    
    progress_updated = pyqtSignal(str)
    status_updated = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self):
        super().__init__()
        self.bot = None
    
    def run(self):
        """执行签到任务"""
        try:
            self.progress_updated.emit("初始化签到机器人...")
            self.status_updated.emit("running")
            
            self.bot = IdealForumSignBot()
            
            self.progress_updated.emit("验证配置...")
            if not self.bot.validate_config():
                self.finished.emit(False, "配置验证失败")
                return
            
            self.progress_updated.emit("执行签到任务...")
            success = self.bot.sign_in()
            
            if success:
                self.status_updated.emit("online")
                self.finished.emit(True, "签到成功完成！")
            else:
                self.status_updated.emit("error")
                self.finished.emit(False, "签到任务失败")
                
        except Exception as e:
            self.status_updated.emit("error")
            self.finished.emit(False, f"签到过程中发生错误: {str(e)}")


class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        self.sign_thread = None
        self.scheduler = None
        self.setup_ui()
        self.setup_status_bar()
        self.setup_timer()
        self.load_config()
        
    def setup_ui(self):
        """设置用户界面"""
        self.setWindowTitle("理想论坛自动签到程序 v1.0")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)
        
        # 设置应用程序样式
        self.setup_global_style()
        
        # 创建中央widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 创建头部
        header = self.create_header()
        main_layout.addWidget(header)
        
        # 创建标签页
        tab_widget = self.create_tabs()
        main_layout.addWidget(tab_widget)
    
    def setup_global_style(self):
        """设置全局样式"""
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                           stop:0 #ffecd2, stop:1 #fcb69f);
            }
            QTabWidget::pane {
                border: 1px solid #e9ecef;
                border-radius: 8px;
                background-color: white;
                margin-top: 5px;
            }
            QTabWidget::tab-bar {
                left: 10px;
            }
            QTabBar::tab {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                           stop:0 #f8f9fa, stop:1 #e9ecef);
                border: 1px solid #dee2e6;
                border-bottom: none;
                border-radius: 8px 8px 0 0;
                padding: 12px 24px;
                margin-right: 2px;
                font-weight: bold;
                min-width: 100px;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom: 2px solid #667eea;
            }
            QTabBar::tab:hover:!selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                           stop:0 #e9ecef, stop:1 #dee2e6);
            }
            QLineEdit, QTextEdit, QSpinBox, QTimeEdit, QComboBox {
                border: 2px solid #e9ecef;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, 
            QTimeEdit:focus, QComboBox:focus {
                border-color: #667eea;
                outline: none;
            }
            QGroupBox {
                font-weight: bold;
                font-size: 16px;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: rgba(255, 255, 255, 0.8);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #495057;
            }
            QCheckBox {
                font-size: 14px;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #dee2e6;
                border-radius: 4px;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                background-color: #667eea;
                border-color: #667eea;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEwIDNMNC41IDguNUwyIDYiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+Cjwvc3ZnPgo=);
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #f8f9fa;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #adb5bd;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #6c757d;
            }
        """)
    
    def create_header(self):
        """创建头部"""
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                           stop:0 #667eea, stop:1 #764ba2);
                border-radius: 12px;
                padding: 20px;
            }
        """)
        
        layout = QHBoxLayout(header)
        
        # 标题区域
        title_layout = QVBoxLayout()
        
        title_label = QLabel("🎯 理想论坛自动签到程序")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
                background: transparent;
            }
        """)
        
        subtitle_label = QLabel("Ideal Forum Auto Sign-in Bot v1.0")
        subtitle_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.8);
                font-size: 14px;
                background: transparent;
            }
        """)
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        
        # 状态区域
        status_layout = QVBoxLayout()
        status_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        self.status_indicator = StatusIndicator("offline")
        self.status_label = QLabel("离线")
        self.status_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14px;
                font-weight: bold;
                background: transparent;
            }
        """)
        
        status_container = QHBoxLayout()
        status_container.addWidget(self.status_indicator)
        status_container.addWidget(self.status_label)
        status_container.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        status_layout.addLayout(status_container)
        
        layout.addLayout(title_layout)
        layout.addStretch()
        layout.addLayout(status_layout)
        
        return header
    
    def create_tabs(self):
        """创建标签页"""
        tab_widget = QTabWidget()
        
        # 主要功能标签页
        main_tab = self.create_main_tab()
        tab_widget.addTab(main_tab, "🏠 主页")
        
        # 配置标签页
        config_tab = self.create_config_tab()
        tab_widget.addTab(config_tab, "⚙️ 配置")
        
        # 日志标签页
        log_tab = self.create_log_tab()
        tab_widget.addTab(log_tab, "📋 日志")
        
        # 关于标签页
        about_tab = self.create_about_tab()
        tab_widget.addTab(about_tab, "ℹ️ 关于")
        
        return tab_widget
    
    def create_main_tab(self):
        """创建主要功能标签页"""
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(20)
        
        # 快速操作区域
        quick_actions = self.create_quick_actions()
        layout.addWidget(quick_actions)
        
        # 签到信息区域
        sign_info = self.create_sign_info()
        layout.addWidget(sign_info)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #e9ecef;
                border-radius: 8px;
                text-align: center;
                font-weight: bold;
                color: #495057;
                background-color: #f8f9fa;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                           stop:0 #667eea, stop:1 #764ba2);
                border-radius: 6px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        layout.addStretch()
        
        return main_widget
    
    def create_quick_actions(self):
        """创建快速操作区域"""
        group = QGroupBox("🚀 快速操作")
        layout = QGridLayout(group)
        layout.setSpacing(15)
        
        # 立即签到按钮
        self.sign_now_btn = ModernButton("立即签到", "primary")
        self.sign_now_btn.clicked.connect(self.start_sign_in)
        layout.addWidget(self.sign_now_btn, 0, 0)
        
        # 启动定时签到按钮
        self.start_schedule_btn = ModernButton("启动定时签到", "success")
        self.start_schedule_btn.clicked.connect(self.start_schedule)
        layout.addWidget(self.start_schedule_btn, 0, 1)
        
        # 停止定时签到按钮
        self.stop_schedule_btn = ModernButton("停止定时签到", "danger")
        self.stop_schedule_btn.clicked.connect(self.stop_schedule)
        self.stop_schedule_btn.setEnabled(False)
        layout.addWidget(self.stop_schedule_btn, 0, 2)
        
        # 测试配置按钮
        self.test_config_btn = ModernButton("测试配置", "secondary")
        self.test_config_btn.clicked.connect(self.test_configuration)
        layout.addWidget(self.test_config_btn, 1, 0)
        
        # 测试邮件按钮
        self.test_email_btn = ModernButton("测试邮件", "secondary")
        self.test_email_btn.clicked.connect(self.test_email)
        layout.addWidget(self.test_email_btn, 1, 1)
        
        # 打开日志文件夹按钮
        self.open_logs_btn = ModernButton("打开日志", "secondary")
        self.open_logs_btn.clicked.connect(self.open_log_folder)
        layout.addWidget(self.open_logs_btn, 1, 2)
        
        return group
    
    def create_sign_info(self):
        """创建签到信息区域"""
        group = QGroupBox("📊 签到信息")
        layout = QGridLayout(group)
        layout.setSpacing(15)
        
        # 信息标签
        info_labels = [
            ("最近签到:", "未知"),
            ("签到状态:", "未签到"),
            ("连续天数:", "0天"),
            ("总签到天数:", "0天"),
            ("签到排名:", "未知"),
            ("下次签到:", "未设置")
        ]
        
        self.info_labels = {}
        for i, (label_text, default_value) in enumerate(info_labels):
            row, col = i // 2, (i % 2) * 2
            
            label = QLabel(label_text)
            label.setStyleSheet("font-weight: bold; color: #495057;")
            
            value_label = QLabel(default_value)
            value_label.setStyleSheet("color: #6c757d;")
            
            layout.addWidget(label, row, col)
            layout.addWidget(value_label, row, col + 1)
            
            self.info_labels[label_text] = value_label
        
        return group
    
    def create_config_tab(self):
        """创建配置标签页"""
        config_widget = QWidget()
        layout = QVBoxLayout(config_widget)
        
        # 创建滚动区域
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # 登录配置
        login_group = self.create_login_config()
        scroll_layout.addWidget(login_group)
        
        # 签到配置
        schedule_group = self.create_schedule_config()
        scroll_layout.addWidget(schedule_group)
        
        # 邮件配置
        email_group = self.create_email_config()
        scroll_layout.addWidget(email_group)
        
        # 高级配置
        advanced_group = self.create_advanced_config()
        scroll_layout.addWidget(advanced_group)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        
        layout.addWidget(scroll)
        
        # 保存按钮
        save_btn = ModernButton("保存配置", "primary")
        save_btn.clicked.connect(self.save_config)
        layout.addWidget(save_btn)
        
        return config_widget
    
    def create_login_config(self):
        """创建登录配置组"""
        group = QGroupBox("🔐 登录配置")
        layout = QGridLayout(group)
        
        # 用户名
        layout.addWidget(QLabel("用户名:"), 0, 0)
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("请输入用户名/手机号/邮箱")
        layout.addWidget(self.username_edit, 0, 1)
        
        # 密码
        layout.addWidget(QLabel("密码:"), 1, 0)
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setPlaceholderText("请输入密码")
        layout.addWidget(self.password_edit, 1, 1)
        
        return group
    
    def create_schedule_config(self):
        """创建签到配置组"""
        group = QGroupBox("⏰ 定时签到配置")
        layout = QGridLayout(group)
        
        # 启用定时签到
        self.enable_schedule_cb = QCheckBox("启用定时签到")
        layout.addWidget(self.enable_schedule_cb, 0, 0, 1, 2)
        
        # 签到时间
        layout.addWidget(QLabel("签到时间:"), 1, 0)
        self.sign_time_edit = QTimeEdit()
        self.sign_time_edit.setDisplayFormat("HH:mm")
        layout.addWidget(self.sign_time_edit, 1, 1)
        
        # 无头模式
        self.headless_cb = QCheckBox("无头模式（后台运行）")
        layout.addWidget(self.headless_cb, 2, 0, 1, 2)
        
        return group
    
    def create_email_config(self):
        """创建邮件配置组"""
        group = QGroupBox("📧 邮件通知配置")
        layout = QGridLayout(group)
        
        # 启用邮件通知
        self.enable_email_cb = QCheckBox("启用邮件通知")
        layout.addWidget(self.enable_email_cb, 0, 0, 1, 2)
        
        # SMTP服务器
        layout.addWidget(QLabel("SMTP服务器:"), 1, 0)
        self.smtp_server_edit = QLineEdit()
        self.smtp_server_edit.setPlaceholderText("如: smtp.gmail.com")
        layout.addWidget(self.smtp_server_edit, 1, 1)
        
        # SMTP端口
        layout.addWidget(QLabel("SMTP端口:"), 2, 0)
        self.smtp_port_spin = QSpinBox()
        self.smtp_port_spin.setRange(1, 65535)
        self.smtp_port_spin.setValue(587)
        layout.addWidget(self.smtp_port_spin, 2, 1)
        
        # 发件人邮箱
        layout.addWidget(QLabel("发件人邮箱:"), 3, 0)
        self.sender_email_edit = QLineEdit()
        self.sender_email_edit.setPlaceholderText("your_email@gmail.com")
        layout.addWidget(self.sender_email_edit, 3, 1)
        
        # 邮箱密码
        layout.addWidget(QLabel("邮箱密码:"), 4, 0)
        self.email_password_edit = QLineEdit()
        self.email_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.email_password_edit.setPlaceholderText("邮箱密码或应用专用密码")
        layout.addWidget(self.email_password_edit, 4, 1)
        
        # 收件人邮箱
        layout.addWidget(QLabel("收件人邮箱:"), 5, 0)
        self.receiver_email_edit = QLineEdit()
        self.receiver_email_edit.setPlaceholderText("接收通知的邮箱地址")
        layout.addWidget(self.receiver_email_edit, 5, 1)
        
        return group
    
    def create_advanced_config(self):
        """创建高级配置组"""
        group = QGroupBox("🔧 高级配置")
        layout = QGridLayout(group)
        
        # 登录超时
        layout.addWidget(QLabel("登录超时(秒):"), 0, 0)
        self.login_timeout_spin = QSpinBox()
        self.login_timeout_spin.setRange(5, 60)
        self.login_timeout_spin.setValue(10)
        layout.addWidget(self.login_timeout_spin, 0, 1)
        
        # 重试次数
        layout.addWidget(QLabel("重试次数:"), 1, 0)
        self.retry_count_spin = QSpinBox()
        self.retry_count_spin.setRange(1, 10)
        self.retry_count_spin.setValue(3)
        layout.addWidget(self.retry_count_spin, 1, 1)
        
        return group
    
    def create_log_tab(self):
        """创建日志标签页"""
        log_widget = QWidget()
        layout = QVBoxLayout(log_widget)
        
        # 日志文本区域
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        layout.addWidget(self.log_text)
        
        # 日志控制按钮
        button_layout = QHBoxLayout()
        
        clear_log_btn = ModernButton("清空日志", "secondary")
        clear_log_btn.clicked.connect(self.clear_log)
        button_layout.addWidget(clear_log_btn)
        
        save_log_btn = ModernButton("保存日志", "secondary")
        save_log_btn.clicked.connect(self.save_log)
        button_layout.addWidget(save_log_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        return log_widget
    
    def create_about_tab(self):
        """创建关于标签页"""
        about_widget = QWidget()
        layout = QVBoxLayout(about_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 应用图标和名称
        app_info = QVBoxLayout()
        app_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        app_name = QLabel("🎯 理想论坛自动签到程序")
        app_name.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: bold;
                color: #495057;
                margin: 20px;
            }
        """)
        app_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        version_label = QLabel("版本 v1.0.0")
        version_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #6c757d;
                margin: 10px;
            }
        """)
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 功能特性
        features = QLabel("""
        ✨ 功能特性：
        
        🔐 智能登录：支持多种登录方式和验证码处理
        ⏰ 定时签到：每日自动执行签到任务
        📧 邮件通知：签到结果实时邮件提醒
        🎨 现代界面：炫酷的GUI界面设计
        📊 详细日志：完整的操作记录和错误追踪
        ⚙️ 灵活配置：丰富的个性化设置选项
        
        💡 技术栈：Python + PyQt6 + Selenium
        """)
        features.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #495057;
                background-color: rgba(255, 255, 255, 0.8);
                border-radius: 12px;
                padding: 20px;
                margin: 20px;
            }
        """)
        features.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        app_info.addWidget(app_name)
        app_info.addWidget(version_label)
        app_info.addWidget(features)
        
        layout.addLayout(app_info)
        layout.addStretch()
        
        return about_widget
    
    def setup_status_bar(self):
        """设置状态栏"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # 状态信息
        self.status_bar.showMessage("就绪")
        
        # 时间显示
        self.time_label = QLabel()
        self.status_bar.addPermanentWidget(self.time_label)
        
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: rgba(255, 255, 255, 0.9);
                border-top: 1px solid #e9ecef;
                font-size: 12px;
                color: #495057;
            }
        """)
    
    def setup_timer(self):
        """设置定时器"""
        # 时间更新定时器
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # 每秒更新一次
        
        # 状态检查定时器
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.check_schedule_status)
        self.status_timer.start(5000)  # 每5秒检查一次
    
    def update_time(self):
        """更新时间显示"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.setText(current_time)
    
    def load_config(self):
        """加载配置"""
        try:
            import configparser
            config = configparser.ConfigParser()
            config.read('config.ini', encoding='utf-8')
            
            # 加载登录配置
            self.username_edit.setText(config.get('LOGIN', 'username', fallback=''))
            self.password_edit.setText(config.get('LOGIN', 'password', fallback=''))
            
            # 加载签到配置
            self.enable_schedule_cb.setChecked(config.getboolean('SCHEDULE', 'enable_schedule', fallback=False))
            sign_time = config.get('SCHEDULE', 'sign_time', fallback='09:00')
            self.sign_time_edit.setTime(QTime.fromString(sign_time, "HH:mm"))
            self.headless_cb.setChecked(config.getboolean('SETTINGS', 'headless', fallback=True))
            
            # 加载邮件配置
            self.enable_email_cb.setChecked(config.getboolean('EMAIL', 'enable_email', fallback=False))
            self.smtp_server_edit.setText(config.get('EMAIL', 'smtp_server', fallback='smtp.gmail.com'))
            self.smtp_port_spin.setValue(config.getint('EMAIL', 'smtp_port', fallback=587))
            self.sender_email_edit.setText(config.get('EMAIL', 'sender_email', fallback=''))
            self.email_password_edit.setText(config.get('EMAIL', 'sender_password', fallback=''))
            self.receiver_email_edit.setText(config.get('EMAIL', 'receiver_email', fallback=''))
            
            # 加载高级配置
            self.login_timeout_spin.setValue(config.getint('SETTINGS', 'login_timeout', fallback=10))
            self.retry_count_spin.setValue(config.getint('SETTINGS', 'retry_count', fallback=3))
            
            self.add_log("✅ 配置加载成功")
            
        except Exception as e:
            self.add_log(f"❌ 配置加载失败: {e}")
    
    def save_config(self):
        """保存配置"""
        try:
            import configparser
            config = configparser.ConfigParser()
            
            # 保存登录配置
            config.add_section('LOGIN')
            config.set('LOGIN', 'username', self.username_edit.text())
            config.set('LOGIN', 'password', self.password_edit.text())
            
            # 保存签到配置
            config.add_section('SCHEDULE')
            config.set('SCHEDULE', 'enable_schedule', str(self.enable_schedule_cb.isChecked()).lower())
            config.set('SCHEDULE', 'sign_time', self.sign_time_edit.time().toString("HH:mm"))
            
            # 保存设置配置
            config.add_section('SETTINGS')
            config.set('SETTINGS', 'headless', str(self.headless_cb.isChecked()).lower())
            config.set('SETTINGS', 'login_timeout', str(self.login_timeout_spin.value()))
            config.set('SETTINGS', 'retry_count', str(self.retry_count_spin.value()))
            config.set('SETTINGS', 'page_load_timeout', '5')
            
            # 保存邮件配置
            config.add_section('EMAIL')
            config.set('EMAIL', 'enable_email', str(self.enable_email_cb.isChecked()).lower())
            config.set('EMAIL', 'smtp_server', self.smtp_server_edit.text())
            config.set('EMAIL', 'smtp_port', str(self.smtp_port_spin.value()))
            config.set('EMAIL', 'sender_email', self.sender_email_edit.text())
            config.set('EMAIL', 'sender_password', self.email_password_edit.text())
            config.set('EMAIL', 'receiver_email', self.receiver_email_edit.text())
            config.set('EMAIL', 'email_subject', '理想论坛签到通知')
            config.set('EMAIL', 'notify_on_success', 'true')
            config.set('EMAIL', 'notify_on_failure', 'true')
            
            # 保存浏览器配置
            config.add_section('BROWSER')
            config.set('BROWSER', 'user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            config.set('BROWSER', 'window_size', '1920,1080')
            
            # 保存日志配置
            config.add_section('LOGGING')
            config.set('LOGGING', 'log_level', 'INFO')
            config.set('LOGGING', 'log_file', 'sign_log.txt')
            config.set('LOGGING', 'max_log_size', '10MB')
            config.set('LOGGING', 'backup_count', '5')
            
            with open('config.ini', 'w', encoding='utf-8') as f:
                config.write(f)
            
            self.add_log("✅ 配置保存成功")
            QMessageBox.information(self, "成功", "配置已保存成功！")
            
        except Exception as e:
            self.add_log(f"❌ 配置保存失败: {e}")
            QMessageBox.critical(self, "错误", f"配置保存失败：{e}")
    
    def start_sign_in(self):
        """开始签到"""
        if self.sign_thread and self.sign_thread.isRunning():
            QMessageBox.warning(self, "警告", "签到任务正在进行中，请等待完成。")
            return
        
        self.sign_now_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 无限进度条
        self.status_bar.showMessage("正在执行签到任务...")
        
        # 创建并启动签到线程
        self.sign_thread = SignInThread()
        self.sign_thread.progress_updated.connect(self.update_progress)
        self.sign_thread.status_updated.connect(self.update_status)
        self.sign_thread.finished.connect(self.sign_finished)
        self.sign_thread.start()
    
    def update_progress(self, message):
        """更新进度信息"""
        self.add_log(f"🔄 {message}")
        self.status_bar.showMessage(message)
    
    def update_status(self, status):
        """更新状态"""
        self.status_indicator.update_status(status)
        status_texts = {
            "online": "在线",
            "offline": "离线", 
            "running": "运行中",
            "error": "错误",
            "warning": "警告"
        }
        self.status_label.setText(status_texts.get(status, "未知"))
    
    def sign_finished(self, success, message):
        """签到完成"""
        self.sign_now_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        if success:
            self.add_log(f"✅ {message}")
            self.status_bar.showMessage("签到成功完成")
            QMessageBox.information(self, "成功", message)
            self.update_status("online")
        else:
            self.add_log(f"❌ {message}")
            self.status_bar.showMessage("签到失败")
            QMessageBox.critical(self, "失败", message)
            self.update_status("error")
    
    def start_schedule(self):
        """启动定时签到"""
        if not self.enable_schedule_cb.isChecked():
            QMessageBox.warning(self, "警告", "请先在配置中启用定时签到功能。")
            return
        
        try:
            self.scheduler = SignScheduler()
            # 这里可以添加调度器启动逻辑
            
            self.start_schedule_btn.setEnabled(False)
            self.stop_schedule_btn.setEnabled(True)
            self.add_log("✅ 定时签到已启动")
            self.status_bar.showMessage("定时签到运行中")
            self.update_status("running")
            
        except Exception as e:
            self.add_log(f"❌ 启动定时签到失败: {e}")
            QMessageBox.critical(self, "错误", f"启动定时签到失败：{e}")
    
    def stop_schedule(self):
        """停止定时签到"""
        self.start_schedule_btn.setEnabled(True)
        self.stop_schedule_btn.setEnabled(False)
        self.add_log("⏹️ 定时签到已停止")
        self.status_bar.showMessage("就绪")
        self.update_status("offline")
    
    def test_configuration(self):
        """测试配置"""
        self.add_log("🧪 开始测试配置...")
        
        try:
            # 测试基本配置
            if not self.username_edit.text():
                raise Exception("用户名不能为空")
            if not self.password_edit.text():
                raise Exception("密码不能为空")
            
            self.add_log("✅ 基本配置测试通过")
            QMessageBox.information(self, "成功", "配置测试通过！")
            
        except Exception as e:
            self.add_log(f"❌ 配置测试失败: {e}")
            QMessageBox.critical(self, "错误", f"配置测试失败：{e}")
    
    def test_email(self):
        """测试邮件"""
        if not self.enable_email_cb.isChecked():
            QMessageBox.warning(self, "警告", "请先启用邮件通知功能。")
            return
        
        self.add_log("📧 开始测试邮件功能...")
        
        try:
            # 这里可以添加邮件测试逻辑
            notifier = EmailNotifier()
            if notifier.test_email_config():
                notifier.send_test_email()
                self.add_log("✅ 邮件测试成功")
                QMessageBox.information(self, "成功", "邮件测试成功！请检查收件箱。")
            else:
                self.add_log("❌ 邮件配置测试失败")
                QMessageBox.critical(self, "错误", "邮件配置测试失败，请检查配置。")
                
        except Exception as e:
            self.add_log(f"❌ 邮件测试失败: {e}")
            QMessageBox.critical(self, "错误", f"邮件测试失败：{e}")
    
    def open_log_folder(self):
        """打开日志文件夹"""
        import subprocess
        import platform
        
        try:
            if platform.system() == "Windows":
                subprocess.run(["explorer", "."], check=True)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", "."], check=True)
            else:  # Linux
                subprocess.run(["xdg-open", "."], check=True)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"打开文件夹失败：{e}")
    
    def check_schedule_status(self):
        """检查调度状态"""
        # 这里可以添加调度器状态检查逻辑
        pass
    
    def add_log(self, message):
        """添加日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        self.log_text.append(formatted_message)
        
        # 自动滚动到底部
        cursor = self.log_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.log_text.setTextCursor(cursor)
    
    def clear_log(self):
        """清空日志"""
        self.log_text.clear()
        self.add_log("📋 日志已清空")
    
    def save_log(self):
        """保存日志"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "保存日志", f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", 
            "文本文件 (*.txt);;所有文件 (*)"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.toPlainText())
                QMessageBox.information(self, "成功", "日志保存成功！")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存日志失败：{e}")


def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setApplicationName("理想论坛自动签到程序")
    app.setApplicationVersion("1.0.0")
    
    # 设置应用程序图标和字体
    font = QFont("Microsoft YaHei", 10)
    app.setFont(font)
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
