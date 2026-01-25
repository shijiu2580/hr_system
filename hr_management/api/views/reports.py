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
    """部门人员分布统计"""
    permission_classes = [permissions.IsAuthenticated, HasRBACPermission]
    rbac_perms = [Permissions.REPORT_EMPLOYEE]
    
    def get(self, request):
        # 按部门统计在职员工数量
        dept_stats = Department.objects.annotate(
            employee_count=Count('employee', filter=Q(employee__is_active=True))
        ).values('id', 'name', 'employee_count').order_by('-employee_count')
        
        labels = []
        values = []
        colors = [
            '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
            '#06b6d4', '#ec4899', '#84cc16', '#f97316', '#6366f1'
        ]
        
        for i, dept in enumerate(dept_stats):
            if dept['employee_count'] > 0:
                labels.append(dept['name'])
                values.append(dept['employee_count'])
        
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
        
        type_stats = {}
        for t, label in Attendance.ATTENDANCE_TYPE_CHOICES:
            type_stats[t] = {'label': label, 'count': 0}
        
        for row in qs.values('attendance_type').annotate(cnt=Count('id')):
            t = row['attendance_type']
            if t in type_stats:
                type_stats[t]['count'] = row['cnt']
        
        total = sum(s['count'] for s in type_stats.values())
        
        # 计算出勤率（正常+迟到）
        normal_count = type_stats.get('normal', {}).get('count', 0)
        late_count = type_stats.get('late', {}).get('count', 0)
        attendance_rate = 0
        if total > 0:
            attendance_rate = round((normal_count + late_count) / total * 100, 1)
        
        labels = [s['label'] for s in type_stats.values()]
        values = [s['count'] for s in type_stats.values()]
        
        return Response({
            'detail': 'ok',
            'days': days,
            'labels': labels,
            'values': values,
            'total': total,
            'attendance_rate': attendance_rate,
            'stats': type_stats
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
        for i in range(months - 1, -1, -1):
            target_date = today - timedelta(days=i * 30)
            
            # 统计截止该日期的员工数
            total = Employee.objects.filter(hire_date__lte=target_date).count()
            active = Employee.objects.filter(
                hire_date__lte=target_date,
                is_active=True
            ).count()
            
            results.append({
                'date': target_date.strftime('%Y-%m'),
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
        late_this_month = Attendance.objects.filter(
            date__gte=this_month_start, date__lte=today,
            attendance_type='late'
        ).count()
        
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
                'rate': round((attendance_this_month - late_this_month) / max(attendance_this_month, 1) * 100, 1)
            },
            'leaves': {
                'this_month': leave_this_month,
                'pending': leave_pending
            }
        })
