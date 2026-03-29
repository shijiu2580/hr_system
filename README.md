<div align="center">

# 🚀 HR 人力资源管理系统

### 企业级全栈解决方案 | Production-Ready HR Management System

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.2-092E20?style=for-the-badge&logo=django&logoColor=white)](https://djangoproject.com)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.x-4FC08D?style=for-the-badge&logo=vue.js&logoColor=white)](https://vuejs.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

**🎯 一套代码，三端覆盖 | Web + Mobile H5 + RESTful API**

[功能特性](#-功能亮点) • [快速开始](#-快速开始) • [技术架构](#-技术架构) • [API文档](docs/API.md) • [部署指南](#-生产部署)

</div>

---

## 💡 为什么选择这个项目？

> 🔥 **不是玩具项目**，而是经过生产环境验证的完整解决方案

| 特性 | 说明 |
|------|------|
| 🏗️ **企业级架构** | 前后端完全分离，RESTful API 设计，支持水平扩展 |
| 🔐 **完整权限系统** | 自研 RBAC 权限模型，细粒度控制到按钮级别 |
| 📱 **三端统一** | 一套后端 API，同时支持 Web、移动端 H5、小程序 |
| 🐳 **一键部署** | Docker Compose 编排，5分钟完成生产环境部署 |
| 🗺️ **GPS 定位打卡** | 集成高德地图，支持地理围栏、逆地理编码 |
| 📊 **数据可视化** | ECharts 图表，考勤/薪资/绩效多维度分析 |

---

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

### 📊 数据报表
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

---

## 🛠 技术架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        Nginx 反向代理                            │
│                    (SSL/负载均衡/静态资源)                        │
└──────────────┬──────────────────┬──────────────────┬────────────┘
               │                  │                  │
               ▼                  ▼                  ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│   Web Frontend   │  │  Mobile H5       │  │   API Server     │
│   Vue 3 + Vite   │  │  Vue 3 + Vant    │  │   Django REST    │
│   Element Plus   │  │  高德地图 API     │  │   Framework      │
│   ECharts        │  │                  │  │                  │
│   :3000          │  │  :3001           │  │  :8000           │
└──────────────────┘  └──────────────────┘  └────────┬─────────┘
                                                      │
                                           ┌──────────▼─────────┐
                                           │    Data Layer      │
                                           │  ┌──────────────┐  │
                                           │  │   SQLite /   │  │
                                           │  │  PostgreSQL  │  │
                                           │  └──────────────┘  │
                                           └────────────────────┘
```

### 核心技术栈

| 层级 | 技术选型 | 说明 |
|------|----------|------|
| **后端** | Python 3.11 + Django 4.2 | 成熟稳定的 Web 框架 |
| **API** | Django REST Framework | RESTful API 最佳实践 |
| **认证** | SimpleJWT | 无状态 Token 认证 |
| **Web前端** | Vue 3 + Vite + Element Plus | 现代化 SPA 架构 |
| **移动端** | Vue 3 + Vant 4 | 移动端 H5 最佳体验 |
| **地图** | 高德地图 Web API | GPS 定位 + 逆地理编码 |
| **图表** | ECharts 5 | 企业级数据可视化 |
| **部署** | Docker + Nginx | 容器化一键部署 |

---

## 📁 项目结构

```
django_hr_system/
├── 📂 hr_management/        # 🎯 Django 核心应用
│   ├── api/                 #    API 视图层
│   ├── models.py            #    数据模型
│   ├── permissions.py       #    权限控制
│   ├── rbac.py              #    RBAC 权限引擎
│   └── services.py          #    业务逻辑层
├── 📂 hr_system/            # ⚙️ Django 项目配置
├── 📂 frontend/             # 🖥️ Vue3 Web 前端
│   └── src/
│       ├── components/      #    可复用组件
│       ├── pages/           #    页面组件
│       ├── stores/          #    Pinia 状态管理
│       └── utils/           #    工具函数
├── 📂 mobile/               # 📱 Vue3 移动端 H5
│   └── src/
│       ├── views/           #    页面视图
│       └── stores/          #    状态管理
├── 📂 nginx/                # 🌐 Nginx 配置
├── 📂 docs/                 # 📚 项目文档
│   ├── API.md               #    接口文档
│   └── RBAC.md              #    权限系统文档
├── 📂 scripts/              # 🔧 脚本工具
├── 🐳 docker-compose.yml    # Docker 编排
├── 🐳 Dockerfile            # 后端镜像
└── 📋 requirements.txt      # Python 依赖
```

---

## 🚀 快速开始

### ⚡ 方式一：Docker 一键部署（推荐）

> 💡 5 分钟启动完整系统，无需配置环境

```bash
# 1. 克隆项目
git clone https://github.com/shijiu2580/hr_system.git
cd hr_system

# 2. 复制并编辑生产环境变量
cp .env.example .env
# 修改 DATABASE_URL / REDIS_URL / SECRET_KEY / 邮件账号等配置

# 3. 一键启动所有服务（Nginx + Web + Mobile + API + PostgreSQL + Redis）
docker compose up -d --build

# 4. 创建超级管理员
docker exec -it hr-backend python manage.py createsuperuser

# 5. 🎉 访问系统
# 📍 Web 管理端:  http://localhost
# 📍 移动端 H5:   http://m.canway.site (配置 DNS 后)
# 📍 API 接口:    http://localhost/api/
```

> 说明：当前 Docker 编排默认通过网关 Nginx 统一入口，不再直接暴露 backend/frontend/mobile 的容器端口。

### 🛠️ 方式二：本地开发环境

> 💡 当前仓库已经切到项目内虚拟环境开发流程：推荐直接使用 `uv` 或一键脚本；本地开发端口为 Web `5173`、Mobile `5174`、API `8000`。

<details>
<summary><b>📦 后端启动</b></summary>

```powershell
# 创建项目虚拟环境（推荐）
uv venv venv --python 3.11

# 安装依赖
uv pip install --python .\venv\Scripts\python.exe -r requirements.txt

# 数据库迁移
.\venv\Scripts\python.exe manage.py migrate

# 初始化 RBAC 示例权限/角色
.\venv\Scripts\python.exe manage.py init_rbac_permissions --with-roles

# 创建管理员
.\venv\Scripts\python.exe manage.py createsuperuser

# 启动服务 → http://127.0.0.1:8000
.\venv\Scripts\python.exe manage.py runserver
```
</details>

<details>
<summary><b>🖥️ Web 前端启动</b></summary>

```powershell
cd frontend
npm install
npm run dev
# → http://127.0.0.1:5173
```
</details>

<details>
<summary><b>📱 移动端启动</b></summary>

```powershell
cd mobile
npm install
npm run dev
# → http://127.0.0.1:5174
```
</details>

### 🎯 方式三：一键启动脚本

```powershell
# Windows 一键启动
.\scripts\start_dev.ps1

# 首次运行（自动安装 Python/前端依赖、迁移数据库、初始化 RBAC 示例角色）
.\scripts\start_dev.ps1 -Install
```

脚本当前行为：
- 优先使用项目内 [django_hr_system/venv/Scripts/python.exe](django_hr_system/venv/Scripts/python.exe)
- 优先使用 D 盘的 npm 环境
- `-Install` 时优先使用 `uv` 安装 Python 依赖，避免 Windows 编码导致的 `pip` 读取失败

---

## 📚 完整文档

| 文档 | 说明 |
|------|------|
| 📖 [详细文档](docs/README.md) | 完整项目文档、配置说明 |
| 🔌 [API 文档](docs/API.md) | RESTful API 接口规范 |
| 🔐 [RBAC 文档](docs/RBAC.md) | 权限系统设计与使用 |

---

## ⚙️ 环境配置

<details>
<summary><b>🔧 后端配置 (.env)</b></summary>

```env
SECRET_KEY=your-super-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com
DATABASE_URL=postgresql://hr_user:change_me@postgres:5432/hr_system
REDIS_URL=redis://redis:6379/1

# 邮件服务（密码重置）
EMAIL_HOST=smtp.qq.com
EMAIL_PORT=465
EMAIL_USE_SSL=True
EMAIL_HOST_USER=your-email@qq.com
EMAIL_HOST_PASSWORD=your-auth-code
```
</details>

<details>
<summary><b>🎨 前端配置 (.env)</b></summary>

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api
```
</details>

---

## 🔒 生产部署

### 当前推荐架构（双机）

| 服务器 | 角色 | 承载服务 | 对外职责 |
|------|------|----------|----------|
| 腾讯云 | 入口层 | Nginx + HTTPS + frontend + mobile | `canway.site` / `m.canway.site` / `api.canway.site` |
| 阿里云 | 核心层 | gateway + backend + PostgreSQL + Redis | API、管理后台、数据库、缓存、媒体文件 |

> 说明：当前项目不建议做双后端双活。原因是 Django 应用启动时会自动拉起简易 scheduler，且媒体文件默认写本地磁盘。更稳的方案是“腾讯云入口层 + 阿里云核心业务层”。

<details>
<summary><b>🏗️ 双机部署文件说明</b></summary>

```text
docker-compose.tencent.yml    # 腾讯云入口层，只启动 Web/Mobile 容器
docker-compose.aliyun.yml     # 阿里云核心层，只启动 gateway/backend/postgres/redis
nginx/canway.site.conf        # 腾讯云 HTTPS 正式入口配置
nginx/canway.site.http.conf   # 腾讯云 HTTP 调试/应急入口配置
nginx/docker.core.conf        # 阿里云核心层网关配置
scripts/reset_postgres_sequences.py  # SQLite -> PostgreSQL 导入后重置序列
```
</details>

<details>
<summary><b>🚀 双机部署步骤（腾讯云入口层 + 阿里云核心层）</b></summary>

```bash
# 1. 腾讯云：拉代码并启动入口层容器
git clone https://github.com/shijiu2580/hr_system.git
cd hr_system
docker compose -f docker-compose.tencent.yml up -d --build

# 2. 腾讯云：安装并启用 Nginx / HTTPS
apt install -y nginx certbot python3-certbot-nginx
cp nginx/canway.site.conf /etc/nginx/sites-available/canway.site
ln -sf /etc/nginx/sites-available/canway.site /etc/nginx/sites-enabled/canway.site
nginx -t && systemctl reload nginx
certbot certonly --nginx \
    -d canway.site -d www.canway.site -d m.canway.site -d api.canway.site

# 3. 阿里云：拉代码并启动核心层容器
git clone https://github.com/shijiu2580/hr_system.git
cd hr_system
docker-compose -f docker-compose.aliyun.yml up -d --build
```

上线验证：

```bash
curl -I https://canway.site/
curl -I https://m.canway.site/
curl -I https://api.canway.site/api/health/
```
</details>

<details>
<summary><b>🗃️ SQLite 迁移到 PostgreSQL（已验证）</b></summary>

```bash
# 1. 本地导出 SQLite 数据
python manage.py dumpdata \
    --natural-foreign \
    --natural-primary \
    --exclude contenttypes \
    --exclude auth.permission \
    --exclude sessions \
    --indent 2 > sqlite_to_pg_export.json

# 2. 备份阿里云 PostgreSQL
docker exec hr-postgres pg_dump -U hr_user -d hr_system > backups/hr_system_before_import.sql

# 3. 上传导出文件到阿里云
scp sqlite_to_pg_export.json aliyun-hr:/opt/hr_system/sqlite_to_pg_export.json

# 4. 停止核心入口与后端，避免导入期间产生并发写入
docker stop hr-gateway hr-backend

# 5. 清空阿里云 PG 现有业务数据
docker run --rm --network hr_system_hr_core_network \
    --env-file /opt/hr_system/.env \
    -e DISABLE_SCHEDULER=true \
    hr_system_backend:latest \
    python manage.py flush --no-input

# 6. 导入 JSON 数据
docker run --rm --network hr_system_hr_core_network \
    --env-file /opt/hr_system/.env \
    -e DISABLE_SCHEDULER=true \
    -v /opt/hr_system:/import \
    hr_system_backend:latest \
    python manage.py loaddata /import/sqlite_to_pg_export.json

# 7. 重置 PostgreSQL 自增序列
docker run --rm -w /app --network hr_system_hr_core_network \
    --env-file /opt/hr_system/.env \
    -e DISABLE_SCHEDULER=true \
    -e PYTHONPATH=/app \
    -v /opt/hr_system:/import \
    hr_system_backend:latest \
    python /import/scripts/reset_postgres_sequences.py

# 8. 启动核心层服务
docker-compose -f docker-compose.aliyun.yml up -d
```

本项目实测迁移过程中，额外处理了两类历史脏数据：

- `Employee.gender` 的旧值 `male/female` 需要标准化为 `M/F`
- 6 条 `VerificationCode.phone` 被错误写成邮箱地址，导入前应剔除
</details>

<details>
<summary><b>🖼️ media 文件同步到阿里云</b></summary>

```bash
# 1. 上传本地 media 到阿里云临时目录
scp -r media/* aliyun-hr:/opt/hr_system/media_sync_local/

# 2. 写入后端容器挂载卷
docker cp /opt/hr_system/media_sync_local/. hr-backend:/app/media/

# 3. 校验文件数量
docker exec hr-backend sh -c 'find /app/media -type f | wc -l'
```

说明：数据库迁移只迁表数据，不迁上传文件；头像、部门图标、公司文档等静态上传资源需要单独同步。
</details>

<details>
<summary><b>🔐 SSL 证书配置</b></summary>

```bash
# 安装 Certbot
apt install certbot python3-certbot-nginx

# 自动获取 Let's Encrypt 证书
certbot --nginx -d your-domain.com -d m.your-domain.com -d api.your-domain.com
```
</details>

<details>
<summary><b>🌐 Nginx 配置</b></summary>

参考 `nginx/` 目录下的配置文件，支持：
- HTTPS 强制跳转
- WebSocket 代理
- 静态资源缓存
- Gzip 压缩
</details>

<details>
<summary><b>💾 数据库备份</b></summary>

系统内置自动备份功能：
- 备份文件位置：`media/backups/`
- 支持一键恢复
- 管理后台可视化操作
</details>

---

## 🖼️ 系统截图

<table>
<tr>
<td width="50%">

**🖥️ Web 管理端**
- 登录认证页面
- 员工信息管理
- 考勤数据分析
- 部门组织架构
- 权限角色配置

</td>
<td width="50%">

**📱 移动端 H5**
- 快速登录
- 首页考勤状态
- GPS 定位打卡
- 考勤历史记录
- 个人信息中心

</td>
</tr>
</table>

---

## 🗺️ 开发路线图

- [x] 🎯 核心人事管理模块
- [x] ⏰ GPS 定位考勤系统
- [x] 📝 请假审批流程
- [x] 💰 薪资管理模块
- [x] 🔐 RBAC 权限系统
- [x] 📱 移动端 H5 应用
- [x] 🐳 Docker 容器化部署
- [ ] 📊 绩效考核模块
- [ ] 🤖 智能排班系统
- [ ] 📈 BI 数据看板
- [ ] 🔔 消息推送中心

---

## 🤝 参与贡献

欢迎参与项目贡献！请查看 [贡献指南](CONTRIBUTING.md)

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

---

## 📄 开源许可

本项目基于 [MIT License](LICENSE) 开源协议

---

<div align="center">

**如果这个项目对你有帮助，请给个 ⭐ Star 支持一下！**

Made with ❤️ by [Your Name]

</div>
