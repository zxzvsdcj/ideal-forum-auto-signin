#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
理想论坛自动签到定时任务调度器
功能：定时执行签到任务，支持每日自动运行
"""

import schedule
import time
import configparser
import os
import sys
from datetime import datetime
from sign_bot import IdealForumSignBot
from loguru import logger


class SignScheduler:
    """签到任务调度器"""
    
    def __init__(self, config_file='config.ini'):
        """
        初始化调度器
        
        Args:
            config_file: 配置文件路径
        """
        self.config = configparser.ConfigParser()
        self.config.read(config_file, encoding='utf-8')
        self.setup_logging()
        
        # 从配置文件读取调度设置
        self.sign_time = self.config.get('SCHEDULE', 'sign_time')
        self.enable_schedule = self.config.getboolean('SCHEDULE', 'enable_schedule')
        
        logger.info(f"定时任务调度器初始化完成，签到时间: {self.sign_time}")
        
    def setup_logging(self):
        """设置日志记录"""
        log_file = "scheduler_log.txt"
        
        # 配置loguru日志
        logger.remove()  # 移除默认处理器
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level="INFO"
        )
        logger.add(
            log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="INFO",
            rotation="10 MB",
            retention="30 days",
            encoding="utf-8"
        )
    
    def execute_sign_task(self):
        """执行签到任务"""
        try:
            logger.info("🕐 定时签到任务开始执行...")
            
            # 创建签到机器人实例
            bot = IdealForumSignBot()
            
            # 验证配置
            if not bot.validate_config():
                logger.error("配置验证失败，跳过本次签到")
                return False
            
            # 执行签到
            success = bot.sign_in()
            
            if success:
                logger.success("✅ 定时签到任务执行成功！")
                return True
            else:
                logger.error("❌ 定时签到任务执行失败！")
                return False
                
        except Exception as e:
            logger.error(f"💥 定时签到任务执行时发生错误: {e}")
            return False
    
    def setup_schedule(self):
        """设置定时任务"""
        if not self.enable_schedule:
            logger.warning("定时任务未启用，请在config.ini中启用")
            return False
        
        try:
            # 设置每日定时签到
            schedule.every().day.at(self.sign_time).do(self.execute_sign_task)
            logger.info(f"✅ 定时任务设置成功，每日 {self.sign_time} 执行签到")
            
            # 显示下次执行时间
            next_run = schedule.next_run()
            if next_run:
                logger.info(f"📅 下次执行时间: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
            
            return True
            
        except Exception as e:
            logger.error(f"设置定时任务时发生错误: {e}")
            return False
    
    def run_scheduler(self):
        """运行调度器（阻塞模式）"""
        if not self.setup_schedule():
            return
        
        logger.info("🚀 签到调度器已启动，等待执行时间...")
        logger.info("按 Ctrl+C 停止调度器")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # 每分钟检查一次
                
        except KeyboardInterrupt:
            logger.info("⏹️  用户停止了调度器")
        except Exception as e:
            logger.error(f"调度器运行时发生错误: {e}")
        finally:
            logger.info("调度器已停止")
    
    def run_once_now(self):
        """立即执行一次签到任务（测试用）"""
        logger.info("🧪 立即执行签到任务（测试模式）")
        return self.execute_sign_task()
    
    def show_schedule_info(self):
        """显示调度信息"""
        if not self.enable_schedule:
            print("❌ 定时任务未启用")
            return
        
        print(f"📋 调度器配置信息:")
        print(f"   签到时间: {self.sign_time}")
        print(f"   启用状态: {'✅ 已启用' if self.enable_schedule else '❌ 未启用'}")
        
        if schedule.jobs:
            next_run = schedule.next_run()
            if next_run:
                print(f"   下次执行: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print("   当前无定时任务")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='理想论坛自动签到调度器')
    parser.add_argument('--run', action='store_true', help='启动定时调度器')
    parser.add_argument('--test', action='store_true', help='立即执行一次签到任务（测试）')
    parser.add_argument('--info', action='store_true', help='显示调度器配置信息')
    
    args = parser.parse_args()
    
    # 检查配置文件是否存在
    if not os.path.exists('config.ini'):
        print("❌ 未找到config.ini配置文件，请先配置!")
        sys.exit(1)
    
    # 创建调度器实例
    scheduler = SignScheduler()
    
    if args.test:
        # 测试模式：立即执行一次
        print("🧪 测试模式：立即执行签到任务")
        success = scheduler.run_once_now()
        sys.exit(0 if success else 1)
    
    elif args.info:
        # 显示配置信息
        scheduler.show_schedule_info()
        sys.exit(0)
    
    elif args.run:
        # 运行调度器
        scheduler.run_scheduler()
    
    else:
        # 默认显示帮助信息
        parser.print_help()
        print("\n💡 使用示例:")
        print("  python scheduler.py --test    # 立即测试签到功能")
        print("  python scheduler.py --run     # 启动定时调度器")
        print("  python scheduler.py --info    # 显示配置信息")


if __name__ == "__main__":
    main()
