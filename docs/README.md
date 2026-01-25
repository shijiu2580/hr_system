# Django HR 人力资源管理系统

<p align="center">
  <img src="../frontend/public/images/logo.png" alt="Logo" width="80" height="80">
</p>

<p align="center">
  一款功能完善的企业级人力资源管理系统，采用前后端分离架构
</p>

---

## 📋 项目简介

Django HR 管理系统是一套完整的企业人力资源解决方案，涵盖员工管理、考勤管理、请假审批、薪资发放、出差报销、离职流程等核心业务模块。系统采用 **Django REST Framework + Vue 3** 前后端分离架构，支持 **RBAC 权限控制**、**移动端自助入职**、**Docker 容器化部署** 等企业级特性。

## ✨ 核心特性

| 模块 | 功能亮点 |
|------|----------|
| **员工管理** | 档案管理、批量导入/导出、多级部门、职位薪资区间 |
| **考勤管理** | GPS 定位打卡、多地点配置、异常提醒、补签审批 |
| **请假管理** | 多类型请假、审批流程、自动计算时长 |
| **出差管理** | 出差申请、差旅报销、发票上传、审批发放 |
| **薪资管理** | 薪资生成、批量发放、工资条导出 |
| **离职管理** | 离职申请、审批流程、交接管理 |
| **权限系统** | 基于 RBAC 的细粒度权限控制 |
| **系统管理** | 操作日志、数据备份与恢复、系统监控 |
| **移动端** | H5 自助入职、信息填写、审核流程 |

## 🛠 技术栈

### 后端技术
| 技术 | 版本 | 说明 |
|------|------|------|
| Django | 4.2.7 | Web 框架 |
| Django REST Framework | 3.14.0 | RESTful API |
| SimpleJWT | 5.3.1 | JWT 认证 |
| SQLite / PostgreSQL | - | 数据库 |
| Gunicorn | 21.2.0 | WSGI 服务器 |
| Pillow | 10.1.0 | 图片处理 |
| openpyxl | 3.1.2 | Excel 导入导出 |
| psutil | 5.9.8 | 系统监控 |

### 前端技术
| 技术 | 说明 |
|------|------|
| Vue 3 | 渐进式框架 (Composition API) |
| Vite | 构建工具 |
| Pinia | 状态管理 |
| Vue Router | 路由管理 |
| Axios | HTTP 客户端 |
| Chart.js | 图表可视化 |

### 部署方案
| 方案 | 说明 |
|------|------|
| Docker + Docker Compose | 容器化部署 |
| Kubernetes (K8s) | 云原生部署 |
| Nginx | 反向代理 & 静态资源 |
| Render | 云平台一键部署 |

## 📁 项目结构

```
django_hr_system/
├── docs/                       # 📚 项目文档
│   ├── README.md              # 项目说明
│   ├── API.md                 # API 接口文档
│   └── RBAC.md                # 权限系统文档
├── frontend/                   # 🖥️ Vue3 前端项目
│   ├── src/
│   │   ├── components/        # 通用组件
│   │   ├── pages/             # 页面组件
│   │   │   ├── attendance/    # 考勤模块
│   │   │   ├── employees/     # 员工模块
│   │   │   ├── leaves/        # 请假/出差模块
│   │   │   ├── salaries/      # 薪资模块
│   │   │   ├── departments/   # 部门管理
│   │   │   ├── positions/     # 职位管理
│   │   │   ├── rbac/          # 权限管理
│   │   │   ├── reports/       # 数据报表
│   │   │   └── system/        # 系统管理
│   │   ├── router/            # 路由配置
│   │   ├── stores/            # Pinia 状态
│   │   └── utils/             # 工具函数
│   └── package.json
├── mobile/                     # 📱 移动端 H5 项目
│   └── src/                   # 自助入职等功能
├── hr_management/              # 🔧 Django 核心应用
│   ├── api/                   # API 视图层
│   │   ├── views/             # 视图集
│   │   └── serializers/       # 序列化器
│   ├── models.py              # 数据模型
│   ├── permissions.py         # 权限类
│   ├── rbac.py                # RBAC 权限定义
│   ├── services.py            # 业务逻辑层
│   └── api_urls.py            # API 路由
├── hr_system/                  # ⚙️ Django 项目配置
│   └── settings.py            # 项目设置
├── k8s/                        # ☸️ Kubernetes 配置
├── scripts/                    # 🚀 启动脚本
├── media/                      # 📂 用户上传文件
│   ├── avatars/               # 员工头像
│   ├── documents/             # 公司文档
│   ├── invoices/              # 报销发票
│   └── backups/               # 数据备份
├── docker-compose.yml          # Docker 编排
├── Dockerfile                  # 后端镜像
├── requirements.txt            # Python 依赖
└── manage.py
```

## 🚀 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- npm 或 pnpm

### 方式一：本地开发

```powershell
# 1. 克隆项目
git clone <repo-url>
cd django_hr_system

# 2. 后端设置
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py init_rbac          # 初始化权限数据
python manage.py createsuperuser    # 创建管理员

# 3. 启动后端 (http://127.0.0.1:8000)
python manage.py runserver

# 4. 前端设置（新终端）
cd frontend
npm install
npm run dev                         # http://127.0.0.1:5173
```

### 方式二：一键启动脚本

```powershell
# 使用自动化脚本
.\scripts\start_dev.ps1

# 首次运行（安装依赖）
.\scripts\start_dev.ps1 -Install
```

### 方式三：Docker 部署

```bash
# 构建并启动
docker-compose up -d --build

# 查看状态
docker-compose ps

# 初始化数据
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py init_rbac
docker-compose exec backend python manage.py createsuperuser
```

## ⚙️ 环境配置

### 后端环境变量 (`.env`)

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# 数据库 (生产环境使用 PostgreSQL)
DATABASE_URL=sqlite:///db.sqlite3
# DATABASE_URL=postgres://user:password@localhost:5432/hr_db
```

### 前端环境变量 (`frontend/.env.local`)

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api
```

## 📖 相关文档

- [API 接口文档](./API.md) - 完整的 RESTful API 说明
- [RBAC 权限文档](./RBAC.md) - 权限系统设计与使用

## 🔐 默认账户

| 角色 | 用户名 | 密码 | 说明 |
|------|--------|------|------|
| 超级管理员 | admin | (自行设置) | 拥有所有权限 |

## 📝 开发指南

### 后端开发

```python
# 新增 API 端点
# 1. 在 hr_management/api/views/ 下创建视图
# 2. 在 hr_management/api/serializers/ 下创建序列化器
# 3. 在 hr_management/api_urls.py 注册路由
```

### 前端开发

```javascript
// 新增页面
// 1. 在 frontend/src/pages/ 下创建页面组件
// 2. 在 frontend/src/router/index.js 注册路由
// 3. 使用 frontend/src/utils/api.js 调用接口
```

### 权限开发

```python
# 新增权限
# 1. 在 hr_management/rbac.py 添加权限常量
# 2. 运行 python manage.py init_rbac --force
# 3. 前端同步更新 frontend/src/utils/permissions.js
```

## 🚢 生产部署

### Docker 生产部署

```yaml
# docker-compose.prod.yml
services:
  backend:
    environment:
      - DEBUG=False
      - ALLOWED_HOSTS=your-domain.com
```

### Kubernetes 部署

```bash
# 应用 K8s 配置
kubectl apply -k k8s/
```

### Render 一键部署

项目包含 `render.yaml`，可直接在 [Render](https://render.com) 平台部署。

## 📄 许可证

本项目采用 [MIT License](../LICENSE) 开源协议。

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request
