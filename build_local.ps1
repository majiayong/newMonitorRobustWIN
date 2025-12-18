# ============================================
# 本地 Windows APK 构建脚本
# ============================================

Write-Host "======================================"
Write-Host "  Windows 本地 APK 构建工具"
Write-Host "======================================"
Write-Host ""

# 切换到项目目录
$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectDir
Write-Host "[1/8] 项目目录: $projectDir"
Write-Host ""

# 检查虚拟环境
Write-Host "[2/8] 检查虚拟环境..."
if (-not (Test-Path ".\buildozer-venv\Scripts\Activate.ps1")) {
    Write-Host "❌ 虚拟环境不存在，正在创建..."
    python -m venv buildozer-venv
    Write-Host "✓ 虚拟环境创建成功"
} else {
    Write-Host "✓ 虚拟环境已存在"
}
Write-Host ""

# 激活虚拟环境
Write-Host "[3/8] 激活虚拟环境..."
.\buildozer-venv\Scripts\Activate.ps1
Write-Host "✓ 虚拟环境已激活"
Write-Host ""

# 检查并安装依赖
Write-Host "[4/8] 检查 Python 依赖..."
$packages = @("setuptools", "packaging", "buildozer==1.5.0", "cython==0.29.36")
foreach ($pkg in $packages) {
    $pkgName = $pkg.Split("==")[0]
    $installed = pip list --format=freeze | Select-String "^$pkgName=="
    if (-not $installed) {
        Write-Host "  安装 $pkg..."
        pip install $pkg
    } else {
        Write-Host "  ✓ $pkgName 已安装"
    }
}
Write-Host ""

# 检查 Java 环境
Write-Host "[5/8] 检查 Java 环境..."
$javaHome = $env:JAVA_HOME
if (-not $javaHome) {
    Write-Host "⚠ JAVA_HOME 未设置，尝试查找 JDK 17..."

    # 查找常见的 JDK 路径
    $possiblePaths = @(
        "F:\tool\jdk17",
        "C:\Program Files\Java\jdk-17",
        "C:\Program Files\OpenJDK\jdk-17"
    )

    foreach ($path in $possiblePaths) {
        if (Test-Path "$path\bin\java.exe") {
            $env:JAVA_HOME = $path
            $env:Path = "$path\bin;$env:Path"
            Write-Host "  ✓ 找到 JDK: $path"
            break
        }
    }
}

if ($env:JAVA_HOME) {
    Write-Host "  ✓ JAVA_HOME: $env:JAVA_HOME"
    & "$env:JAVA_HOME\bin\java.exe" -version
} else {
    Write-Host "  ❌ 未找到 JDK 17"
    Write-Host "  请安装 JDK 17 或设置 JAVA_HOME 环境变量"
    Write-Host ""
    Write-Host "安装方法："
    Write-Host "  choco install openjdk17 -y"
    pause
    exit 1
}
Write-Host ""

# 确保 Git 在 PATH 中
Write-Host "[6/8] 检查 Git..."
$gitPaths = @(
    "C:\Program Files\Git\cmd",
    "C:\Program Files\Git\mingw64\bin"
)
foreach ($gitPath in $gitPaths) {
    if (Test-Path $gitPath) {
        $env:Path = "$gitPath;$env:Path"
    }
}

try {
    $gitVersion = git --version
    Write-Host "  ✓ $gitVersion"
} catch {
    Write-Host "  ❌ Git 未安装或不在 PATH 中"
    Write-Host "  请安装 Git: choco install git -y"
    pause
    exit 1
}
Write-Host ""

# Patch buildozer
Write-Host "[7/8] Patch Buildozer 源代码..."
$buildozerModule = python -c "import buildozer; print(buildozer.__file__)"
if ($buildozerModule) {
    Write-Host "  Buildozer 路径: $buildozerModule"

    # 运行 patch 脚本
    python patch_buildozer.py "$buildozerModule"

    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Patch 成功"
    } else {
        Write-Host "  ⚠ Patch 失败，但继续尝试构建"
    }
} else {
    Write-Host "  ❌ 未找到 Buildozer"
    exit 1
}
Write-Host ""

# 开始构建
Write-Host "[8/8] 开始构建 APK..."
Write-Host "======================================"
Write-Host ""
Write-Host "这可能需要 30-60 分钟（首次构建）"
Write-Host "Buildozer 将下载 Android SDK/NDK"
Write-Host ""
Write-Host "按 Ctrl+C 可以随时取消"
Write-Host ""
Write-Host "======================================"
Write-Host ""

# 设置环境变量
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUNBUFFERED = "1"

# 再次确保 Git 和 Java 在 PATH 中（buildozer需要）
$gitPath = "C:\Program Files\Git\cmd"
if (Test-Path $gitPath) {
    $env:Path = "$gitPath;$env:Path"
}
if ($env:JAVA_HOME) {
    $env:Path = "$env:JAVA_HOME\bin;$env:Path"
}

# 显示 buildozer 版本
buildozer --version

# 开始构建
Write-Host ""
Write-Host ">>> 开始构建..."
Write-Host ""

buildozer -v android debug

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "======================================"
    Write-Host "  ✓ 构建成功！"
    Write-Host "======================================"
    Write-Host ""
    Write-Host "APK 文件位置："
    Get-ChildItem -Path ".\bin\*.apk" | ForEach-Object {
        Write-Host "  -> $($_.FullName)"
    }
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "======================================"
    Write-Host "  ❌ 构建失败"
    Write-Host "======================================"
    Write-Host ""
    Write-Host "请检查上面的错误信息"
    Write-Host ""
}

Write-Host "按任意键退出..."
pause
