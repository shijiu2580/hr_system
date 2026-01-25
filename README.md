# Django HR 管理系统

> **完全前后端分离架构**: Django REST API + Vue3 SPA

##  项目简介

现代化的人力资源管理系统，采用前后端完全分离架构。后端使用 Django REST Framework 提供 RESTful API，前端使用 Vue 3 构建单页应用，提供流畅的用户体验。

##  核心功能

-  员工信息管理
-  部门与职位管理
-  考勤记录管理
-  请假申请与审批
-  薪资管理与发放
-  角色权限管理 (RBAC)
-  系统操作日志
-  数据库备份与恢复
-  JWT 认证与刷新
-  首次登录强制修改密码

##  技术栈

### 后端
- Django 4.2.7 + Django REST Framework
- JWT 认证 (SimpleJWT)
- SQLite (开发) / PostgreSQL (生产推荐)
- 自定义 RBAC 权限系统

### 前端
- Vue 3 + Vite
- Pinia (状态管理)
- Vue Router
- Axios + Chart.js

##  项目结构

```
django_hr_system/
 docs/                    #  文档目录
    README.md           # 详细文档
    API.md              # API 接口文档
 frontend/                #  Vue3 前端
    src/
       components/     # 可复用组件
       pages/          # 页面组件
       router/         # 路由配置
       stores/         # Pinia 状态管理
       utils/          # 工具函数
    package.json
 hr_management/           #  Django 应用
    api_serializers.py  # DRF 序列化器
    api_views.py        # API 视图集
    api_urls.py         # API 路由
    models.py           # 数据模型
    permissions.py      # 权限控制
 hr_system/               #  Django 项目配置
 media/                   #  用户上传文件
 scripts/                 #  启动脚本
    start_dev.ps1       # 开发环境启动
 venv/                    #  Python 虚拟环境
 manage.py
 requirements.txt
 README.md
```

##  快速开始

### 方式一：一键启动（推荐）

```powershell
# 使用自动化启动脚本
.\scripts\start_dev.ps1

# 首次启动（安装依赖）
.\scripts\start_dev.ps1 -Install

# 仅启动后端
.\scripts\start_dev.ps1 -NoFrontend
```

### 方式二：手动启动

**后端启动**

```powershell
# 激活虚拟环境
.\venv\Scripts\Activate.ps1

# 安装依赖
pip install -r requirements.txt

# 数据库迁移
python manage.py migrate

# 创建超级管理员
python manage.py createsuperuser

# 启动后端服务 (http://127.0.0.1:8000)
python manage.py runserver
```

**前端启动**

```powershell
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器 (http://127.0.0.1:5173)
npm run dev
```

##  文档

- [详细文档](docs/README.md) - 完整的项目文档和开发指南
- [API 文档](docs/API.md) - RESTful API 接口文档

##  默认账户

首次启动后需要创建超级管理员账户：

```powershell
python manage.py createsuperuser
```

##  环境变量

项目根目录 `.env` 文件:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

前端 `frontend/.env.local` 文件:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api
```

##  依赖管理

**后端依赖**
```powershell
pip install -r requirements.txt
```

**前端依赖**
```powershell
cd frontend
npm install
```

##  生产部署

### 后端部署建议

1. 设置 `DEBUG=False`
2. 配置生产级数据库 (PostgreSQL)
3. 使用 Gunicorn + Nginx
4. 配置 HTTPS

### 前端部署建议

1. 构建生产版本: `npm run build`
2. 部署 `dist/` 目录
3. 配置 Nginx 反向代理

##  许可证

MIT License

##  贡献

欢迎提交 Issue 和 Pull Request！

---

更多详细信息请查看 [完整文档](docs/README.md)
