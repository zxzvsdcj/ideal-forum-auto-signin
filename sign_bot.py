#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
理想论坛自动签到程序
功能：自动登录理想论坛并完成每日签到任务
"""

import time
import configparser
import os
import sys
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from loguru import logger


class IdealForumSignBot:
    """理想论坛签到机器人"""
    
    def __init__(self, config_file='config.ini'):
        """
        初始化签到机器人
        
        Args:
            config_file: 配置文件路径
        """
        self.config = configparser.ConfigParser()
        self.config.read(config_file, encoding='utf-8')
        self.driver = None
        self.setup_logging()
        
        # 从配置文件读取设置
        self.username = self.config.get('LOGIN', 'username')
        self.password = self.config.get('LOGIN', 'password')
        self.login_timeout = self.config.getint('SETTINGS', 'login_timeout')
        self.page_load_timeout = self.config.getint('SETTINGS', 'page_load_timeout')
        self.retry_count = self.config.getint('SETTINGS', 'retry_count')
        self.headless = self.config.getboolean('SETTINGS', 'headless')
        
        # URL配置
        self.login_url = "https://passport.55188.com/index/login/"
        self.main_site_url = "https://www.55188.com"
        
    def setup_logging(self):
        """设置日志记录"""
        log_file = self.config.get('LOGGING', 'log_file')
        log_level = self.config.get('LOGGING', 'log_level')
        
        # 配置loguru日志
        logger.remove()  # 移除默认处理器
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level=log_level
        )
        logger.add(
            log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level=log_level,
            rotation="10 MB",
            retention="7 days",
            encoding="utf-8"
        )
    
    def setup_driver(self):
        """设置Chrome浏览器驱动"""
        try:
            chrome_options = Options()
            
            if self.headless:
                chrome_options.add_argument('--headless')
            
            # 添加常用的Chrome选项
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-web-security')
            chrome_options.add_argument('--allow-running-insecure-content')
            
            # 设置User-Agent
            user_agent = self.config.get('BROWSER', 'user_agent')
            chrome_options.add_argument(f'--user-agent={user_agent}')
            
            # 设置窗口大小
            window_size = self.config.get('BROWSER', 'window_size')
            chrome_options.add_argument(f'--window-size={window_size}')
            
            # 自动下载和设置ChromeDriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # 设置页面加载超时
            self.driver.set_page_load_timeout(30)
            self.driver.implicitly_wait(10)
            
            logger.info("Chrome浏览器驱动设置成功")
            return True
            
        except Exception as e:
            logger.error(f"设置浏览器驱动失败: {e}")
            return False
    
    def login(self):
        """
        登录理想论坛
        
        Returns:
            bool: 登录是否成功
        """
        try:
            logger.info("开始登录理想论坛...")
            
            # 访问登录页面
            self.driver.get(self.login_url)
            logger.info(f"访问登录页面: {self.login_url}")
            
            # 等待页面加载
            wait = WebDriverWait(self.driver, self.login_timeout)
            
            # 查找并填写用户名
            username_input = wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='用户名/Email/手机号码']"))
            )
            username_input.clear()
            username_input.send_keys(self.username)
            logger.info(f"输入用户名: {self.username}")
            
            # 查找并填写密码
            password_input = self.driver.find_element(By.XPATH, "//input[@placeholder='密码']")
            password_input.clear()
            password_input.send_keys(self.password)
            logger.info("输入密码完成")
            
            # 点击登录按钮
            login_button = self.driver.find_element(By.XPATH, "//button[text()='立即登录']")
            login_button.click()
            logger.info("点击登录按钮")
            
            # 等待登录完成，检查是否出现"退出"按钮
            time.sleep(3)  # 等待页面跳转
            
            # 尝试查找"退出"按钮来确认登录成功
            try:
                logout_element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//*[contains(text(), '退出')]"))
                )
                logger.success("登录成功！检测到退出按钮")
                return True
            except TimeoutException:
                # 如果没找到退出按钮，检查是否有错误信息
                try:
                    error_element = self.driver.find_element(By.CLASS_NAME, "error")
                    error_msg = error_element.text
                    logger.error(f"登录失败，错误信息: {error_msg}")
                except NoSuchElementException:
                    logger.warning("登录状态不明确，未找到退出按钮也未找到错误信息")
                return False
                
        except TimeoutException:
            logger.error("登录超时，页面元素加载失败")
            return False
        except Exception as e:
            logger.error(f"登录过程中发生错误: {e}")
            return False
    
    def find_and_click_sign_button(self):
        """
        查找并点击签到按钮
        
        Returns:
            bool: 是否成功点击签到按钮
        """
        try:
            logger.info("开始查找签到按钮...")
            
            # 首先尝试访问主站页面
            self.driver.get(self.main_site_url)
            time.sleep(2)
            
            wait = WebDriverWait(self.driver, 15)
            
            # 尝试多种方式查找签到按钮
            sign_selectors = [
                "//a[contains(text(), '签到')]",
                "//button[contains(text(), '签到')]",
                "//div[contains(text(), '签到')]",
                "//span[contains(text(), '签到')]",
                "//a[@href*='sign']",
                "//a[contains(@class, 'sign')]"
            ]
            
            sign_button = None
            for selector in sign_selectors:
                try:
                    sign_button = wait.until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    logger.info(f"找到签到按钮，选择器: {selector}")
                    break
                except TimeoutException:
                    continue
            
            if sign_button is None:
                logger.error("未找到签到按钮")
                return False
            
            # 点击签到按钮
            self.driver.execute_script("arguments[0].click();", sign_button)
            logger.info("点击签到按钮")
            time.sleep(3)  # 等待页面响应
            
            return True
            
        except Exception as e:
            logger.error(f"查找或点击签到按钮时发生错误: {e}")
            return False
    
    def check_sign_success(self):
        """
        检查签到是否成功
        
        Returns:
            bool: 签到是否成功
        """
        try:
            logger.info("检查签到状态...")
            
            # 等待页面加载
            time.sleep(3)
            
            # 查找"今日已签到"标志
            success_indicators = [
                "//*[contains(text(), '今日已签到')]",
                "//*[contains(text(), '已签到')]",
                "//*[contains(text(), '签到成功')]",
                "//*[contains(text(), '今天已经签到')]"
            ]
            
            for indicator in success_indicators:
                try:
                    success_element = self.driver.find_element(By.XPATH, indicator)
                    if success_element:
                        logger.success(f"签到成功！找到成功标志: {success_element.text}")
                        return True
                except NoSuchElementException:
                    continue
            
            # 如果没找到成功标志，检查是否有已签到的其他提示
            already_signed_indicators = [
                "//*[contains(text(), '您今日已经签到')]",
                "//*[contains(text(), '重复签到')]"
            ]
            
            for indicator in already_signed_indicators:
                try:
                    element = self.driver.find_element(By.XPATH, indicator)
                    if element:
                        logger.info(f"今日已经签到过了: {element.text}")
                        return True
                except NoSuchElementException:
                    continue
            
            logger.warning("未找到签到成功的确认信息")
            return False
            
        except Exception as e:
            logger.error(f"检查签到状态时发生错误: {e}")
            return False
    
    def sign_in(self):
        """
        执行完整的签到流程
        
        Returns:
            bool: 签到是否成功
        """
        success = False
        
        try:
            # 设置浏览器驱动
            if not self.setup_driver():
                return False
            
            # 执行登录
            if not self.login():
                logger.error("登录失败，终止签到流程")
                return False
            
            # 查找并点击签到按钮
            if not self.find_and_click_sign_button():
                logger.error("点击签到按钮失败")
                return False
            
            # 检查签到是否成功
            success = self.check_sign_success()
            
            if success:
                logger.success("🎉 签到流程完成！")
            else:
                logger.error("❌ 签到流程失败")
                
        except Exception as e:
            logger.error(f"签到流程中发生未预期的错误: {e}")
            
        finally:
            # 清理资源
            if self.driver:
                try:
                    self.driver.quit()
                    logger.info("浏览器驱动已关闭")
                except Exception as e:
                    logger.warning(f"关闭浏览器驱动时发生错误: {e}")
        
        return success
    
    def validate_config(self):
        """验证配置文件"""
        if not self.username or self.username == 'your_username_here':
            logger.error("请在config.ini中配置正确的用户名")
            return False
        
        if not self.password or self.password == 'your_password_here':
            logger.error("请在config.ini中配置正确的密码")
            return False
        
        return True


def main():
    """主函数"""
    print("🚀 理想论坛自动签到程序启动")
    print("=" * 50)
    
    # 检查配置文件是否存在
    if not os.path.exists('config.ini'):
        print("❌ 未找到config.ini配置文件，请先配置!")
        sys.exit(1)
    
    # 创建签到机器人实例
    bot = IdealForumSignBot()
    
    # 验证配置
    if not bot.validate_config():
        sys.exit(1)
    
    # 执行签到
    try:
        success = bot.sign_in()
        if success:
            print("✅ 签到成功完成！")
            sys.exit(0)
        else:
            print("❌ 签到失败！")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️  用户中断程序")
        sys.exit(0)
    except Exception as e:
        print(f"💥 程序执行错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
