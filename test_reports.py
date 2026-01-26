import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_system.settings')
django.setup()

from hr_management.models import Attendance, Employee, Department, LeaveRequest, SalaryRecord, Position
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import timedelta
from collections import defaultdict

print('=== 测试各报表API的数据逻辑 ===\n')

# 1. 部门分布
print('=== 1. 部门人员分布 ===')
dept_stats = Department.objects.annotate(
    employee_count=Count('employee', filter=Q(employee__is_active=True))
).values('id', 'name', 'employee_count').order_by('-employee_count')
for dept in dept_stats:
    if dept['employee_count'] > 0:
        print(f"  {dept['name']}: {dept['employee_count']}人")
no_dept = Employee.objects.filter(is_active=True, department__isnull=True).count()
if no_dept > 0:
    print(f"  未分配部门: {no_dept}人")

# 2. 考勤统计
print('\n=== 2. 考勤结构 (30天) ===')
today = timezone.now().date()
start_date = today - timedelta(days=29)
qs = Attendance.objects.filter(date__gte=start_date, date__lte=today)

status_mapping = {
    'check_in': 'normal',
    'check_out': 'normal',
    'late': 'late',
    'early_leave': 'early_leave',
    'absent': 'absent',
    'leave': 'leave',
}

stats = {
    'normal': {'label': '正常出勤', 'count': 0},
    'late': {'label': '迟到', 'count': 0},
    'early_leave': {'label': '早退', 'count': 0},
    'absent': {'label': '缺勤', 'count': 0},
    'leave': {'label': '请假', 'count': 0},
}

for row in qs.values('attendance_type').annotate(cnt=Count('id')):
    t = row['attendance_type']
    mapped = status_mapping.get(t, t)
    if mapped in stats:
        stats[mapped]['count'] += row['cnt']

total = sum(s['count'] for s in stats.values())
present_count = stats['normal']['count'] + stats['late']['count'] + stats['early_leave']['count']
attendance_rate = round(present_count / total * 100, 1) if total > 0 else 0

print(f"  总记录: {total}")
for key, s in stats.items():
    if s['count'] > 0:
        print(f"  {s['label']}: {s['count']}")
print(f"  出勤率: {attendance_rate}%")

# 3. 月度薪资
print('\n=== 3. 月度薪资趋势 (12个月) ===')
end_index = today.year * 12 + (today.month - 1) - 1  # 不含当月
for i in range(11, -1, -1):
    target_index = end_index - i
    y = target_index // 12
    m = (target_index % 12) + 1
    stats_sal = SalaryRecord.objects.filter(year=y, month=m).aggregate(total=Sum('net_salary'), cnt=Count('id'))
    total = stats_sal['total'] or 0
    if total > 0:
        print(f"  {y}-{str(m).zfill(2)}: ￥{float(total):.0f} ({stats_sal['cnt']}人)")

# 4. 请假分析
print('\n=== 4. 请假类型分析 (90天) ===')
since = timezone.now() - timedelta(days=90)
leave_qs = LeaveRequest.objects.filter(created_at__gte=since)
for t, label in LeaveRequest.LEAVE_TYPE_CHOICES:
    count = leave_qs.filter(leave_type=t).count()
    if count > 0:
        print(f"  {label}: {count}次")

# 5. 职位分布
print('\n=== 5. 职位分布 Top 15 ===')
pos_stats = Position.objects.annotate(
    employee_count=Count('employee', filter=Q(employee__is_active=True))
).values('id', 'name', 'employee_count').order_by('-employee_count')[:15]
for pos in pos_stats:
    if pos['employee_count'] > 0:
        print(f"  {pos['name']}: {pos['employee_count']}人")

# 6. 员工增长
print('\n=== 6. 员工规模变化 (12个月) ===')
from django.db.models.functions import TruncMonth
for i in range(11, -1, -1):
    target_index = today.year * 12 + today.month - 1 - i
    target_year = target_index // 12
    target_month = (target_index % 12) + 1

    if target_month == 12:
        month_end = today.replace(year=target_year, month=12, day=31)
    else:
        from datetime import date
        next_m = target_month + 1
        next_y = target_year
        if next_m > 12:
            next_m = 1
            next_y += 1
        month_end = date(next_y, next_m, 1) - timedelta(days=1)

    if target_year == today.year and target_month == today.month:
        month_end = today

    total_emp = Employee.objects.filter(hire_date__lte=month_end).count()
    active_emp = Employee.objects.filter(hire_date__lte=month_end, is_active=True).count()

    label = f"{target_year}-{str(target_month).zfill(2)}"
    print(f"  {label}: 总数={total_emp}, 在职={active_emp}")

# 7. 总览数据
print('\n=== 7. 报表总览 ===')
this_month_start = today.replace(day=1)
last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)

emp_total = Employee.objects.count()
emp_active = Employee.objects.filter(is_active=True).count()
emp_pending = Employee.objects.filter(onboard_status='pending').count()
emp_new_this_month = Employee.objects.filter(hire_date__gte=this_month_start).count()

attendance_this_month = Attendance.objects.filter(date__gte=this_month_start, date__lte=today).count()
normal_att = Attendance.objects.filter(
    date__gte=this_month_start, date__lte=today,
    attendance_type__in=['check_in', 'check_out', 'late', 'early_leave']
).count()
late_this_month = Attendance.objects.filter(
    date__gte=this_month_start, date__lte=today,
    attendance_type='late'
).count()
rate = round(normal_att / attendance_this_month * 100, 1) if attendance_this_month > 0 else 0

leave_this_month = LeaveRequest.objects.filter(created_at__date__gte=this_month_start).count()
leave_pending = LeaveRequest.objects.filter(status='pending').count()

print(f"  员工: 总数={emp_total}, 在职={emp_active}, 待入职={emp_pending}, 本月新入职={emp_new_this_month}")
print(f"  考勤: 本月打卡={attendance_this_month}, 迟到={late_this_month}, 出勤率={rate}%")
print(f"  请假: 本月={leave_this_month}, 待审批={leave_pending}")
