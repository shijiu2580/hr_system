"""
数据库查询优化工具

提供查询分析、索引建议和常用优化查询
"""
from django.db import connection
from django.db.models import Q, Count, Sum, Avg, F, Prefetch
from django.utils import timezone
from datetime import date, timedelta


class QueryOptimizer:
    """查询优化器 - 提供常用的优化查询方法"""
    
    @staticmethod
    def get_employees_with_relations(filters=None, only_active=True):
        """获取员工列表（优化版，预加载所有关联）"""
        from .models import Employee
        
        qs = Employee.objects.select_related(
            'user', 'department', 'position', 'position__department'
        ).prefetch_related(
            'checkin_locations'
        )
        
        if only_active:
            qs = qs.filter(is_active=True)
        
        if filters:
            qs = qs.filter(**filters)
        
        return qs
    
    @staticmethod
    def get_attendance_with_employee(date_from=None, date_to=None, employee_ids=None):
        """获取考勤记录（优化版）"""
        from .models import Attendance
        
        qs = Attendance.objects.select_related(
            'employee', 'employee__department', 'employee__user'
        )
        
        if date_from:
            qs = qs.filter(date__gte=date_from)
        if date_to:
            qs = qs.filter(date__lte=date_to)
        if employee_ids:
            qs = qs.filter(employee_id__in=employee_ids)
        
        return qs.order_by('-date', 'employee__name')
    
    @staticmethod
    def get_leave_requests_with_details(status=None, employee_id=None):
        """获取请假记录（优化版）"""
        from .models import LeaveRequest
        
        qs = LeaveRequest.objects.select_related(
            'employee', 'employee__department', 'approved_by'
        )
        
        if status:
            qs = qs.filter(status=status)
        if employee_id:
            qs = qs.filter(employee_id=employee_id)
        
        return qs.order_by('-created_at')
    
    @staticmethod
    def get_salary_records_with_employee(year=None, month=None):
        """获取薪资记录（优化版）"""
        from .models import SalaryRecord
        
        qs = SalaryRecord.objects.select_related(
            'employee', 'employee__department', 'employee__position'
        )
        
        if year:
            qs = qs.filter(year=year)
        if month:
            qs = qs.filter(month=month)
        
        return qs.order_by('-year', '-month', 'employee__name')
    
    @staticmethod
    def get_department_tree_optimized():
        """获取部门树（优化版 - 一次查询）"""
        from .models import Department
        
        departments = Department.objects.select_related(
            'manager', 'parent'
        ).prefetch_related(
            'supervisors', 'children'
        ).all()
        
        # 构建树形结构
        dept_dict = {d.id: d for d in departments}
        root_depts = []
        
        for dept in departments:
            if dept.parent_id is None:
                root_depts.append(dept)
        
        return root_depts, dept_dict
    
    @staticmethod
    def get_pending_approvals_count(user):
        """获取待审批数量（优化版 - 单次查询）"""
        from .models import LeaveRequest, AttendanceSupplement, BusinessTrip, TravelExpense
        from django.db.models import Value
        from django.db.models.functions import Coalesce
        
        counts = {
            'leaves': LeaveRequest.objects.filter(status='pending').count(),
            'supplements': AttendanceSupplement.objects.filter(status='pending').count(),
            'trips': BusinessTrip.objects.filter(status='pending').count(),
            'expenses': TravelExpense.objects.filter(status='pending').count(),
        }
        counts['total'] = sum(counts.values())
        return counts


class BulkOperations:
    """批量操作工具"""
    
    @staticmethod
    def bulk_update_attendance_status(attendance_ids, updates):
        """批量更新考勤状态"""
        from .models import Attendance
        return Attendance.objects.filter(id__in=attendance_ids).update(**updates)
    
    @staticmethod
    def bulk_approve_leaves(leave_ids, approved_by, comments=''):
        """批量审批请假"""
        from .models import LeaveRequest
        return LeaveRequest.objects.filter(
            id__in=leave_ids, 
            status='pending'
        ).update(
            status='approved',
            approved_by=approved_by,
            approved_at=timezone.now(),
            comments=comments
        )
    
    @staticmethod
    def bulk_reject_leaves(leave_ids, approved_by, comments=''):
        """批量拒绝请假"""
        from .models import LeaveRequest
        return LeaveRequest.objects.filter(
            id__in=leave_ids,
            status='pending'
        ).update(
            status='rejected',
            approved_by=approved_by,
            approved_at=timezone.now(),
            comments=comments
        )
    
    @staticmethod
    def bulk_create_salary_records(records_data):
        """批量创建薪资记录"""
        from .models import SalaryRecord
        records = [SalaryRecord(**data) for data in records_data]
        return SalaryRecord.objects.bulk_create(records, ignore_conflicts=True)
    
    @staticmethod
    def bulk_mark_salaries_paid(salary_ids):
        """批量标记薪资已发放"""
        from .models import SalaryRecord
        return SalaryRecord.objects.filter(
            id__in=salary_ids,
            paid=False
        ).update(
            paid=True,
            paid_at=timezone.now()
        )


class ReportQueries:
    """报表查询优化"""
    
    @staticmethod
    def get_attendance_summary(year, month, department_id=None):
        """获取考勤汇总（优化版）"""
        from .models import Attendance, Employee
        from django.db.models import Count, Q
        from datetime import time
        import calendar
        
        _, last_day = calendar.monthrange(year, month)
        start_date = date(year, month, 1)
        end_date = date(year, month, last_day)
        
        # 基础查询
        qs = Attendance.objects.filter(
            date__gte=start_date,
            date__lte=end_date,
            employee__is_active=True
        )
        
        if department_id:
            qs = qs.filter(employee__department_id=department_id)
        
        # 使用聚合获取统计
        summary = qs.aggregate(
            total_records=Count('id'),
            late_count=Count('id', filter=Q(check_in_time__gt=time(9, 0))),
            early_leave_count=Count('id', filter=Q(check_out_time__lt=time(18, 0))),
        )
        
        return summary
    
    @staticmethod
    def get_salary_summary(year, month=None):
        """获取薪资汇总"""
        from .models import SalaryRecord
        from django.db.models import Sum, Avg, Count
        
        qs = SalaryRecord.objects.filter(year=year)
        if month:
            qs = qs.filter(month=month)
        
        return qs.aggregate(
            total_employees=Count('employee', distinct=True),
            total_basic=Sum('basic_salary'),
            total_bonus=Sum('bonus'),
            total_overtime=Sum('overtime_pay'),
            total_allowance=Sum('allowance'),
            total_net=Sum('net_salary'),
            avg_salary=Avg('net_salary'),
            paid_count=Count('id', filter=Q(paid=True)),
            unpaid_count=Count('id', filter=Q(paid=False)),
        )
    
    @staticmethod
    def get_leave_statistics(year, department_id=None):
        """获取请假统计"""
        from .models import LeaveRequest
        from django.db.models import Sum, Count
        
        qs = LeaveRequest.objects.filter(
            start_date__year=year,
            status='approved'
        )
        
        if department_id:
            qs = qs.filter(employee__department_id=department_id)
        
        return qs.values('leave_type').annotate(
            count=Count('id'),
            total_days=Sum('days')
        ).order_by('-total_days')
