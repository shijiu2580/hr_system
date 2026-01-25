"""HR Management API Package

按功能模块组织的 API 视图和序列化器。

目录结构:
- views/: API 视图模块
    - auth.py: 认证相关 (登录、登出、密码)
    - dashboard.py: 仪表板统计
    - employees.py: 员工管理
    - attendance.py: 考勤管理
    - leaves.py: 请假管理
    - salaries.py: 薪资管理
    - organization.py: 部门与职位
    - rbac.py: 角色权限管理
    - system.py: 系统管理 (日志、备份、文档)
- serializers/: 序列化器模块
"""
