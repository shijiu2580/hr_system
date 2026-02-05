#!/usr/bin/env python
"""设置测试账号脚本"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_system.settings')
os.environ['DISABLE_SCHEDULER'] = '1'
django.setup()

from hr_management.models import Employee, Role, Position, Department
from django.contrib.auth.models import User

def setup():
    print("=== 配置测试账号 ===\n")

    # 1. 查看所有职位及其角色
    print("=== 所有职位及角色 ===")
    for pos in Position.objects.all():
        roles = list(pos.default_roles.values_list('code', flat=True))
        print(f"  {pos.id}: {pos.department.name if pos.department else '无部门'} - {pos.name} -> {roles}")

    # 2. 获取或创建部门经理职位
    print("\n=== 配置部门经理职位 ===")
    dept = Department.objects.first()
    dept_mgr_pos, created = Position.objects.get_or_create(
        name='部门经理',
        defaults={'department': dept}
    )
    if created:
        print(f"  创建职位: {dept_mgr_pos}")
    else:
        print(f"  已存在职位: {dept_mgr_pos}")

    # 配置部门经理职位的角色
    dept_mgr_role = Role.objects.get(code='department_manager')
    emp_role = Role.objects.get(code='employees')
    dept_mgr_pos.default_roles.clear()
    dept_mgr_pos.default_roles.add(dept_mgr_role, emp_role)
    print(f"  设置角色: {list(dept_mgr_pos.default_roles.values_list('code', flat=True))}")

    # 3. 获取或创建人事经理职位
    print("\n=== 配置人事经理职位 ===")
    hr_mgr_pos, created = Position.objects.get_or_create(
        name='人事经理',
        defaults={'department': dept}
    )
    if created:
        print(f"  创建职位: {hr_mgr_pos}")
    else:
        print(f"  已存在职位: {hr_mgr_pos}")

    hr_mgr_role = Role.objects.get(code='hr_manager')
    hr_mgr_pos.default_roles.clear()
    hr_mgr_pos.default_roles.add(hr_mgr_role, emp_role)
    print(f"  设置角色: {list(hr_mgr_pos.default_roles.values_list('code', flat=True))}")

    # 4. 配置测试员工
    print("\n=== 配置测试员工 ===")

    # 7951 -> 部门经理
    emp_7951 = Employee.objects.get(user__username='7951')
    emp_7951.position = dept_mgr_pos
    emp_7951.save()
    emp_7951.user.set_password('test123456')
    emp_7951.user.save()
    print(f"  部门经理: {emp_7951.name} ({emp_7951.user.username}) -> {dept_mgr_pos}")

    # employee001 -> 人事经理
    emp_hr = Employee.objects.get(user__username='employee001')
    emp_hr.position = hr_mgr_pos
    emp_hr.save()
    emp_hr.user.set_password('test123456')
    emp_hr.user.save()
    print(f"  人事经理: {emp_hr.name} ({emp_hr.user.username}) -> {hr_mgr_pos}")

    # 0001 -> 普通员工
    emp_0001 = Employee.objects.get(user__username='0001')
    # 确保普通员工职位只有 employees 角色
    if emp_0001.position:
        emp_0001.position.default_roles.clear()
        emp_0001.position.default_roles.add(emp_role)
    print(f"  普通员工: {emp_0001.name} ({emp_0001.user.username}) -> {emp_0001.position}")

    print("\n=== 配置完成 ===")
    print("\n测试账号:")
    print("  部门经理: 7951 / test123456")
    print("  人事经理: employee001 / test123456")
    print("  普通员工: 0001 / test123456")

def setup_admin_test():
    """创建非 superuser 的管理员测试账号"""
    print("\n=== 配置管理员测试账号 ===")

    username = 'admin_test'
    try:
        user = User.objects.get(username=username)
        print(f"  用户已存在: {username}")
    except User.DoesNotExist:
        user = User.objects.create_user(
            username=username,
            password='test123456',
            is_superuser=False,
            is_staff=False
        )
        print(f"  创建用户: {username}")

    # 关联 admin 角色
    admin_role = Role.objects.get(code='admin')
    user.roles.add(admin_role)
    print(f"  关联角色: {admin_role.name}")

    # 创建员工记录
    dept = Department.objects.filter(name='IT部').first() or Department.objects.first()
    pos = Position.objects.filter(name='系统管理员').first()
    if not pos:
        pos = Position.objects.create(department=dept, name='系统管理员')
        pos.default_roles.add(admin_role)

    try:
        emp = Employee.objects.get(user=user)
        print(f"  员工已存在: {emp.name}")
    except Employee.DoesNotExist:
        emp = Employee.objects.create(
            user=user,
            employee_id='ADMIN_TEST',
            name='测试管理员',
            department=dept,
            position=pos,
            gender='male',
            phone='13800000000'
        )
        print(f"  创建员工: {emp.name}")

    user.set_password('test123456')
    user.save()

    print(f"\n  管理员测试账号: {username} / test123456")
    print(f"  is_superuser: {user.is_superuser}")

if __name__ == '__main__':
    setup()
    setup_admin_test()
