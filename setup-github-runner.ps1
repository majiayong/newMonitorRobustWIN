# GitHub Self-Hosted Runner 安装脚本 (Windows)
# 使用方法: 以管理员身份运行 PowerShell，然后执行此脚本

param(
    [Parameter(Mandatory=$false)]
    [string]$RunnerToken = "",

    [Parameter(Mandatory=$false)]
    [string]$GithubUrl = "https://github.com/majiayong/newMonitorRobustWIN",

    [Parameter(Mandatory=$false)]
    [string]$RunnerName = "$env:COMPUTERNAME-runner",

    [Parameter(Mandatory=$false)]
    [string]$InstallPath = "C:\actions-runner"
)

# 颜色输出函数
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

Write-ColorOutput Green "=========================================="
Write-ColorOutput Green "  GitHub Self-Hosted Runner 安装脚本"
Write-ColorOutput Green "=========================================="
Write-Output ""

# 检查是否以管理员身份运行
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-ColorOutput Red "错误: 请以管理员身份运行此脚本！"
    Write-Output "右键点击 PowerShell，选择 '以管理员身份运行'"
    exit 1
}

# 检查是否提供了 Token
if ($RunnerToken -eq "") {
    Write-ColorOutput Yellow "=========================================="
    Write-ColorOutput Yellow "  获取 Runner Token 的步骤:"
    Write-ColorOutput Yellow "=========================================="
    Write-Output ""
    Write-Output "1. 访问你的 GitHub 仓库:"
    Write-ColorOutput Cyan "   $GithubUrl"
    Write-Output ""
    Write-Output "2. 点击 Settings (设置)"
    Write-Output ""
    Write-Output "3. 在左侧菜单中找到 Actions > Runners"
    Write-Output ""
    Write-Output "4. 点击 'New self-hosted runner' 按钮"
    Write-Output ""
    Write-Output "5. 选择 Windows 和 x64"
    Write-Output ""
    Write-Output "6. 复制 '--token' 后面的 token 值"
    Write-Output ""
    Write-ColorOutput Yellow "然后重新运行此脚本:"
    Write-ColorOutput Cyan '.\setup-github-runner.ps1 -RunnerToken "你的TOKEN"'
    Write-Output ""

    # 打开浏览器到设置页面
    $settingsUrl = "$GithubUrl/settings/actions/runners/new"
    Write-Output "是否要打开浏览器到 Runner 设置页面？(Y/N)"
    $response = Read-Host
    if ($response -eq "Y" -or $response -eq "y") {
        Start-Process $settingsUrl
    }

    exit 0
}

Write-Output "配置信息:"
Write-Output "  GitHub 仓库: $GithubUrl"
Write-Output "  Runner 名称: $RunnerName"
Write-Output "  安装路径: $InstallPath"
Write-Output ""

# 创建安装目录
Write-ColorOutput Cyan "[1/6] 创建安装目录..."
if (-not (Test-Path $InstallPath)) {
    New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null
    Write-ColorOutput Green "✓ 目录创建成功: $InstallPath"
} else {
    Write-ColorOutput Yellow "! 目录已存在: $InstallPath"
}

# 下载最新的 Runner
Write-ColorOutput Cyan "`n[2/6] 下载 GitHub Actions Runner..."
$RunnerVersion = "2.321.0"  # 可以更新到最新版本
$RunnerUrl = "https://github.com/actions/runner/releases/download/v$RunnerVersion/actions-runner-win-x64-$RunnerVersion.zip"
$RunnerZip = "$InstallPath\actions-runner.zip"

try {
    Write-Output "下载地址: $RunnerUrl"
    Invoke-WebRequest -Uri $RunnerUrl -OutFile $RunnerZip
    Write-ColorOutput Green "✓ 下载完成"
} catch {
    Write-ColorOutput Red "✗ 下载失败: $_"
    Write-Output ""
    Write-ColorOutput Yellow "如果下载失败，你也可以手动下载:"
    Write-Output "1. 访问: https://github.com/actions/runner/releases"
    Write-Output "2. 下载 actions-runner-win-x64-*.zip"
    Write-Output "3. 解压到: $InstallPath"
    exit 1
}

# 解压 Runner
Write-ColorOutput Cyan "`n[3/6] 解压 Runner..."
try {
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    [System.IO.Compression.ZipFile]::ExtractToDirectory($RunnerZip, $InstallPath)
    Remove-Item $RunnerZip
    Write-ColorOutput Green "✓ 解压完成"
} catch {
    Write-ColorOutput Red "✗ 解压失败: $_"
    exit 1
}

# 配置 Runner
Write-ColorOutput Cyan "`n[4/6] 配置 Runner..."
Set-Location $InstallPath

try {
    $configCmd = ".\config.cmd --url $GithubUrl --token $RunnerToken --name $RunnerName --work _work --runasservice --labels windows,x64,self-hosted --unattended"
    Write-Output "执行配置命令..."
    Invoke-Expression $configCmd
    Write-ColorOutput Green "✓ Runner 配置成功"
} catch {
    Write-ColorOutput Red "✗ 配置失败: $_"
    Write-Output ""
    Write-ColorOutput Yellow "可能的原因:"
    Write-Output "1. Token 已过期或无效"
    Write-Output "2. 网络连接问题"
    Write-Output "3. 已经有同名的 Runner"
    Write-Output ""
    Write-ColorOutput Yellow "请检查后重试"
    exit 1
}

# 安装 Runner 服务
Write-ColorOutput Cyan "`n[5/6] 安装为 Windows 服务..."
try {
    .\svc.cmd install
    Write-ColorOutput Green "✓ 服务安装成功"
} catch {
    Write-ColorOutput Red "✗ 服务安装失败: $_"
    Write-Output ""
    Write-ColorOutput Yellow "你可以选择不安装服务，手动运行 Runner:"
    Write-Output "cd $InstallPath"
    Write-Output ".\run.cmd"
}

# 启动 Runner 服务
Write-ColorOutput Cyan "`n[6/6] 启动 Runner 服务..."
try {
    .\svc.cmd start
    Write-ColorOutput Green "✓ 服务启动成功"
} catch {
    Write-ColorOutput Red "✗ 服务启动失败: $_"
}

# 完成
Write-Output ""
Write-ColorOutput Green "=========================================="
Write-ColorOutput Green "  ✓ 安装完成！"
Write-ColorOutput Green "=========================================="
Write-Output ""
Write-Output "Runner 已安装并启动为 Windows 服务"
Write-Output ""
Write-ColorOutput Cyan "管理命令:"
Write-Output ""
Write-Output "  查看服务状态:"
Write-Output "    .\svc.cmd status"
Write-Output ""
Write-Output "  停止服务:"
Write-Output "    .\svc.cmd stop"
Write-Output ""
Write-Output "  启动服务:"
Write-Output "    .\svc.cmd start"
Write-Output ""
Write-Output "  卸载服务:"
Write-Output "    .\svc.cmd uninstall"
Write-Output ""
Write-Output "  手动运行 (不使用服务):"
Write-Output "    .\run.cmd"
Write-Output ""
Write-ColorOutput Cyan "验证 Runner:"
Write-Output ""
Write-Output "1. 访问: $GithubUrl/settings/actions/runners"
Write-Output "2. 应该能看到名为 '$RunnerName' 的 Runner，状态为 'Idle'"
Write-Output ""
Write-ColorOutput Yellow "注意事项:"
Write-Output ""
Write-Output "1. Runner 现在作为 Windows 服务运行，开机自动启动"
Write-Output "2. 确保安装了所需的构建工具 (Java, Python 等)"
Write-Output "3. 详细配置请参考 WINDOWS_SETUP.md"
Write-Output ""
Write-ColorOutput Green "现在你可以推送代码到 GitHub，Actions 将在此 Runner 上运行！"
Write-Output ""
