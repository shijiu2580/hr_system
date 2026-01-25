# Django HR 管理系统

## 项目简介

完全前后端分离的人力资源管理系统，采用 Django REST Framework + Vue 3 架构。

## 技术栈

### 后端
- **框架**: Django 4.2.7
- **API**: Django REST Framework
- **认证**: SimpleJWT (JWT Token)
- **数据库**: SQLite (开发) / PostgreSQL (生产推荐)
- **权限**: 自定义 RBAC 系统

### 前端
- **框架**: Vue 3
- **构建工具**: Vite
- **状态管理**: Pinia
- **路由**: Vue Router
- **HTTP 客户端**: Axios
- **图表**: Chart.js

## 核心功能

- ✅ 员工信息管理
- ✅ 部门与职位管理
- ✅ 考勤记录管理
- ✅ 请假申请与审批
- ✅ 薪资管理与发放
- ✅ 角色权限管理 (RBAC)
- ✅ 系统操作日志
- ✅ 数据库备份与恢复
- ✅ JWT 认证与刷新
- ✅ 首次登录强制修改密码

## 快速开始

### 1. 环境准备

确保已安装:
- Python 3.8+
- Node.js 18+
- npm 或 yarn

### 2. 后端启动

```powershell
# 激活虚拟环境
.\venv\Scripts\Activate.ps1

# 安装依赖
pip install -r requirements.txt

# 数据库迁移
python manage.py migrate

# 创建超级管理员
python manage.py createsuperuser

# 启动后端服务 (默认 http://127.0.0.1:8000)
python manage.py runserver
```

### 3. 前端启动

```powershell
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器 (默认 http://127.0.0.1:5173)
npm run dev
```

### 4. 一键启动（推荐）

```powershell
# 使用自动化启动脚本
.\scripts\start_dev.ps1

# 带参数启动（安装依赖）
.\scripts\start_dev.ps1 -Install

# 仅启动后端
.\scripts\start_dev.ps1 -NoFrontend
```

## 项目结构

```
django_hr_system/
├── docs/                    # 文档目录
│   └── API.md              # API 接口文档
├── frontend/                # Vue3 前端项目
│   ├── src/
│   │   ├── components/     # 可复用组件
│   │   ├── pages/          # 页面组件
│   │   ├── router/         # 路由配置
│   │   ├── stores/         # Pinia 状态管理
│   │   └── utils/          # 工具函数
│   └── package.json
├── hr_management/           # Django 应用
│   ├── api_serializers.py  # DRF 序列化器
│   ├── api_views.py        # API 视图集
│   ├── api_urls.py         # API 路由
│   ├── models.py           # 数据模型
│   ├── permissions.py      # 权限类
│   └── utils.py            # 工具函数
├── hr_system/               # Django 项目配置
│   ├── settings.py         # 项目设置
│   ├── urls.py             # 根路由
│   └── wsgi.py
├── media/                   # 用户上传文件
│   ├── avatars/            # 头像
│   ├── documents/          # 文档
│   └── backups/            # 数据库备份
├── scripts/                 # 启动脚本
│   └── start_dev.ps1       # 开发环境启动脚本
├── venv/                    # Python 虚拟环境
├── manage.py
├── requirements.txt        # Python 依赖
└── README.md
```

## 环境变量配置

创建 `.env` 文件并配置以下变量:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
```

前端环境变量 (`frontend/.env.local`):

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api
```

## API 文档

详细的 API 接口文档请参考 [docs/API.md](docs/API.md)

## 权限系统

系统采用基于角色的访问控制 (RBAC):

- **超级管理员**: 拥有所有权限
- **人事管理员**: 员工管理、薪资管理、考勤管理
- **部门经理**: 查看本部门数据、审批请假
- **普通员工**: 查看个人信息、提交请假、查看考勤

## 自动化任务

系统支持通过 Windows 任务计划程序实现:

- 每月自动生成薪资记录
- 每月自动发放薪资

详细配置请参考源码中的注释。

## 开发指南

### 后端开发

- 所有 API 端点定义在 `hr_management/api_urls.py`
- 业务逻辑在 `hr_management/api_views.py`
- 数据模型在 `hr_management/models.py`
- 权限控制在 `hr_management/permissions.py`

### 前端开发

- 页面组件放在 `frontend/src/pages/`
- 通用组件放在 `frontend/src/components/`
- API 调用统一在 `frontend/src/utils/api.js`
- 状态管理使用 Pinia stores

## 生产部署

### 后端部署

1. 设置 `DEBUG=False`
2. 配置 `ALLOWED_HOSTS`
3. 使用生产级数据库 (PostgreSQL)
4. 收集静态文件: `python manage.py collectstatic`
5. 使用 Gunicorn + Nginx

### 前端部署

1. 构建生产版本: `npm run build`
2. 部署 `dist/` 目录到 Web 服务器
3. 配置 Nginx 反向代理

## 贡献指南

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 联系方式

如有问题，请提交 Issue 或联系项目维护者。
