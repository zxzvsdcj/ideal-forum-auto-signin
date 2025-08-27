#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
理想论坛自动签到测试脚本
功能：测试自动签到功能的各个组件
"""

import os
import sys
import time
import configparser
from sign_bot import IdealForumSignBot
from scheduler import SignScheduler


def test_config_file():
    """测试配置文件是否正确"""
    print("🔍 测试配置文件...")
    
    if not os.path.exists('config.ini'):
        print("❌ config.ini 文件不存在")
        return False
    
    try:
        config = configparser.ConfigParser()
        config.read('config.ini', encoding='utf-8')
        
        # 检查必要的配置项
        required_sections = ['LOGIN', 'SETTINGS', 'SCHEDULE', 'BROWSER', 'LOGGING']
        for section in required_sections:
            if not config.has_section(section):
                print(f"❌ 配置文件缺少 [{section}] 部分")
                return False
        
        # 检查登录配置
        username = config.get('LOGIN', 'username')
        password = config.get('LOGIN', 'password')
        
        if username == 'your_username_here' or not username:
            print("❌ 请在config.ini中配置正确的用户名")
            return False
        
        if password == 'your_password_here' or not password:
            print("❌ 请在config.ini中配置正确的密码")
            return False
        
        print(f"✅ 配置文件检查通过")
        print(f"   用户名: {username}")
        print(f"   签到时间: {config.get('SCHEDULE', 'sign_time')}")
        return True
        
    except Exception as e:
        print(f"❌ 配置文件格式错误: {e}")
        return False


def test_dependencies():
    """测试依赖包是否安装"""
    print("\n🔍 测试依赖包...")
    
    dependencies = [
        'selenium',
        'configparser',
        'schedule',
        'webdriver_manager',
        'loguru'
    ]
    
    missing_deps = []
    
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep}")
        except ImportError:
            print(f"❌ {dep} - 未安装")
            missing_deps.append(dep)
    
    if missing_deps:
        print(f"\n💡 请安装缺失的依赖包:")
        print(f"   pip install {' '.join(missing_deps)}")
        return False
    
    print("✅ 所有依赖包检查通过")
    return True


def test_bot_initialization():
    """测试机器人初始化"""
    print("\n🔍 测试机器人初始化...")
    
    try:
        bot = IdealForumSignBot()
        
        if not bot.validate_config():
            print("❌ 配置验证失败")
            return False
        
        print("✅ 机器人初始化成功")
        return True
        
    except Exception as e:
        print(f"❌ 机器人初始化失败: {e}")
        return False


def test_browser_setup():
    """测试浏览器设置（无头模式）"""
    print("\n🔍 测试浏览器设置...")
    
    try:
        bot = IdealForumSignBot()
        
        # 临时设置为无头模式进行测试
        original_headless = bot.headless
        bot.headless = True
        
        success = bot.setup_driver()
        
        if success and bot.driver:
            print("✅ 浏览器驱动设置成功")
            bot.driver.quit()
            return True
        else:
            print("❌ 浏览器驱动设置失败")
            return False
            
    except Exception as e:
        print(f"❌ 浏览器设置测试失败: {e}")
        return False


def test_login_page_access():
    """测试登录页面访问"""
    print("\n🔍 测试登录页面访问...")
    
    try:
        bot = IdealForumSignBot()
        bot.headless = True  # 使用无头模式测试
        
        if not bot.setup_driver():
            print("❌ 浏览器驱动设置失败")
            return False
        
        # 访问登录页面
        bot.driver.get(bot.login_url)
        time.sleep(3)
        
        # 检查页面标题
        title = bot.driver.title
        if "登录" in title or "理想" in title:
            print(f"✅ 登录页面访问成功，页面标题: {title}")
            bot.driver.quit()
            return True
        else:
            print(f"❌ 登录页面访问异常，页面标题: {title}")
            bot.driver.quit()
            return False
            
    except Exception as e:
        print(f"❌ 登录页面访问测试失败: {e}")
        return False


def test_scheduler_setup():
    """测试调度器设置"""
    print("\n🔍 测试调度器设置...")
    
    try:
        scheduler = SignScheduler()
        
        if scheduler.setup_schedule():
            print("✅ 调度器设置成功")
            return True
        else:
            print("❌ 调度器设置失败")
            return False
            
    except Exception as e:
        print(f"❌ 调度器设置测试失败: {e}")
        return False


def run_full_test():
    """运行完整功能测试（实际登录和签到）"""
    print("\n🧪 运行完整功能测试（实际登录和签到）...")
    print("⚠️  这将使用真实的用户名密码进行登录测试")
    
    confirm = input("是否继续？(y/N): ").lower().strip()
    if confirm != 'y':
        print("❌ 用户取消了完整功能测试")
        return False
    
    try:
        bot = IdealForumSignBot()
        success = bot.sign_in()
        
        if success:
            print("✅ 完整功能测试成功！")
            return True
        else:
            print("❌ 完整功能测试失败")
            return False
            
    except Exception as e:
        print(f"❌ 完整功能测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("🚀 理想论坛自动签到功能测试")
    print("=" * 50)
    
    tests = [
        ("配置文件测试", test_config_file),
        ("依赖包测试", test_dependencies),
        ("机器人初始化测试", test_bot_initialization),
        ("浏览器设置测试", test_browser_setup),
        ("登录页面访问测试", test_login_page_access),
        ("调度器设置测试", test_scheduler_setup),
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    # 运行基础测试
    for test_name, test_func in tests:
        try:
            if test_func():
                passed_tests += 1
        except KeyboardInterrupt:
            print("\n⏹️  用户中断测试")
            sys.exit(0)
        except Exception as e:
            print(f"❌ {test_name} 执行异常: {e}")
    
    print(f"\n📊 基础测试结果: {passed_tests}/{total_tests} 通过")
    
    if passed_tests == total_tests:
        print("✅ 所有基础测试通过！")
        
        # 询问是否进行完整功能测试
        print("\n" + "=" * 50)
        run_full_test()
    else:
        print("❌ 存在失败的测试，请检查配置和环境")
        sys.exit(1)


if __name__ == "__main__":
    main()
