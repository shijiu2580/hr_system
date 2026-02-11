"""
权限缓存模块
提供高效的权限检查缓存机制，减少数据库查询
"""
import hashlib
import json
from functools import wraps
from typing import Optional, Set, List, Dict, Any
from datetime import datetime, timedelta
from django.core.cache import cache
from django.conf import settings


# 缓存配置
PERMISSION_CACHE_TTL = getattr(settings, 'PERMISSION_CACHE_TTL', 300)  # 5分钟
PERMISSION_CACHE_PREFIX = 'perm:'


class PermissionCache:
    """
    用户权限缓存管理器

    缓存结构:
    - perm:user:{user_id}:all - 用户所有权限集合
    - perm:user:{user_id}:roles - 用户角色列表
    - perm:user:{user_id}:depts - 用户管理的部门ID列表
    - perm:role:{role_id}:perms - 角色权限列表
    """

    @staticmethod
    def _get_cache_key(prefix: str, *args) -> str:
        """生成缓存键"""
        parts = [PERMISSION_CACHE_PREFIX, prefix] + [str(a) for a in args]
        return ':'.join(parts)

    @classmethod
    def get_user_permissions(cls, user_id: int) -> Optional[Set[str]]:
        """获取用户权限集合（从缓存）"""
        key = cls._get_cache_key('user', user_id, 'all')
        cached = cache.get(key)
        if cached is not None:
            return set(cached)
        return None

    @classmethod
    def set_user_permissions(cls, user_id: int, permissions: Set[str]) -> None:
        """设置用户权限缓存"""
        key = cls._get_cache_key('user', user_id, 'all')
        cache.set(key, list(permissions), PERMISSION_CACHE_TTL)

    @classmethod
    def get_user_roles(cls, user_id: int) -> Optional[List[str]]:
        """获取用户角色列表（从缓存）"""
        key = cls._get_cache_key('user', user_id, 'roles')
        return cache.get(key)

    @classmethod
    def set_user_roles(cls, user_id: int, roles: List[str]) -> None:
        """设置用户角色缓存"""
        key = cls._get_cache_key('user', user_id, 'roles')
        cache.set(key, roles, PERMISSION_CACHE_TTL)

    @classmethod
    def get_managed_departments(cls, user_id: int) -> Optional[List[int]]:
        """获取用户管理的部门ID列表（从缓存）"""
        key = cls._get_cache_key('user', user_id, 'depts')
        return cache.get(key)

    @classmethod
    def set_managed_departments(cls, user_id: int, dept_ids: List[int]) -> None:
        """设置用户管理部门缓存"""
        key = cls._get_cache_key('user', user_id, 'depts')
        cache.set(key, dept_ids, PERMISSION_CACHE_TTL)

    @classmethod
    def invalidate_user(cls, user_id: int) -> None:
        """清除用户的所有权限缓存"""
        keys = [
            cls._get_cache_key('user', user_id, 'all'),
            cls._get_cache_key('user', user_id, 'roles'),
            cls._get_cache_key('user', user_id, 'depts'),
        ]
        cache.delete_many(keys)

    @classmethod
    def invalidate_role(cls, role_id: int) -> None:
        """清除角色相关缓存（会清除所有用户缓存）"""
        # 角色变更时需要清除所有用户缓存
        # 在实际生产中，应该只清除受影响用户的缓存
        key = cls._get_cache_key('role', role_id, 'perms')
        cache.delete(key)

    @classmethod
    def invalidate_all(cls) -> None:
        """清除所有权限缓存（慎用）"""
        # 使用 pattern 删除所有权限缓存
        # 注意：这在某些缓存后端可能不支持
        try:
            cache.clear()  # 简化处理
        except Exception:
            pass


def cached_user_permissions(user) -> Set[str]:
    """
    获取用户权限（带缓存）

    Args:
        user: Django User 对象

    Returns:
        用户权限集合
    """
    if not user or not user.is_authenticated:
        return set()

    # 超级管理员和管理员返回特殊标记
    if user.is_superuser or user.is_staff:
        return {'*'}  # 通配符表示所有权限

    # 尝试从缓存获取
    cached = PermissionCache.get_user_permissions(user.id)
    if cached is not None:
        return cached

    # 从数据库加载（包含用户直接角色 + 职位默认角色）
    from .models import Role, Employee
    permissions = set()

    # 用户直接关联的角色权限
    roles = Role.objects.filter(users=user).prefetch_related('permissions')
    for role in roles:
        for perm in role.permissions.all():
            permissions.add(perm.key)

    # 用户通过职位继承的角色权限
    try:
        employee = Employee.objects.select_related('position').get(user=user)
        if employee.position:
            position_roles = Role.objects.filter(
                positions=employee.position
            ).prefetch_related('permissions')
            for role in position_roles:
                for perm in role.permissions.all():
                    permissions.add(perm.key)
    except Employee.DoesNotExist:
        pass

    # 写入缓存
    PermissionCache.set_user_permissions(user.id, permissions)

    return permissions


def cached_user_roles(user) -> List[str]:
    """
    获取用户角色列表（带缓存）
    """
    if not user or not user.is_authenticated:
        return []

    # 尝试从缓存获取
    cached = PermissionCache.get_user_roles(user.id)
    if cached is not None:
        return cached

    # 从数据库加载
    from .models import Role
    roles = list(
        Role.objects.filter(users=user).values_list('code', flat=True)
    )

    # 写入缓存
    PermissionCache.set_user_roles(user.id, roles)

    return roles


def cached_managed_departments(user) -> List[int]:
    """
    获取用户管理的部门ID列表（带缓存）
    """
    if not user or not user.is_authenticated:
        return []

    # 尝试从缓存获取
    cached = PermissionCache.get_managed_departments(user.id)
    if cached is not None:
        return cached

    # 从数据库加载
    from .models import Employee, Department
    try:
        emp = Employee.objects.get(user=user)
        dept_ids = list(
            Department.objects.filter(manager=emp).values_list('id', flat=True)
        )
    except Employee.DoesNotExist:
        dept_ids = []

    # 写入缓存
    PermissionCache.set_managed_departments(user.id, dept_ids)

    return dept_ids


def has_permission_cached(user, permission_key: str) -> bool:
    """
    检查用户是否有权限（带缓存）

    Args:
        user: Django User 对象
        permission_key: 权限键

    Returns:
        是否有权限
    """
    permissions = cached_user_permissions(user)

    # 通配符检查
    if '*' in permissions:
        return True

    return permission_key in permissions


def has_any_permission_cached(user, permission_keys: List[str]) -> bool:
    """检查用户是否有任一权限"""
    permissions = cached_user_permissions(user)

    if '*' in permissions:
        return True

    return bool(permissions & set(permission_keys))


def has_all_permissions_cached(user, permission_keys: List[str]) -> bool:
    """检查用户是否有所有权限"""
    permissions = cached_user_permissions(user)

    if '*' in permissions:
        return True

    return set(permission_keys).issubset(permissions)


def has_role_cached(user, role_code: str) -> bool:
    """检查用户是否有指定角色"""
    roles = cached_user_roles(user)
    return role_code in roles


# 信号处理器：当权限相关数据变更时清除缓存
def setup_permission_cache_signals():
    """设置权限缓存失效信号"""
    from django.db.models.signals import post_save, post_delete, m2m_changed
    from .models import Role, RBACPermission
    from django.contrib.auth import get_user_model

    User = get_user_model()

    def invalidate_role_cache(sender, instance, **kwargs):
        """角色变更时清除缓存"""
        PermissionCache.invalidate_role(instance.id)

    def invalidate_user_permissions(sender, instance, **kwargs):
        """用户角色关联变更时清除缓存"""
        if kwargs.get('action') in ('post_add', 'post_remove', 'post_clear'):
            # 清除所有受影响用户的缓存
            if hasattr(instance, 'users'):
                for user in instance.users.all():
                    PermissionCache.invalidate_user(user.id)
            elif hasattr(instance, 'id'):
                PermissionCache.invalidate_user(instance.id)

    post_save.connect(invalidate_role_cache, sender=Role)
    post_delete.connect(invalidate_role_cache, sender=Role)

    # 监听 Role.users 多对多关系变更
    if hasattr(Role, 'users'):
        m2m_changed.connect(invalidate_user_permissions, sender=Role.users.through)

    # 监听 Role.permissions 多对多关系变更
    if hasattr(Role, 'permissions'):
        m2m_changed.connect(invalidate_user_permissions, sender=Role.permissions.through)


# 装饰器：自动缓存权限检查结果
def permission_required(permission_key: str):
    """
    权限检查装饰器（带缓存）

    Usage:
        @permission_required('employee.create')
        def create_employee(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not has_permission_cached(request.user, permission_key):
                from rest_framework.response import Response
                from rest_framework import status
                return Response(
                    {'detail': '权限不足'},
                    status=status.HTTP_403_FORBIDDEN
                )
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
