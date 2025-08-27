#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
理想论坛登录测试脚本（可视化模式）
功能：测试登录功能，浏览器可见，方便调试
"""

import os
import sys
import time
import configparser
from sign_bot import IdealForumSignBot


def test_login_with_visible_browser():
    """测试登录功能（可视化浏览器）"""
    print("🧪 理想论坛登录测试（可视化模式）")
    print("=" * 50)
    
    # 检查配置文件
    if not os.path.exists('config.ini'):
        print("❌ 未找到config.ini配置文件，请先配置!")
        return False
    
    try:
        # 创建签到机器人实例
        bot = IdealForumSignBot()
        
        # 强制设置为非无头模式
        bot.headless = False
        
        # 验证配置
        if not bot.validate_config():
            print("❌ 配置验证失败")
            return False
        
        print(f"📋 配置信息:")
        print(f"   用户名: {bot.username}")
        print(f"   无头模式: {bot.headless}")
        print()
        
        # 设置浏览器驱动
        print("🔧 设置浏览器驱动...")
        if not bot.setup_driver():
            print("❌ 浏览器驱动设置失败")
            return False
        
        print("✅ 浏览器已启动，你现在可以看到浏览器窗口")
        print()
        
        # 执行登录测试
        print("🚀 开始登录测试...")
        success = bot.login()
        
        if success:
            print("✅ 登录测试成功！")
            
            # 等待用户观察
            print("\n🔍 登录成功，浏览器将保持打开5秒供您观察...")
            time.sleep(5)
            
            # 测试访问主页面查找签到按钮
            print("\n🎯 尝试访问主页面查找签到按钮...")
            try:
                bot.driver.get("https://www.55188.com")
                time.sleep(3)
                
                # 查找签到按钮
                sign_selectors = [
                    "//a[contains(text(), '签到')]",
                    "//button[contains(text(), '签到')]",
                    "//div[contains(text(), '签到')]",
                    "//span[contains(text(), '签到')]",
                    "//a[@href*='sign']"
                ]
                
                found_sign_button = False
                for selector in sign_selectors:
                    try:
                        elements = bot.driver.find_elements(By.XPATH, selector)
                        if elements:
                            print(f"✅ 找到签到相关元素: {selector}")
                            for elem in elements:
                                print(f"   元素文本: {elem.text[:50]}...")
                            found_sign_button = True
                            break
                    except Exception as e:
                        continue
                
                if not found_sign_button:
                    print("⚠️ 未找到明显的签到按钮，可能需要调整定位策略")
                
                print("\n🔍 主页面将保持打开5秒供您观察...")
                time.sleep(5)
                
            except Exception as e:
                print(f"❌ 访问主页面时发生错误: {e}")
            
        else:
            print("❌ 登录测试失败")
            
            # 等待用户观察错误状态
            print("\n🔍 登录失败，浏览器将保持打开10秒供您观察错误原因...")
            time.sleep(10)
        
        return success
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        return False
    
    finally:
        # 询问用户是否关闭浏览器
        try:
            input("\n按Enter键关闭浏览器...")
        except:
            time.sleep(3)
        
        # 关闭浏览器
        if 'bot' in locals() and bot.driver:
            try:
                bot.driver.quit()
                print("🔧 浏览器已关闭")
            except:
                pass


def main():
    """主函数"""
    print("🎯 理想论坛登录可视化测试")
    print("这个测试将打开可见的浏览器窗口，方便您观察登录过程")
    print()
    
    # 导入必要的模块
    try:
        from selenium.webdriver.common.by import By
        globals()['By'] = By
    except ImportError:
        print("❌ 请确保已安装selenium: pip install selenium")
        return
    
    # 运行测试
    success = test_login_with_visible_browser()
    
    if success:
        print("\n🎉 测试完成：登录功能正常")
    else:
        print("\n❌ 测试完成：登录功能存在问题，请检查配置和网络")


if __name__ == "__main__":
    main()
