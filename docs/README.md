# Django HR 人力资源管理系统

<p align="center">
  <img src="../frontend/public/images/logo.png" alt="Logo" width="80" height="80">
</p>

<p align="center">
  一款功能完善的企业级人力资源管理系统，采用前后端分离架构
</p>

---

## 📋 项目简介

Django HR 管理系统是一套完整的企业人力资源解决方案，涵盖员工管理、考勤管理、请假审批、薪资发放、出差报销、离职流程等核心业务模块。系统采用 **Django REST Framework + Vue 3** 前后端分离架构，支持 **RBAC 权限控制**、**移动端 H5 签到打卡**、**Docker 容器化部署** 等企业级特性。

## ✨ 功能模块详情

### 👥 员工管理
| 功能页面 | 功能说明 |
|----------|----------|
| 员工列表 | 全员信息查看、高级搜索、**Excel 批量导入**、导出 |
| 员工详情 | 完整档案（个人信息、户籍、教育、银行卡、紧急联系人） |
| 员工创建/编辑 | 表单校验、头像上传、身份证照片 |
| 入职审核 | 自助注册 → HR 审核 → 正式入职流程 |

### ⏰ 考勤管理
| 功能页面 | 功能说明 |
|----------|----------|
| 考勤记录 | 全员考勤查看、多维度筛选 |
| 我的考勤 | 个人打卡记录、加班打卡、**Excel 导出** |
| 考勤异常 | 缺勤/迟到/早退分组统计、按员工聚合 |
| 补签申请 | 员工提交补签、审批流程 |
| 签到地点 | 多地点管理、**地理围栏范围**、员工关联 |

### 📝 请假与出差
| 功能页面 | 功能说明 |
|----------|----------|
| 请假申请 | 病假/事假/年假/产假/陪产假等多类型、附件上传 |
| 请假审批 | 审批流程、审批意见 |
| 出差申请 | 国内/海外出差、自动计算天数 |
| 出差审批 | 审批流程、变更/取消 |

### 🚪 离职管理
| 功能页面 | 功能说明 |
|----------|----------|
| 离职申请 | 员工提交离职申请 |
| 离职进度 | 进度跟踪、状态显示 |
| 离职审批 | **双审批流程**（直属上级 + HR） |

### 💰 薪资与报销
| 功能页面 | 功能说明 |
|----------|----------|
| 薪资列表 | 全员薪资记录、发放状态 |
| 新建薪资 | 手动添加 + **Excel 批量导入** + 模板下载 |
| 我的工资条 | 员工个人薪资查看 |
| 差旅报销 | 交通费/住宿费/餐饮费、**发票上传** |
| 报销审批 | 审批 → 已报销状态流转 |

### 🏢 组织架构
| 功能页面 | 功能说明 |
|----------|----------|
| 部门管理 | **多级树形结构**、部门经理、部门主管 |
| 职位管理 | 薪资范围、任职要求、**默认角色关联** |

### 📊 数据报表（6 种图表）
| 图表类型 | 说明 |
|----------|------|
| 部门人员分布 | 饼图展示各部门占比 |
| 考勤结构 | 30天考勤类型分布 |
| 月度薪资趋势 | 12个月薪资支出折线图 |
| 请假类型分析 | 90天请假类型统计 |
| 职位分布 Top15 | 在职人数最多的职位 |
| 员工规模变化 | 12个月员工总数与在职人数 |

### 🔐 系统管理
| 功能页面 | 功能说明 |
|----------|----------|
| 系统维护 | **一键备份/恢复**、系统信息、运行状态监控 |
| 操作日志 | 用户操作记录、IP 地址、异常告警 |
| 公司文档 | 政策/流程/模板/公告/培训资料、版本管理 |
| RBAC 权限 | 角色管理、权限分配、用户角色关联 |
| 用户管理 | 账号列表、密码重置、状态管理 |

### 📱 移动端 H5
| 功能页面 | 功能说明 |
|----------|----------|
| 首页 | 今日考勤状态、快捷入口 |
| 签到打卡 | **GPS 定位** + **高德地图地址显示** |
| 考勤记录 | 历史打卡、补签标记显示 |
| 请假申请 | 移动端请假提交 |
| 个人中心 | 个人信息、退出登录 |

## 🛠 技术栈

### 后端技术
| 技术 | 版本 | 说明 |
|------|------|------|
| Python | 3.11 | 编程语言 |
| Django | 4.2.7 | Web 框架 |
| Django REST Framework | 3.14.0 | RESTful API |
| SimpleJWT | 5.3.1 | JWT 认证 |
| SQLite / PostgreSQL | - | 数据库 |
| Gunicorn | 21.2.0 | WSGI 服务器 |
| Pillow | 10.1.0 | 图片处理 |
| openpyxl | 3.1.2 | Excel 导入导出 |
| psutil | 5.9.8 | 系统监控 |

### Web 前端技术
| 技术 | 说明 |
|------|------|
| Vue 3 | 渐进式框架 (Composition API) |
| Vite | 构建工具 |
| Pinia | 状态管理 |
| Vue Router | 路由管理 |
| Axios | HTTP 客户端 |
| ECharts | 图表可视化 |

### 移动端 H5 技术
| 技术 | 说明 |
|------|------|
| Vue 3 | 渐进式框架 |
| Vant 4 | 移动端 UI 组件库 |
| 高德地图 API | 逆地理编码（坐标转地址） |

### 部署方案
| 方案 | 说明 |
|------|------|
| Docker + Docker Compose | 容器化部署 |
| Nginx | 反向代理 & 静态资源 |
| Let's Encrypt | SSL 证书（HTTPS）|

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
├── mobile/                    # 移动端 H5 项目
│   └── src/                   # 自助入职等功能
├── hr_management/             #  Django 核心应用
│   ├── api/                   # API 视图层
│   │   ├── views/             # 视图集
│   │   └── serializers/       # 序列化器
│   ├── models.py              # 数据模型
│   ├── permissions.py         # 权限类
│   ├── rbac.py                # RBAC 权限定义
│   ├── services.py            # 业务逻辑层
│   └── api_urls.py            # API 路由
├── hr_system/                 #  Django 项目配置
│   └── settings.py            # 项目设置
├── scripts/                   # 启动脚本
├── media/                     # 用户上传文件
│   ├── avatars/               # 员工头像
│   ├── documents/             # 公司文档
│   ├── invoices/              # 报销发票
│   └── backups/               # 数据备份
├── docker-compose.yml         # Docker 编排
├── Dockerfile                 # 后端镜像
├── requirements.txt           # Python 依赖
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
