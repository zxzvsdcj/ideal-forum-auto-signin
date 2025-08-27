@echo off
chcp 65001 >nul
title 理想论坛自动签到程序

echo.
echo 欢迎使用理想论坛自动签到程序！
echo.
echo 请选择操作：
echo [1] 环境检查和测试
echo [2] 立即执行签到
echo [3] 启动定时签到调度器
echo [4] 显示配置信息
echo [5] 完整功能测试
echo [0] 退出
echo.

:menu
set /p choice=请输入选择 (0-5): 

if "%choice%"=="1" (
    echo.
    echo 正在检查环境...
    python run.py --check
    goto end
)

if "%choice%"=="2" (
    echo.
    echo 正在执行签到...
    python run.py --sign
    goto end
)

if "%choice%"=="3" (
    echo.
    echo 正在启动定时调度器...
    echo 注意：程序将保持运行，按 Ctrl+C 可以停止
    python run.py --schedule
    goto end
)

if "%choice%"=="4" (
    echo.
    echo 显示配置信息...
    python run.py --config
    goto end
)

if "%choice%"=="5" (
    echo.
    echo 运行完整功能测试...
    python run.py --full-test
    goto end
)

if "%choice%"=="0" (
    echo 谢谢使用！
    exit /b 0
)

echo 无效选择，请重新输入
goto menu

:end
echo.
echo 按任意键返回菜单...
pause >nul
goto menu
