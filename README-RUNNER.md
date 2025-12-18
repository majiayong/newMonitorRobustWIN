# 🚀 Self-Hosted Runner 快速指南

## ✅ 已完成配置

本项目已配置为使用 **Self-Hosted Runner** 和 **VPN代理加速**，可以在您的 MacBook Pro 上快速构建 APK。

### 核心特性

- ✅ 支持 macOS 和 Linux 双平台
- ✅ 自动使用 VPN 代理（127.0.0.1:7890）加速下载
- ✅ 智能缓存，后续构建更快
- ✅ 超时保护（180分钟）
- ✅ 自动发布到 GitHub Release

## 🏃 使用步骤

### 1. 确保 Runner 正在运行

```bash
cd ~/actions-runner  # 或您的runner安装目录
./run.sh
```

应该看到：
```
√ Connected to GitHub
Listening for Jobs
```

### 2. 确保 VPN 正在运行

代理端口：`127.0.0.1:7890`

### 3. 推送代码触发构建

```bash
git add .
git commit -m "更新"
git push
```

或在 GitHub Actions 页面手动触发。

### 4. 等待构建完成

- 首次构建：60-120分钟
- 后续构建：25-35分钟（有缓存）

### 5. 下载 APK

在 Actions 页面的 Artifacts 部分下载。

## 📦 项目信息

- **应用名称**：PriceMonitor
- **包名**：org.crypto.pricemonitor
- **主文件**：monitor_android_kivy.py
- **Python版本**：3.9
- **目标架构**：arm64-v8a
- **最低Android**：5.0 (API 21)
- **目标Android**：12 (API 31)

## 🔧 依赖项

- Kivy（UI框架）
- Requests（HTTP请求）
- Numpy（数值计算）
- Plyer（Android功能）
- urllib3（HTTP客户端）

## 🐛 故障排除

### Runner 离线
```bash
cd ~/actions-runner
./run.sh
```

### 下载很慢
检查：
1. VPN是否运行？
2. 代理端口是否是7890？
3. 查看构建日志中的HTTP_PROXY设置

### Homebrew 依赖安装失败
```bash
brew update
brew install sdl2 sdl2_image sdl2_ttf sdl2_mixer
```

## 📊 构建时间预估

| 阶段 | 首次 | 后续 |
|-----|------|------|
| 安装依赖 | 5-10分钟 | 1分钟 |
| 下载SDK/NDK | 20-40分钟 | 跳过 |
| 构建APK | 30-60分钟 | 20-30分钟 |
| **总计** | **60-120分钟** | **25-35分钟** |

## 🎯 优势

| 特性 | GitHub Runner | Self-Hosted |
|-----|---------------|-------------|
| 排队时间 | 可能很长 | **立即开始** |
| 下载速度 | 慢 | **VPN加速** |
| 使用限制 | 2000分钟/月 | **无限制** |
| 缓存持久 | 临时 | **永久** |

## 📝 注意事项

1. 构建期间保持 VPN 运行
2. 构建期间保持电脑开机（不要睡眠）
3. 首次构建会下载约 10-20GB 数据
4. `.buildozer` 目录可能很大，可定期清理

## 🔄 自动发布

推送到 `main` 分支时会自动：
1. 构建 APK
2. 创建 Release
3. 上传 APK 到 Release

版本号格式：`v{构建编号}`

## 💡 提示

- 使用 `workflow_dispatch` 可手动触发
- 查看 `.github/workflows/build.yml` 了解详细配置
- 构建日志会自动上传到 Artifacts

---

**快速开始：确保 Runner 和 VPN 运行，然后推送代码！** 🎉
