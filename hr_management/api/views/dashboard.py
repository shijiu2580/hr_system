"""仪表板统计 API 视图"""
from rest_framework import permissions, views
from rest_framework.response import Response
from django.core.cache import cache
from django.utils import timezone

from ...models import Employee, Department, Position, Attendance, LeaveRequest, SalaryRecord, SystemLog, RBACPermission, Role
from ...services import CacheKeys


class SystemSummaryAPIView(views.APIView):
    """系统概览统计（带缓存，60 秒 TTL）"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        cached_data = cache.get(CacheKeys.DASHBOARD_SUMMARY)
        if cached_data:
            return Response(cached_data)

        emp_total = Employee.objects.count()
        emp_active = Employee.objects.filter(is_active=True).count()
        dept_count = Department.objects.count()
        pos_count = Position.objects.count()

        today = timezone.now().date()
        last7 = today - timezone.timedelta(days=6)
        attendance_7d = Attendance.objects.filter(date__gte=last7, date__lte=today).count()
        leave_pending = LeaveRequest.objects.filter(status='pending').count()
        leave_recent = LeaveRequest.objects.filter(created_at__gte=timezone.now()-timezone.timedelta(days=7)).count()

        year = today.year
        salary_records_year = SalaryRecord.objects.filter(year=year).count()
        logs_24h = SystemLog.objects.filter(timestamp__gte=timezone.now()-timezone.timedelta(hours=24)).count()
        perm_count = RBACPermission.objects.count()
        role_count = Role.objects.count()

        response_data = {
            'detail': 'ok',
            'timestamp': timezone.now().isoformat(),
            'data': {
                'employees': {'total': emp_total, 'active': emp_active, 'inactive': emp_total - emp_active},
                'org': {'departments': dept_count, 'positions': pos_count},
                'attendance': {'last7d': attendance_7d},
                'leaves': {'pending': leave_pending, 'recent7d': leave_recent},
                'salary': {'year': year, 'records': salary_records_year},
                'logs': {'last24h': logs_24h},
                'security': {'permissions': perm_count, 'roles': role_count}
            }
        }
        cache.set(CacheKeys.DASHBOARD_SUMMARY, response_data, CacheKeys.TIMEOUT_SHORT)
        return Response(response_data)


class MyTodoSummaryAPIView(views.APIView):
    """我的待办（最小版）：返回当前用户需要处理的审批数量。

    规则：
    - 直属上级：可看到本部门员工的离职申请（resignation）在「直属上级待处理」阶段的待办。
    - 人事（is_staff）：
        - 非离职请假 pending 待办
        - 离职申请在「人事待处理」阶段的待办（直属上级已同意且人事仍 pending）
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # 直属上级待办：离职申请（manager stage）
        managed_dept_ids = list(
            Department.objects.filter(manager__user=request.user).values_list('id', flat=True)
        )
        manager_qs = LeaveRequest.objects.none()
        if managed_dept_ids:
            manager_qs = LeaveRequest.objects.filter(
                leave_type='resignation',
                resignation_manager_status='pending',
                employee__department_id__in=managed_dept_ids,
            )

        # 人事待办（HR stage + 普通请假）
        hr_leave_qs = LeaveRequest.objects.none()
        hr_resign_qs = LeaveRequest.objects.none()
        if request.user.is_staff or request.user.is_superuser:
            hr_leave_qs = LeaveRequest.objects.filter(
                status='pending'
            ).exclude(leave_type='resignation')
            hr_resign_qs = LeaveRequest.objects.filter(
                leave_type='resignation',
                resignation_manager_status='approved',
                resignation_hr_status='pending',
            )

        manager_pending = manager_qs.count()
        hr_pending = hr_leave_qs.count() + hr_resign_qs.count()
        total = manager_pending + hr_pending

        # 轻量返回一些待办项（最多 8 条），便于前端后续扩展
        items = []
        def append_items(qs, stage, limit):
            for leave in qs.select_related('employee', 'employee__department')[:limit]:
                items.append({
                    'id': leave.id,
                    'stage': stage,
                    'leave_type': leave.leave_type,
                    'status': leave.status,
                    'employee': {
                        'id': leave.employee_id,
                        'name': getattr(leave.employee, 'name', '') or leave.employee.user.username,
                        'department': getattr(getattr(leave.employee, 'department', None), 'name', None),
                    },
                    'start_date': leave.start_date.isoformat() if leave.start_date else None,
                    'end_date': leave.end_date.isoformat() if leave.end_date else None,
                    'created_at': leave.created_at.isoformat() if leave.created_at else None,
                })

        remaining = 8
        if remaining > 0 and manager_pending:
            append_items(manager_qs.order_by('created_at'), 'manager', remaining)
            remaining = 8 - len(items)
        if remaining > 0 and (request.user.is_staff or request.user.is_superuser):
            # HR 先展示离职 HR 待办，再展示普通请假
            append_items(hr_resign_qs.order_by('created_at'), 'hr', remaining)
            remaining = 8 - len(items)
            if remaining > 0:
                append_items(hr_leave_qs.order_by('created_at'), 'hr', remaining)

        return Response({
            'detail': 'ok',
            'timestamp': timezone.now().isoformat(),
            'data': {
                'todos': {
                    'total': total,
                    'manager_pending': manager_pending,
                    'hr_pending': hr_pending,
                },
                'items': items,
            }
        })


class AttendanceTrendAPIView(views.APIView):
    """考勤趋势统计 - 只统计当前用户自己的考勤"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        days = int(request.query_params.get('days', 30))
        days = max(1, min(days, 90))

        today = timezone.now().date()
        start = today - timezone.timedelta(days=days-1)

        stats = {}
        for i in range(days):
            d = start + timezone.timedelta(days=i)
            stats[d] = {'total': 0, 'late': 0, 'absent': 0}

        # 只统计当前用户自己的考勤
        qs = Attendance.objects.filter(date__gte=start, date__lte=today)
        try:
            employee = Employee.objects.get(user=request.user)
            qs = qs.filter(employee=employee)
        except Employee.DoesNotExist:
            # 用户没有关联员工，返回空数据
            pass

        for att in qs.values('date', 'attendance_type'):
            rec = stats.get(att['date'])
            if rec:
                rec['total'] += 1
                if att['attendance_type'] == 'late':
                    rec['late'] += 1
                if att['attendance_type'] == 'absent':
                    rec['absent'] += 1

        labels = [d.strftime('%m-%d') for d in sorted(stats.keys())]
        total_series = [stats[d]['total'] for d in sorted(stats.keys())]
        late_series = [stats[d]['late'] for d in sorted(stats.keys())]
        absent_series = [stats[d]['absent'] for d in sorted(stats.keys())]

        return Response({
            'detail': 'ok',
            'days': days,
            'labels': labels,
            'series': {'total': total_series, 'late': late_series, 'absent': absent_series}
        })


class LeaveTypeStatsAPIView(views.APIView):
    """请假类型统计"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        recent_days = int(request.query_params.get('recent_days', 60))
        recent_days = max(1, min(recent_days, 180))

        since = timezone.now() - timezone.timedelta(days=recent_days)
        qs = LeaveRequest.objects.filter(created_at__gte=since)

        type_counts = {key: 0 for key, _ in LeaveRequest.LEAVE_TYPE_CHOICES}
        for item in qs.values('leave_type'):
            t = item['leave_type']
            if t in type_counts:
                type_counts[t] += 1

        labels = []
        values = []
        for key, label in LeaveRequest.LEAVE_TYPE_CHOICES:
            labels.append(label)
            values.append(type_counts.get(key, 0))

        return Response({'detail': 'ok', 'recent_days': recent_days, 'labels': labels, 'values': values})


class LogTypeStatsAPIView(views.APIView):
    """系统日志类型统计"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        days = int(request.query_params.get('days', 30))
        days = max(1, min(days, 90))

        since = timezone.now() - timezone.timedelta(days=days)
        qs = SystemLog.objects.filter(timestamp__gte=since)

        levels = {k: 0 for k, _ in SystemLog.LEVEL_CHOICES}
        for row in qs.values('level'):
            lvl = row['level']
            if lvl in levels:
                levels[lvl] += 1

        action_counts = {}
        for row in qs.values('action'):
            a = row['action'] or ''
            action_counts[a] = action_counts.get(a, 0) + 1

        top_actions = sorted(
            [{'action': a, 'count': c} for a, c in action_counts.items()],
            key=lambda x: x['count'], reverse=True
        )[:10]

        return Response({'detail': 'ok', 'days': days, 'levels': levels, 'top_actions': top_actions})


class LogCalendarStatsAPIView(views.APIView):
    """当月日志日历统计"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from calendar import monthrange

        now = timezone.now()
        year = now.year
        month = now.month
        days_in_month = monthrange(year, month)[1]
        first_day = now.replace(day=1).date()
        last_day = first_day.replace(day=days_in_month)

        base_levels = {k: 0 for k, _ in SystemLog.LEVEL_CHOICES}
        stats = {}
        for d in range(1, days_in_month + 1):
            date_obj = first_day.replace(day=d)
            stats[date_obj] = {'total': 0, 'levels': base_levels.copy()}

        qs = SystemLog.objects.filter(timestamp__date__gte=first_day, timestamp__date__lte=last_day)
        for row in qs.values('timestamp', 'level'):
            d = row['timestamp'].date()
            rec = stats.get(d)
            if rec:
                rec['total'] += 1
                lvl = row['level']
                if lvl in rec['levels']:
                    rec['levels'][lvl] += 1

        day_items = []
        for date_obj in sorted(stats.keys()):
            item = stats[date_obj]
            day_items.append({
                'day': date_obj.day,
                'date': date_obj.isoformat(),
                'total': item['total'],
                'levels': item['levels']
            })

        return Response({
            'detail': 'ok',
            'year': year,
            'month': month,
            'today': now.date().isoformat(),
            'days': day_items
        })


class EmployeeChurnStatsAPIView(views.APIView):
    """员工流失率统计"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        days = int(request.query_params.get('days', 60))
        days = max(1, min(days, 180))

        since = timezone.now() - timezone.timedelta(days=days)
        # 排除待入职员工，只统计正式员工
        current_active = Employee.objects.filter(is_active=True, onboard_status='onboarded').count()
        # 离职员工：is_active=False 且不是待入职状态（已经入职过的才算离职）
        recently_inactive = Employee.objects.filter(
            is_active=False,
            onboard_status__in=['onboarded', 'resigned'],
            updated_at__gte=since
        ).count()
        start_active_est = current_active + recently_inactive

        churn_rate = 0.0
        if start_active_est > 0:
            churn_rate = round(recently_inactive / start_active_est * 100, 2)

        return Response({
            'detail': 'ok',
            'days': days,
            'current_active': current_active,
            'recently_inactive': recently_inactive,
            'start_active_est': start_active_est,
            'churn_rate_pct': churn_rate
        })
