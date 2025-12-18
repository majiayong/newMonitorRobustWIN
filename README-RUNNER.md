# 🚀 Self-Hosted Runner 快速指南 (Windows)

## ✅ 已完成配置

本项目已配置为使用 **Windows Self-Hosted Runner** 构建 Android APK。

### 核心特性

- ✅ 支持 Windows 系统
- ✅ 智能缓存，后续构建更快
- ✅ 超时保护（180分钟）
- ✅ 自动发布到 GitHub Release
- ✅ PowerShell 自动化脚本

## 🏃 使用步骤

### 1. 确保 Runner 正在运行

```powershell
cd C:\actions-runner  # 或您的runner安装目录
.\run.cmd
```

应该看到：
```
√ Connected to GitHub
Listening for Jobs
```

### 2. 推送代码触发构建

```powershell
git add .
git commit -m "更新"
git push
```

或在 GitHub Actions 页面手动触发。

### 3. 等待构建完成

- 首次构建：60-120分钟
- 后续构建：25-35分钟（有缓存）

### 4. 下载 APK

在 Actions 页面的 Artifacts 部分下载。

## 📦 项目信息

- **应用名称**：PriceMonitor
- **包名**：org.crypto.pricemonitor
- **主文件**：main.py
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
```powershell
cd C:\actions-runner
.\run.cmd
```

### Java 未找到
```powershell
# 安装 Java
choco install openjdk17 -y
refreshenv

# 验证
java -version
```

### Python 版本问题
GitHub Actions 会自动安装 Python 3.9，无需手动配置。

### 磁盘空间不足
```powershell
# 清理 Buildozer 缓存
Remove-Item -Recurse -Force "$env:USERPROFILE\.buildozer"

# 清理 pip 缓存
pip cache purge
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
| 使用限制 | 2000分钟/月 | **无限制** |
| 缓存持久 | 临时 | **永久** |
| 自定义环境 | 受限 | **完全控制** |

## 📝 注意事项

1. 构建期间保持电脑开机（不要睡眠）
2. 首次构建会下载约 10-20GB 数据
3. `.buildozer` 目录可能很大（位于 `C:\Users\用户名\.buildozer`）
4. 确保有足够的磁盘空间（至少 20GB）

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
- 详细的 Windows 配置说明请参考 `WINDOWS_SETUP.md`

## 📖 详细文档

更多详细信息，请参阅：
- **WINDOWS_SETUP.md** - 完整的 Windows 环境配置指南
- **.github/workflows/build.yml** - GitHub Actions 配置文件
- **buildozer.spec** - Buildozer 构建配置

## 🌟 与 macOS 版本的区别

主要变化：
- Shell 脚本从 bash 改为 PowerShell
- 包管理器从 Homebrew/apt 改为 Chocolatey
- 路径格式使用 Windows 反斜杠
- 移除了 ccache（Windows 上不常用）
- 移除了 VPN 代理配置（可根据需要添加）

核心构建流程保持不变。

---

**快速开始：确保 Runner 运行，然后推送代码！** 🎉
