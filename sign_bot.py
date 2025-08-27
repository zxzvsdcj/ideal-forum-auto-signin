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
from email_notifier import EmailNotifier


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
        
        # 初始化邮件通知器
        self.email_notifier = EmailNotifier(config_file)
        
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
            try:
                username_input = wait.until(
                    EC.presence_of_element_located((By.XPATH, "//input[@placeholder='用户名/Email/手机号码']"))
                )
                username_input.clear()
                username_input.send_keys(self.username)
                logger.info(f"输入用户名: {self.username}")
            except Exception as e:
                logger.warning(f"用户名输入框定位失败，尝试其他方式: {e}")
                # 尝试其他定位方式
                username_input = wait.until(
                    EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder, '用户名') or contains(@placeholder, '手机') or contains(@placeholder, 'Email')]"))
                )
                username_input.clear()
                username_input.send_keys(self.username)
                logger.info(f"使用备用方式输入用户名: {self.username}")
            
            # 查找并填写密码
            try:
                password_input = self.driver.find_element(By.XPATH, "//input[@placeholder='密码']")
                password_input.clear()
                password_input.send_keys(self.password)
                logger.info("输入密码完成")
            except Exception as e:
                logger.warning(f"密码输入框定位失败，尝试其他方式: {e}")
                # 尝试其他定位方式
                password_input = self.driver.find_element(By.XPATH, "//input[@type='password']")
                password_input.clear()
                password_input.send_keys(self.password)
                logger.info("使用备用方式输入密码完成")
            
            # 检查是否有验证码需要处理
            try:
                # 检查是否有Geetest验证码
                captcha_element = self.driver.find_element(By.XPATH, "//div[contains(@class, 'geetest') or contains(text(), '验证') or contains(text(), '点击')]")
                if captcha_element:
                    logger.warning("检测到验证码，请手动完成验证码验证...")
                    logger.info("程序将等待30秒供用户手动完成验证码")
                    
                    # 等待验证码完成或者30秒超时
                    for i in range(30):
                        try:
                            # 检查验证码是否消失或登录按钮变为可点击
                            login_button = self.driver.find_element(By.XPATH, "//button[contains(text(), '立即登录')]")
                            if login_button and login_button.is_enabled():
                                logger.info("验证码似乎已完成，继续登录流程")
                                break
                        except:
                            pass
                        time.sleep(1)
                        if i % 5 == 0:
                            logger.info(f"等待验证码完成... ({30-i}秒)")
            except:
                logger.info("未检测到验证码，继续登录流程")
            
            # 查找并点击登录按钮 - 优化版本，减少备用方式调用
            login_selectors = [
                "//button[contains(text(), '立即登录')]",  # 最常见的情况
                "//button[text()='立即登录']",           # 精确匹配
                "//input[@value='立即登录']",            # input按钮
                "//button[@type='submit']",             # 提交按钮
                "//input[@type='submit']",              # 提交输入框
                "//a[contains(text(), '登录')]"         # 链接形式
            ]
            
            login_button = None
            successful_selector = None
            
            # 依次尝试所有选择器，找到第一个可用的
            for i, selector in enumerate(login_selectors):
                try:
                    if i == 0:
                        # 第一个选择器使用等待机制
                        login_button = wait.until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                    else:
                        # 其他选择器直接查找
                        login_button = self.driver.find_element(By.XPATH, selector)
                        
                    if login_button and login_button.is_enabled():
                        successful_selector = selector
                        break
                        
                except Exception as e:
                    if i == 0:
                        logger.debug(f"主要选择器失败: {selector}")
                    continue
            
            if login_button and successful_selector:
                try:
                    login_button.click()
                    if successful_selector == login_selectors[0]:
                        logger.info("点击登录按钮")
                    else:
                        logger.info(f"使用备用选择器点击登录按钮: {successful_selector}")
                except Exception as e:
                    logger.warning(f"点击登录按钮时发生错误: {e}")
                    raise Exception("登录按钮点击失败")
            else:
                raise Exception("无法找到可用的登录按钮")
            
            # 等待登录完成，检查是否出现"退出"按钮
            logger.info("等待登录完成...")
            time.sleep(5)  # 增加等待时间，等待页面跳转
            
            # 尝试查找"退出"按钮来确认登录成功
            try:
                # 多种方式检测登录成功
                success_indicators = [
                    "//*[contains(text(), '退出')]",
                    "//a[contains(text(), '退出')]",
                    "//link[contains(text(), '退出')]",
                    "//div[contains(@class, 'logout')]",
                    "//*[contains(text(), 'UID')]",  # 用户ID显示
                    "//*[contains(text(), '个人资料')]"  # 个人资料链接
                ]
                
                login_success = False
                for indicator in success_indicators:
                    try:
                        element = WebDriverWait(self.driver, 3).until(
                            EC.presence_of_element_located((By.XPATH, indicator))
                        )
                        if element:
                            logger.success(f"登录成功！检测到成功指示器: {element.text[:20]}...")
                            login_success = True
                            break
                    except TimeoutException:
                        continue
                
                if login_success:
                    return True
                else:
                    # 检查当前URL是否变化
                    current_url = self.driver.current_url
                    if "login" not in current_url and "passport.55188.com" in current_url:
                        logger.success("登录成功！URL已跳转到用户页面")
                        return True
                    
                    logger.warning("登录状态不明确，未找到明确的成功指示器")
                    return False
                    
            except Exception as e:
                logger.error(f"检查登录状态时发生错误: {e}")
                
                # 最后尝试检查是否有错误信息
                try:
                    error_selectors = [
                        "//div[contains(@class, 'error')]",
                        "//span[contains(@class, 'error')]",
                        "//*[contains(text(), '错误')]",
                        "//*[contains(text(), '失败')]",
                        "//*[contains(text(), '验证码')]"
                    ]
                    
                    for selector in error_selectors:
                        try:
                            error_element = self.driver.find_element(By.XPATH, selector)
                            if error_element:
                                error_msg = error_element.text
                                logger.error(f"登录失败，错误信息: {error_msg}")
                                return False
                        except:
                            continue
                    
                    logger.warning("未找到明确的错误信息")
                except Exception as e2:
                    logger.error(f"检查错误信息时发生异常: {e2}")
                
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
            
            # 查找"今日已签到"标志或签到页面特征
            success_indicators = [
                "//*[contains(text(), '今日已签到')]",
                "//*[contains(text(), '已签到')]", 
                "//*[contains(text(), '签到成功')]",
                "//*[contains(text(), '今天已经签到')]",
                "//*[contains(text(), '您的签到排名')]",  # 签到页面特有的元素
                "//*[contains(text(), '连续签到')]",      # 连续签到天数
                "//*[contains(text(), '总天数')]",        # 总签到天数
                "//*[contains(text(), '签到等级')]",      # 签到等级
                "//*[contains(text(), '今日签到人数')]",  # 今日签到人数统计
                "//h1[contains(text(), '每日签到')]"     # 签到页面标题
            ]
            
            signed_indicators_found = 0
            for indicator in success_indicators:
                try:
                    success_element = self.driver.find_element(By.XPATH, indicator)
                    if success_element:
                        logger.info(f"找到签到相关元素: {success_element.text[:30]}...")
                        signed_indicators_found += 1
                        
                        # 特别检查签到排名，这是已签到的明确标志
                        if "签到排名" in success_element.text:
                            logger.success(f"签到成功！检测到签到排名信息: {success_element.text}")
                            return True
                            
                except NoSuchElementException:
                    continue
            
            # 如果找到3个或以上签到相关元素，认为已经在签到页面且已签到
            if signed_indicators_found >= 3:
                logger.success(f"签到成功！检测到{signed_indicators_found}个签到相关元素，确认已在签到页面")
                return True
            
            # 检查当前URL是否为签到页面
            current_url = self.driver.current_url
            if "plugin.php?id=sign" in current_url:
                logger.success("签到成功！当前页面为签到页面，说明签到操作已完成")
                return True
            
            # 如果没找到成功标志，检查是否有已签到的其他提示
            already_signed_indicators = [
                "//*[contains(text(), '您今日已经签到')]",
                "//*[contains(text(), '重复签到')]",
                "//*[contains(text(), '今天已经签到了')]"
            ]
            
            for indicator in already_signed_indicators:
                try:
                    element = self.driver.find_element(By.XPATH, indicator)
                    if element:
                        logger.info(f"今日已经签到过了: {element.text}")
                        return True
                except NoSuchElementException:
                    continue
            
            logger.warning(f"未找到明确的签到成功确认信息，找到{signed_indicators_found}个相关元素")
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
            
            # 获取签到信息发送邮件通知
            sign_info = {}
            try:
                # 尝试获取签到排名信息
                ranking_element = self.driver.find_element(By.XPATH, "//*[contains(text(), '您的签到排名')]")
                if ranking_element:
                    sign_info["签到排名"] = ranking_element.text.replace("您的签到排名：", "").strip()
            except:
                pass
            
            try:
                # 尝试获取连续签到天数
                continuous_element = self.driver.find_element(By.XPATH, "//*[contains(text(), '连续签到')]/following-sibling::*")
                if continuous_element:
                    sign_info["连续签到"] = continuous_element.text.strip()
            except:
                pass
            
            try:
                # 尝试获取总签到天数
                total_element = self.driver.find_element(By.XPATH, "//*[contains(text(), '总天数')]/following-sibling::*")
                if total_element:
                    sign_info["总签到天数"] = total_element.text.strip()
            except:
                pass
            
            # 发送成功通知邮件
            self.email_notifier.send_notification(
                success=True,
                message="恭喜！今日签到任务已成功完成。",
                additional_info=sign_info if sign_info else None
            )
        else:
            logger.error("❌ 签到流程失败")
            
            # 发送失败通知邮件
            self.email_notifier.send_notification(
                success=False,
                message="很遗憾，今日签到任务执行失败，请检查网络连接和账户状态。"
            )
                
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
