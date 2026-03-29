"""大数据报表 API 视图"""
from rest_framework import permissions, views
from rest_framework.response import Response
from django.core.cache import cache
from django.utils import timezone
from django.db.models import Sum, Count, Avg, Q
from django.db.models.functions import TruncMonth
from datetime import timedelta
from decimal import Decimal

from ...models import Employee, Department, Position, Attendance, LeaveRequest, SalaryRecord
from ...permissions import HasRBACPermission
from ...rbac import Permissions
from ...services import CacheKeys


ATTENDANCE_COLORS = {
    'normal': '#22c55e',
    'late': '#f97316',
    'early_leave': '#eab308',
    'absent': '#ef4444',
    'leave': '#a855f7',
}


def build_department_distribution_data():
    departments = list(Department.objects.values('id', 'name', 'parent_id'))
    labels = []
    values = []
    colors = [
        '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
        '#06b6d4', '#ec4899', '#84cc16', '#f97316', '#6366f1'
    ]

    if not departments:
        return {'detail': 'ok', 'labels': [], 'values': [], 'colors': [], 'total': 0}

    children_map = {}
    names = {}
    top_level_ids = []
    for dept in departments:
        dept_id = dept['id']
        names[dept_id] = dept['name']
        parent_id = dept['parent_id']
        children_map.setdefault(parent_id, []).append(dept_id)
        if parent_id is None:
            top_level_ids.append(dept_id)

    active_counts = {
        row['department_id']: row['cnt']
        for row in Employee.objects.filter(is_active=True, department_id__isnull=False)
        .values('department_id').annotate(cnt=Count('id'))
    }

    def count_department_tree(root_id):
        total = 0
        stack = [root_id]
        while stack:
            current_id = stack.pop()
            total += active_counts.get(current_id, 0)
            stack.extend(children_map.get(current_id, []))
        return total

    dept_data = []
    for dept_id in top_level_ids:
        count = count_department_tree(dept_id)
        if count > 0:
            dept_data.append({'name': names[dept_id], 'count': count})

    dept_data.sort(key=lambda item: item['count'], reverse=True)
    labels.extend(item['name'] for item in dept_data)
    values.extend(item['count'] for item in dept_data)

    no_dept_count = Employee.objects.filter(is_active=True, department__isnull=True).count()
    if no_dept_count > 0:
        labels.append('未分配部门')
        values.append(no_dept_count)

    return {
        'detail': 'ok',
        'labels': labels,
        'values': values,
        'colors': colors[:len(labels)],
        'total': sum(values),
    }


def build_monthly_salary_data(months=12, include_current=False):
    months = max(1, min(int(months), 24))
    today = timezone.localdate()
    end_index = today.year * 12 + (today.month - 1)
    if not include_current:
        end_index -= 1

    results = []
    for i in range(months - 1, -1, -1):
        target_index = end_index - i
        year = target_index // 12
        month = (target_index % 12) + 1
        stats = SalaryRecord.objects.filter(year=year, month=month).aggregate(
            total=Sum('net_salary'),
            count=Count('id'),
            avg=Avg('net_salary'),
        )
        results.append({
            'year': year,
            'month': month,
            'label': f'{year}-{str(month).zfill(2)}',
            'total': float(stats['total'] or 0),
            'count': stats['count'] or 0,
            'avg': float(stats['avg'] or 0),
        })

    return {
        'detail': 'ok',
        'months': months,
        'include_current': include_current,
        'labels': [item['label'] for item in results],
        'totals': [item['total'] for item in results],
        'counts': [item['count'] for item in results],
        'records': results,
    }


def build_attendance_rate_data(days=30):
    days = max(1, min(int(days), 90))
    today = timezone.localdate()
    start_date = today - timedelta(days=days - 1)
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
        mapped = status_mapping.get(row['attendance_type'], row['attendance_type'])
        if mapped in stats:
            stats[mapped]['count'] += row['cnt']

    total = sum(item['count'] for item in stats.values())
    present_count = stats['normal']['count'] + stats['late']['count'] + stats['early_leave']['count']
    attendance_rate = round(present_count / total * 100, 1) if total > 0 else 0

    labels = []
    values = []
    colors = []
    for key, item in stats.items():
        if item['count'] > 0:
            labels.append(item['label'])
            values.append(item['count'])
            colors.append(ATTENDANCE_COLORS[key])

    empty = total == 0
    if empty:
        labels = ['暂无考勤数据']
        values = [1]
        colors = ['#e5e7eb']

    return {
        'detail': 'ok',
        'days': days,
        'labels': labels,
        'values': values,
        'colors': colors,
        'total': total,
        'attendance_rate': attendance_rate,
        'stats': stats,
        'empty': empty,
    }


def build_leave_analysis_data(days=90):
    days = max(1, min(int(days), 365))
    since = timezone.now() - timedelta(days=days)
    qs = LeaveRequest.objects.filter(created_at__gte=since)

    type_stats = {leave_type: {'label': label, 'count': 0, 'days': 0} for leave_type, label in LeaveRequest.LEAVE_TYPE_CHOICES}
    for row in qs.values('leave_type').annotate(cnt=Count('id'), total_days=Sum('days')):
        leave_type = row['leave_type']
        if leave_type in type_stats:
            type_stats[leave_type]['count'] = row['cnt']
            type_stats[leave_type]['days'] = row['total_days'] or 0

    status_stats = {status: {'label': label, 'count': 0} for status, label in LeaveRequest.STATUS_CHOICES}
    for row in qs.values('status').annotate(cnt=Count('id')):
        status = row['status']
        if status in status_stats:
            status_stats[status]['count'] = row['cnt']

    monthly = qs.annotate(month=TruncMonth('created_at')).values('month').annotate(cnt=Count('id')).order_by('month')
    trend_labels = []
    trend_values = []
    for row in monthly:
        if row['month']:
            trend_labels.append(row['month'].strftime('%Y-%m'))
            trend_values.append(row['cnt'])

    return {
        'detail': 'ok',
        'days': days,
        'type_stats': type_stats,
        'status_stats': status_stats,
        'trend': {'labels': trend_labels, 'values': trend_values},
        'total': qs.count(),
    }


def build_employee_growth_data(months=12):
    months = max(1, min(int(months), 24))
    today = timezone.localdate()
    results = []
    for i in range(months - 1, -1, -1):
        target_index = today.year * 12 + today.month - 1 - i
        target_year = target_index // 12
        target_month = (target_index % 12) + 1
        if target_month == 12:
            month_end_date = today.replace(year=target_year, month=12, day=31)
        else:
            from datetime import date
            next_month = target_month + 1
            next_year = target_year
            if next_month > 12:
                next_month = 1
                next_year += 1
            month_end_date = date(next_year, next_month, 1) - timedelta(days=1)

        if target_year == today.year and target_month == today.month:
            month_end_date = today

        from datetime import datetime
        month_end_dt = datetime.combine(month_end_date, datetime.max.time())
        if timezone.is_aware(timezone.now()):
            month_end_dt = timezone.make_aware(month_end_dt)

        total = Employee.objects.filter(created_at__lte=month_end_dt).count()
        active = Employee.objects.filter(created_at__lte=month_end_dt, is_active=True).count()
        results.append({'date': f'{target_year}-{str(target_month).zfill(2)}', 'total': total, 'active': active})

    return {
        'detail': 'ok',
        'months': months,
        'labels': [item['date'] for item in results],
        'total_series': [item['total'] for item in results],
        'active_series': [item['active'] for item in results],
    }


def build_position_distribution_data():
    pos_stats = Position.objects.annotate(
        employee_count=Count('employee', filter=Q(employee__is_active=True))
    ).values('name', 'employee_count').order_by('-employee_count')[:15]

    labels = []
    values = []
    for pos in pos_stats:
        if pos['employee_count'] > 0:
            labels.append(pos['name'])
            values.append(pos['employee_count'])

    return {'detail': 'ok', 'labels': labels, 'values': values, 'total': sum(values)}


def build_report_overview_data():
    today = timezone.localdate()
    this_month_start = today.replace(day=1)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    end_index = today.year * 12 + (today.month - 1)
    payroll_index = end_index - 1
    prev_payroll_index = end_index - 2
    payroll_year = payroll_index // 12
    payroll_month = (payroll_index % 12) + 1
    prev_payroll_year = prev_payroll_index // 12
    prev_payroll_month = (prev_payroll_index % 12) + 1

    emp_total = Employee.objects.count()
    emp_active = Employee.objects.filter(is_active=True).count()
    emp_pending = Employee.objects.filter(onboard_status='pending').count()
    emp_new_this_month = Employee.objects.filter(hire_date__gte=this_month_start).count()
    emp_new_last_month = Employee.objects.filter(hire_date__gte=last_month_start, hire_date__lt=this_month_start).count()

    salary_this_month = SalaryRecord.objects.filter(year=payroll_year, month=payroll_month, paid=True).aggregate(total=Sum('net_salary'))['total'] or Decimal('0')
    salary_last_month = SalaryRecord.objects.filter(year=prev_payroll_year, month=prev_payroll_month, paid=True).aggregate(total=Sum('net_salary'))['total'] or Decimal('0')

    attendance_this_month = Attendance.objects.filter(date__gte=this_month_start, date__lte=today).count()
    normal_attendance = Attendance.objects.filter(
        date__gte=this_month_start,
        date__lte=today,
        attendance_type__in=['check_in', 'check_out', 'late', 'early_leave'],
    ).count()
    late_this_month = Attendance.objects.filter(date__gte=this_month_start, date__lte=today, attendance_type='late').count()
    attendance_rate = round(normal_attendance / attendance_this_month * 100, 1) if attendance_this_month > 0 else 0

    leave_this_month = LeaveRequest.objects.filter(created_at__date__gte=this_month_start).count()
    leave_pending = LeaveRequest.objects.filter(status='pending').count()

    return {
        'detail': 'ok',
        'timestamp': timezone.now().isoformat(),
        'employees': {
            'total': emp_total,
            'active': emp_active,
            'pending': emp_pending,
            'new_this_month': emp_new_this_month,
            'new_last_month': emp_new_last_month,
            'growth': emp_new_this_month - emp_new_last_month,
        },
        'salary': {
            'this_month': float(salary_this_month),
            'last_month': float(salary_last_month),
            'change': float(salary_this_month - salary_last_month),
        },
        'attendance': {
            'this_month': attendance_this_month,
            'late_this_month': late_this_month,
            'rate': attendance_rate,
        },
        'leaves': {
            'this_month': leave_this_month,
            'pending': leave_pending,
        },
    }


def build_report_snapshot_data():
    return {
        'detail': 'ok',
        'timestamp': timezone.now().isoformat(),
        'overview': build_report_overview_data(),
        'department_distribution': build_department_distribution_data(),
        'monthly_salary': build_monthly_salary_data(months=12),
        'attendance_rate': build_attendance_rate_data(days=30),
        'leave_analysis': build_leave_analysis_data(days=90),
        'employee_growth': build_employee_growth_data(months=12),
        'position_distribution': build_position_distribution_data(),
    }


class DepartmentDistributionAPIView(views.APIView):
    """部门人员分布统计 - 只统计顶级部门，子部门员工归入父部门"""
    permission_classes = [permissions.IsAuthenticated, HasRBACPermission]
    rbac_perms = [Permissions.REPORT_EMPLOYEE]

    def get(self, request):
        return Response(build_department_distribution_data())


class MonthlySalaryAPIView(views.APIView):
    """月度薪资支出统计"""
    permission_classes = [permissions.IsAuthenticated, HasRBACPermission]
    rbac_perms = [Permissions.REPORT_SALARY]

    def get(self, request):
        include_current = str(request.query_params.get('include_current', '')).lower() in ('1', 'true', 'yes', 'y')
        return Response(build_monthly_salary_data(request.query_params.get('months', 12), include_current))


class AttendanceRateAPIView(views.APIView):
    """考勤率统计"""
    permission_classes = [permissions.IsAuthenticated, HasRBACPermission]
    rbac_perms = [Permissions.REPORT_ATTENDANCE]

    def get(self, request):
        return Response(build_attendance_rate_data(request.query_params.get('days', 30)))


class LeaveAnalysisAPIView(views.APIView):
    """请假分析统计"""
    permission_classes = [permissions.IsAuthenticated, HasRBACPermission]
    rbac_perms = [Permissions.REPORT_LEAVE]

    def get(self, request):
        return Response(build_leave_analysis_data(request.query_params.get('days', 90)))


class EmployeeGrowthAPIView(views.APIView):
    """员工增长趋势"""
    permission_classes = [permissions.IsAuthenticated, HasRBACPermission]
    rbac_perms = [Permissions.REPORT_EMPLOYEE]

    def get(self, request):
        return Response(build_employee_growth_data(request.query_params.get('months', 12)))


class PositionDistributionAPIView(views.APIView):
    """职位分布统计"""
    permission_classes = [permissions.IsAuthenticated, HasRBACPermission]
    rbac_perms = [Permissions.REPORT_EMPLOYEE]

    def get(self, request):
        return Response(build_position_distribution_data())


class ReportOverviewAPIView(views.APIView):
    """报表总览数据"""
    permission_classes = [permissions.IsAuthenticated, HasRBACPermission]
    rbac_perms_any = [Permissions.REPORT_EMPLOYEE, Permissions.REPORT_SALARY, Permissions.REPORT_ATTENDANCE, Permissions.REPORT_LEAVE]

    def get(self, request):
        cached_data = cache.get(CacheKeys.REPORT_OVERVIEW)
        if cached_data:
            return Response(cached_data)

        response_data = build_report_overview_data()
        cache.set(CacheKeys.REPORT_OVERVIEW, response_data, CacheKeys.TIMEOUT_SHORT)
        return Response(response_data)


class ReportSnapshotAPIView(views.APIView):
    """报表页快照接口，减少前端多次往返请求。"""
    permission_classes = [permissions.IsAuthenticated, HasRBACPermission]
    rbac_perms_any = [Permissions.REPORT_EMPLOYEE, Permissions.REPORT_SALARY, Permissions.REPORT_ATTENDANCE, Permissions.REPORT_LEAVE]

    def get(self, request):
        cached_data = cache.get(CacheKeys.REPORT_SNAPSHOT)
        if cached_data:
            return Response(cached_data)

        response_data = build_report_snapshot_data()
        cache.set(CacheKeys.REPORT_SNAPSHOT, response_data, CacheKeys.TIMEOUT_SHORT)
        return Response(response_data)
