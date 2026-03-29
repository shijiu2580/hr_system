# RBAC 权限系统设计文档

## 📋 概述

本系统采用 **基于角色的访问控制（Role-Based Access Control, RBAC）** 模型，实现灵活、可扩展的权限管理。通过角色作为用户与权限之间的桥梁，简化权限分配，支持细粒度的功能访问控制。

当前仓库中有两套初始化命令：
- `init_rbac`：基于 [django_hr_system/hr_management/rbac.py](django_hr_system/hr_management/rbac.py) 的点号风格权限键，例如 `employee.view`
- `init_rbac_permissions`：用于快速生成示例权限与角色，默认以后台管理/初始化脚本为主

前端路由守卫、权限指令和大部分界面展示目前仍以 `employee.view` 这一类点号风格 key 为准。

## 🏗️ 系统架构

### 核心概念

```
┌──────────┐      ┌──────────┐      ┌──────────────────┐
│   用户   │ ──── │   角色   │ ──── │      权限        │
│  (User)  │  M:N │  (Role)  │  M:N │ (RBACPermission) │
└──────────┘      └──────────┘      └──────────────────┘
```

| 概念 | 说明 |
|------|------|
| **用户 (User)** | 系统登录账户，可分配多个角色 |
| **角色 (Role)** | 权限集合，如"人事经理"、"普通员工" |
| **权限 (Permission)** | 最小操作单元，如 `employee.create` |

### 数据模型

```python
class Role(models.Model):
    code = models.CharField(max_length=50, unique=True)    # 角色代码
    name = models.CharField(max_length=100)                 # 角色名称
    description = models.TextField(blank=True)              # 描述
    permissions = models.ManyToManyField('RBACPermission')  # 关联权限
    users = models.ManyToManyField(User, related_name='rbac_roles')

class RBACPermission(models.Model):
    code = models.CharField(max_length=100, unique=True)   # 权限代码
    name = models.CharField(max_length=100)                 # 权限名称
    group = models.CharField(max_length=50)                 # 所属分组
```

---

## 🔐 权限清单

### 👥 员工模块 (employee)

| 权限代码 | 权限名称 | 说明 |
|----------|----------|------|
| `employee.view` | 查看员工 | 查看员工列表和详情 |
| `employee.create` | 创建员工 | 新建员工档案 |
| `employee.edit` | 编辑员工 | 修改员工信息 |
| `employee.delete` | 删除员工 | 删除员工档案 |
| `employee.import` | 导入员工 | Excel 批量导入 |
| `employee.export` | 导出员工 | 导出员工数据 |

### ⏰ 考勤模块 (attendance)

| 权限代码 | 权限名称 | 说明 |
|----------|----------|------|
| `attendance.view` | 查看考勤 | 查看个人考勤记录 |
| `attendance.view_all` | 查看所有考勤 | 查看全部员工考勤 |
| `attendance.create` | 签到签退 | 日常打卡操作 |
| `attendance.edit` | 编辑考勤 | 修改考勤记录 |
| `attendance.approve` | 审批补签 | 审批员工补签申请 |
| `attendance.location` | 管理地点 | 设置打卡地点范围 |

### 📝 请假模块 (leave)

| 权限代码 | 权限名称 | 说明 |
|----------|----------|------|
| `leave.view` | 查看请假 | 查看个人请假记录 |
| `leave.view_all` | 查看所有请假 | 查看全部请假记录 |
| `leave.create` | 申请请假 | 提交请假申请 |
| `leave.approve` | 审批请假 | 审批员工请假 |

### ✈️ 出差模块 (trip)

| 权限代码 | 权限名称 | 说明 |
|----------|----------|------|
| `trip.view` | 查看出差 | 查看个人出差记录 |
| `trip.view_all` | 查看所有出差 | 查看全部出差记录 |
| `trip.create` | 申请出差 | 提交出差申请 |
| `trip.approve` | 审批出差 | 审批员工出差 |

### 💰 薪资模块 (salary)

| 权限代码 | 权限名称 | 说明 |
|----------|----------|------|
| `salary.view` | 查看薪资 | 查看个人薪资记录 |
| `salary.view_all` | 查看所有薪资 | 查看全部薪资数据 |
| `salary.create` | 创建薪资 | 生成薪资记录 |
| `salary.edit` | 编辑薪资 | 修改薪资记录 |
| `salary.delete` | 删除薪资 | 删除薪资记录 |
| `salary.disburse` | 发放薪资 | 批量发放薪资 |

### 💳 报销模块 (expense)

| 权限代码 | 权限名称 | 说明 |
|----------|----------|------|
| `expense.view` | 查看报销 | 查看个人报销记录 |
| `expense.view_all` | 查看所有报销 | 查看全部报销记录 |
| `expense.create` | 申请报销 | 提交报销申请 |
| `expense.approve` | 审批报销 | 审批报销申请 |

### 🏛️ 部门模块 (department)

| 权限代码 | 权限名称 | 说明 |
|----------|----------|------|
| `department.view` | 查看部门 | 查看部门列表 |
| `department.create` | 创建部门 | 新建部门 |
| `department.edit` | 编辑部门 | 修改部门信息 |
| `department.delete` | 删除部门 | 删除部门 |

### 🏢 职位模块 (position)

| 权限代码 | 权限名称 | 说明 |
|----------|----------|------|
| `position.view` | 查看职位 | 查看职位列表 |
| `position.create` | 创建职位 | 新建职位 |
| `position.edit` | 编辑职位 | 修改职位信息 |
| `position.delete` | 删除职位 | 删除职位 |

### 🚪 离职模块 (resignation)

| 权限代码 | 权限名称 | 说明 |
|----------|----------|------|
| `resignation.view` | 查看离职 | 查看个人离职申请 |
| `resignation.view_all` | 查看所有离职 | 查看全部离职记录 |
| `resignation.create` | 发起离职 | 提交离职申请 |
| `resignation.approve` | 审批离职 | 审批离职申请 |

### 📄 文档模块 (document)

| 权限代码 | 权限名称 | 说明 |
|----------|----------|------|
| `document.view` | 查看文档 | 查看公司文档 |
| `document.upload` | 上传文档 | 上传新文档 |
| `document.create` | 创建文档 | 创建文档记录 |
| `document.edit` | 编辑文档 | 编辑文档信息 |
| `document.delete` | 删除文档 | 删除文档 |
| `document.manage` | 管理文档 | 管理公开文档 |

### 📊 报表模块 (report)

| 权限代码 | 权限名称 | 说明 |
|----------|----------|------|
| `report.view` | 访问报表 | 进入报表页面 |
| `report.employee` | 员工报表 | 查看员工统计 |
| `report.attendance` | 考勤报表 | 查看考勤统计 |
| `report.salary` | 薪资报表 | 查看薪资统计 |
| `report.leave` | 请假报表 | 查看请假统计 |
| `report.export` | 导出报表 | 导出报表数据 |

### ⚙️ 系统模块 (system)

| 权限代码 | 权限名称 | 说明 |
|----------|----------|------|
| `system.view` | 访问系统 | 进入系统管理 |
| `system.log_view` | 查看日志 | 查看系统日志 |
| `system.log_clear` | 清除日志 | 清空系统日志 |
| `system.backup_view` | 查看备份 | 查看备份列表 |
| `system.backup_create` | 创建备份 | 创建系统备份 |
| `system.backup_restore` | 恢复备份 | 从备份恢复 |

### 🔐 权限管理模块 (rbac)

| 权限代码 | 权限名称 | 说明 |
|----------|----------|------|
| `rbac.view` | 访问权限 | 进入权限管理 |
| `rbac.role_manage` | 管理角色 | 增删改角色 |
| `rbac.permission_manage` | 管理权限 | 增删改权限 |
| `rbac.manage` | 完全管理 | 角色权限完全管理 |

### 👤 用户管理模块 (user)

| 权限代码 | 权限名称 | 说明 |
|----------|----------|------|
| `user.view` | 访问用户 | 进入用户管理 |
| `user.create` | 创建用户 | 创建新用户 |
| `user.edit` | 编辑用户 | 修改用户信息 |
| `user.delete` | 删除用户 | 删除用户 |
| `user.reset_password` | 重置密码 | 重置用户密码 |

---

## 👔 默认角色

| 角色 | 代码 | 权限范围 |
|------|------|----------|
| **系统管理员** | `admin` | 拥有所有权限 |
| **人事经理** | `hr_manager` | 员工、考勤、薪资、请假审批等 |
| **部门经理** | `department_manager` | 部门数据、审批权限 |
| **普通员工** | `employee` | 个人数据查看、申请提交 |

> 注意：`init_rbac_permissions --with-roles` 生成的示例角色代码与名称略有不同，例如 `dept_manager`、`employees`、`auditor`。如果你是通过启动脚本初始化数据，请以数据库中的实际角色为准。

---

## 💻 开发指南

### 后端使用

#### 1. 在视图中检查权限

```python
from hr_management.permissions import HasRBACPermission
from hr_management.rbac import Permissions

class EmployeeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    
    # 方式一：动态获取所需权限
    def get_rbac_permissions(self):
        if self.request.method == 'POST':
            return [Permissions.EMPLOYEE_CREATE]
        elif self.request.method in ['PUT', 'PATCH']:
            return [Permissions.EMPLOYEE_EDIT]
        elif self.request.method == 'DELETE':
            return [Permissions.EMPLOYEE_DELETE]
        return [Permissions.EMPLOYEE_VIEW]
    
    # 方式二：静态声明权限
    rbac_perms = [Permissions.EMPLOYEE_VIEW]
```

#### 2. 在代码中检查权限

```python
from hr_management.permissions import has_permission
from hr_management.rbac import Permissions

def my_view(request):
    if has_permission(request.user, Permissions.SALARY_DISBURSE):
        # 执行发放薪资操作
        pass
```

### 前端使用

#### 1. 模板中使用指令

```vue
<template>
  <!-- 基本用法：有权限显示，无权限隐藏 -->
  <button v-permission="'employee.create'">新建员工</button>
  
  <!-- 任一权限满足即可（or 关系） -->
  <button v-permission.any="['employee.edit', 'employee.delete']">
    操作
  </button>
  
  <!-- 无权限时禁用而非隐藏 -->
  <button v-permission.disable="'salary.disburse'">发放薪资</button>
</template>
```

#### 2. 脚本中检查权限

```javascript
import { hasPermission, Permissions } from '@/utils/permissions'

// 检查单个权限
if (hasPermission(Permissions.EMPLOYEE_CREATE)) {
  // 有创建员工权限
}

// 检查多个权限（任一满足）
if (hasPermission([Permissions.LEAVE_APPROVE, Permissions.TRIP_APPROVE], 'any')) {
  // 有审批权限
}
```

#### 3. 路由守卫

```javascript
// router/index.js
{
  path: '/employees/manage',
  component: EmployeeManage,
  meta: {
    requiresAuth: true,
    permissions: ['employee.view']  // 所需权限
  }
}
```

---

## 🛠️ 管理命令

### 初始化 RBAC 数据

```bash
# 首次部署，推荐执行示例权限/角色初始化
python manage.py init_rbac_permissions --with-roles

# 强制更新示例角色的权限集合
python manage.py init_rbac_permissions --with-roles --force

# 兼容旧权限体系（点号风格 key）
python manage.py init_rbac

# 强制同步旧权限体系
python manage.py init_rbac --force
```

---

## ⚠️ 注意事项

1. **超级管理员 (`is_superuser`) 和 `is_staff` 用户自动拥有所有权限**
2. **`admin` 角色也自动拥有所有权限**，无需单独配置
3. 新增权限后需根据你使用的权限体系运行 `init_rbac --force` 或 `init_rbac_permissions --with-roles --force`
4. 前后端权限常量需保持一致（后端 `rbac.py`，前端 `permissions.js`）
5. 无权限访问时前端会重定向到 403 页面

---

## 📊 权限继承关系

```
superuser / is_staff
    └── 自动拥有所有权限

admin 角色
    └── 自动拥有所有权限

hr_manager 角色
    ├── employee.* (所有员工权限)
    ├── attendance.* (所有考勤权限)
    ├── salary.* (所有薪资权限)
    └── ...

普通用户
    └── 根据分配的角色获取权限
```
