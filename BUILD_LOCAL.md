# Windows 本地构建指南

## 快速开始

### 1. 一键构建（推荐）

直接运行构建脚本：

```powershell
.\build_local.ps1
```

脚本会自动：
- ✓ 检查和创建虚拟环境
- ✓ 安装必要的依赖
- ✓ 检查 Java 和 Git
- ✓ Patch buildozer
- ✓ 开始构建 APK

### 2. 手动构建

如果你想手动执行每一步：

```powershell
# 1. 激活虚拟环境
.\buildozer-venv\Scripts\Activate.ps1

# 2. 确保 Git 在 PATH 中
$env:Path = "C:\Program Files\Git\cmd;$env:Path"

# 3. 设置 JAVA_HOME（如果需要）
$env:JAVA_HOME = "F:\tool\jdk17"
$env:Path = "$env:JAVA_HOME\bin;$env:Path"

# 4. Patch buildozer
python patch_buildozer.py ".\buildozer-venv\lib\site-packages\buildozer\__init__.py"

# 5. 构建
buildozer -v android debug
```

## 环境要求

### 必需软件
- [x] Python 3.9+ （你有 3.13.5）
- [x] Git （你有 2.39.1）
- [ ] **JDK 17** （你当前是 Java 8，需要升级！）

### 安装 JDK 17

你当前使用的是 Java 8，但项目需要 **JDK 17**。

**方法 1：使用 Chocolatey（推荐）**
```powershell
# 以管理员身份运行 PowerShell
choco install openjdk17 -y
```

**方法 2：手动安装**
1. 下载 JDK 17：https://adoptium.net/temurin/releases/
2. 安装到 `F:\tool\jdk17`（或其他位置）
3. 设置环境变量：
   ```powershell
   [System.Environment]::SetEnvironmentVariable("JAVA_HOME", "F:\tool\jdk17", "User")
   ```

## 首次构建说明

### 构建时间
- **首次构建：** 30-60 分钟
  - 需要下载 Android SDK (~3GB)
  - 需要下载 Android NDK (~1GB)
  - 编译所有依赖库
- **后续构建：** 5-10 分钟

### 磁盘空间
确保至少有 **15GB 可用空间**：
- Android SDK: ~3GB
- Android NDK: ~1GB
- 构建缓存: ~5GB
- APK 和中间文件: ~2GB

### 网络要求
首次构建需要下载大量文件，建议：
- 使用稳定的网络连接
- 如果网络慢，可以配置代理

## 输出文件

构建成功后，APK 文件位于：
```
bin/PriceMonitor-1.0.0-arm64-v8a-debug.apk
```

## 常见问题

### Q: 报错 "Git not found"
**A:** 运行以下命令添加 Git 到 PATH：
```powershell
$env:Path = "C:\Program Files\Git\cmd;$env:Path"
```

### Q: 报错 "Java version mismatch"
**A:** 确保使用 JDK 17，而不是 Java 8：
```powershell
$env:JAVA_HOME = "F:\tool\jdk17"
java -version  # 应该显示 "openjdk version 17.x.x"
```

### Q: 构建速度太慢
**A:** 首次构建需要下载 SDK/NDK，这是正常的。后续构建会快得多。

### Q: 报错 "buildozer not found"
**A:** 确保激活了虚拟环境：
```powershell
.\buildozer-venv\Scripts\Activate.ps1
```

### Q: 想要清理重新构建
**A:** 删除构建缓存：
```powershell
Remove-Item -Recurse -Force .buildozer
Remove-Item -Recurse -Force bin
```

## 下一步

构建成功后：
1. 在 `bin/` 目录找到 APK 文件
2. 传输到 Android 手机
3. 安装并测试

## 需要帮助？

如果遇到问题：
1. 检查错误信息
2. 确认环境要求都满足
3. 尝试清理缓存重新构建
