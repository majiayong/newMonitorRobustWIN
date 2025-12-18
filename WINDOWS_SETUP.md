# Windows 系统构建配置说明

本项目已配置为在 Windows 系统上使用 GitHub Actions 构建 Android APK。

## 前置要求

### 1. Windows Self-Hosted Runner 环境

如果你使用 GitHub self-hosted runner，需要在 Windows 机器上安装以下软件：

#### 必需软件

1. **Chocolatey** (Windows 包管理器)
   - 打开 PowerShell (管理员模式)
   - 运行以下命令安装:
   ```powershell
   Set-ExecutionPolicy Bypass -Scope Process -Force
   [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
   iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
   ```

2. **Python 3.9**
   - GitHub Actions 会自动设置
   - 或手动安装: `choco install python39 -y`

3. **Java JDK 17**
   - GitHub Actions 会自动检查并安装
   - 或手动安装: `choco install openjdk17 -y`

4. **Git**
   - GitHub Actions 会自动检查并安装
   - 或手动安装: `choco install git -y`

#### 可选软件

- **Visual Studio Build Tools** (如果遇到编译错误)
  ```powershell
  choco install visualstudio2022buildtools -y
  choco install visualstudio2022-workload-vctools -y
  ```

### 2. 硬件要求

- **磁盘空间**: 至少 20GB 可用空间 (Android SDK + NDK 需要大量空间)
- **内存**: 至少 8GB RAM (推荐 16GB)
- **CPU**: 多核处理器 (构建时会使用所有核心进行并行编译)

### 3. 网络配置

#### 代理设置 (可选)

如果你的 Windows 机器需要通过代理访问互联网，请编辑 `.github/workflows/build.yml` 文件，取消注释以下行并修改为你的代理地址:

```yaml
env:
  http_proxy: http://127.0.0.1:7890
  https_proxy: http://127.0.0.1:7890
  NO_PROXY: localhost,127.0.0.1
```

## 构建流程

### 自动构建 (GitHub Actions)

1. 将代码推送到 GitHub 的 `main` 或 `master` 分支
2. GitHub Actions 会自动触发构建
3. 构建完成后，APK 文件会作为 artifact 上传
4. 如果推送到 main 分支，还会自动创建 Release

### 手动触发构建

1. 进入 GitHub 仓库的 "Actions" 页面
2. 选择 "Build Android APK (Windows)" workflow
3. 点击 "Run workflow" 按钮
4. 等待构建完成

### 本地构建 (可选)

如果你想在本地 Windows 机器上构建:

```powershell
# 1. 创建虚拟环境
python -m venv buildozer-venv

# 2. 激活虚拟环境
.\buildozer-venv\Scripts\Activate.ps1

# 3. 安装依赖
pip install --upgrade pip setuptools
pip install cython==0.29.36
pip install buildozer==1.5.0

# 4. 构建 APK
buildozer -v android debug
```

**注意**: 本地首次构建可能需要 30-60 分钟，因为需要下载 Android SDK 和 NDK。

## 常见问题

### 1. 构建失败: "找不到 Java"

**解决方法**:
```powershell
# 手动安装 Java
choco install openjdk17 -y
refreshenv

# 验证安装
java -version
```

### 2. 构建失败: "Android SDK License 未接受"

**解决方法**:
已在 `buildozer.spec` 中配置 `android.accept_sdk_license = True`，应该会自动接受。

### 3. 构建速度慢

**优化建议**:
- 使用 GitHub Actions cache (已配置)
- 确保机器有足够的 CPU 核心
- 首次构建较慢是正常的，后续构建会快很多

### 4. 磁盘空间不足

**解决方法**:
```powershell
# 清理 Buildozer 缓存
Remove-Item -Recurse -Force "$env:USERPROFILE\.buildozer"

# 清理 pip 缓存
pip cache purge
```

### 5. PowerShell 执行策略错误

**解决方法**:
```powershell
# 以管理员身份运行
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 构建产物

构建成功后，你可以在以下位置找到 APK:

1. **GitHub Actions Artifacts**
   - 进入 Actions 页面
   - 选择对应的 workflow run
   - 下载 "android-apk" artifact

2. **GitHub Releases** (如果推送到 main 分支)
   - 进入仓库的 Releases 页面
   - 下载最新的 release 中的 APK 文件

3. **本地构建**
   - APK 位于: `bin/` 目录

## 项目结构

```
newMonitorRobustWIN/
├── .github/
│   └── workflows/
│       └── build.yml          # GitHub Actions 配置 (Windows)
├── buildozer.spec             # Buildozer 配置文件
├── main.py                    # 应用入口文件
├── monitor_android_kivy.py    # 主应用代码
├── WINDOWS_SETUP.md           # 本文件
└── bin/                       # 构建输出目录 (生成后)
```

## 与 macOS 版本的区别

主要变化:
1. **Shell**: 从 bash 改为 PowerShell
2. **包管理器**: 从 brew/apt 改为 Chocolatey
3. **路径**: Windows 路径格式 (反斜杠)
4. **虚拟环境激活**: `.\buildozer-venv\Scripts\Activate.ps1`
5. **移除 ccache**: Windows 上不常用

核心构建逻辑保持不变，Buildozer 和 Python-for-Android 是跨平台的。

## 技术支持

如果遇到问题:
1. 查看 GitHub Actions 的构建日志
2. 下载 "build-log" artifact 查看详细日志
3. 确认所有前置软件已正确安装
4. 检查磁盘空间是否充足

## 下一步

配置完成后，你可以:
1. 推送代码到 GitHub 触发自动构建
2. 在 GitHub 设置中配置 self-hosted runner
3. 根据需要调整 `buildozer.spec` 中的应用配置
