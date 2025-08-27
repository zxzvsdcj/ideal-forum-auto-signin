# 理想论坛自动签到程序

一个基于Python + Selenium的理想论坛自动签到工具，支持定时任务和多种运行模式。

## 🚀 功能特性

- ✅ **自动登录**: 支持用户名/手机号/邮箱登录
- ✅ **自动签到**: 智能查找并点击签到按钮
- ✅ **定时任务**: 支持每日定时自动签到
- ✅ **状态检测**: 自动检测登录状态和签到结果
- ✅ **日志记录**: 详细的操作日志和错误记录
- ✅ **配置灵活**: 支持配置文件自定义各种参数
- ✅ **测试功能**: 完整的测试脚本验证功能
- ✅ **错误处理**: 完善的异常处理和重试机制

## 📋 系统要求

- Python 3.7+
- Chrome 浏览器
- Windows/macOS/Linux

## 🛠️ 安装说明

### 1. 克隆或下载项目
```bash
git clone <项目地址>
cd 理想论坛签到器
```

### 2. 安装依赖包
```bash
pip install -r requirements.txt
```

### 3. 配置登录信息
编辑 `config.ini` 文件，填入您的登录信息：

```ini
[LOGIN]
username = your_username_here    # 改为您的用户名/手机号/邮箱
password = your_password_here    # 改为您的密码

[SCHEDULE]
sign_time = 09:00               # 每日签到时间
enable_schedule = true          # 是否启用定时任务
```

## 📖 使用方法

### 快速开始

1. **环境检查**
```bash
python run.py --check
```

2. **测试配置**
```bash
python run.py --test
```

3. **立即签到**
```bash
python run.py --sign
```

4. **启动定时签到**
```bash
python run.py --schedule
```

### 详细命令

| 命令 | 功能 | 说明 |
|------|------|------|
| `python run.py --check` | 环境检查 | 检查依赖包和配置文件 |
| `python run.py --test` | 基础测试 | 测试环境配置但不实际登录 |
| `python run.py --sign` | 立即签到 | 立即执行一次签到任务 |
| `python run.py --schedule` | 定时签到 | 启动定时签到调度器 |
| `python run.py --config` | 显示配置 | 查看当前配置信息 |
| `python run.py --full-test` | 完整测试 | 实际登录测试（需要用户确认） |

### 高级用法

**直接使用核心模块：**
```bash
# 直接运行签到程序
python sign_bot.py

# 使用调度器
python scheduler.py --run      # 启动调度器
python scheduler.py --test     # 立即测试签到
python scheduler.py --info     # 显示调度信息

# 运行测试
python test_sign.py
```

## ⚙️ 配置说明

### config.ini 配置文件详解

```ini
[LOGIN]
# 理想论坛登录配置
username = your_username_here    # 用户名/手机号/邮箱
password = your_password_here    # 登录密码

[SETTINGS]
# 基础设置
login_timeout = 10              # 登录超时时间（秒）
page_load_timeout = 5           # 页面加载超时时间（秒）
retry_count = 3                 # 失败重试次数
headless = true                 # 无头模式（true/false）

[SCHEDULE]
# 定时任务设置
sign_time = 09:00              # 签到时间（24小时格式）
enable_schedule = true         # 启用定时任务（true/false）

[BROWSER]
# 浏览器设置
user_agent = Mozilla/5.0...    # User-Agent
window_size = 1920,1080        # 窗口大小

[LOGGING]
# 日志设置
log_level = INFO               # 日志级别（DEBUG/INFO/WARNING/ERROR）
log_file = sign_log.txt        # 日志文件名
max_log_size = 10MB           # 最大日志文件大小
backup_count = 5              # 日志文件备份数量
```

## 📁 项目结构

```
理想论坛签到器/
├── config.ini          # 配置文件
├── requirements.txt     # 依赖包列表
├── run.py              # 主启动脚本
├── sign_bot.py         # 核心签到逻辑
├── scheduler.py        # 定时任务调度器
├── test_sign.py        # 测试脚本
├── README.md           # 说明文档
├── sign_log.txt        # 签到日志（运行后生成）
└── scheduler_log.txt   # 调度器日志（运行后生成）
```

## 🔍 工作流程

1. **访问登录页面**: `https://passport.55188.com/index/login/`
2. **输入登录信息**: 自动填写用户名和密码
3. **点击登录按钮**: 提交登录表单
4. **验证登录状态**: 检查页面是否出现"退出"按钮
5. **查找签到按钮**: 在主页面查找签到相关按钮
6. **执行签到操作**: 点击签到按钮
7. **验证签到结果**: 检查是否出现"今日已签到"提示

## 📊 日志说明

程序运行时会生成两个日志文件：

- **sign_log.txt**: 签到操作的详细日志
- **scheduler_log.txt**: 定时任务调度的日志

日志级别说明：
- `INFO`: 一般信息（绿色）
- `SUCCESS`: 成功操作（绿色加粗）
- `WARNING`: 警告信息（黄色）
- `ERROR`: 错误信息（红色）

## ❗ 常见问题

### 1. Chrome浏览器相关问题

**问题**: 找不到Chrome浏览器或驱动
**解决**: 
- 确保已安装Chrome浏览器
- 程序会自动下载ChromeDriver，请确保网络连接正常

### 2. 登录失败

**问题**: 提示用户名密码错误
**解决**:
- 检查config.ini中的用户名密码是否正确
- 确认账号没有被冻结或需要验证码
- 尝试手动登录网站确认账号状态

### 3. 签到按钮找不到

**问题**: 程序无法找到签到按钮
**解决**:
- 网站页面结构可能发生变化
- 检查是否已经签到过了
- 运行测试模式查看详细日志

### 4. 定时任务不工作

**问题**: 定时任务没有在指定时间执行
**解决**:
- 确保config.ini中enable_schedule = true
- 检查sign_time格式是否正确（HH:MM）
- 程序需要保持运行状态

### 5. 权限错误

**问题**: 文件读写权限错误
**解决**:
- 确保有写入日志文件的权限
- 在Windows上可能需要以管理员身份运行

## 🔧 故障排除

### 1. 运行环境检查
```bash
python run.py --check
```

### 2. 查看详细日志
```bash
# 查看签到日志
cat sign_log.txt

# 查看调度器日志  
cat scheduler_log.txt
```

### 3. 测试网络连接
```bash
# 测试是否能访问理想论坛
ping www.55188.com
```

### 4. 重新安装依赖
```bash
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

## 🛡️ 安全说明

- 配置文件包含敏感信息，请妥善保管
- 建议在个人电脑上使用，避免在公共设备上运行
- 程序仅用于学习和个人使用，请勿用于商业目的
- 使用前请确保符合理想论坛的使用条款

## 📝 更新日志

### v1.0.0 (2025-01-27)
- ✅ 初始版本发布
- ✅ 支持自动登录和签到
- ✅ 添加定时任务功能
- ✅ 完善日志和错误处理
- ✅ 提供完整的测试脚本

## 📞 技术支持

如果您在使用过程中遇到问题：

1. 首先查看日志文件获取错误详情
2. 运行测试脚本诊断问题
3. 检查配置文件格式是否正确
4. 确认网络连接和浏览器环境

## ⚖️ 免责声明

本程序仅供学习和研究使用，使用者需要自行承担使用风险。作者不对因使用本程序导致的任何问题承担责任。

---

🎯 **祝您使用愉快！如有问题欢迎反馈。**
