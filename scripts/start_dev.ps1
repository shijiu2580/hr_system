Param(
  [switch]$Install,
  [switch]$NoFrontend,
  [string]$BindHost = '127.0.0.1',
  [int]$Port = 8000
)

# 设置 UTF-8 编码，避免 npm 输出乱码
$OutputEncoding = [Console]::OutputEncoding = [Text.UTF8Encoding]::UTF8

Write-Host "== HR System Dev Starter ==" -ForegroundColor Cyan

# 1. Python venv activation (optional)
if (Test-Path .\venv\Scripts\Activate.ps1) {
  Write-Host "Activating virtual environment..." -ForegroundColor DarkCyan
  . .\venv\Scripts\Activate.ps1
} else {
  Write-Host "No venv found (./venv). You can create one: python -m venv venv" -ForegroundColor Yellow
}

if ($Install) {
  Write-Host "Installing Python dependencies..." -ForegroundColor DarkCyan
  try {
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) { throw "Python dependency install failed ($LASTEXITCODE)" }
  } catch {
    Write-Host "pip install failed: $_" -ForegroundColor Red
    exit 1
  }
  if (Test-Path ./frontend/package.json) {
    Write-Host "Installing frontend dependencies..." -ForegroundColor DarkCyan
      Push-Location frontend
    try {
      npm install
      if ($LASTEXITCODE -ne 0) { throw "npm install failed ($LASTEXITCODE)" }
    } catch {
      Write-Host "npm install failed: $_" -ForegroundColor Red
        Pop-Location
      exit 1
    }
      Pop-Location
  }
}

# 2. Run Django migrations (safe to call repeatedly)
Write-Host "Applying migrations..." -ForegroundColor DarkCyan
try {
  python manage.py migrate
  if ($LASTEXITCODE -ne 0) { throw "migrate failed ($LASTEXITCODE)" }
} catch {
  Write-Host "Migration failed: $_" -ForegroundColor Red
  exit 1
}

# 3. (Optional) seed RBAC permissions if first time
if ($Install) {
  Write-Host "Seeding RBAC default permissions & roles..." -ForegroundColor DarkCyan
  python manage.py init_rbac_permissions --with-roles
}

# 4. Start backend
Write-Host ("Starting Django backend on http://{0}:{1} ..." -f $BindHost,$Port) -ForegroundColor Green
$address = "{0}:{1}" -f $BindHost,$Port
$backend = Start-Process -FilePath python -ArgumentList @('manage.py','runserver',$address) -PassThru

# 5. Start frontend (unless skipped)
if (-not $NoFrontend -and (Test-Path ./frontend/package.json)) {
  Write-Host "Starting Vite frontend (http://127.0.0.1:5173)..." -ForegroundColor Green
    Push-Location frontend
  $frontend = Start-Process -FilePath npm -ArgumentList @('run','dev') -PassThru
    Pop-Location
} else {
  Write-Host "Skipping frontend start (use --NoFrontend to suppress, or missing frontend)." -ForegroundColor Yellow
}

Write-Host ("`nBackend PID: {0}" -f $backend.Id) -ForegroundColor Cyan
if ($frontend) { Write-Host ("Frontend PID: {0}" -f $frontend.Id) -ForegroundColor Cyan }
Write-Host "\nPress ENTER to stop both..." -ForegroundColor Magenta
[void][Console]::ReadLine()

Write-Host "Stopping processes..." -ForegroundColor DarkYellow
try { if ($frontend) { Stop-Process $frontend -Force } } catch {}
try { Stop-Process $backend -Force } catch {}
Write-Host "Done." -ForegroundColor Green
