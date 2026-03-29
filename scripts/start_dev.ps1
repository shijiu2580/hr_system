Param(
  [switch]$Install,
  [switch]$NoFrontend,
  [string]$BindHost = '127.0.0.1',
  [int]$Port = 8000
)

# 设置 UTF-8 编码，避免 npm 输出乱码
$OutputEncoding = [Console]::OutputEncoding = [Text.UTF8Encoding]::UTF8

$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$VenvPython = Join-Path $ProjectRoot 'venv\Scripts\python.exe'
$VenvPip = Join-Path $ProjectRoot 'venv\Scripts\pip.exe'
$PreferredNpm = 'D:\xia_zai\npm\npm.cmd'
$PreferredUv = 'C:\Users\lpf25\.local\bin\uv.exe'

Set-Location $ProjectRoot

$env:PYTHONUTF8 = '1'
$env:PIP_DISABLE_PIP_VERSION_CHECK = '1'

Write-Host "== HR System Dev Starter ==" -ForegroundColor Cyan

# 1. Resolve runtime executables
if (Test-Path $VenvPython) {
  $PythonExe = $VenvPython
  Write-Host "Using project virtual environment Python: $PythonExe" -ForegroundColor DarkCyan
} else {
  $PythonExe = 'python'
  Write-Host "No project venv found, falling back to PATH Python." -ForegroundColor Yellow
}

if (Test-Path $VenvPip) {
  $PipExe = $VenvPip
} else {
  $PipExe = 'pip'
}

if (Test-Path $PreferredUv) {
  $UvExe = $PreferredUv
} else {
  $UvExe = $null
}

if (Test-Path $PreferredNpm) {
  $NpmExe = $PreferredNpm
} else {
  $NpmExe = 'npm'
}

if ($Install) {
  Write-Host "Installing Python dependencies..." -ForegroundColor DarkCyan
  try {
    if ($UvExe) {
      & $UvExe pip install --python $PythonExe -r requirements.txt
    } else {
      & $PipExe install -r requirements.txt
    }
    if ($LASTEXITCODE -ne 0) { throw "Python dependency install failed ($LASTEXITCODE)" }
  } catch {
    Write-Host "pip install failed: $_" -ForegroundColor Red
    exit 1
  }
  if (Test-Path ./frontend/package.json) {
    Write-Host "Installing frontend dependencies..." -ForegroundColor DarkCyan
    try {
      Set-Location (Join-Path $ProjectRoot 'frontend')
      & $NpmExe install
      if ($LASTEXITCODE -ne 0) { throw "npm install failed ($LASTEXITCODE)" }
    } catch {
      Write-Host "npm install failed: $_" -ForegroundColor Red
      exit 1
    } finally {
      Set-Location $ProjectRoot
    }
  }
}

# 2. Run Django migrations (safe to call repeatedly)
Write-Host "Applying migrations..." -ForegroundColor DarkCyan
try {
  & $PythonExe manage.py migrate
  if ($LASTEXITCODE -ne 0) { throw "migrate failed ($LASTEXITCODE)" }
} catch {
  Write-Host "Migration failed: $_" -ForegroundColor Red
  exit 1
}

# 3. (Optional) seed RBAC permissions if first time
if ($Install) {
  Write-Host "Seeding RBAC default permissions & roles..." -ForegroundColor DarkCyan
  & $PythonExe manage.py init_rbac_permissions --with-roles
}

# 4. Start backend
Write-Host ("Starting Django backend on http://{0}:{1} ..." -f $BindHost,$Port) -ForegroundColor Green
$address = "{0}:{1}" -f $BindHost,$Port
$backend = Start-Process -FilePath $PythonExe -WorkingDirectory $ProjectRoot -ArgumentList @('manage.py','runserver',$address) -PassThru

# 5. Start frontend (unless skipped)
if (-not $NoFrontend -and (Test-Path ./frontend/package.json)) {
  Write-Host "Starting Vite frontend (http://127.0.0.1:5173)..." -ForegroundColor Green
  $frontend = Start-Process -FilePath $NpmExe -WorkingDirectory (Join-Path $ProjectRoot 'frontend') -ArgumentList @('run','dev') -PassThru
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
