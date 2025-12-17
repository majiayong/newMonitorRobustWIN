[app]

# 应用名称
title = 价格监控

# 包名（反向域名格式）
package.name = pricemonitor

# 包的域名
package.domain = org.crypto

# 源代码目录
source.dir = .

# 源代码文件
source.include_exts = py,png,jpg,kv,atlas

# 应用入口文件
source.main = monitor_android_kivy.py

# 应用版本
version = 1.0.0

# 应用依赖
requirements = python3,kivy,requests,urllib3,numpy,plyer,android

# 安卓权限
android.permissions = INTERNET,VIBRATE,WAKE_LOCK,FOREGROUND_SERVICE

# 安卓API版本
android.api = 31

# 最小API版本
android.minapi = 21

# Android NDK版本
android.ndk = 23b

# 应用图标（可选，如果有的话）
# icon.filename = %(source.dir)s/data/icon.png

# 启动画面（可选）
# presplash.filename = %(source.dir)s/data/presplash.png

# 应用方向
orientation = portrait

# 全屏显示
fullscreen = 0

# Android架构
android.archs = arm64-v8a,armeabi-v7a

# 允许后台运行
android.services = MonitorService:./service.py:foreground

# P4A bootstrap
p4a.bootstrap = sdl2

[buildozer]

# 日志级别
log_level = 2

# 警告作为错误
warn_on_root = 1

# Buildozer输出目录
# bin_dir = ./bin
