<#
.SYNOPSIS
    推送代码到私有仓库和公开仓库

.DESCRIPTION
    - 私有仓库 (origin): 推送全部文件，包括数据库和敏感配置
    - 公开仓库 (public): 只推送代码，排除敏感数据

.PARAMETER Target
    推送目标: private, public, both (默认 both)

.PARAMETER Message
    Git 提交信息 (默认: "update")

.EXAMPLE
    .\scripts\git_push.ps1                           # 推送到两个仓库
    .\scripts\git_push.ps1 -Target private           # 只推送到私有仓库
    .\scripts\git_push.ps1 -Target public            # 只推送到公开仓库
    .\scripts\git_push.ps1 -Message "fix: bug fix"   # 自定义提交信息
#>

param(
    [ValidateSet("private", "public", "both")]
    [string]$Target = "both",
    [string]$Message = "update"
)

$ErrorActionPreference = "Stop"

# 颜色输出
function Write-Success { param($msg) Write-Host "✅ $msg" -ForegroundColor Green }
function Write-Info { param($msg) Write-Host "📌 $msg" -ForegroundColor Cyan }
function Write-Warn { param($msg) Write-Host "⚠️  $msg" -ForegroundColor Yellow }

# 敏感文件列表
$SensitiveFiles = @(
    ".env",
    "data/db.sqlite3",
    "db.sqlite3",
    "data_clean.json",
    "db_base64.txt",
    "db_copy.sqlite3"
)

Write-Host ""
Write-Host "========================================" -ForegroundColor Magenta
Write-Host "   Django HR System - Git Push Tool    " -ForegroundColor Magenta
Write-Host "========================================" -ForegroundColor Magenta
Write-Host ""

# 检查是否有更改
$status = git status --porcelain
if (-not $status -and $Target -ne "public") {
    Write-Warn "没有检测到文件更改"
}

# ============ 推送到私有仓库 ============
if ($Target -eq "private" -or $Target -eq "both") {
    Write-Info "推送到私有仓库 (origin)..."

    # 添加所有文件，包括敏感文件
    git add -A
    foreach ($file in $SensitiveFiles) {
        if (Test-Path $file) {
            git add -f $file 2>$null
        }
    }

    # 提交
    $commitResult = git commit -m "$Message" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   提交成功: $Message" -ForegroundColor Gray
    }

    # 推送
    git push origin main
    if ($LASTEXITCODE -eq 0) {
        Write-Success "私有仓库推送完成"
    } else {
        Write-Warn "私有仓库推送失败"
    }
    Write-Host ""
}

# ============ 推送到公开仓库 ============
if ($Target -eq "public" -or $Target -eq "both") {
    Write-Info "推送到公开仓库 (public)..."

    # 临时移除敏感文件的跟踪
    $removedFiles = @()
    foreach ($file in $SensitiveFiles) {
        $result = git rm --cached $file 2>&1
        if ($LASTEXITCODE -eq 0) {
            $removedFiles += $file
        }
    }

    if ($removedFiles.Count -gt 0) {
        Write-Host "   已排除敏感文件: $($removedFiles -join ', ')" -ForegroundColor Gray
        git commit -m "chore: exclude sensitive files for public repo" 2>$null
    }

    # 推送到公开仓库
    git push public main
    if ($LASTEXITCODE -eq 0) {
        Write-Success "公开仓库推送完成"
    } else {
        Write-Warn "公开仓库推送失败"
    }

    # 恢复敏感文件到私有仓库跟踪
    if ($removedFiles.Count -gt 0 -and ($Target -eq "both")) {
        foreach ($file in $removedFiles) {
            if (Test-Path $file) {
                git add -f $file 2>$null
            }
        }
        git commit -m "private: restore sensitive files" 2>$null
        git push origin main 2>$null
        Write-Host "   已恢复敏感文件到私有仓库" -ForegroundColor Gray
    }
    Write-Host ""
}

Write-Host "========================================" -ForegroundColor Magenta
Write-Success "推送完成！"
Write-Host ""
Write-Host "仓库状态:" -ForegroundColor White
Write-Host "  私有: https://github.com/shijiu2580/hr_system_private" -ForegroundColor Gray
Write-Host "  公开: https://github.com/shijiu2580/hr_system" -ForegroundColor Gray
Write-Host ""
