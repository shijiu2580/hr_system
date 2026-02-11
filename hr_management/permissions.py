from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import Employee, Department
from .permission_cache import (
    cached_user_permissions,
    cached_managed_departments,
    has_permission_cached,
)


def get_managed_department_ids(user):
    """获取用户作为部门经理管理的部门ID列表（带缓存）"""
    if not user or not user.is_authenticated:
        return []
    return cached_managed_departments(user)


def user_has_rbac_permission(user, permission_key):
    """检查用户是否拥有指定的RBAC权限（带缓存）

    使用 permission_cache 模块的缓存机制，避免每次请求查询数据库。
    缓存会在角色/权限变更时自动失效。

    Args:
        user: Django User 对象
        permission_key: 权限键字符串

    Returns:
        bool: 是否拥有权限
    """
    if not user or not user.is_authenticated:
        return False

    # 超级管理员和系统管理员拥有所有权限
    if user.is_superuser or user.is_staff:
        return True

    return has_permission_cached(user, permission_key)


class HasRBACPermission(BasePermission):
    """基于RBAC的权限检查

    支持多种配置方式:

    1. 字典形式（按HTTP方法）:
        rbac_perms = {
            'GET': ['employee.view'],
            'POST': ['employee.create'],
            'PUT': ['employee.edit'],
            'PATCH': ['employee.edit'],
            'DELETE': ['employee.delete'],
        }

    2. 列表形式（所有方法使用相同权限）:
        rbac_perms = ['employee.view']  # 需要所有列出的权限
        rbac_perms_any = ['employee.view', 'admin']  # 任一权限即可

    3. 通过 get_rbac_permissions() 方法动态获取:
        def get_rbac_permissions(self):
            if self.request.method == 'POST':
                return ['employee.create']
            return ['employee.view']
    """
    message = '权限不足'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # 超级管理员和管理员直接放行
        if request.user.is_superuser or request.user.is_staff:
            return True

        method = request.method

        # 优先使用 get_rbac_permissions 方法获取权限
        if hasattr(view, 'get_rbac_permissions') and callable(view.get_rbac_permissions):
            required_perms = view.get_rbac_permissions()
            if required_perms:
                for perm in required_perms:
                    if not user_has_rbac_permission(request.user, perm):
                        return False
                return True

        # 获取视图上配置的权限
        rbac_perms = getattr(view, 'rbac_perms', {})
        rbac_perms_any = getattr(view, 'rbac_perms_any', {})

        # 处理 rbac_perms (需要所有权限)
        if isinstance(rbac_perms, dict):
            required_perms = rbac_perms.get(method, [])
        else:
            # 列表形式，所有方法使用相同权限
            required_perms = rbac_perms if isinstance(rbac_perms, list) else []

        if required_perms:
            for perm in required_perms:
                if not user_has_rbac_permission(request.user, perm):
                    return False

        # 处理 rbac_perms_any (只需任一权限)
        if isinstance(rbac_perms_any, dict):
            any_perms = rbac_perms_any.get(method, [])
        else:
            # 列表形式，所有方法使用相同权限
            any_perms = rbac_perms_any if isinstance(rbac_perms_any, list) else []

        if any_perms:
            if not any(user_has_rbac_permission(request.user, perm) for perm in any_perms):
                return False

        return True


class IsStaffOrReadOwnEmployee(BasePermission):
    """员工资源：管理员完全访问；部门经理可读本部门；普通用户仅能读取/修改自己的员工记录。"""
    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_staff:
            return True
        if not isinstance(obj, Employee):
            return False
        # 本人可以读写自己的记录
        if obj.user_id == request.user.id:
            return True
        # 部门经理可以读取本部门员工（只读）
        if request.method in SAFE_METHODS:
            managed_ids = get_managed_department_ids(request.user)
            if obj.department_id and obj.department_id in managed_ids:
                return True
        return False


class IsStaffOrOwnRelated(BasePermission):
    """考勤/请假/薪资等：管理员全访问；部门经理可读本部门；普通用户仅能访问自己关联的记录。"""
    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_staff:
            return True
        # 记录需具有关联 employee 字段
        employee = getattr(obj, 'employee', None)
        if not employee:
            return False
        # 本人可以读写自己的记录
        if employee.user_id == request.user.id:
            return True
        # 部门经理可以读取本部门员工的记录（只读）
        if request.method in SAFE_METHODS:
            managed_ids = get_managed_department_ids(request.user)
            if employee.department_id and employee.department_id in managed_ids:
                return True
        return False

    def has_permission(self, request, view):
        # 列表视图在 queryset 过滤层处理，这里仅要求已认证
        return request.user and request.user.is_authenticated


class IsStaffOrReadOnly(BasePermission):
    """职位/部门等：管理员完全访问；普通用户仅可读。"""
    def has_permission(self, request, view):
        if request.user and request.user.is_staff:
            return True
        # 普通用户仅允许读操作
        return request.method in SAFE_METHODS


class IsStaffOrOwner(BasePermission):
    """文档等：管理员完全访问；普通用户可创建，但只能修改/删除自己的。"""
    def has_permission(self, request, view):
        # 所有认证用户可以列表和创建
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # 管理员完全访问
        if request.user and request.user.is_staff:
            return True
        # 读操作所有人可以
        if request.method in SAFE_METHODS:
            return True
        # 写操作只能操作自己的
        return obj.uploaded_by_id == request.user.id
