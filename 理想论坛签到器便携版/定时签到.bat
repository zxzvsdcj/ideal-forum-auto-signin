@echo off
chcp 65001 >nul
title 理想论坛定时签到
echo 正在启动定时签到...
echo 按 Ctrl+C 可以停止定时任务
"理想论坛签到器.exe" --schedule
