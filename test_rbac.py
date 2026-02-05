#!/usr/bin/env python
"""RBAC权限综合测试脚本"""
import requests

BASE = 'http://localhost:8000/api'

def test_role(name, username, password, tests):
    print(f"\n{'='*50}")
    print(f"  测试角色: {name} ({username})")
    print(f"{'='*50}")
    r = requests.post(f'{BASE}/auth/token/', json={'username': username, 'password': password})
    if r.status_code != 200:
        print(f"  登录失败: {r.status_code}")
        return 0, len(tests)
    token = r.json()['access']
    headers = {'Authorization': f'Bearer {token}'}

    passed = 0
    for test_name, method, url, expected in tests:
        if method == 'GET':
            resp = requests.get(f'{BASE}{url}', headers=headers)
        elif method == 'POST':
            resp = requests.post(f'{BASE}{url}', headers=headers, json={})
        elif method == 'DELETE':
            resp = requests.delete(f'{BASE}{url}', headers=headers)

        # 200/201 = 允许, 403 = 禁止, 400 = 参数错误(但权限通过), 404 = 资源不存在(但权限通过)
        if expected == 'allow':
            ok = resp.status_code in [200, 201, 400, 404]
        else:  # deny
            ok = resp.status_code == 403

        status = '✓' if ok else '✗'
        if ok:
            passed += 1
        print(f"  [{status}] {test_name}: {resp.status_code} (期望: {expected})")

    print(f"\n  结果: {passed}/{len(tests)}")
    return passed, len(tests)

def main():
    all_results = []

    # ========== 普通员工测试 ==========
    emp_tests = [
        # 基本资源访问
        ('查看员工列表', 'GET', '/employees/', 'allow'),
        ('查看自己信息', 'GET', '/employees/me/', 'allow'),
        ('创建员工', 'POST', '/employees/', 'deny'),
        # 考勤
        ('考勤打卡', 'GET', '/attendance/today/', 'allow'),
        ('查看我的考勤', 'GET', '/attendance/my/', 'allow'),
        ('查看所有考勤', 'GET', '/attendance/', 'allow'),
        # 请假
        ('查看请假', 'GET', '/leaves/', 'allow'),
        # 薪资
        ('查看薪资', 'GET', '/salaries/', 'deny'),
        # 报表
        ('查看报表', 'GET', '/reports/overview/', 'deny'),
        # 系统日志
        ('查看系统日志', 'GET', '/logs/', 'deny'),
        # 角色管理
        ('查看角色列表', 'GET', '/roles/manage/', 'deny'),
    ]
    p, t = test_role('普通员工', '0001', 'test123456', emp_tests)
    all_results.append(('普通员工', p, t))

    # ========== 部门经理测试 ==========
    dept_tests = [
        # 员工管理
        ('查看员工列表', 'GET', '/employees/', 'allow'),
        ('查看员工详情', 'GET', '/employees/me/', 'allow'),
        ('创建员工', 'POST', '/employees/', 'deny'),
        # 考勤
        ('查看考勤', 'GET', '/attendance/', 'allow'),
        # 请假
        ('查看请假', 'GET', '/leaves/', 'allow'),
        # 薪资
        ('查看薪资', 'GET', '/salaries/', 'deny'),
        # 报表
        ('查看报表概览', 'GET', '/reports/overview/', 'allow'),
        ('员工分布', 'GET', '/reports/department_distribution/', 'allow'),
        # 系统日志
        ('查看系统日志', 'GET', '/logs/', 'deny'),
        # 角色管理
        ('管理角色', 'GET', '/roles/manage/', 'deny'),
    ]
    p, t = test_role('部门经理', '7951', 'test123456', dept_tests)
    all_results.append(('部门经理', p, t))

    # ========== 人事经理测试 ==========
    hr_tests = [
        # 员工管理
        ('查看员工列表', 'GET', '/employees/', 'allow'),
        ('创建员工', 'POST', '/employees/', 'allow'),
        # 考勤
        ('查看考勤', 'GET', '/attendance/', 'allow'),
        # 请假
        ('查看请假', 'GET', '/leaves/', 'allow'),
        # 薪资
        ('查看薪资', 'GET', '/salaries/', 'allow'),
        # 报表
        ('查看报表概览', 'GET', '/reports/overview/', 'allow'),
        ('员工分布', 'GET', '/reports/department_distribution/', 'allow'),
        ('薪资报表', 'GET', '/reports/monthly_salary/', 'allow'),
        # 系统日志 (人事经理没有系统日志权限,这是管理员专有)
        ('查看系统日志', 'GET', '/logs/', 'deny'),
        # 角色管理 (人事经理应该没权限管角色)
        ('管理角色', 'GET', '/roles/manage/', 'deny'),
    ]
    p, t = test_role('人事经理', 'employee001', 'test123456', hr_tests)
    all_results.append(('人事经理', p, t))

    # 总结
    print(f"\n{'='*50}")
    print("  测试总结")
    print(f"{'='*50}")
    total_pass = 0
    total_tests = 0
    for name, p, t in all_results:
        status = '✓ PASS' if p == t else '✗ FAIL'
        print(f"  [{status}] {name}: {p}/{t}")
        total_pass += p
        total_tests += t

    print(f"\n  总计: {total_pass}/{total_tests}")
    if total_pass == total_tests:
        print("\n  🎉 所有测试通过！RBAC 权限系统工作正常！")
    else:
        print(f"\n  ⚠️ 有 {total_tests - total_pass} 个测试失败")

if __name__ == '__main__':
    main()
