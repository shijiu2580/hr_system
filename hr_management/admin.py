from django.contrib import admin
from django.utils.html import format_html
from .models import Department, Position, Employee, Attendance, LeaveRequest, SalaryRecord


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'manager', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    ordering = ['name']


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ['name', 'department', 'salary_range_min', 'salary_range_max', 'created_at']
    list_filter = ['department', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['department', 'name']


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'name', 'department', 'position', 'hire_date', 'is_active']
    list_filter = ['department', 'position', 'is_active', 'gender', 'marital_status', 'hire_date']
    search_fields = ['employee_id', 'name', 'phone', 'email', 'id_card']
    ordering = ['employee_id']
    readonly_fields = ['created_at', 'updated_at', 'age', 'work_years']


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['employee', 'date', 'check_in_time', 'check_out_time', 'attendance_type']
    list_filter = ['attendance_type', 'date', 'employee__department']
    search_fields = ['employee__name', 'employee__employee_id']
    ordering = ['-date', 'employee']
    date_hierarchy = 'date'


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ['employee', 'leave_type', 'start_date', 'end_date', 'days', 'status', 'resignation_manager_status', 'resignation_hr_status', 'created_at']
    list_filter = ['leave_type', 'status', 'resignation_manager_status', 'resignation_hr_status', 'created_at', 'employee__department']
    search_fields = ['employee__name', 'employee__employee_id', 'reason']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'


@admin.register(SalaryRecord)
class SalaryRecordAdmin(admin.ModelAdmin):
    list_display = ['employee', 'year', 'month', 'basic_salary', 'net_salary', 'created_at']
    list_filter = ['year', 'month', 'employee__department']
    search_fields = ['employee__name', 'employee__employee_id']
    ordering = ['-year', '-month', 'employee']
