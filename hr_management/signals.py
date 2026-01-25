"""
Django 信号处理器 - 自动清除缓存和触发相关操作

当数据发生变化时，自动清除相关缓存，保证数据一致性
"""
from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from django.core.cache import cache

from .models import (
    Department, Employee, Position, Attendance, AttendanceSupplement,
    LeaveRequest, SalaryRecord, Role, RBACPermission, CheckInLocation
)
from .services import CacheKeys


# ============ 部门相关信号 ============
@receiver([post_save, post_delete], sender=Department)
def invalidate_department_cache(sender, instance, **kwargs):
    """部门变更时清除缓存"""
    cache.delete_many([
        CacheKeys.DEPARTMENT_TREE,
        CacheKeys.DEPARTMENT_LIST,
        CacheKeys.DASHBOARD_SUMMARY,
    ])


# ============ 员工相关信号 ============
@receiver([post_save, post_delete], sender=Employee)
def invalidate_employee_cache(sender, instance, **kwargs):
    """员工变更时清除缓存"""
    cache.delete_many([
        CacheKeys.EMPLOYEE_COUNT,
        CacheKeys.DASHBOARD_SUMMARY,
    ])
    # 清除该员工的考勤缓存
    cache.delete(CacheKeys.ATTENDANCE_TODAY.format(employee_id=instance.id))


@receiver(m2m_changed, sender=Employee.checkin_locations.through)
def employee_locations_changed(sender, instance, action, **kwargs):
    """员工考勤地点变更"""
    if action in ('post_add', 'post_remove', 'post_clear'):
        cache.delete(CacheKeys.ATTENDANCE_TODAY.format(employee_id=instance.id))


# ============ 考勤相关信号 ============
@receiver([post_save, post_delete], sender=Attendance)
def invalidate_attendance_cache(sender, instance, **kwargs):
    """考勤变更时清除缓存"""
    cache.delete(CacheKeys.ATTENDANCE_TODAY.format(employee_id=instance.employee_id))
    cache.delete(CacheKeys.DASHBOARD_SUMMARY)


@receiver([post_save, post_delete], sender=AttendanceSupplement)
def invalidate_supplement_cache(sender, instance, **kwargs):
    """补签申请变更时清除缓存"""
    cache.delete(CacheKeys.DASHBOARD_SUMMARY)


# ============ 请假相关信号 ============
@receiver([post_save, post_delete], sender=LeaveRequest)
def invalidate_leave_cache(sender, instance, **kwargs):
    """请假变更时清除缓存"""
    cache.delete(CacheKeys.DASHBOARD_SUMMARY)


# ============ 权限相关信号 ============
@receiver([post_save, post_delete], sender=Role)
def invalidate_role_cache(sender, instance, **kwargs):
    """角色变更时清除相关用户的权限缓存"""
    for user in instance.users.all():
        cache.delete(CacheKeys.USER_PERMISSIONS.format(user_id=user.id))


@receiver(m2m_changed, sender=Role.users.through)
def role_users_changed(sender, instance, action, pk_set, **kwargs):
    """角色-用户关系变更时清除权限缓存"""
    if action in ('post_add', 'post_remove', 'post_clear'):
        # instance 是 Role
        if pk_set:
            for user_id in pk_set:
                cache.delete(CacheKeys.USER_PERMISSIONS.format(user_id=user_id))
        else:
            # clear 操作，清除所有该角色用户的缓存
            for user in instance.users.all():
                cache.delete(CacheKeys.USER_PERMISSIONS.format(user_id=user.id))


@receiver(m2m_changed, sender=Role.permissions.through)
def role_permissions_changed(sender, instance, action, **kwargs):
    """角色-权限关系变更时清除所有用户的权限缓存"""
    if action in ('post_add', 'post_remove', 'post_clear'):
        for user in instance.users.all():
            cache.delete(CacheKeys.USER_PERMISSIONS.format(user_id=user.id))


# ============ 位置相关信号 ============
@receiver([post_save, post_delete], sender=CheckInLocation)
def invalidate_location_cache(sender, instance, **kwargs):
    """签到地点变更时清除相关缓存"""
    # 清除所有关联员工的考勤缓存
    for emp in instance.employees.all():
        cache.delete(CacheKeys.ATTENDANCE_TODAY.format(employee_id=emp.id))
