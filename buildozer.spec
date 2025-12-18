[app]

# 应用信息
title = PriceMonitor
package.name = pricemonitor
package.domain = org.crypto

# 源代码
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
# buildozer 默认使用 main.py 作为入口点

# 版本
version = 1.0.0

# 依赖 - 移除版本号以避免冲突
requirements = python3,kivy,requests,numpy,plyer,android,urllib3

# 权限
android.permissions = INTERNET,VIBRATE,WAKE_LOCK

# API版本
android.api = 31
android.minapi = 21

# ✅ 关键修复：使用 NDK 25b 或更高版本
# android.ndk = 25b  # 如果使用指定版本添加注释
# 或者使用系统 NDK（推荐）
android.accept_sdk_license = True

# 架构 - 只构建 arm64 加快速度
android.archs = arm64-v8a

# 屏幕方向
orientation = portrait
fullscreen = 0

# Bootstrap
p4a.bootstrap = sdl2

# 源码排除
source.exclude_exts = spec

# 日志
log_level = 2
warn_on_root = 1

[buildozer]
log_level = 2
warn_on_root = 1
