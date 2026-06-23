---
name: windows-env-check
description: >
  Verify PowerShell tool reliability on Windows. Tests basic execution, dollar sign escaping,
  backtick escaping, quotes, Unicode, file system access, external programs, and error handling.
  Use on any new Windows machine before starting real work, when user says "check environment",
  "env check", "windows check", "powershell check", or "test powershell".
---

# Windows Environment Check

Verify that the PowerShell tool in this Claude Code instance works correctly before doing real work.

## When to run

- First time using Claude Code on a new Windows machine
- After updating the Claude Code extension
- When user suspects environment issues
- User says "check env", "test powershell", "windows check", etc.

## Test procedure

Run ALL 7 tests below using the PowerShell tool. Do NOT skip any. Do NOT use Bash to call pwsh — test the PowerShell tool directly (that's the whole point).

All tests MUST succeed. If any fail, tell the user which one and stop.

### 1. Basic execution

```
1 + 1
```
Expected: output contains `2`, no error.

### 2. Dollar sign in strings

```
Write-Output "Expand: $env:OS"; Write-Output 'Literal: $env:OS'
```
Expected: first line shows `Expand: Windows_NT`, second line shows `Literal: $env:OS`.

### 3. Backtick escape sequences

```
Write-Output "tab:`there newline:`nline2"
```
Expected: output contains a tab between `tab:` and `here`, and `newline:` followed by a newline then `line2`.

### 4. Unicode and Chinese

```
Write-Output "中文测试"; Write-Output "🎲⚔️🛡️"
```
Expected: both lines output correctly, no garbled characters.

### 5. Quotes and special chars

```
Write-Output 'single quotes: $ stays literal'; Write-Output "double quotes:`$ escaped dollar"
```
Expected: `$` appears as literal in single-quoted string. `$` appears as literal in double-quoted string (because backtick-escaped).

### 6. File system access

```
Get-ChildItem "$env:USERPROFILE" -ErrorAction SilentlyContinue | Select-Object -First 1 Name
```
Expected: lists one item from user profile, no error.

### 7. External program

```
git --version 2>&1
```
Expected: outputs git version string, no error. If git is not installed, this is NOT a PowerShell failure — mark as "SKIP (git not found)" rather than FAIL.

## Output format

After running all tests, print a single report:

```
Windows Env Check Report
========================
1. Basic execution   : PASS/FAIL
2. Dollar sign       : PASS/FAIL
3. Backtick escape   : PASS/FAIL
4. Unicode           : PASS/FAIL
5. Quotes/special    : PASS/FAIL
6. File system       : PASS/FAIL
7. External program  : PASS/FAIL/SKIP
========================
Overall: ALL PASS / N FAILURES (list failures)

Verdict: READY / NOT READY
```

If `NOT READY`, explain the failing tests and suggest fixes.

## Troubleshooting

### PowerShell tool always exits with code 1 (all tests fail)

**根因**：VSCode 扩展（侧边栏/插件模式）的宿主进程有限制，扩展内置的 PowerShell 工具在该上下文中 spawn 子进程会失败。这不是路径或配置问题——是扩展本身的 bug。

**修复**：切换到终端模式使用 CC，而非 VSCode 扩展。
- 在 **VSCode 终端**（Ctrl+` → 切到 PowerShell/Git Bash）或 **外置 PowerShell 终端** 里启动 `claude`
- 终端模式下 PowerShell 工具正常工作

**settings.json 参考配置**（终端模式下生效）：
```json
{
  "env": {
    "CLAUDE_CODE_USE_POWERSHELL_TOOL": "1",
    "CLAUDE_CODE_POWERSHELL_PATH": "powershell.exe"
  }
}
```
设置后重启 CC 会话。`CLAUDE_CODE_POWERSHELL_PATH` 不设也能自动检测，显式指定可避免 WindowsApps 路径探测失败。

### Other common issues

- **PowerShell not found**: Run `where pwsh` and `where powershell` in cmd to verify installation
- **Execution policy blocks scripts**: Run `Get-ExecutionPolicy` in PowerShell — should be `RemoteSigned` or `Unrestricted`
- **Claude Code version too old**: Update via VSCode extension marketplace
- **Only specific tests fail**: Check the 2>&1 error output in the failed test report for details

### 中文输出乱码（PowerShell 通过 cmd.exe Bash 工具调用时）

**根因**：Kilo 的 Bash 工具使用 `cmd.exe`（默认代码页 CP936/ANSI）作为 shell。PowerShell 输出的 Unicode 经 ANSI 转码后，中文等非 ASCII 字符截断为乱码。

**修复**：在 PowerShell 命令前置设置编码：

```powershell
$OutputEncoding = [Console]::OutputEncoding = [Text.Encoding]::UTF8; cmd /c "chcp 65001>nul" | out-null; <实际命令>
```

示例：
```powershell
$OutputEncoding = [Console]::OutputEncoding = [Text.Encoding]::UTF8; cmd /c "chcp 65001>nul" | out-null; Get-ChildItem -Recurse -Name 目录含中文
```

> 注：`chcp 65001` 单独调用无效，必须配合 `[Console]::OutputEncoding` 和 `$OutputEncoding` 同时设置。
