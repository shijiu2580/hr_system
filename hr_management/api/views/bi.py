"""BI 报表 API 视图 —— 提供深度交叉分析数据"""
from rest_framework import permissions, views
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Sum, Count, Avg, Q, F, Value, CharField
from django.db.models.functions import TruncMonth, TruncDate, ExtractWeekDay, Concat
from datetime import timedelta, date, datetime
from decimal import Decimal

from ...models import Employee, Department, Attendance, LeaveRequest, SalaryRecord
from ...permissions import HasRBACPermission
from ...rbac import Permissions


class BIDepartmentCostAPIView(views.APIView):
    """部门人力成本分析：各部门薪资总额、人均薪资、占比"""
    permission_classes = [permissions.IsAuthenticated, HasRBACPermission]
    rbac_perms = [Permissions.REPORT_SALARY]

    def _get_all_descendant_ids(self, dept):
        ids = [dept.id]
        for child in dept.children.all():
            ids.extend(self._get_all_descendant_ids(child))
        return ids

    def get(self, request):
        today = timezone.now().date()
        # 默认统计上个月
        idx = today.year * 12 + (today.month - 1) - 1
        year = idx // 12
        month = (idx % 12) + 1

        top_depts = Department.objects.filter(parent__isnull=True)
        items = []
        grand_total = Decimal('0')

        for dept in top_depts:
            dept_ids = self._get_all_descendant_ids(dept)
            emp_ids = list(Employee.objects.filter(
                is_active=True, department_id__in=dept_ids
            ).values_list('id', flat=True))

            stats = SalaryRecord.objects.filter(
                year=year, month=month, employee_id__in=emp_ids
            ).aggregate(total=Sum('net_salary'), cnt=Count('id'), avg=Avg('net_salary'))

            total = stats['total'] or Decimal('0')
            grand_total += total
            items.append({
                'department': dept.name,
                'headcount': len(emp_ids),
                'total_salary': float(total),
                'avg_salary': float(stats['avg'] or 0),
                'count': stats['cnt'] or 0,
            })

        # 未分配部门
        no_dept_ids = list(Employee.objects.filter(
            is_active=True, department__isnull=True
        ).values_list('id', flat=True))
        if no_dept_ids:
            stats = SalaryRecord.objects.filter(
                year=year, month=month, employee_id__in=no_dept_ids
            ).aggregate(total=Sum('net_salary'), cnt=Count('id'), avg=Avg('net_salary'))
            total = stats['total'] or Decimal('0')
            grand_total += total
            items.append({
                'department': '未分配部门',
                'headcount': len(no_dept_ids),
                'total_salary': float(total),
                'avg_salary': float(stats['avg'] or 0),
                'count': stats['cnt'] or 0,
            })

        # 计算占比
        for item in items:
            item['ratio'] = round(item['total_salary'] / float(grand_total) * 100, 1) if grand_total else 0

        items.sort(key=lambda x: x['total_salary'], reverse=True)

        return Response({
            'period': f'{year}-{str(month).zfill(2)}',
            'grand_total': float(grand_total),
            'items': items,
        })


class BIAttendanceHeatmapAPIView(views.APIView):
    """考勤热力图：按周几×时段统计打卡频次"""
    permission_classes = [permissions.IsAuthenticated, HasRBACPermission]
    rbac_perms = [Permissions.REPORT_ATTENDANCE]

    def get(self, request):
        days = int(request.query_params.get('days', 30))
        days = max(7, min(days, 90))
        today = timezone.now().date()
        start = today - timedelta(days=days - 1)

        # 按星期×考勤类型
        qs = Attendance.objects.filter(date__gte=start, date__lte=today)

        weekday_names = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        type_labels = {'normal': '正常', 'late': '迟到', 'early_leave': '早退', 'absent': '缺勤'}
        type_map = {'check_in': 'normal', 'check_out': 'normal'}

        # 初始化 7×4 矩阵
        matrix = [[0] * len(type_labels) for _ in range(7)]

        for row in qs.values('date', 'attendance_type'):
            wd = row['date'].weekday()  # 0=Mon
            at = type_map.get(row['attendance_type'], row['attendance_type'])
            type_keys = list(type_labels.keys())
            if at in type_keys:
                col = type_keys.index(at)
                matrix[wd][col] += 1

        return Response({
            'days': days,
            'weekdays': weekday_names,
            'types': list(type_labels.values()),
            'matrix': matrix,
        })


class BITurnoverAPIView(views.APIView):
    """员工流动率分析：月度入职/离职/净增长"""
    permission_classes = [permissions.IsAuthenticated, HasRBACPermission]
    rbac_perms = [Permissions.REPORT_EMPLOYEE]

    def get(self, request):
        months = int(request.query_params.get('months', 12))
        months = max(3, min(months, 24))
        today = timezone.now().date()

        results = []
        for i in range(months - 1, -1, -1):
            idx = today.year * 12 + today.month - 1 - i
            y = idx // 12
            m = (idx % 12) + 1

            # 月初月末
            month_start = date(y, m, 1)
            if m == 12:
                month_end = date(y, 12, 31)
            else:
                month_end = date(y, m + 1, 1) - timedelta(days=1)
            if month_end > today:
                month_end = today

            # 入职人数（hire_date 在本月）
            joined = Employee.objects.filter(
                hire_date__gte=month_start, hire_date__lte=month_end
            ).count()

            # 离职人数（离职请假已批准，结束日期在本月）
            left = LeaveRequest.objects.filter(
                leave_type='resignation',
                status='approved',
                end_date__gte=month_start,
                end_date__lte=month_end,
            ).count()

            # 月末在职人数
            active_end = Employee.objects.filter(
                is_active=True, created_at__date__lte=month_end
            ).count()

            results.append({
                'label': f'{y}-{str(m).zfill(2)}',
                'joined': joined,
                'left': left,
                'net': joined - left,
                'active': active_end,
                'turnover_rate': round(left / active_end * 100, 1) if active_end else 0,
            })

        return Response({
            'months': months,
            'labels': [r['label'] for r in results],
            'joined': [r['joined'] for r in results],
            'left': [r['left'] for r in results],
            'net': [r['net'] for r in results],
            'active': [r['active'] for r in results],
            'turnover_rate': [r['turnover_rate'] for r in results],
        })


class BISalaryRangeAPIView(views.APIView):
    """薪资区间分布：统计各薪资段人数"""
    permission_classes = [permissions.IsAuthenticated, HasRBACPermission]
    rbac_perms = [Permissions.REPORT_SALARY]

    def get(self, request):
        today = timezone.now().date()
        idx = today.year * 12 + (today.month - 1) - 1
        year = idx // 12
        month = (idx % 12) + 1

        records = list(SalaryRecord.objects.filter(year=year, month=month).values_list('net_salary', flat=True))

        ranges = [
            (0, 3000, '0-3K'),
            (3000, 5000, '3K-5K'),
            (5000, 8000, '5K-8K'),
            (8000, 10000, '8K-10K'),
            (10000, 15000, '10K-15K'),
            (15000, 20000, '15K-20K'),
            (20000, 30000, '20K-30K'),
            (30000, 50000, '30K-50K'),
            (50000, float('inf'), '50K+'),
        ]

        distribution = []
        for lo, hi, label in ranges:
            count = sum(1 for s in records if s is not None and lo <= float(s) < hi)
            distribution.append({'label': label, 'count': count})

        return Response({
            'period': f'{year}-{str(month).zfill(2)}',
            'total': len(records),
            'distribution': distribution,
            'labels': [d['label'] for d in distribution],
            'values': [d['count'] for d in distribution],
        })


class BILeaveBalanceAPIView(views.APIView):
    """请假趋势与部门对比"""
    permission_classes = [permissions.IsAuthenticated, HasRBACPermission]
    rbac_perms = [Permissions.REPORT_LEAVE]

    def _get_all_descendant_ids(self, dept):
        ids = [dept.id]
        for child in dept.children.all():
            ids.extend(self._get_all_descendant_ids(child))
        return ids

    def get(self, request):
        days = int(request.query_params.get('days', 90))
        days = max(7, min(days, 365))
        since = timezone.now() - timedelta(days=days)

        # 按部门统计请假天数
        top_depts = Department.objects.filter(parent__isnull=True)
        dept_stats = []

        for dept in top_depts:
            dept_ids = self._get_all_descendant_ids(dept)
            emp_ids = list(Employee.objects.filter(
                department_id__in=dept_ids
            ).values_list('id', flat=True))
            emp_count = Employee.objects.filter(
                is_active=True, department_id__in=dept_ids
            ).count()

            leave_data = LeaveRequest.objects.filter(
                employee_id__in=emp_ids,
                created_at__gte=since,
                status='approved'
            ).aggregate(
                total_days=Sum('days'),
                total_count=Count('id')
            )

            total_days = float(leave_data['total_days'] or 0)
            dept_stats.append({
                'department': dept.name,
                'headcount': emp_count,
                'leave_count': leave_data['total_count'] or 0,
                'leave_days': total_days,
                'avg_days': round(total_days / emp_count, 1) if emp_count else 0,
            })

        dept_stats.sort(key=lambda x: x['leave_days'], reverse=True)

        return Response({
            'days': days,
            'dept_stats': dept_stats,
            'labels': [d['department'] for d in dept_stats],
            'values': [d['leave_days'] for d in dept_stats],
        })


class BIDailyAttendanceAPIView(views.APIView):
    """每日出勤率趋势（折线图用）"""
    permission_classes = [permissions.IsAuthenticated, HasRBACPermission]
    rbac_perms = [Permissions.REPORT_ATTENDANCE]

    def get(self, request):
        days = int(request.query_params.get('days', 30))
        days = max(7, min(days, 90))
        today = timezone.now().date()
        start = today - timedelta(days=days - 1)

        # 每日出勤统计
        daily = Attendance.objects.filter(
            date__gte=start, date__lte=today
        ).values('date').annotate(
            total=Count('id'),
            present=Count('id', filter=Q(
                attendance_type__in=['check_in', 'check_out', 'late', 'early_leave']
            )),
            late=Count('id', filter=Q(attendance_type='late')),
            absent=Count('id', filter=Q(attendance_type='absent')),
        ).order_by('date')

        labels = []
        rates = []
        presents = []
        lates = []
        absents = []
        totals = []

        for row in daily:
            labels.append(row['date'].strftime('%m-%d'))
            rate = round(row['present'] / row['total'] * 100, 1) if row['total'] else 0
            rates.append(rate)
            presents.append(row['present'])
            lates.append(row['late'])
            absents.append(row['absent'])
            totals.append(row['total'])

        return Response({
            'days': days,
            'labels': labels,
            'rates': rates,
            'presents': presents,
            'lates': lates,
            'absents': absents,
            'totals': totals,
        })
