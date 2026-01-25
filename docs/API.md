# API 文档

## 认证端点

### POST /api/auth/login/
登录获取 JWT Token

**请求体:**
```json
{
  "username": "string",
  "password": "string"
}
```

**响应:**
```json
{
  "access": "string",
  "refresh": "string",
  "user": {
    "id": "number",
    "username": "string",
    "employee": {...}
  }
}
```

### POST /api/auth/token/refresh/
刷新 Access Token

**请求体:**
```json
{
  "refresh": "string"
}
```

### POST /api/auth/logout/
登出（需要认证）

### POST /api/auth/change-password/
修改密码（需要认证）

**请求体:**
```json
{
  "old_password": "string",
  "new_password": "string"
}
```

## 员工管理

### GET /api/employees/
获取员工列表（支持分页、搜索、筛选）

**查询参数:**
- `page`: 页码
- `search`: 搜索关键字
- `department`: 部门ID
- `position`: 职位ID

### GET /api/employees/{id}/
获取员工详情

### POST /api/employees/
创建员工（需要管理员权限）

### PUT/PATCH /api/employees/{id}/
更新员工信息（需要管理员权限）

### DELETE /api/employees/{id}/
删除员工（需要管理员权限）

## 部门管理

### GET /api/departments/
获取部门列表

### POST /api/departments/
创建部门（需要管理员权限）

## 考勤管理

### GET /api/attendances/
获取考勤记录列表

### POST /api/attendances/
创建考勤记录

### GET /api/attendances/my-records/
获取我的考勤记录

## 请假管理

### GET /api/leaves/
获取请假申请列表

### POST /api/leaves/
提交请假申请

### PATCH /api/leaves/{id}/approve/
审批请假（需要管理员权限）

## 薪资管理

### GET /api/salaries/
获取薪资记录列表

### POST /api/salaries/
创建薪资记录（需要管理员权限）

### GET /api/salaries/my-salary/
获取我的薪资记录

## 批量导入

### POST /api/import/employees/
批量导入员工（需要管理员权限）

**请求类型:** `multipart/form-data`

**请求体:**
- `file`: Excel 文件 (.xlsx, .xls)

**响应:**
```json
{
  "success": true,
  "data": {
    "success": 10,
    "failed": 2,
    "errors": ["第3行: 部门不存在", "第5行: 工号重复"]
  }
}
```

### POST /api/import/attendance/
批量导入考勤（需要管理员权限）

**请求类型:** `multipart/form-data`

### POST /api/import/salaries/
批量导入薪资（需要管理员权限）

**请求类型:** `multipart/form-data`

### GET /api/import/template/{type}/
下载导入模板

**路径参数:**
- `type`: 模板类型，可选值: `employee`, `attendance`, `salary`

## 权限管理

### GET /api/roles/
获取角色列表

### GET /api/permissions/
获取权限列表

### GET /api/user-permissions/
获取当前用户的权限列表

## 系统管理

### GET /api/system/logs/
获取系统日志列表

### POST /api/system/backup/
创建数据库备份

### POST /api/system/restore/
恢复数据库备份

## 通用响应格式

### 成功响应
```json
{
  "count": 100,
  "next": "url",
  "previous": "url",
  "results": [...]
}
```

### 错误响应
```json
{
  "detail": "错误信息"
}
```

或

```json
{
  "field_name": ["错误信息1", "错误信息2"]
}
```
