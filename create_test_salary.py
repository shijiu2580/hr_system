"""创建待发放薪资测试数据"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_system.settings')
import django
django.setup()

from hr_management.models import SalaryRecord, Employee
from decimal import Decimal

# 创建一些待发放记录用于测试
employees = list(Employee.objects.filter(is_active=True)[:3])
count = 0
for emp in employees:
    # 创建2026年3月的记录（待发放）
    if not SalaryRecord.objects.filter(employee=emp, year=2026, month=3).exists():
        base = emp.salary or Decimal('8000')
        SalaryRecord.objects.create(
            employee=emp, year=2026, month=3,
            basic_salary=base,
            bonus=Decimal('1000'),
            overtime_pay=Decimal('500'),
            allowance=Decimal('300'),
            paid=False
        )
        count += 1
        print(f'创建: {emp.name} 2026年3月')

print(f'创建 {count} 条待发放记录')

# 查看待发放
pending = SalaryRecord.objects.filter(paid=False)
print(f'待发放总数: {pending.count()} 条')
for r in pending:
    print(f'  {r.year}年{r.month}月 - {r.employee.name}: ¥{r.net_salary}')
