param(
    [ValidateSet("private", "public", "both")]
    [string]$Target = "both",
    [string]$Message = "update"
)

$ErrorActionPreference = "Continue"

# Sensitive files list
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

# Push to private repo
if ($Target -eq "private" -or $Target -eq "both") {
    Write-Host "[INFO] Pushing to private repo (origin)..." -ForegroundColor Cyan

    git add -A
    foreach ($file in $SensitiveFiles) {
        if (Test-Path $file) {
            git add -f $file 2>$null
        }
    }

    git commit -m $Message 2>$null
    git push origin main

    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Private repo pushed" -ForegroundColor Green
    } else {
        Write-Host "[WARN] Private repo push failed or up-to-date" -ForegroundColor Yellow
    }
    Write-Host ""
}

# Push to public repo
if ($Target -eq "public" -or $Target -eq "both") {
    Write-Host "[INFO] Pushing to public repo (public)..." -ForegroundColor Cyan

    # Remove sensitive files from tracking
    $removedFiles = @()
    foreach ($file in $SensitiveFiles) {
        git rm --cached $file 2>$null
        if ($LASTEXITCODE -eq 0) {
            $removedFiles += $file
        }
    }

    if ($removedFiles.Count -gt 0) {
        Write-Host "  Excluded: $($removedFiles -join ', ')" -ForegroundColor Gray
        git commit -m "chore: exclude sensitive files" 2>$null
    }

    git push public main

    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Public repo pushed" -ForegroundColor Green
    } else {
        Write-Host "[WARN] Public repo push failed" -ForegroundColor Yellow
    }

    # Restore sensitive files for private repo
    if ($removedFiles.Count -gt 0 -and $Target -eq "both") {
        foreach ($file in $removedFiles) {
            if (Test-Path $file) {
                git add -f $file 2>$null
            }
        }
        git commit -m "private: restore sensitive files" 2>$null
        git push origin main 2>$null
        Write-Host "  Restored files to private repo" -ForegroundColor Gray
    }
    Write-Host ""
}

Write-Host "========================================" -ForegroundColor Magenta
Write-Host "[DONE] Push completed!" -ForegroundColor Green
Write-Host ""
Write-Host "Repos:" -ForegroundColor White
Write-Host "  Private: https://github.com/shijiu2580/hr_system_private" -ForegroundColor Gray
Write-Host "  Public:  https://github.com/shijiu2580/hr_system" -ForegroundColor Gray
Write-Host ""
