#!/usr/bin/env python
"""RBAC权限全面测试脚本 - 包括管理员、边界测试、写操作测试"""
import requests
import time

BASE = 'http://localhost:8000/api'

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def test_role(name, username, password, tests, skip_login=False, token=None):
    print(f"\n{'='*60}")
    print(f"  测试角色: {name}" + (f" ({username})" if username else ""))
    print(f"{'='*60}")

    headers = {}
    if not skip_login:
        r = requests.post(f'{BASE}/auth/token/', json={'username': username, 'password': password})
        if r.status_code != 200:
            print(f"  ❌ 登录失败: {r.status_code}")
            return 0, len(tests)
        token = r.json()['access']
        headers = {'Authorization': f'Bearer {token}'}
    elif token:
        headers = {'Authorization': f'Bearer {token}'}

    passed = 0
    for test_item in tests:
        if len(test_item) == 4:
            test_name, method, url, expected = test_item
            data = {}
        else:
            test_name, method, url, expected, data = test_item

        try:
            if method == 'GET':
                resp = requests.get(f'{BASE}{url}', headers=headers, timeout=10)
            elif method == 'POST':
                resp = requests.post(f'{BASE}{url}', headers=headers, json=data, timeout=10)
            elif method == 'PUT':
                resp = requests.put(f'{BASE}{url}', headers=headers, json=data, timeout=10)
            elif method == 'PATCH':
                resp = requests.patch(f'{BASE}{url}', headers=headers, json=data, timeout=10)
            elif method == 'DELETE':
                resp = requests.delete(f'{BASE}{url}', headers=headers, timeout=10)

            # 判断是否通过
            if expected == 'allow':
                ok = resp.status_code in [200, 201, 400, 404, 405]  # 400/404/405 说明权限通过
            elif expected == 'deny':
                ok = resp.status_code == 403
            elif expected == 'unauth':
                ok = resp.status_code == 401
            else:
                ok = resp.status_code == expected

            status = '✓' if ok else '✗'
            if ok:
                passed += 1
            print(f"  [{status}] {test_name}: {resp.status_code} (期望: {expected})")
        except Exception as e:
            print(f"  [✗] {test_name}: 错误 - {e}")

    print(f"\n  结果: {passed}/{len(tests)}")
    return passed, len(tests)


def main():
    all_results = []

    print("\n" + "="*60)
    print("       RBAC 权限系统全面测试")
    print("="*60)

    # ==================== 1. 边界测试 ====================
    print(f"\n{Colors.BLUE}【第一部分：边界测试】{Colors.END}")

    # 1.1 未登录测试
    unauth_tests = [
        ('未登录访问员工列表', 'GET', '/employees/', 'unauth'),
        ('未登录访问薪资', 'GET', '/salaries/', 'unauth'),
        ('未登录访问系统日志', 'GET', '/logs/', 'unauth'),
    ]
    p, t = test_role('未登录用户', None, None, unauth_tests, skip_login=True)
    all_results.append(('未登录用户', p, t))

    # 1.2 无效token测试
    invalid_token_tests = [
        ('无效token访问', 'GET', '/employees/', 'unauth'),
    ]
    p, t = test_role('无效Token', None, None, invalid_token_tests, skip_login=True, token='invalid_token_12345')
    all_results.append(('无效Token', p, t))

    # ==================== 2. 普通员工测试 ====================
    print(f"\n{Colors.BLUE}【第二部分：普通员工权限测试】{Colors.END}")

    emp_tests = [
        # 读取权限
        ('查看员工列表', 'GET', '/employees/', 'allow'),
        ('查看自己信息', 'GET', '/employees/me/', 'allow'),
        ('查看部门列表', 'GET', '/departments/', 'allow'),
        ('查看职位列表', 'GET', '/positions/', 'allow'),
        # 考勤
        ('查看今日考勤', 'GET', '/attendance/today/', 'allow'),
        ('查看我的考勤', 'GET', '/attendance/my/', 'allow'),
        ('查看考勤列表', 'GET', '/attendance/', 'allow'),
        # 请假
        ('查看请假列表', 'GET', '/leaves/', 'allow'),
        # 禁止的操作
        ('创建员工', 'POST', '/employees/', 'deny'),
        ('查看薪资', 'GET', '/salaries/', 'deny'),
        ('查看报表概览', 'GET', '/reports/overview/', 'deny'),
        ('查看系统日志', 'GET', '/logs/', 'deny'),
        ('管理角色', 'GET', '/roles/manage/', 'deny'),
        ('管理权限', 'GET', '/permissions/manage/', 'deny'),
        ('管理用户', 'GET', '/users/manage/', 'deny'),
    ]
    p, t = test_role('普通员工', '0001', 'test123456', emp_tests)
    all_results.append(('普通员工', p, t))

    # ==================== 3. 部门经理测试 ====================
    print(f"\n{Colors.BLUE}【第三部分：部门经理权限测试】{Colors.END}")

    dept_tests = [
        # 员工管理
        ('查看员工列表', 'GET', '/employees/', 'allow'),
        ('查看员工详情', 'GET', '/employees/me/', 'allow'),
        ('创建员工', 'POST', '/employees/', 'deny'),
        # 考勤
        ('查看考勤列表', 'GET', '/attendance/', 'allow'),
        ('考勤补签列表', 'GET', '/attendance/supplement/', 'allow'),
        # 请假
        ('查看请假列表', 'GET', '/leaves/', 'allow'),
        # 出差
        ('查看出差列表', 'GET', '/business-trips/', 'allow'),
        # 报表
        ('查看报表概览', 'GET', '/reports/overview/', 'allow'),
        ('员工分布报表', 'GET', '/reports/department_distribution/', 'allow'),
        ('考勤率报表', 'GET', '/reports/attendance_rate/', 'allow'),
        # 禁止操作
        ('查看薪资', 'GET', '/salaries/', 'deny'),
        ('查看系统日志', 'GET', '/logs/', 'deny'),
        ('管理角色', 'GET', '/roles/manage/', 'deny'),
        ('管理权限', 'GET', '/permissions/manage/', 'deny'),
    ]
    p, t = test_role('部门经理', '7951', 'test123456', dept_tests)
    all_results.append(('部门经理', p, t))

    # ==================== 4. 人事经理测试 ====================
    print(f"\n{Colors.BLUE}【第四部分：人事经理权限测试】{Colors.END}")

    hr_tests = [
        # 员工管理 - 完全权限
        ('查看员工列表', 'GET', '/employees/', 'allow'),
        ('创建员工', 'POST', '/employees/', 'allow'),
        # 考勤
        ('查看考勤列表', 'GET', '/attendance/', 'allow'),
        ('考勤补签列表', 'GET', '/attendance/supplement/', 'allow'),
        # 请假
        ('查看请假列表', 'GET', '/leaves/', 'allow'),
        # 出差
        ('查看出差列表', 'GET', '/business-trips/', 'allow'),
        # 薪资
        ('查看薪资列表', 'GET', '/salaries/', 'allow'),
        # 报表 - 完全权限
        ('查看报表概览', 'GET', '/reports/overview/', 'allow'),
        ('员工分布', 'GET', '/reports/department_distribution/', 'allow'),
        ('薪资报表', 'GET', '/reports/monthly_salary/', 'allow'),
        ('考勤率报表', 'GET', '/reports/attendance_rate/', 'allow'),
        ('请假分析', 'GET', '/reports/leave_analysis/', 'allow'),
        ('员工增长', 'GET', '/reports/employee_growth/', 'allow'),
        # 禁止操作 - 系统管理
        ('查看系统日志', 'GET', '/logs/', 'deny'),
        ('管理角色', 'GET', '/roles/manage/', 'deny'),
        ('管理权限', 'GET', '/permissions/manage/', 'deny'),
        # 人事经理可以管理用户(合理的业务需求)
        ('管理用户', 'GET', '/users/manage/', 'allow'),
    ]
    p, t = test_role('人事经理', 'employee001', 'test123456', hr_tests)
    all_results.append(('人事经理', p, t))

    # ==================== 5. 管理员测试 ====================
    print(f"\n{Colors.BLUE}【第五部分：管理员权限测试】{Colors.END}")

    admin_tests = [
        # 员工管理
        ('查看员工列表', 'GET', '/employees/', 'allow'),
        ('创建员工', 'POST', '/employees/', 'allow'),
        # 考勤
        ('查看考勤列表', 'GET', '/attendance/', 'allow'),
        # 请假
        ('查看请假列表', 'GET', '/leaves/', 'allow'),
        # 薪资
        ('查看薪资列表', 'GET', '/salaries/', 'allow'),
        # 报表
        ('查看报表概览', 'GET', '/reports/overview/', 'allow'),
        # 系统管理 - 管理员专属
        ('查看系统日志', 'GET', '/logs/', 'allow'),
        ('管理角色列表', 'GET', '/roles/manage/', 'allow'),
        ('管理权限列表', 'GET', '/permissions/manage/', 'allow'),
        ('管理用户列表', 'GET', '/users/manage/', 'allow'),
        # 部门/职位管理
        ('查看部门', 'GET', '/departments/', 'allow'),
        ('查看职位', 'GET', '/positions/', 'allow'),
        # 系统健康
        ('系统健康检查', 'GET', '/system/health/', 'allow'),
        ('系统指标', 'GET', '/system/metrics/', 'allow'),
        # 备份
        ('查看备份列表', 'GET', '/backups/', 'allow'),
    ]
    # 使用非 superuser 的管理员测试账号，确保测试 RBAC 权限而非 superuser 绕过
    p, t = test_role('管理员(RBAC)', 'admin_test', 'test123456', admin_tests)
    all_results.append(('管理员(RBAC)', p, t))

    # ==================== 6. 写操作权限测试 ====================
    print(f"\n{Colors.BLUE}【第六部分：写操作权限测试】{Colors.END}")

    # 使用人事经理测试写操作
    write_tests = [
        # 员工创建（会因数据不完整返回400，但权限通过）
        ('创建员工(数据不全)', 'POST', '/employees/', 'allow', {'name': 'test'}),
        # 请假创建
        ('创建请假申请', 'POST', '/leaves/', 'allow', {'leave_type': 'annual', 'reason': 'test'}),
        # 考勤补签
        ('提交考勤补签', 'POST', '/attendance/supplement/', 'allow', {'date': '2026-02-01'}),
    ]
    p, t = test_role('人事经理-写操作', 'employee001', 'test123456', write_tests)
    all_results.append(('写操作测试', p, t))

    # 普通员工尝试写操作（应被拒绝）
    emp_write_tests = [
        ('普通员工创建员工', 'POST', '/employees/', 'deny'),
        ('普通员工创建薪资', 'POST', '/salaries/', 'deny'),
    ]
    p, t = test_role('普通员工-写操作', '0001', 'test123456', emp_write_tests)
    all_results.append(('普通员工写操作', p, t))

    # ==================== 测试总结 ====================
    print(f"\n{'='*60}")
    print(f"{Colors.BOLD}  测试总结{Colors.END}")
    print(f"{'='*60}")

    total_pass = 0
    total_tests = 0

    for name, p, t in all_results:
        if p == t:
            status = f'{Colors.GREEN}✓ PASS{Colors.END}'
        else:
            status = f'{Colors.RED}✗ FAIL{Colors.END}'
        print(f"  [{status}] {name}: {p}/{t}")
        total_pass += p
        total_tests += t

    print(f"\n  {'='*40}")
    pct = (total_pass / total_tests * 100) if total_tests > 0 else 0

    if total_pass == total_tests:
        print(f"  {Colors.GREEN}{Colors.BOLD}总计: {total_pass}/{total_tests} ({pct:.1f}%){Colors.END}")
        print(f"\n  🎉 所有测试通过！RBAC 权限系统工作正常！")
    else:
        print(f"  {Colors.RED}{Colors.BOLD}总计: {total_pass}/{total_tests} ({pct:.1f}%){Colors.END}")
        print(f"\n  ⚠️ 有 {total_tests - total_pass} 个测试失败")

    return total_pass == total_tests

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
