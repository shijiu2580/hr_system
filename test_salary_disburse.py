"""测试薪资发放功能"""
import requests
import json

BASE = 'http://127.0.0.1:8000/api'

def test_salary_disburse():
    # 使用 HR Manager 登录
    print("=== 登录 HR Manager ===")
    login_resp = requests.post(f'{BASE}/auth/token/', json={'username': 'employee001', 'password': 'test123456'})
    if login_resp.status_code != 200:
        print('登录失败:', login_resp.text)
        return
    resp_data = login_resp.json()
    token = resp_data.get('data', {}).get('access') or resp_data.get('access')
    headers = {'Authorization': f'Bearer {token}'}
    print("登录成功!")

    print()
    print('=== 查看待发放薪资 ===')
    resp = requests.get(f'{BASE}/salaries/pending/', headers=headers)
    print(f'状态码: {resp.status_code}')
    data = resp.json()
    if data.get('success'):
        pending = data['data']
        if pending:
            for p in pending:
                print(f"  {p['year']}年{p['month']}月: {p['count']}人, 总计 ¥{p['total']}")
        else:
            print("  没有待发放的薪资记录")
    else:
        print('错误:', data.get('message'))

    print()
    print('=== 发放2026年3月薪资 ===')
    resp = requests.post(f'{BASE}/salaries/disburse/',
        headers=headers,
        json={'year': 2026, 'month': 3})
