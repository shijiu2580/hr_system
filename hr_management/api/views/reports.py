"""大数据报表 API 视图"""
from rest_framework import permissions, views
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Sum, Count, Avg, Q
from django.db.models.functions import TruncMonth, TruncDate
from datetime import timedelta
from decimal import Decimal

from ...models import Employee, Department, Position, Attendance, LeaveRequest, SalaryRecord
from ...permissions import HasRBACPermission
from ...rbac import Permissions


class DepartmentDistributionAPIView(views.APIView):
    """部门人员分布统计 - 只统计顶级部门，子部门员工归入父部门"""
    permission_classes = [permissions.IsAuthenticated, HasRBACPermission]
    rbac_perms = [Permissions.REPORT_EMPLOYEE]

    def _get_all_descendant_ids(self, dept):
        """递归获取部门及其所有子部门的ID列表"""
        ids = [dept.id]
        for child in dept.children.all():
            ids.extend(self._get_all_descendant_ids(child))
        return ids

    def get(self, request):
        # 只统计顶级部门（parent为空），子部门员工数累加到父部门
        top_level_depts = Department.objects.filter(parent__isnull=True)

        labels = []
        values = []
        colors = [
            '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
            '#06b6d4', '#ec4899', '#84cc16', '#f97316', '#6366f1'
        ]

        dept_data = []
        for dept in top_level_depts:
            # 获取该部门及所有子部门的ID
            all_dept_ids = self._get_all_descendant_ids(dept)
            # 统计这些部门的所有在职员工
            count = Employee.objects.filter(
                is_active=True,
                department_id__in=all_dept_ids
            ).count()
            if count > 0:
                dept_data.append({'name': dept.name, 'count': count})

        # 按人数降序排列
        dept_data.sort(key=lambda x: x['count'], reverse=True)

        for item in dept_data:
            labels.append(item['name'])
            values.append(item['count'])

        # 统计未分配部门的员工
        no_dept_count = Employee.objects.filter(is_active=True, department__isnull=True).count()
        if no_dept_count > 0:
            labels.append('未分配部门')
            values.append(no_dept_count)

        return Response({
            'detail': 'ok',
            'labels': labels,
            'values': values,
            'colors': colors[:len(labels)],
            'total': sum(values)
        })


class MonthlySalaryAPIView(views.APIView):
    """月度薪资支出统计"""
    permission_classes = [permissions.IsAuthenticated, HasRBACPermission]
    rbac_perms = [Permissions.REPORT_SALARY]

    def get(self, request):
        months = int(request.query_params.get('months', 12))
        months = max(1, min(months, 24))
        include_current = str(request.query_params.get('include_current', '')).lower() in ('1', 'true', 'yes', 'y')

        # 获取最近N个月的薪资数据
        today = timezone.now().date()
        # 默认不包含当月（当月工资通常尚未生成/发放，避免趋势图末尾出现 0 断崖）
        end_index = today.year * 12 + (today.month - 1)
        if not include_current:
            end_index -= 1

        results = []
        for i in range(months - 1, -1, -1):
            target_index = end_index - i
            y = target_index // 12
            m = (target_index % 12) + 1

            stats = SalaryRecord.objects.filter(year=y, month=m).aggregate(
                total=Sum('net_salary'),
                count=Count('id'),
                avg=Avg('net_salary')
            )

            results.append({
                'year': y,
                'month': m,
                'label': f'{y}-{str(m).zfill(2)}',
                'total': float(stats['total'] or 0),
                'count': stats['count'] or 0,
                'avg': float(stats['avg'] or 0)
            })

        labels = [r['label'] for r in results]
        totals = [r['total'] for r in results]
        counts = [r['count'] for r in results]

        return Response({
            'detail': 'ok',
            'months': months,
            'include_current': include_current,
            'labels': labels,
            'totals': totals,
            'counts': counts,
            'records': results
        })


class AttendanceRateAPIView(views.APIView):
    """考勤率统计"""
    permission_classes = [permissions.IsAuthenticated, HasRBACPermission]
    rbac_perms = [Permissions.REPORT_ATTENDANCE]

    def get(self, request):
        days = int(request.query_params.get('days', 30))
        days = max(1, min(days, 90))

        today = timezone.now().date()
        start_date = today - timedelta(days=days - 1)

        # 统计各类型考勤
        qs = Attendance.objects.filter(date__gte=start_date, date__lte=today)

        # 考勤状态映射：将 check_in/check_out 视为"正常出勤"
        status_mapping = {
            'check_in': 'normal',
            'check_out': 'normal',
            'late': 'late',
            'early_leave': 'early_leave',
            'absent': 'absent',
            'leave': 'leave',
        }

        # 统计用的分类
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

        # 计算出勤率（正常+迟到+早退）/ 总数
        present_count = stats['normal']['count'] + stats['late']['count'] + stats['early_leave']['count']
        attendance_rate = 0
        if total > 0:
            attendance_rate = round(present_count / total * 100, 1)

        # 只返回有数据的项
        labels = []
        values = []
        colors = ['#22c55e', '#f97316', '#eab308', '#ef4444', '#a855f7']

        for i, (key, s) in enumerate(stats.items()):
            if s['count'] > 0:
                labels.append(s['label'])
                values.append(s['count'])

        return Response({
            'detail': 'ok',
            'days': days,
            'labels': labels,
            'values': values,
            'total': total,
            'attendance_rate': attendance_rate,
            'stats': stats
        })


class LeaveAnalysisAPIView(views.APIView):
    """请假分析统计"""
    permission_classes = [permissions.IsAuthenticated, HasRBACPermission]
    rbac_perms = [Permissions.REPORT_LEAVE]

    def get(self, request):
        days = int(request.query_params.get('days', 90))
        days = max(1, min(days, 365))

        since = timezone.now() - timedelta(days=days)
        qs = LeaveRequest.objects.filter(created_at__gte=since)

        # 按类型统计
        type_stats = {}
        for t, label in LeaveRequest.LEAVE_TYPE_CHOICES:
            type_stats[t] = {'label': label, 'count': 0, 'days': 0}

        for row in qs.values('leave_type').annotate(
            cnt=Count('id'),
            total_days=Sum('days')
        ):
            t = row['leave_type']
            if t in type_stats:
                type_stats[t]['count'] = row['cnt']
                type_stats[t]['days'] = row['total_days'] or 0

        # 按状态统计
        status_stats = {}
        for s, label in LeaveRequest.STATUS_CHOICES:
            status_stats[s] = {'label': label, 'count': 0}

        for row in qs.values('status').annotate(cnt=Count('id')):
            s = row['status']
            if s in status_stats:
                status_stats[s]['count'] = row['cnt']

        # 按月趋势
        monthly = qs.annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(cnt=Count('id')).order_by('month')

        trend_labels = []
        trend_values = []
        for row in monthly:
            if row['month']:
                trend_labels.append(row['month'].strftime('%Y-%m'))
                trend_values.append(row['cnt'])

        return Response({
            'detail': 'ok',
            'days': days,
            'type_stats': type_stats,
            'status_stats': status_stats,
            'trend': {'labels': trend_labels, 'values': trend_values},
            'total': qs.count()
        })


class EmployeeGrowthAPIView(views.APIView):
    """员工增长趋势"""
    permission_classes = [permissions.IsAuthenticated, HasRBACPermission]
    rbac_perms = [Permissions.REPORT_EMPLOYEE]

    def get(self, request):
        months = int(request.query_params.get('months', 12))
        months = max(1, min(months, 24))

        today = timezone.now().date()

        results = []
        # 按月份精确计算，从当前月往前推
        for i in range(months - 1, -1, -1):
            # 计算目标月份
            target_index = today.year * 12 + today.month - 1 - i
            target_year = target_index // 12
            target_month = (target_index % 12) + 1

            # 月末日期时间（包含整天）
            if target_month == 12:
                month_end_date = today.replace(year=target_year, month=12, day=31)
            else:
                from datetime import date
                next_m = target_month + 1
                next_y = target_year
                if next_m > 12:
                    next_m = 1
                    next_y += 1
                month_end_date = date(next_y, next_m, 1) - timedelta(days=1)

            # 如果是当前月，用今天的日期
            if target_year == today.year and target_month == today.month:
                month_end_date = today

            # 月末日期转换为datetime（含当天）
            from datetime import datetime
            month_end_dt = datetime.combine(month_end_date, datetime.max.time())
            if timezone.is_aware(timezone.now()):
                month_end_dt = timezone.make_aware(month_end_dt)

            # 员工总数：根据记录创建时间统计（更准确，避免hire_date缺失问题）
            total = Employee.objects.filter(created_at__lte=month_end_dt).count()
            # 在职人数：创建于该月末之前且当前在职
            # 注意：这里简化处理，假设员工一旦创建就计入，is_active表示当前状态
            active = Employee.objects.filter(
                created_at__lte=month_end_dt,
                is_active=True
            ).count()

            results.append({
                'date': f'{target_year}-{str(target_month).zfill(2)}',
                'total': total,
                'active': active
            })

        labels = [r['date'] for r in results]
        total_series = [r['total'] for r in results]
        active_series = [r['active'] for r in results]

        return Response({
            'detail': 'ok',
            'months': months,
            'labels': labels,
            'total_series': total_series,
            'active_series': active_series
        })


class PositionDistributionAPIView(views.APIView):
    """职位分布统计"""
    permission_classes = [permissions.IsAuthenticated, HasRBACPermission]
    rbac_perms = [Permissions.REPORT_EMPLOYEE]

    def get(self, request):
        pos_stats = Position.objects.annotate(
            employee_count=Count('employee', filter=Q(employee__is_active=True))
        ).values('id', 'name', 'employee_count').order_by('-employee_count')[:15]

        labels = []
        values = []

        for pos in pos_stats:
            if pos['employee_count'] > 0:
                labels.append(pos['name'])
                values.append(pos['employee_count'])

        return Response({
            'detail': 'ok',
            'labels': labels,
            'values': values,
            'total': sum(values)
        })


class ReportOverviewAPIView(views.APIView):
    """报表总览数据"""
    permission_classes = [permissions.IsAuthenticated, HasRBACPermission]
    rbac_perms_any = [Permissions.REPORT_EMPLOYEE, Permissions.REPORT_SALARY, Permissions.REPORT_ATTENDANCE, Permissions.REPORT_LEAVE]

    def get(self, request):
        today = timezone.now().date()
        this_month_start = today.replace(day=1)
        last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
        # 统计口径：本月发放的通常是“上个月工资”。因此这里按“工资所属月份(year/month)”统计：
        # - this_month: 上个月工资（例如 1 月显示 12 月工资）
        # - last_month: 上上个月工资（例如 1 月较上月对比 11 月工资）
        end_index = today.year * 12 + (today.month - 1)
        payroll_index = end_index - 1
        prev_payroll_index = end_index - 2
        payroll_year = payroll_index // 12
        payroll_month = (payroll_index % 12) + 1
        prev_payroll_year = prev_payroll_index // 12
        prev_payroll_month = (prev_payroll_index % 12) + 1

        # 员工统计
        emp_total = Employee.objects.count()
        emp_active = Employee.objects.filter(is_active=True).count()
        emp_pending = Employee.objects.filter(onboard_status='pending').count()
        emp_new_this_month = Employee.objects.filter(hire_date__gte=this_month_start).count()
        emp_new_last_month = Employee.objects.filter(
            hire_date__gte=last_month_start,
            hire_date__lt=this_month_start
        ).count()

        # 薪资统计
        salary_this_month = SalaryRecord.objects.filter(
            year=payroll_year,
            month=payroll_month,
            paid=True,
        ).aggregate(total=Sum('net_salary'))['total'] or Decimal('0')
        salary_last_month = SalaryRecord.objects.filter(
            year=prev_payroll_year,
            month=prev_payroll_month,
            paid=True,
        ).aggregate(total=Sum('net_salary'))['total'] or Decimal('0')

        # 考勤统计 (本月)
        attendance_this_month = Attendance.objects.filter(
            date__gte=this_month_start, date__lte=today
        ).count()
        # 正常出勤包括 check_in, check_out, late, early_leave (都算到岗)
        normal_attendance = Attendance.objects.filter(
            date__gte=this_month_start, date__lte=today,
            attendance_type__in=['check_in', 'check_out', 'late', 'early_leave']
        ).count()
        late_this_month = Attendance.objects.filter(
            date__gte=this_month_start, date__lte=today,
            attendance_type='late'
        ).count()

        # 出勤率 = 到岗人次 / 总记录数
        attendance_rate = 0
        if attendance_this_month > 0:
            attendance_rate = round(normal_attendance / attendance_this_month * 100, 1)

        # 请假统计 (本月)
        leave_this_month = LeaveRequest.objects.filter(
            created_at__date__gte=this_month_start
        ).count()
        leave_pending = LeaveRequest.objects.filter(status='pending').count()

        return Response({
            'detail': 'ok',
            'timestamp': timezone.now().isoformat(),
            'employees': {
                'total': emp_total,
                'active': emp_active,
                'pending': emp_pending,
                'new_this_month': emp_new_this_month,
                'new_last_month': emp_new_last_month,
                'growth': emp_new_this_month - emp_new_last_month
            },
            'salary': {
                'this_month': float(salary_this_month),
                'last_month': float(salary_last_month),
                'change': float(salary_this_month - salary_last_month)
            },
            'attendance': {
                'this_month': attendance_this_month,
                'late_this_month': late_this_month,
                'rate': attendance_rate
            },
            'leaves': {
                'this_month': leave_this_month,
                'pending': leave_pending
            }
        })
