#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
邮件通知模块
功能：发送签到结果通知邮件
"""

import smtplib
import configparser
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from loguru import logger


class EmailNotifier:
    """邮件通知类"""
    
    def __init__(self, config_file='config.ini'):
        """
        初始化邮件通知器
        
        Args:
            config_file: 配置文件路径
        """
        self.config = configparser.ConfigParser()
        self.config.read(config_file, encoding='utf-8')
        
        # 读取邮件配置
        self.enable_email = self.config.getboolean('EMAIL', 'enable_email', fallback=False)
        if not self.enable_email:
            logger.info("邮件通知功能未启用")
            return
            
        self.smtp_server = self.config.get('EMAIL', 'smtp_server')
        self.smtp_port = self.config.getint('EMAIL', 'smtp_port')
        self.sender_email = self.config.get('EMAIL', 'sender_email')
        self.sender_password = self.config.get('EMAIL', 'sender_password')
        self.receiver_email = self.config.get('EMAIL', 'receiver_email')
        self.email_subject = self.config.get('EMAIL', 'email_subject')
        self.notify_on_success = self.config.getboolean('EMAIL', 'notify_on_success', fallback=True)
        self.notify_on_failure = self.config.getboolean('EMAIL', 'notify_on_failure', fallback=True)
        
        logger.info("邮件通知器初始化完成")
    
    def send_notification(self, success, message="", additional_info=None):
        """
        发送签到通知邮件
        
        Args:
            success (bool): 签到是否成功
            message (str): 附加消息
            additional_info (dict): 额外信息，如签到排名等
        """
        if not self.enable_email:
            return
        
        # 根据配置决定是否发送
        if success and not self.notify_on_success:
            return
        if not success and not self.notify_on_failure:
            return
        
        try:
            # 构建邮件内容
            email_body = self._build_email_content(success, message, additional_info)
            
            # 创建邮件
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = self.receiver_email
            msg['Subject'] = self._build_subject(success)
            
            # 添加邮件正文
            msg.attach(MIMEText(email_body, 'html', 'utf-8'))
            
            # 发送邮件
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            logger.success(f"邮件通知发送成功: {self.receiver_email}")
            
        except Exception as e:
            logger.error(f"发送邮件通知失败: {e}")
    
    def _build_subject(self, success):
        """构建邮件主题"""
        status = "成功" if success else "失败"
        current_time = datetime.now().strftime("%Y-%m-%d")
        return f"{self.email_subject} - {status} ({current_time})"
    
    def _build_email_content(self, success, message, additional_info):
        """构建邮件内容"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "✅ 成功" if success else "❌ 失败"
        status_color = "#4CAF50" if success else "#F44336"
        
        # 构建额外信息部分
        extra_info_html = ""
        if additional_info:
            extra_info_html = "<h3>📊 签到信息</h3><ul>"
            for key, value in additional_info.items():
                extra_info_html += f"<li><strong>{key}:</strong> {value}</li>"
            extra_info_html += "</ul>"
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>理想论坛签到通知</title>
            <style>
                body {{
                    font-family: 'Microsoft YaHei', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .container {{
                    background: white;
                    border-radius: 10px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    overflow: hidden;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px 20px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 24px;
                }}
                .content {{
                    padding: 30px 20px;
                }}
                .status {{
                    text-align: center;
                    margin: 20px 0;
                    padding: 20px;
                    border-radius: 8px;
                    background-color: {status_color};
                    color: white;
                    font-size: 18px;
                    font-weight: bold;
                }}
                .info-box {{
                    background: #f8f9fa;
                    border-left: 4px solid #667eea;
                    padding: 15px;
                    margin: 20px 0;
                    border-radius: 4px;
                }}
                .info-box h3 {{
                    margin-top: 0;
                    color: #667eea;
                }}
                .info-box ul {{
                    margin: 10px 0;
                    padding-left: 20px;
                }}
                .info-box li {{
                    margin: 5px 0;
                }}
                .footer {{
                    background: #f8f9fa;
                    padding: 20px;
                    text-align: center;
                    color: #666;
                    border-top: 1px solid #e9ecef;
                }}
                .time {{
                    color: #666;
                    font-size: 14px;
                    text-align: center;
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎯 理想论坛自动签到通知</h1>
                </div>
                
                <div class="content">
                    <div class="status">
                        签到状态: {status}
                    </div>
                    
                    <div class="time">
                        📅 通知时间: {current_time}
                    </div>
                    
                    {f'<div class="info-box"><h3>📝 详细信息</h3><p>{message}</p></div>' if message else ''}
                    
                    {f'<div class="info-box">{extra_info_html}</div>' if extra_info_html else ''}
                    
                    <div class="info-box">
                        <h3>🔧 系统信息</h3>
                        <ul>
                            <li><strong>程序版本:</strong> v1.0.0</li>
                            <li><strong>运行模式:</strong> 自动签到</li>
                            <li><strong>通知类型:</strong> 邮件通知</li>
                        </ul>
                    </div>
                </div>
                
                <div class="footer">
                    <p>💡 这是一条自动生成的通知邮件</p>
                    <p>如需修改通知设置，请编辑 config.ini 文件中的 [EMAIL] 部分</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def test_email_config(self):
        """测试邮件配置"""
        if not self.enable_email:
            logger.warning("邮件通知功能未启用，请在config.ini中设置 enable_email = true")
            return False
        
        # 检查必要的配置项
        required_fields = {
            'smtp_server': self.smtp_server,
            'sender_email': self.sender_email,
            'sender_password': self.sender_password,
            'receiver_email': self.receiver_email
        }
        
        missing_fields = []
        for field, value in required_fields.items():
            if not value or value.startswith('your_'):
                missing_fields.append(field)
        
        if missing_fields:
            logger.error(f"邮件配置不完整，缺少或未正确设置: {', '.join(missing_fields)}")
            return False
        
        try:
            # 测试SMTP连接
            logger.info("测试SMTP连接...")
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
            
            logger.success("邮件配置测试成功!")
            return True
            
        except Exception as e:
            logger.error(f"邮件配置测试失败: {e}")
            return False
    
    def send_test_email(self):
        """发送测试邮件"""
        if not self.enable_email:
            logger.warning("邮件通知功能未启用")
            return False
        
        try:
            test_info = {
                "测试类型": "配置测试",
                "测试时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "配置状态": "正常"
            }
            
            self.send_notification(
                success=True,
                message="这是一封测试邮件，用于验证邮件通知功能是否正常工作。",
                additional_info=test_info
            )
            return True
            
        except Exception as e:
            logger.error(f"发送测试邮件失败: {e}")
            return False


def main():
    """测试邮件功能"""
    print("🧪 测试邮件通知功能")
    print("=" * 50)
    
    notifier = EmailNotifier()
    
    if not notifier.enable_email:
        print("❌ 邮件功能未启用，请在config.ini中配置")
        return
    
    # 测试配置
    print("🔧 测试邮件配置...")
    if notifier.test_email_config():
        print("✅ 邮件配置测试通过")
        
        # 发送测试邮件
        print("📧 发送测试邮件...")
        if notifier.send_test_email():
            print("✅ 测试邮件发送成功")
        else:
            print("❌ 测试邮件发送失败")
    else:
        print("❌ 邮件配置测试失败")


if __name__ == "__main__":
    main()
