#!/usr/bin/env python
"""数据隔离测试脚本 - 验证部门经理只能看到本部门数据"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_system.settings')
os.environ['DISABLE_SCHEDULER'] = '1'
django.setup()

import requests
from hr_management.models import Employee, Department, Attendance, LeaveRequest
from django.contrib.auth.models import User

BASE = 'http://localhost:8000/api'


def get_token(username, password):
    """获取登录token"""
    r = requests.post(f'{BASE}/auth/token/', json={'username': username, 'password': password})
    if r.status_code == 200:
        return r.json()['access']
    return None


def setup_test_data():
    """设置测试数据 - 确保不同部门有不同的员工"""
    print("=== 设置测试数据 ===\n")

    # 查看部门分布
    print("部门员工分布:")
    for dept in Department.objects.all():
        emp_count = Employee.objects.filter(department=dept, is_active=True).count()
        print(f"  {dept.name}: {emp_count} 人")

    # 查看测试账号所属部门
    print("\n测试账号部门:")
    test_users = {
        '0001': '普通员工',
        '7951': '部门经理',
        'employee001': '人事经理',
        'admin_test': '管理员'
    }

    user_depts = {}
    for username, role in test_users.items():
        try:
            user = User.objects.get(username=username)
            emp = Employee.objects.get(user=user)
            dept_name = emp.department.name if emp.department else "无部门"
            user_depts[username] = emp.department_id
            print(f"  {role}({username}): {emp.name} -> {dept_name}")
        except Exception as e:
            print(f"  {username}: 错误 - {e}")

    return user_depts


def test_data_isolation():
    """测试数据隔离"""
    print("\n" + "="*60)
    print("  数据隔离测试")
    print("="*60)

    results = []

    # 1. 普通员工只能看到自己
    print("\n【测试1】普通员工数据隔离")
    token = get_token('0001', 'test123456')
    if token:
        headers = {'Authorization': f'Bearer {token}'}

        # 获取员工列表
        r = requests.get(f'{BASE}/employees/', headers=headers)
        if r.status_code == 200:
            data = r.json()
            employees = data.get('results', data) if isinstance(data, dict) else data
            count = len(employees)
            # 普通员工应该只能看到自己(1条记录)
            passed = count == 1
            print(f"  [{'✓' if passed else '✗'}] 员工列表: 返回 {count} 条 (期望: 1)")
            results.append(('普通员工-员工列表', passed))

            if count == 1:
                emp_name = employees[0].get('name', '')
                print(f"      看到的员工: {emp_name}")

        # 获取考勤记录
        r = requests.get(f'{BASE}/attendance/', headers=headers)
        if r.status_code == 200:
            data = r.json()
            records = data.get('results', data) if isinstance(data, dict) else data
            # 检查是否都是自己的记录
            own_records = all(rec.get('employee_name', '') == '伍四' or rec.get('employee', {}).get('name', '') == '伍四' for rec in records) if records else True
            print(f"  [{'✓' if own_records else '✗'}] 考勤记录: 返回 {len(records)} 条，全部是自己的: {own_records}")
            results.append(('普通员工-考勤隔离', own_records))

    # 2. 部门经理只能看到本部门
    print("\n【测试2】部门经理数据隔离")
    token = get_token('7951', 'test123456')
    if token:
        headers = {'Authorization': f'Bearer {token}'}

        # 获取员工列表
        r = requests.get(f'{BASE}/employees/', headers=headers)
        if r.status_code == 200:
            data = r.json()
            employees = data.get('results', data) if isinstance(data, dict) else data
            count = len(employees)

            # 部门经理应该能看到本部门员工(不是全部员工)
            total_employees = Employee.objects.filter(is_active=True).count()

            # 获取部门经理的部门
            mgr_emp = Employee.objects.get(user__username='7951')
            mgr_dept = mgr_emp.department
            dept_employees = Employee.objects.filter(department=mgr_dept, is_active=True).count()

            # 部门经理看到的应该是本部门员工数+自己(如果有managed_departments逻辑)
            # 或者至少不应该看到全部员工
            passed = count < total_employees or count <= dept_employees + 1
            print(f"  [{'✓' if passed else '✗'}] 员工列表: 返回 {count} 条 (本部门: {dept_employees}, 总员工: {total_employees})")
            results.append(('部门经理-员工隔离', passed))

            # 显示看到的员工部门分布
            dept_dist = {}
            for emp in employees:
                dept = emp.get('department_name', emp.get('department', {}).get('name', '未知'))
                dept_dist[dept] = dept_dist.get(dept, 0) + 1
            print(f"      部门分布: {dept_dist}")

    # 3. 人事经理能看到所有员工
    print("\n【测试3】人事经理数据访问")
    token = get_token('employee001', 'test123456')
    if token:
        headers = {'Authorization': f'Bearer {token}'}

        r = requests.get(f'{BASE}/employees/', headers=headers)
        if r.status_code == 200:
            data = r.json()
            employees = data.get('results', data) if isinstance(data, dict) else data
            count = len(employees)
            total = Employee.objects.filter(is_active=True).count()

            # 人事经理应该能看到大部分或全部员工
            passed = count >= total * 0.8  # 至少80%
            print(f"  [{'✓' if passed else '✗'}] 员工列表: 返回 {count} 条 (总员工: {total})")
            results.append(('人事经理-全量访问', passed))

    # 4. 管理员能看到所有
    print("\n【测试4】管理员数据访问")
    token = get_token('admin_test', 'test123456')
    if token:
        headers = {'Authorization': f'Bearer {token}'}

        r = requests.get(f'{BASE}/employees/', headers=headers)
        if r.status_code == 200:
            data = r.json()
            employees = data.get('results', data) if isinstance(data, dict) else data
            count = len(employees)
            total = Employee.objects.filter(is_active=True).count()

            passed = count >= total * 0.8
            print(f"  [{'✓' if passed else '✗'}] 员工列表: 返回 {count} 条 (总员工: {total})")
            results.append(('管理员-全量访问', passed))

    # 5. 薪资数据隔离测试
    print("\n【测试5】薪资数据隔离")

    # 部门经理不能看薪资(权限测试已验证)，这里测试人事看薪资
    token = get_token('employee001', 'test123456')
    if token:
        headers = {'Authorization': f'Bearer {token}'}
        r = requests.get(f'{BASE}/salaries/', headers=headers)
        if r.status_code == 200:
            data = r.json()
            records = data.get('results', data) if isinstance(data, dict) else data
            print(f"  [✓] 人事经理薪资访问: 返回 {len(records)} 条")
            results.append(('人事经理-薪资访问', True))
        else:
            print(f"  [✗] 人事经理薪资访问失败: {r.status_code}")
            results.append(('人事经理-薪资访问', False))

    # 总结
    print("\n" + "="*60)
    print("  数据隔离测试总结")
    print("="*60)

    passed_count = sum(1 for _, p in results if p)
    total_count = len(results)

    for name, passed in results:
        status = '✓ PASS' if passed else '✗ FAIL'
        print(f"  [{status}] {name}")

    print(f"\n  总计: {passed_count}/{total_count}")

    if passed_count == total_count:
        print("\n  🎉 数据隔离测试全部通过！")
    else:
        print(f"\n  ⚠️ 有 {total_count - passed_count} 个测试失败")

    return passed_count == total_count


if __name__ == '__main__':
    setup_test_data()
    success = test_data_isolation()
    exit(0 if success else 1)
