# API 接口文档

## 📋 概述

本文档描述 Django HR 系统的 RESTful API 接口规范。所有 API 均以 `/api/` 为前缀。

**本地开发 Base URL**: `http://127.0.0.1:8000/api/`

**Docker / Nginx 访问入口**:
- Web: `http://localhost:3000`
- Mobile: `http://localhost:3001`
- API: `http://localhost:8000/api/`

**交互式接口文档**:
- Swagger UI: `/api/docs/`
- OpenAPI Schema: `/api/schema/`
- ReDoc: `/api/redoc/`

---

## 🔐 认证 (Authentication)

系统使用 **SimpleJWT + JWT (JSON Web Token)** 进行身份认证。

### 登录获取 Token

```http
POST /api/auth/token/
```

**请求体:**
```json
{
  "username": "admin",
  "password": "password123"
}
```

**响应 (200):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "admin",
    "is_staff": true,
    "employee": {
      "id": 1,
      "name": "管理员",
      "employee_id": "EMP001"
    }
  }
}
```

> 💡 支持用户名或手机号登录

> 💡 管理后台与接口文档默认都运行在同一个 Django 服务中，无需单独启动文档服务。

### 刷新 Token

```http
POST /api/auth/token/refresh/
```

**请求体:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**响应 (200):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### 登出

```http
POST /api/auth/logout/
Authorization: Bearer <access_token>
```

### 获取当前用户

```http
GET /api/auth/me/
Authorization: Bearer <access_token>
```

**响应:**
```json
{
  "id": 1,
  "username": "admin",
  "is_staff": true,
  "is_superuser": true,
  "employee": { ... },
  "permissions": ["employee.view", "employee.create", ...],
  "roles": [{"code": "admin", "name": "系统管理员"}]
}
```

### 修改密码

```http
POST /api/auth/change_password/
Authorization: Bearer <access_token>
```

**请求体:**
```json
{
  "old_password": "oldpass123",
  "new_password": "newpass456"
}
```

### 找回密码 (验证码)

```http
# 1. 发送验证码
POST /api/auth/send_code/
{
  "phone": "13800138000"
}

# 2. 验证并重置密码
POST /api/auth/reset_password/
{
  "phone": "13800138000",
  "code": "123456",
  "new_password": "newpass123"
}
```

---

## 👥 员工管理 (Employees)

### 获取员工列表

```http
GET /api/employees/
Authorization: Bearer <access_token>
```

**查询参数:**
| 参数 | 类型 | 说明 |
|------|------|------|
| `page` | int | 页码 |
| `page_size` | int | 每页条数 (默认 20) |
| `search` | string | 搜索 (姓名/工号/手机) |
| `department` | int | 部门 ID |
| `position` | int | 职位 ID |
| `status` | string | 状态: `pending`/`onboarded`/`resigned` |

**响应:**
```json
{
  "count": 100,
  "next": "http://localhost:8000/api/employees/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "employee_id": "EMP001",
      "name": "张三",
      "gender": "M",
      "phone": "13800138000",
      "email": "zhangsan@example.com",
      "department": { "id": 1, "name": "技术部" },
      "position": { "id": 1, "name": "高级工程师" },
      "hire_date": "2023-01-15",
      "onboard_status": "onboarded"
    }
  ]
}
```

### 获取员工详情

```http
GET /api/employees/{id}/
```

### 创建员工

```http
POST /api/employees/
Authorization: Bearer <access_token>
```

**请求体:**
```json
{
  "employee_id": "EMP002",
  "name": "李四",
  "gender": "M",
  "phone": "13900139000",
  "email": "lisi@example.com",
  "department": 1,
  "position": 1,
  "hire_date": "2024-01-01",
  "basic_salary": 10000
}
```

### 更新员工

```http
PUT /api/employees/{id}/
PATCH /api/employees/{id}/
```

### 删除员工

```http
DELETE /api/employees/{id}/
```

### 获取当前员工

```http
GET /api/employees/me/
```

---

## 🏛️ 部门管理 (Departments)

### 获取部门列表

```http
GET /api/departments/
```

**响应:**
```json
{
  "results": [
    {
      "id": 1,
      "name": "技术部",
      "description": "负责技术研发",
      "parent": null,
      "children": [
        { "id": 2, "name": "前端组" },
        { "id": 3, "name": "后端组" }
      ],
      "manager": { "id": 1, "name": "张三" },
      "supervisors": [],
      "employee_count": 15
    }
  ]
}
```

### 创建部门

```http
POST /api/departments/
```

**请求体:**
```json
{
  "name": "新部门",
  "description": "部门描述",
  "parent": 1,
  "manager": 1
}
```

### 更新/删除部门

```http
PUT /api/departments/{id}/
DELETE /api/departments/{id}/
```

---

## 🏢 职位管理 (Positions)

```http
GET    /api/positions/           # 列表
POST   /api/positions/           # 创建
GET    /api/positions/{id}/      # 详情
PUT    /api/positions/{id}/      # 更新
DELETE /api/positions/{id}/      # 删除
```

**创建/更新请求体:**
```json
{
  "name": "高级工程师",
  "department": 1,
  "description": "负责核心业务开发",
  "salary_range_min": 15000,
  "salary_range_max": 30000,
  "requirements": "5年以上工作经验"
}
```

---

## ⏰ 考勤管理 (Attendance)

### 获取考勤记录

```http
GET /api/attendance/
```

**查询参数:**
| 参数 | 类型 | 说明 |
|------|------|------|
| `employee` | int | 员工 ID |
| `date` | date | 日期 (YYYY-MM-DD) |
| `date_from` | date | 开始日期 |
| `date_to` | date | 结束日期 |

### 签到/签退

```http
POST /api/attendance/check/
```

**请求体:**
```json
{
  "type": "check_in",
  "latitude": 39.9042,
  "longitude": 116.4074
}
```

> `type`: `check_in` (签到) 或 `check_out` (签退)

### 获取今日考勤

```http
GET /api/attendance/today/
```

### 获取我的考勤

```http
GET /api/attendance/my/
```

### 补签申请

```http
# 申请补签
POST /api/attendance/supplement/
{
  "date": "2024-01-15",
  "check_in_time": "09:00:00",
  "check_out_time": "18:00:00",
  "reason": "忘记打卡"
}

# 待审批列表
GET /api/attendance/supplement/pending/

# 审批
POST /api/attendance/supplement/{id}/approve/
{
  "status": "approved",  // approved / rejected
  "comment": "同意"
}
```

### 签到地点管理

```http
GET    /api/checkin-locations/           # 列表
POST   /api/checkin-locations/           # 创建
PUT    /api/checkin-locations/{id}/      # 更新
DELETE /api/checkin-locations/{id}/      # 删除
GET    /api/checkin-locations/active/    # 获取启用的地点
```

---

## 📝 请假管理 (Leaves)

### 获取请假列表

```http
GET /api/leaves/
```

**查询参数:**
| 参数 | 类型 | 说明 |
|------|------|------|
| `employee` | int | 员工 ID |
| `status` | string | 状态: `pending`/`approved`/`rejected`/`cancelled` |
| `leave_type` | string | 类型: `annual`/`sick`/`personal`/`marriage`/`maternity`/`bereavement` |

### 提交请假申请

```http
POST /api/leaves/
```

**请求体:**
```json
{
  "leave_type": "annual",
  "start_date": "2024-02-01",
  "end_date": "2024-02-03",
  "reason": "家庭事务"
}
```

### 审批请假

```http
POST /api/leaves/{id}/approve/
```

**请求体:**
```json
{
  "status": "approved",
  "comment": "同意"
}
```

### 取消请假

```http
POST /api/leaves/{id}/cancel/
```

---

## ✈️ 出差管理 (Business Trips)

```http
GET    /api/business-trips/              # 列表
POST   /api/business-trips/              # 创建
GET    /api/business-trips/{id}/         # 详情
POST   /api/business-trips/{id}/approve/ # 审批
POST   /api/business-trips/{id}/cancel/  # 取消
```

**创建请求体:**
```json
{
  "destination": "上海",
  "start_date": "2024-02-15",
  "end_date": "2024-02-18",
  "purpose": "客户拜访",
  "estimated_cost": 5000.00
}
```

---

## 💳 差旅报销 (Travel Expenses)

```http
GET    /api/travel-expenses/              # 列表
POST   /api/travel-expenses/              # 创建
GET    /api/travel-expenses/{id}/         # 详情
POST   /api/travel-expenses/{id}/approve/ # 审批
POST   /api/travel-expenses/{id}/pay/     # 支付
```

**创建请求体:**
```json
{
  "business_trip": 1,
  "total_amount": 3500.00,
  "items": [
    { "type": "transport", "amount": 1500, "description": "机票" },
    { "type": "hotel", "amount": 1500, "description": "酒店3晚" },
    { "type": "meal", "amount": 500, "description": "餐费" }
  ]
}
```

---

## 💰 薪资管理 (Salaries)

### 获取薪资记录

```http
GET /api/salaries/
```

**查询参数:**
| 参数 | 类型 | 说明 |
|------|------|------|
| `employee` | int | 员工 ID |
| `year` | int | 年份 |
| `month` | int | 月份 |
| `paid` | bool | 是否已发放 |

### 创建薪资记录

```http
POST /api/salaries/
```

**请求体:**
```json
{
  "employee": 1,
  "year": 2024,
  "month": 1,
  "basic_salary": 10000,
  "bonus": 2000,
  "allowance": 500,
  "deductions": 0
}
```

### 更新薪资

```http
PATCH /api/salaries/{id}/
```

### 发放薪资

```http
# 批量发放
POST /api/salaries/disburse/
{
  "ids": [1, 2, 3]
}
```

---

## 📊 数据报表 (Reports)

```http
GET /api/reports/overview/                # 报表概览
GET /api/reports/department_distribution/ # 部门分布
GET /api/reports/monthly_salary/          # 月度薪资
GET /api/reports/attendance_rate/         # 考勤率
GET /api/reports/leave_analysis/          # 请假分析
GET /api/reports/employee_growth/         # 员工增长
GET /api/reports/position_distribution/   # 职位分布
```

---

## 📥 数据导入 (Import)

### 导入员工

```http
POST /api/import/employees/
Content-Type: multipart/form-data
```

**请求体:**
- `file`: Excel 文件 (.xlsx)

**响应:**
```json
{
  "success": true,
  "data": {
    "success": 10,
    "failed": 2,
    "errors": [
      "第3行: 部门不存在",
      "第5行: 工号重复"
    ]
  }
}
```

### 导入考勤/薪资

```http
POST /api/import/attendance/
POST /api/import/salaries/
```

### 下载导入模板

```http
GET /api/import/template/{type}/
```

> `type`: `employee` / `attendance` / `salary`

---

## 📤 数据导出 (Export)

```http
GET /api/export/employees/     # 导出员工
GET /api/export/salaries/      # 导出薪资
GET /api/export/attendance/    # 导出考勤
GET /api/export/leaves/        # 导出请假
GET /api/export/salary-slip/   # 导出个人工资条
```

**查询参数支持筛选:**
```http
GET /api/export/salaries/?year=2024&month=1&paid=true
```

---

## 🔐 权限管理 (RBAC)

### 角色

```http
GET    /api/roles/                # 角色列表 (只读)
GET    /api/roles/manage/         # 角色管理列表
POST   /api/roles/manage/         # 创建角色
PUT    /api/roles/manage/{id}/    # 更新角色
DELETE /api/roles/manage/{id}/    # 删除角色
```

### 权限

```http
GET /api/permissions/             # 权限列表
GET /api/permissions/groups/      # 按分组获取权限
```

### 用户管理

```http
GET    /api/users/                # 用户列表 (只读)
GET    /api/users/manage/         # 用户管理列表
POST   /api/users/manage/         # 创建用户
PUT    /api/users/manage/{id}/    # 更新用户
DELETE /api/users/manage/{id}/    # 删除用户
```

---

## ⚙️ 系统管理 (System)

### 系统日志

```http
GET  /api/logs/                   # 日志列表
POST /api/logs/clear/             # 清空日志
```

### 数据备份

```http
GET  /api/backups/                # 备份列表
POST /api/backups/create/         # 创建备份
POST /api/backups/restore/        # 恢复备份
POST /api/backups/clean/          # 清理旧备份
```

### 系统监控

```http
GET /api/system/health/           # 健康检查
GET /api/system/health/report/    # 健康报告
GET /api/system/metrics/          # 系统指标
```

### 公司文档

```http
GET    /api/documents/            # 文档列表
POST   /api/documents/            # 上传文档
GET    /api/documents/{id}/       # 文档详情
DELETE /api/documents/{id}/       # 删除文档
```

---

## 🔔 通知 (Notifications)

```http
GET  /api/notifications/                    # 通知列表
GET  /api/notifications/unread-count/       # 未读数量
POST /api/notifications/{id}/read/          # 标记已读
POST /api/notifications/read-all/           # 全部已读
POST /api/notifications/clear/              # 清空通知
```

---

## 📱 自助入职 (Onboarding)

```http
# 发送注册验证码
POST /api/onboarding/send-code/
{ "phone": "13800138000" }

# 自助注册
POST /api/onboarding/register/
{
  "phone": "13800138000",
  "code": "123456",
  "name": "张三",
  "id_card": "110101199001011234"
}

# 更新入职资料
PUT /api/onboarding/profile/

# 查看入职状态
GET /api/onboarding/status/

# HR 审核列表
GET /api/onboarding/pending/

# HR 审核
POST /api/onboarding/{id}/approve/
{ "status": "approved" }
```

---

## 📌 通用说明

### 请求头

所有需要认证的接口需携带:

```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

### 分页响应格式

```json
{
  "count": 100,
  "next": "http://localhost:8000/api/xxx/?page=2",
  "previous": null,
  "results": [...]
}
```

### 错误响应

**400 Bad Request:**
```json
{
  "field_name": ["错误信息1", "错误信息2"]
}
```

**401 Unauthorized:**
```json
{
  "detail": "认证凭据无效"
}
```

**403 Forbidden:**
```json
{
  "detail": "您没有执行此操作的权限"
}
```

**404 Not Found:**
```json
{
  "detail": "未找到"
}
```

### HTTP 状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 204 | 删除成功 |
| 400 | 请求参数错误 |
| 401 | 未认证 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 500 | 服务器错误 |
}
```
