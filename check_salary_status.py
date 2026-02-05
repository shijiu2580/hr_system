"""查看薪资发放状态"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_system.settings')
import django
django.setup()

from hr_management.models import SalaryRecord
from django.db.models import Sum, Count

print('=== 薪资发放状态汇总 ===')
summary = SalaryRecord.objects.values('year', 'month', 'paid').annotate(
    count=Count('id'),
    total=Sum('net_salary')
).order_by('-year', '-month', 'paid')

for s in summary:
    status = '✓ 已发放' if s['paid'] else '○ 待发放'
    print(f"{s['year']}年{s['month']:02d}月 {status}: {s['count']:2d}人, ¥{s['total']:,.2f}")

print()
print('=== 定时任务配置说明 ===')
print('自动发薪任务已配置:')
print('  - 每月5号自动发放上月薪资')
print('  - 可通过 settings.SALARY_DISBURSE_DAY 修改发薪日')
print('  - 发放后自动通知员工')
