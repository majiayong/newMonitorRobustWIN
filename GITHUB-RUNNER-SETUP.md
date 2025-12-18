# GitHub Self-Hosted Runner 完整安装指南 (Windows)

本文档提供在 Windows 系统上设置 GitHub Self-Hosted Runner 的完整指南。

## 目录

- [什么是 Self-Hosted Runner](#什么是-self-hosted-runner)
- [为什么使用 Self-Hosted Runner](#为什么使用-self-hosted-runner)
- [系统要求](#系统要求)
- [快速安装（推荐）](#快速安装推荐)
- [手动安装](#手动安装)
- [配置为Windows服务](#配置为windows服务)
- [验证和测试](#验证和测试)
- [日常管理](#日常管理)
- [故障排除](#故障排除)
- [安全建议](#安全建议)

## 什么是 Self-Hosted Runner

Self-Hosted Runner 是运行在你自己的机器上的 GitHub Actions 执行器。与 GitHub 提供的托管运行器不同，它运行在你控制的硬件上，可以访问本地资源。

## 为什么使用 Self-Hosted Runner

| 优势 | GitHub-Hosted | Self-Hosted |
|------|---------------|-------------|
| 使用限制 | 2,000分钟/月（免费版） | 无限制 |
| 排队时间 | 可能需要等待 | 立即开始 |
| 缓存持久化 | 7天后自动清除 | 永久保留 |
| 自定义环境 | 受限 | 完全控制 |
| 网络访问 | 公网 | 可访问内网资源 |
| 构建速度 | 2核CPU，7GB内存 | 取决于你的硬件 |

## 系统要求

### 硬件要求

- **CPU**: 双核或更高（推荐4核以上）
- **内存**: 最低8GB（推荐16GB或更高）
- **磁盘空间**: 至少30GB可用空间
  - Runner本身: ~500MB
  - Android SDK: ~10GB
  - Android NDK: ~5GB
  - 构建缓存: ~5-10GB
  - Python依赖: ~2GB

### 软件要求

- **操作系统**: Windows 10/11 或 Windows Server 2019/2022
- **PowerShell**: 5.1 或更高版本
- **.NET Framework**: 4.6.2 或更高版本（通常已预装）
- **管理员权限**: 安装服务需要管理员权限

### 网络要求

- 能够访问 `github.com` 和 `*.actions.githubusercontent.com`
- 如果需要代理，需要配置代理设置

## 快速安装（推荐）

使用提供的自动化脚本可以一键完成安装。

### 步骤 1: 获取 Runner Token

1. 访问你的 GitHub 仓库:
   ```
   https://github.com/majiayong/newMonitorRobustWIN
   ```

2. 点击 **Settings**（设置）标签

3. 在左侧菜单中，找到 **Actions** > **Runners**

4. 点击右上角的 **New self-hosted runner** 按钮

5. 选择操作系统:
   - **Operating System**: Windows
   - **Architecture**: x64

6. 在 "Configure" 部分，找到类似这样的命令:
   ```powershell
   .\config.cmd --url https://github.com/majiayong/newMonitorRobustWIN --token XXXXXXXXXXXXXXXXXXXXXX
   ```

7. 复制 `--token` 后面的整个 token 值（大约40个字符）

### 步骤 2: 运行安装脚本

1. 以**管理员身份**打开 PowerShell:
   - 按 `Win + X`
   - 选择 "Windows PowerShell (管理员)" 或 "终端 (管理员)"

2. 切换到项目目录:
   ```powershell
   cd C:\Users\Administrator\PycharmProjects\newMonitorRobustWIN
   ```

3. 如果遇到执行策略限制，运行:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
   ```

4. 运行安装脚本:
   ```powershell
   .\setup-github-runner.ps1 -RunnerToken "你的TOKEN"
   ```

5. 脚本会自动完成:
   - ✓ 创建安装目录
   - ✓ 下载最新的 Runner
   - ✓ 解压和配置
   - ✓ 安装为 Windows 服务
   - ✓ 启动服务

### 步骤 3: 验证安装

1. 访问仓库的 Runner 页面:
   ```
   https://github.com/majiayong/newMonitorRobustWIN/settings/actions/runners
   ```

2. 你应该能看到新添加的 Runner，状态为 **Idle**（空闲）

3. 在本地检查服务状态:
   ```powershell
   cd C:\actions-runner
   .\svc.cmd status
   ```

   应该显示:
   ```
   √ actions.runner.majiayong-newMonitorRobustWIN.xxx service is running
   ```

## 手动安装

如果自动脚本失败或你想手动控制每一步，可以按以下步骤操作。

### 1. 创建安装目录

```powershell
# 创建目录
New-Item -ItemType Directory -Path "C:\actions-runner" -Force

# 切换到目录
cd C:\actions-runner
```

### 2. 下载 Runner

访问 [GitHub Actions Runner 发布页面](https://github.com/actions/runner/releases) 下载最新版本，或使用 PowerShell 下载:

```powershell
# 下载最新版本 (以 2.321.0 为例)
$RunnerVersion = "2.321.0"
$Url = "https://github.com/actions/runner/releases/download/v$RunnerVersion/actions-runner-win-x64-$RunnerVersion.zip"

# 下载
Invoke-WebRequest -Uri $Url -OutFile "actions-runner.zip"

# 解压
Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::ExtractToDirectory("$PWD\actions-runner.zip", $PWD)

# 删除压缩包
Remove-Item "actions-runner.zip"
```

### 3. 配置 Runner

使用从 GitHub 获取的 token 配置 Runner:

```powershell
.\config.cmd --url https://github.com/majiayong/newMonitorRobustWIN --token YOUR_TOKEN_HERE --name my-windows-runner --work _work --labels windows,x64,self-hosted
```

**参数说明:**
- `--url`: 仓库地址
- `--token`: 从 GitHub 获取的 token
- `--name`: Runner 的名称（可自定义）
- `--work`: 工作目录
- `--labels`: 标签，用于在 workflow 中指定使用此 Runner

配置过程中会提示:
```
Enter name of runner: [按Enter使用默认名称]
This runner will have the following labels: 'self-hosted', 'Windows', 'X64'
Enter any additional labels (ex. label-1,label-2): [可选，按Enter跳过]
```

### 4. 测试运行

在配置服务之前，先测试 Runner 是否正常工作:

```powershell
.\run.cmd
```

你应该看到:
```
√ Connected to GitHub

Listening for Jobs
```

按 `Ctrl+C` 停止测试运行。

## 配置为Windows服务

将 Runner 配置为 Windows 服务可以实现开机自动启动和后台运行。

### 安装服务

```powershell
# 必须以管理员身份运行
.\svc.cmd install
```

### 启动服务

```powershell
.\svc.cmd start
```

### 其他服务命令

```powershell
# 查看状态
.\svc.cmd status

# 停止服务
.\svc.cmd stop

# 卸载服务
.\svc.cmd uninstall
```

### 服务名称

服务名称格式为: `actions.runner.<账户>-<仓库>.<runner名称>`

例如: `actions.runner.majiayong-newMonitorRobustWIN.DESKTOP-ABC123-runner`

你可以在 Windows 服务管理器中查看:
```powershell
services.msc
```

## 验证和测试

### 1. 检查 Runner 状态

在 GitHub 上:
```
https://github.com/majiayong/newMonitorRobustWIN/settings/actions/runners
```

应该显示:
- **Status**: Idle（空闲）
- **Last used**: Never（如果是新安装）

### 2. 触发测试构建

你可以通过以下方式测试 Runner:

**方法 1: 推送代码**
```powershell
cd C:\Users\Administrator\PycharmProjects\newMonitorRobustWIN
git add .
git commit -m "Test runner"
git push
```

**方法 2: 手动触发**
1. 访问 Actions 页面
2. 选择 workflow
3. 点击 "Run workflow"

### 3. 查看构建日志

1. 在 GitHub Actions 页面查看 workflow 运行状态
2. 在本地查看 Runner 日志:
   ```powershell
   # Worker 日志
   Get-Content C:\actions-runner\_diag\Worker_*.log -Tail 50

   # Runner 日志
   Get-Content C:\actions-runner\_diag\Runner_*.log -Tail 50
   ```

## 日常管理

### 更新 Runner

GitHub 会在新版本发布时自动更新 Runner（如果配置正确）。手动更新:

```powershell
# 停止服务
cd C:\actions-runner
.\svc.cmd stop
.\svc.cmd uninstall

# 删除旧文件（保留 _work 目录）
Remove-Item -Exclude "_work" -Recurse -Force *

# 下载并解压新版本
# （参考手动安装步骤）

# 重新配置和安装服务
.\config.cmd --url ... --token ...
.\svc.cmd install
.\svc.cmd start
```

### 查看磁盘使用情况

```powershell
# 查看工作目录大小
Get-ChildItem C:\actions-runner\_work -Recurse | Measure-Object -Property Length -Sum

# 查看 Buildozer 缓存大小
Get-ChildItem $env:USERPROFILE\.buildozer -Recurse | Measure-Object -Property Length -Sum
```

### 清理缓存

```powershell
# 清理 Actions 工作目录
Remove-Item -Recurse -Force C:\actions-runner\_work\*

# 清理 Buildozer 缓存
Remove-Item -Recurse -Force $env:USERPROFILE\.buildozer

# 清理 pip 缓存
pip cache purge
```

### 监控 Runner

使用 PowerShell 监控 Runner 服务:

```powershell
# 持续监控服务状态
while ($true) {
    Clear-Host
    Write-Host "Runner Service Status - $(Get-Date)" -ForegroundColor Cyan
    .\svc.cmd status
    Start-Sleep -Seconds 5
}
```

## 故障排除

### 问题 1: Runner 显示离线

**症状**: GitHub 上显示 Runner 状态为 "Offline"

**可能原因和解决方法**:

1. **服务未运行**:
   ```powershell
   cd C:\actions-runner
   .\svc.cmd status
   .\svc.cmd start
   ```

2. **网络问题**:
   ```powershell
   # 测试连接
   Test-NetConnection github.com -Port 443
   Test-NetConnection actions.githubusercontent.com -Port 443
   ```

3. **Token 过期**:
   - 重新从 GitHub 获取 token
   - 重新配置 Runner

### 问题 2: 构建失败 - 找不到工具

**症状**: 构建日志显示找不到 Java、Python 等工具

**解决方法**:

1. 确认工具已安装:
   ```powershell
   java -version
   python --version
   git --version
   ```

2. 检查 PATH 环境变量:
   ```powershell
   $env:PATH -split ';'
   ```

3. 重启 Runner 服务以加载新的环境变量:
   ```powershell
   .\svc.cmd stop
   .\svc.cmd start
   ```

### 问题 3: 权限错误

**症状**: 构建时出现权限拒绝错误

**解决方法**:

1. 确认 Runner 服务使用的账户有足够权限
2. 默认情况下，服务使用 Local System 账户，通常有足够权限
3. 如果需要，可以更改服务账户:
   - 打开 `services.msc`
   - 找到 Runner 服务
   - 右键 > 属性 > 登录
   - 更改账户

### 问题 4: 磁盘空间不足

**症状**: 构建失败，提示磁盘空间不足

**解决方法**:

```powershell
# 查看磁盘空间
Get-PSDrive C

# 清理旧的构建
Remove-Item -Recurse -Force C:\actions-runner\_work\*

# 清理 Buildozer 缓存
Remove-Item -Recurse -Force $env:USERPROFILE\.buildozer

# 清理 Windows 临时文件
cleanmgr /sagerun:1
```

### 问题 5: Runner 配置后无法连接

**症状**: 运行 `.\run.cmd` 后显示连接错误

**可能原因和解决方法**:

1. **Token 无效或过期**:
   - 重新从 GitHub 获取 token
   - 运行 `.\config.cmd remove` 移除配置
   - 重新配置

2. **防火墙阻止**:
   ```powershell
   # 添加防火墙规则
   New-NetFirewallRule -DisplayName "GitHub Runner" -Direction Outbound -Action Allow -Protocol TCP -RemotePort 443
   ```

3. **代理设置**:
   如果需要通过代理访问 GitHub:
   ```powershell
   # 设置代理
   $env:http_proxy = "http://proxy.example.com:8080"
   $env:https_proxy = "http://proxy.example.com:8080"
   ```

### 查看详细日志

Runner 的详细日志位于:
```
C:\actions-runner\_diag\
```

查看最新日志:
```powershell
# Worker 日志
Get-Content C:\actions-runner\_diag\Worker_*.log -Tail 100

# Runner 日志
Get-Content C:\actions-runner\_diag\Runner_*.log -Tail 100
```

## 安全建议

### 1. 使用专用机器

- 不要在个人电脑上运行 Runner
- 使用专用的构建服务器
- 确保物理和网络安全

### 2. 网络隔离

- 如果可能，将 Runner 放在隔离的网络中
- 只允许必要的出站连接
- 使用防火墙限制访问

### 3. 权限最小化

```powershell
# 创建专用用户账户
net user github-runner P@ssw0rd /add /passwordchg:no /passwordreq:yes

# 将 Runner 服务配置为使用此账户
# (通过 services.msc 手动配置)
```

### 4. 定期更新

- 定期更新 Runner 到最新版本
- 保持 Windows 系统更新
- 更新所有构建工具

### 5. 监控和审计

```powershell
# 定期检查 Runner 日志
Get-ChildItem C:\actions-runner\_diag\ | Sort-Object LastWriteTime -Descending | Select-Object -First 5
```

### 6. 限制仓库访问

- 只为受信任的仓库配置 Runner
- 使用 GitHub 的 Runner Groups 功能限制访问
- 定期审查 Runner 使用情况

### 7. 不运行公开仓库的工作流

**重要**: 不要将 Self-Hosted Runner 用于公开仓库！

公开仓库的任何人都可以创建 Pull Request 并执行恶意代码。Self-Hosted Runner 只应用于私有仓库。

## 高级配置

### 配置代理

如果需要通过代理访问 GitHub:

```powershell
# 编辑 .env 文件
Set-Content C:\actions-runner\.env @"
http_proxy=http://proxy.example.com:8080
https_proxy=http://proxy.example.com:8080
no_proxy=localhost,127.0.0.1
"@

# 重启服务
.\svc.cmd stop
.\svc.cmd start
```

### 配置 Runner Groups

在 GitHub 组织级别，你可以使用 Runner Groups 来管理多个 Runner。

1. 访问组织设置 > Actions > Runner groups
2. 创建新的 Runner Group
3. 将 Runner 分配到相应的 Group
4. 在 workflow 中指定 Group

### 多个 Runner

如果需要多个 Runner:

```powershell
# 为每个 Runner 创建独立目录
New-Item -ItemType Directory -Path "C:\actions-runner-1" -Force
New-Item -ItemType Directory -Path "C:\actions-runner-2" -Force

# 分别配置每个 Runner，使用不同的名称
cd C:\actions-runner-1
.\config.cmd --name runner-1 ...

cd C:\actions-runner-2
.\config.cmd --name runner-2 ...
```

## 参考资源

- [GitHub Actions Self-Hosted Runners 官方文档](https://docs.github.com/en/actions/hosting-your-own-runners)
- [Runner 发布页面](https://github.com/actions/runner/releases)
- [GitHub Actions 文档](https://docs.github.com/en/actions)

## 相关文档

- **WINDOWS_SETUP.md** - Windows 构建环境配置
- **README-RUNNER.md** - Runner 使用快速指南
- **.github/workflows/build.yml** - GitHub Actions 工作流配置

---

**文档版本**: 1.0
**创建日期**: 2025-12-18
**适用于**: GitHub Actions Runner 2.x, Windows 10/11
