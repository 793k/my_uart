# check-env.ps1 — Yichip AI 环境检查脚本
# 用途：验证用脚手架搭建 AI 开发环境需要的所有条件
# 用法：在 VS Code 终端中运行 .\check-env.ps1

$ErrorActionPreference = "Continue"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Yichip AI 环境检查" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# ── 1. 脚手架文件 ──
Write-Host "`n── 脚手架文件 ──" -ForegroundColor Yellow
$ok = $true

if (Test-Path ".\AGENTS.md") {
    Write-Host "[OK] AGENTS.md 存在" -ForegroundColor Green
} else {
    Write-Host "[FAIL] AGENTS.md 缺失 — 请重新从脚手架仓库复制" -ForegroundColor Red
    $ok = $false
}

if (Test-Path ".\.kilo\kilo.jsonc") {
    Write-Host "[OK] .kilo\kilo.jsonc 存在" -ForegroundColor Green
} else {
    Write-Host "[FAIL] .kilo\ 目录不完整 — 请重新从脚手架仓库复制" -ForegroundColor Red
    $ok = $false
}

# ── 2. VS Code ──
Write-Host "`n── VS Code ──" -ForegroundColor Yellow

$codePath = $null

# 2a. 从注册表找安装路径
$regPaths = @(
    "HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*",
    "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*"
)
foreach ($regPath in $regPaths) {
    $item = Get-ItemProperty $regPath -ErrorAction SilentlyContinue |
        Where-Object { $_.DisplayName -match "Visual Studio Code" } |
        Select-Object -First 1
    if ($item -and $item.InstallLocation) {
        $codeBin = Join-Path $item.InstallLocation "bin\code.cmd"
        if (Test-Path $codeBin) {
            Write-Host "[OK] VS Code 已安装: $($item.InstallLocation)" -ForegroundColor Green
            $codePath = $codeBin
            break
        }
    }
}

# 2b. 注册表没用，试 PATH
if (-not $codePath) {
    try {
        $cmd = (Get-Command "code" -ErrorAction Stop).Source
        Write-Host "[OK] VS Code 命令行可用: $cmd" -ForegroundColor Green
        $codePath = $cmd
    } catch {
        Write-Host "[WARN] 未检测到 VS Code" -ForegroundColor Yellow
        Write-Host "       下载地址: https://code.visualstudio.com" -ForegroundColor Gray
    }
}

# ── 3. Kilo Code 插件 ──
Write-Host "`n── Kilo Code 插件 ──" -ForegroundColor Yellow

$extDir = "$env:USERPROFILE\.vscode\extensions"
$kiloExt = Get-ChildItem -Path $extDir -Directory -Filter "kilocode.*" -ErrorAction SilentlyContinue |
    Select-Object -First 1

if ($kiloExt) {
    Write-Host "[OK] Kilo Code 插件已安装: $($kiloExt.Name)" -ForegroundColor Green
} else {
    Write-Host "[WARN] 未检测到 Kilo Code 插件" -ForegroundColor Yellow
    Write-Host "       VS Code → 扩展(Ctrl+Shift+X) → 搜索 'Kilo Code' → 安装" -ForegroundColor Gray
}

# ── 4. API Key ──
Write-Host "`n── API Key ──" -ForegroundColor Yellow

# API Key 由 VS Code SecretStorage 加密存储，无法通过文件系统直接读取。
# 通过检查 settings.json 中是否有 Kilo 相关配置来判断是否曾经使用过 Kilo。
$settingsFound = $false
$settingsPath = "$env:APPDATA\Code\User\settings.json"
if (Test-Path $settingsPath) {
    $kiloSettings = Select-String -Path $settingsPath -Pattern "kilo-code" -SimpleMatch -ErrorAction SilentlyContinue
    if ($kiloSettings) {
        Write-Host "[OK] VS Code settings.json 中有 Kilo 配置记录" -ForegroundColor Green
        $settingsFound = $true
    }
}

if (-not $settingsFound) {
    Write-Host "[INFO] 未检测到 API Key 配置（或首次使用）" -ForegroundColor Gray
    Write-Host "       在 Kilo Code 面板中：" -ForegroundColor Gray
    Write-Host "         设置(齿轮) → 提供商 → 查看更多 → Deepseek → 填入 API Key" -ForegroundColor Gray
    Write-Host "       还没有 Key？联系葛嘉昊" -ForegroundColor Gray
}

# ── 5. 汇总 ──
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  检查完毕" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
if ($ok) {
    Write-Host "环境基本就绪。下一步：" -ForegroundColor White
} else {
    Write-Host "有文件缺失。下一步：" -ForegroundColor Yellow
}
Write-Host "  1. VS Code 打开当前目录" -ForegroundColor White
Write-Host "  2. 在 Kilo Code 对话框输入 /使用指南" -ForegroundColor White
Write-Host "  3. 或直接告诉 AI 你想做什么" -ForegroundColor White
Write-Host ""
Write-Host "有问题？在公司 AI 群提问。" -ForegroundColor Gray
