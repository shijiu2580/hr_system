# RBAC 权限系统说明

## 概述

系统采用基于角色的访问控制（RBAC）模型，通过角色和权限的组合实现灵活的权限管理。

## 系统架构

```
用户 (User) ←→ 角色 (Role) ←→ 权限 (RBACPermission)
```

- **用户**可以拥有多个角色
- **角色**可以拥有多个权限
- **权限**定义了具体的操作能力

## 页面功能权限

### 🏠 首页（动态）
| 功能 | 权限 | 说明 |
|------|------|------|
| 查看动态 | - | 所有登录用户可访问 |

---

### 👥 员工模块

#### 员工列表
| 功能 | 权限 | 说明 |
|------|------|------|
| 查看列表 | - | 所有用户可查看基础列表 |
| 查看详情 | `employee.view` | 查看员工详细信息 |

#### 员工管理
| 功能 | 权限 | 说明 |
|------|------|------|
| 访问管理页 | `employee.view` | 进入员工管理页面 |
| 新建员工 | `employee.create` | 创建新员工档案 |
| 编辑员工 | `employee.edit` | 修改员工信息 |
| 删除员工 | `employee.delete` | 删除员工档案 |
| 批量导入 | `employee.import` | Excel批量导入 |
| 导出数据 | `employee.export` | 导出员工数据 |

---

### ⏰ 考勤模块

#### 考勤记录
| 功能 | 权限 | 说明 |
|------|------|------|
| 查看个人记录 | `attendance.view` | 查看自己的考勤 |
| 签到/签退 | `attendance.create` | 日常打卡操作 |

#### 考勤管理
| 功能 | 权限 | 说明 |
|------|------|------|
| 访问管理页 | `attendance.view_all` | 查看所有员工考勤 |
| 编辑记录 | `attendance.edit` | 修改考勤记录 |

#### 考勤地点
| 功能 | 权限 | 说明 |
|------|------|------|
| 管理地点 | `attendance.location` | 设置打卡地点范围 |

#### 补签审批
| 功能 | 权限 | 说明 |
|------|------|------|
| 审批补签 | `attendance.approve` | 审批员工补签申请 |

---

### 📝 请假模块

#### 请假申请
| 功能 | 权限 | 说明 |
|------|------|------|
| 查看申请 | `leave.view` | 查看自己的请假 |
| 提交申请 | `leave.create` | 发起请假申请 |

#### 出差申请
| 功能 | 权限 | 说明 |
|------|------|------|
| 查看出差 | `trip.view` | 查看自己的出差 |
| 提交申请 | `trip.create` | 发起出差申请 |

#### 审批流程
| 功能 | 权限 | 说明 |
|------|------|------|
| 审批请假 | `leave.approve` | 审批员工请假 |
| 审批出差 | `trip.approve` | 审批员工出差 |
| 查看所有请假 | `leave.view_all` | 查看全部请假记录 |
| 查看所有出差 | `trip.view_all` | 查看全部出差记录 |

---

### 💰 薪资模块

#### 薪资管理
| 功能 | 权限 | 说明 |
|------|------|------|
| 访问管理页 | `salary.view_all` | 查看所有薪资数据 |
| 创建薪资 | `salary.create` | 生成薪资记录 |
| 编辑薪资 | `salary.edit` | 修改薪资记录 |
| 删除薪资 | `salary.delete` | 删除薪资记录 |
| 发放薪资 | `salary.disburse` | 批量发放薪资 |

#### 薪资记录
| 功能 | 权限 | 说明 |
|------|------|------|
| 查看个人薪资 | `salary.view` | 查看自己的薪资 |

#### 差旅报销
| 功能 | 权限 | 说明 |
|------|------|------|
| 查看报销 | `expense.view` | 查看自己的报销 |
| 提交报销 | `expense.create` | 发起报销申请 |

#### 报销审批
| 功能 | 权限 | 说明 |
|------|------|------|
| 审批报销 | `expense.approve` | 审批报销申请 |
| 查看所有报销 | `expense.view_all` | 查看全部报销记录 |

---

### 🏢 职位管理
| 功能 | 权限 | 说明 |
|------|------|------|
| 查看职位 | `position.view` | 查看职位列表 |
| 新建职位 | `position.create` | 创建新职位 |
| 编辑职位 | `position.edit` | 修改职位信息 |
| 删除职位 | `position.delete` | 删除职位 |

---

### 🏛️ 部门管理
| 功能 | 权限 | 说明 |
|------|------|------|
| 查看部门 | `department.view` | 查看部门列表 |
| 新建部门 | `department.create` | 创建新部门 |
| 编辑部门 | `department.edit` | 修改部门信息 |
| 删除部门 | `department.delete` | 删除部门 |

---

### 📄 文档中心
| 功能 | 权限 | 说明 |
|------|------|------|
| 查看文档 | `document.view` | 查看公司文档 |
| 上传文档 | `document.upload` | 上传新文档 |
| 创建文档 | `document.create` | 创建文档记录 |
| 编辑文档 | `document.edit` | 编辑文档信息 |
| 删除文档 | `document.delete` | 删除文档 |
| 管理文档 | `document.manage` | 管理公司公开文档 |

---

### 📊 大数据报表
| 功能 | 权限 | 说明 |
|------|------|------|
| 访问报表 | `report.view` | 进入报表页面 |
| 员工报表 | `report.employee` | 查看员工统计 |
| 考勤报表 | `report.attendance` | 查看考勤统计 |
| 薪资报表 | `report.salary` | 查看薪资统计 |
| 请假报表 | `report.leave` | 查看请假统计 |
| 导出报表 | `report.export` | 导出报表数据 |

---

### 🚪 离职申请
| 功能 | 权限 | 说明 |
|------|------|------|
| 查看离职 | `resignation.view` | 查看自己的离职申请 |
| 发起离职 | `resignation.create` | 提交离职申请 |
| 审批离职 | `resignation.approve` | 审批离职申请 |
| 查看所有 | `resignation.view_all` | 查看全部离职记录 |

---

### ⚙️ 系统管理
| 功能 | 权限 | 说明 |
|------|------|------|
| 访问系统页 | `system.view` | 进入系统管理 |
| 查看日志 | `system.log_view` | 查看系统日志 |
| 清除日志 | `system.log_clear` | 清空系统日志 |
| 查看备份 | `system.backup_view` | 查看备份列表 |
| 创建备份 | `system.backup_create` | 创建系统备份 |
| 恢复备份 | `system.backup_restore` | 从备份恢复 |

---

### 🔐 权限管理
| 功能 | 权限 | 说明 |
|------|------|------|
| 访问权限页 | `rbac.view` | 进入权限管理 |
| 管理角色 | `rbac.role_manage` | 增删改角色 |
| 管理权限 | `rbac.permission_manage` | 增删改权限 |
| 完全管理 | `rbac.manage` | 角色权限完全管理 |

---

### 👤 用户管理
| 功能 | 权限 | 说明 |
|------|------|------|
| 访问用户页 | `user.view` | 进入用户管理 |
| 创建用户 | `user.create` | 创建新用户 |
| 编辑用户 | `user.edit` | 修改用户信息 |
| 删除用户 | `user.delete` | 删除用户 |
| 重置密码 | `user.reset_password` | 重置用户密码 |

---

### 👤 账号设置
| 功能 | 权限 | 说明 |
|------|------|------|
| 修改密码 | - | 所有用户可修改自己密码 |
| 修改资料 | - | 所有用户可修改个人资料 |

---

## 默认角色

| 角色 | 代码 | 说明 |
|------|------|------|
| 系统管理员 | `admin` | 拥有所有权限 |
| 人事经理 | `hr_manager` | 管理员工、考勤、薪资等 |
| 部门经理 | `department_manager` | 管理本部门相关事务 |
| 普通员工 | `employee` | 基本的个人操作权限 |

## 使用方法

### 后端 API 视图

```python
from hr_management.permissions import HasRBACPermission
from hr_management.rbac import Permissions

class MyAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, HasRBACPermission]
    
    # 方法1：使用 get_rbac_permissions() 动态获取
    def get_rbac_permissions(self):
        if self.request.method == 'POST':
            return [Permissions.EMPLOYEE_CREATE]
        return [Permissions.EMPLOYEE_VIEW]
    
    # 方法2：使用 rbac_perms 属性（列表形式）
    rbac_perms = [Permissions.EMPLOYEE_VIEW]
```

### 前端模板

```vue
<template>
  <!-- 基本用法：有权限才显示 -->
  <button v-permission="'employee.create'">新建员工</button>
  
  <!-- 任一权限即可（使用 .any 修饰符） -->
  <button v-permission.any="['employee.edit', 'employee.delete']">操作</button>
  
  <!-- 禁用而非隐藏（使用 .disable 修饰符） -->
  <button v-permission.disable="'employee.delete'">删除</button>
</template>
```

### 前端 JS

```javascript
import { hasPermission, Permissions } from '@/utils/permissions';

if (hasPermission(Permissions.EMPLOYEE_CREATE)) {
  // 有创建员工权限
}
```

## 管理命令

```bash
# 初始化RBAC数据（首次部署必须执行）
python manage.py init_rbac

# 强制更新（会更新已存在的权限和角色）
python manage.py init_rbac --force
```

## 注意事项

1. **超级管理员和 is_staff** 自动拥有所有权限，无需额外配置
2. **admin 角色** 也自动拥有所有权限
3. 新增权限后需要运行 `init_rbac --force` 同步到数据库
4. 前后端权限常量需要保持一致
5. 路由权限检查会在用户无权限时重定向到 403 页面
