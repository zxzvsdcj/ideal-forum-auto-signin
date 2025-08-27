@echo off
chcp 65001 >nul
title 理想论坛快速签到
echo 正在执行快速签到...
"理想论坛签到器.exe" --sign
echo.
echo 签到完成，5秒后自动关闭...
timeout /t 5 >nul
