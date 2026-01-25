"""
业务服务层 - 封装复杂业务逻辑，提供缓存和查询优化

这一层的目的是:
1. 将业务逻辑从视图中抽离，便于复用和测试
2. 提供统一的缓存策略
3. 优化数据库查询，减少 N+1 问题
"""
from typing import Optional, List, Dict, Any, Callable, TypeVar
from functools import lru_cache, wraps
import hashlib
import json
from django.core.cache import cache
from django.db.models import Count, Sum, Q, Prefetch
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta

from .models import (
    Employee, Department, Position, Attendance, AttendanceSupplement,
    LeaveRequest, SalaryRecord, BusinessTrip, TravelExpense, Role
)


T = TypeVar('T')


# ============ 缓存键定义 ============
class CacheKeys:
    """统一管理缓存键，避免硬编码"""
    # 组织结构
    DEPARTMENT_TREE = 'dept_tree'
    DEPARTMENT_LIST = 'dept_list'
    DEPARTMENT_CHILDREN = 'dept_children_{dept_id}'
    POSITION_LIST = 'position_list'
    
    # 员工
    EMPLOYEE_COUNT = 'employee_count'
    EMPLOYEE_BY_USER = 'emp_user_{user_id}'
    
    # 考勤
    ATTENDANCE_TODAY = 'att_today_{employee_id}'
    ATTENDANCE_MONTH = 'att_month_{employee_id}_{year}_{month}'
    
    # 权限
    USER_PERMISSIONS = 'user_perms_{user_id}'
    USER_ROLES = 'user_roles_{user_id}'
    
    # 仪表盘
    DASHBOARD_SUMMARY = 'dashboard_summary'
    DASHBOARD_CHARTS = 'dashboard_charts_{chart_type}'
    
    # 缓存超时时间(秒)
    TIMEOUT_VERY_SHORT = 30   # 30秒
    TIMEOUT_SHORT = 60        # 1分钟
    TIMEOUT_MEDIUM = 300      # 5分钟
    TIMEOUT_LONG = 3600       # 1小时
    TIMEOUT_DAY = 86400       # 1天


# ============ 缓存装饰器 ============
def cached(key_template: str, timeout: int = CacheKeys.TIMEOUT_MEDIUM):
    """
    缓存装饰器 - 自动缓存函数返回值
    
    Args:
        key_template: 缓存键模板，支持 {arg_name} 格式
        timeout: 缓存超时时间
    
    Example:
        @cached('user_{user_id}', timeout=300)
        def get_user(user_id):
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 构建缓存键
            # 将位置参数转换为关键字参数
            import inspect
            sig = inspect.signature(func)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            
            try:
                cache_key = key_template.format(**bound.arguments)
            except KeyError:
                # 如果模板参数不匹配，使用哈希
                cache_key = f"{func.__name__}_{hashlib.md5(str(bound.arguments).encode()).hexdigest()[:8]}"
            
            # 尝试从缓存获取
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # 执行函数
            result = func(*args, **kwargs)
            
            # 存入缓存
            if result is not None:
                cache.set(cache_key, result, timeout)
            
            return result
        
        # 添加缓存失效方法
        def invalidate(*args, **kwargs):
            import inspect
            sig = inspect.signature(func)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            cache_key = key_template.format(**bound.arguments)
            cache.delete(cache_key)
        
        wrapper.invalidate = invalidate
        wrapper.cache_key_template = key_template
        return wrapper
    
    return decorator


def cache_result(key: str, timeout: int = CacheKeys.TIMEOUT_MEDIUM):
    """简单的缓存包装器 - 用于缓存任意表达式结果"""
    def get_or_set(func: Callable[[], T]) -> T:
        result = cache.get(key)
        if result is not None:
            return result
        result = func()
        cache.set(key, result, timeout)
        return result
    return get_or_set


class CacheManager:
    """缓存管理器 - 提供批量操作和模式匹配"""
    
    @staticmethod
    def invalidate_pattern(pattern: str):
        """清除匹配模式的所有缓存键"""
        # Django 默认缓存不支持模式匹配，这里使用已知的键列表
        known_patterns = {
            'dept_*': [CacheKeys.DEPARTMENT_TREE, CacheKeys.DEPARTMENT_LIST],
            'emp_*': [CacheKeys.EMPLOYEE_COUNT],
            'dashboard_*': [CacheKeys.DASHBOARD_SUMMARY],
        }
        keys = known_patterns.get(pattern, [])
        if keys:
            cache.delete_many(keys)
    
    @staticmethod
    def invalidate_user_related(user_id: int):
        """清除用户相关的所有缓存"""
        keys = [
            CacheKeys.USER_PERMISSIONS.format(user_id=user_id),
            CacheKeys.USER_ROLES.format(user_id=user_id),
            CacheKeys.EMPLOYEE_BY_USER.format(user_id=user_id),
        ]
        cache.delete_many(keys)
    
    @staticmethod
    def invalidate_employee_related(employee_id: int):
        """清除员工相关的所有缓存"""
        today = timezone.localdate()
        keys = [
            CacheKeys.ATTENDANCE_TODAY.format(employee_id=employee_id),
            CacheKeys.ATTENDANCE_MONTH.format(
                employee_id=employee_id,
                year=today.year,
                month=today.month
            ),
        ]
        cache.delete_many(keys)
    
    @staticmethod
    def warm_cache():
        """预热常用缓存"""
        DepartmentService.get_department_tree()
        EmployeeService.get_summary_stats()


# ============ 部门服务 ============
class DepartmentService:
    """部门相关业务逻辑"""
    
    @staticmethod
    def get_department_tree() -> List[Dict]:
        """获取部门树形结构（带缓存）"""
        cached = cache.get(CacheKeys.DEPARTMENT_TREE)
        if cached:
            return cached
        
        # 一次性加载所有部门，避免递归查询
        departments = Department.objects.select_related('manager', 'parent').prefetch_related('supervisors').all()
        
        # 构建id到部门的映射
        dept_map = {d.id: d for d in departments}
        
        # 构建树形结构
        def build_tree_node(dept):
            return {
                'id': dept.id,
                'name': dept.name,
                'manager': {'id': dept.manager.id, 'name': dept.manager.name} if dept.manager else None,
                'parent_id': dept.parent_id,
                'children': []
            }
        
        tree = []
        nodes = {d.id: build_tree_node(d) for d in departments}
        
        for dept in departments:
            node = nodes[dept.id]
            if dept.parent_id and dept.parent_id in nodes:
                nodes[dept.parent_id]['children'].append(node)
            else:
                tree.append(node)
        
        cache.set(CacheKeys.DEPARTMENT_TREE, tree, CacheKeys.TIMEOUT_MEDIUM)
        return tree
    
    @staticmethod
    def get_all_child_ids(department_id: int) -> List[int]:
        """获取部门及所有子部门的ID列表"""
        result = [department_id]
        children = Department.objects.filter(parent_id=department_id).values_list('id', flat=True)
        for child_id in children:
            result.extend(DepartmentService.get_all_child_ids(child_id))
        return result
    
    @staticmethod
    def invalidate_cache():
        """清除部门相关缓存"""
        cache.delete_many([CacheKeys.DEPARTMENT_TREE, CacheKeys.DEPARTMENT_LIST])


# ============ 员工服务 ============
class EmployeeService:
    """员工相关业务逻辑"""
    
    @staticmethod
    def get_optimized_queryset():
        """获取优化后的员工查询集（预加载关联数据）"""
        return Employee.objects.select_related(
            'user', 'department', 'position', 'position__department'
        ).prefetch_related('checkin_locations')
    
    @staticmethod
    def get_employee_by_user(user: User) -> Optional[Employee]:
        """根据用户获取员工信息"""
        try:
            return Employee.objects.select_related('department', 'position').get(user=user)
        except Employee.DoesNotExist:
            return None
    
    @staticmethod
    def get_department_employees(department_id: int, include_children: bool = False) -> List[Employee]:
        """获取部门员工列表"""
        if include_children:
            dept_ids = DepartmentService.get_all_child_ids(department_id)
            return EmployeeService.get_optimized_queryset().filter(department_id__in=dept_ids, is_active=True)
        return EmployeeService.get_optimized_queryset().filter(department_id=department_id, is_active=True)
    
    @staticmethod
    def get_summary_stats() -> Dict[str, int]:
        """获取员工统计摘要（带缓存）"""
        cached = cache.get(CacheKeys.EMPLOYEE_COUNT)
        if cached:
            return cached
        
        stats = Employee.objects.aggregate(
            total=Count('id'),
            active=Count('id', filter=Q(is_active=True)),
            inactive=Count('id', filter=Q(is_active=False))
        )
        
        cache.set(CacheKeys.EMPLOYEE_COUNT, stats, CacheKeys.TIMEOUT_MEDIUM)
        return stats


# ============ 考勤服务 ============
class AttendanceService:
    """考勤相关业务逻辑"""
    
    @staticmethod
    def get_optimized_queryset():
        """获取优化后的考勤查询集"""
        return Attendance.objects.select_related(
            'employee', 'employee__user', 'employee__department'
        )
    
    @staticmethod
    def get_today_record(employee_id: int) -> Optional[Attendance]:
        """获取员工今日考勤记录"""
        cache_key = CacheKeys.ATTENDANCE_TODAY.format(employee_id=employee_id)
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        today = timezone.localdate()
        record = Attendance.objects.filter(employee_id=employee_id, date=today).first()
        
        if record:
            cache.set(cache_key, record, CacheKeys.TIMEOUT_SHORT)
        return record
    
    @staticmethod
    def invalidate_today_cache(employee_id: int):
        """清除员工今日考勤缓存"""
        cache.delete(CacheKeys.ATTENDANCE_TODAY.format(employee_id=employee_id))
    
    @staticmethod
    def get_attendance_stats(employee_id: int, year: int, month: int) -> Dict[str, int]:
        """获取员工月度考勤统计"""
        from datetime import date
        import calendar
        
        _, last_day = calendar.monthrange(year, month)
        start_date = date(year, month, 1)
        end_date = date(year, month, last_day)
        
        records = Attendance.objects.filter(
            employee_id=employee_id,
            date__gte=start_date,
            date__lte=end_date
        )
        
        stats = {
            'total_days': records.count(),
            'normal': 0,
            'late': 0,
            'early_leave': 0,
            'absent': 0,
        }
        
        for r in records:
            if r.check_in_time and r.check_out_time:
                from datetime import time
                if r.check_in_time > time(9, 0):
                    stats['late'] += 1
                elif r.check_out_time < time(18, 0):
                    stats['early_leave'] += 1
                else:
                    stats['normal'] += 1
            elif not r.check_in_time and not r.check_out_time:
                stats['absent'] += 1
        
        return stats


# ============ 权限服务 ============
class PermissionService:
    """权限相关业务逻辑"""
    
    @staticmethod
    def get_user_permissions(user: User) -> List[str]:
        """获取用户所有权限（带缓存）"""
        if not user or not user.is_authenticated:
            return []
        
        cache_key = CacheKeys.USER_PERMISSIONS.format(user_id=user.id)
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
        
        # 超级管理员和管理员拥有所有权限
        if user.is_superuser or user.is_staff:
            from .rbac import Permissions
            permissions = [getattr(Permissions, attr) for attr in dir(Permissions) 
                         if not attr.startswith('_') and isinstance(getattr(Permissions, attr), str)]
            cache.set(cache_key, permissions, CacheKeys.TIMEOUT_MEDIUM)
            return permissions
        
        # 获取用户角色的所有权限
        permissions = list(Role.objects.filter(users=user).values_list(
            'permissions__key', flat=True
        ).distinct())
        permissions = [p for p in permissions if p]  # 过滤 None
        
        cache.set(cache_key, permissions, CacheKeys.TIMEOUT_MEDIUM)
        return permissions
    
    @staticmethod
    def user_has_any_permission(user: User, permission_keys: List[str]) -> bool:
        """检查用户是否拥有任一权限"""
        user_perms = PermissionService.get_user_permissions(user)
        return any(p in user_perms for p in permission_keys)
    
    @staticmethod
    def invalidate_user_cache(user_id: int):
        """清除用户权限缓存"""
        cache.delete(CacheKeys.USER_PERMISSIONS.format(user_id=user_id))


# ============ 仪表盘服务 ============
class DashboardService:
    """仪表盘相关业务逻辑"""
    
    @staticmethod
    def get_summary(user: User) -> Dict[str, Any]:
        """获取系统概览数据（带缓存）"""
        cached = cache.get(CacheKeys.DASHBOARD_SUMMARY)
        if cached:
            return cached
        
        today = timezone.localdate()
        
        summary = {
            'employee_count': Employee.objects.filter(is_active=True).count(),
            'department_count': Department.objects.count(),
            'today_attendance': Attendance.objects.filter(date=today).count(),
            'pending_leaves': LeaveRequest.objects.filter(status='pending').count(),
            'pending_supplements': AttendanceSupplement.objects.filter(status='pending').count(),
            'pending_trips': BusinessTrip.objects.filter(status='pending').count(),
        }
        
        cache.set(CacheKeys.DASHBOARD_SUMMARY, summary, CacheKeys.TIMEOUT_SHORT)
        return summary
    
    @staticmethod
    def invalidate_cache():
        """清除仪表盘缓存"""
        cache.delete(CacheKeys.DASHBOARD_SUMMARY)
