"""
优化版序列化器 - 减少数据库查询，提升序列化性能

这个文件包含针对列表展示优化的轻量级序列化器
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from ...models import (
    Employee, Department, Position, Attendance, LeaveRequest,
    SalaryRecord, AttendanceSupplement, BusinessTrip, TravelExpense
)


# ============ 轻量级序列化器（用于列表和嵌套） ============

class DepartmentLiteSerializer(serializers.ModelSerializer):
    """轻量部门序列化器 - 只包含基本字段"""
    class Meta:
        model = Department
        fields = ['id', 'name']


class PositionLiteSerializer(serializers.ModelSerializer):
    """轻量职位序列化器"""
    department_name = serializers.CharField(source='department.name', read_only=True)
    
    class Meta:
        model = Position
        fields = ['id', 'name', 'department_name']


class UserLiteSerializer(serializers.ModelSerializer):
    """轻量用户序列化器"""
    class Meta:
        model = User
        fields = ['id', 'username', 'is_staff', 'is_active']


class EmployeeLiteSerializer(serializers.ModelSerializer):
    """轻量员工序列化器 - 用于列表展示和关联显示"""
    department_name = serializers.CharField(source='department.name', read_only=True, default='')
    position_name = serializers.CharField(source='position.name', read_only=True, default='')
    username = serializers.CharField(source='user.username', read_only=True, default='')
    
    class Meta:
        model = Employee
        fields = ['id', 'employee_id', 'name', 'department_name', 'position_name', 'username', 'is_active']


# ============ 列表专用序列化器（避免深度嵌套） ============

class AttendanceListSerializer(serializers.ModelSerializer):
    """考勤列表序列化器 - 扁平化数据，减少嵌套"""
    employee_id = serializers.CharField(source='employee.employee_id')
    employee_name = serializers.CharField(source='employee.name')
    department_name = serializers.CharField(source='employee.department.name', default='')
    
    class Meta:
        model = Attendance
        fields = [
            'id', 'date', 'check_in_time', 'check_out_time', 
            'attendance_type', 'notes',
            'employee_id', 'employee_name', 'department_name'
        ]


class LeaveListSerializer(serializers.ModelSerializer):
    """请假列表序列化器"""
    employee_id = serializers.CharField(source='employee.employee_id')
    employee_name = serializers.CharField(source='employee.name')
    department_name = serializers.CharField(source='employee.department.name', default='')
    leave_type_display = serializers.CharField(source='get_leave_type_display')
    status_display = serializers.CharField(source='get_status_display')
    approved_by_name = serializers.CharField(source='approved_by.username', default='')
    
    class Meta:
        model = LeaveRequest
        fields = [
            'id', 'leave_type', 'leave_type_display', 'start_date', 'end_date', 
            'days', 'reason', 'status', 'status_display', 'created_at',
            'employee_id', 'employee_name', 'department_name', 'approved_by_name'
        ]


class SalaryListSerializer(serializers.ModelSerializer):
    """薪资列表序列化器"""
    employee_id = serializers.CharField(source='employee.employee_id')
    employee_name = serializers.CharField(source='employee.name')
    department_name = serializers.CharField(source='employee.department.name', default='')
    
    class Meta:
        model = SalaryRecord
        fields = [
            'id', 'year', 'month', 'basic_salary', 'bonus', 
            'overtime_pay', 'allowance', 'net_salary', 'paid', 'paid_at',
            'employee_id', 'employee_name', 'department_name'
        ]


class SupplementListSerializer(serializers.ModelSerializer):
    """补签列表序列化器"""
    employee_id = serializers.CharField(source='employee.employee_id')
    employee_name = serializers.CharField(source='employee.name')
    department_name = serializers.CharField(source='employee.department.name', default='')
    supplement_type_display = serializers.CharField(source='get_supplement_type_display')
    status_display = serializers.CharField(source='get_status_display')
    
    class Meta:
        model = AttendanceSupplement
        fields = [
            'id', 'date', 'time', 'supplement_type', 'supplement_type_display',
            'reason', 'status', 'status_display', 'created_at',
            'employee_id', 'employee_name', 'department_name'
        ]


class BusinessTripListSerializer(serializers.ModelSerializer):
    """出差列表序列化器"""
    employee_id = serializers.CharField(source='employee.employee_id')
    employee_name = serializers.CharField(source='employee.name')
    department_name = serializers.CharField(source='employee.department.name', default='')
    trip_type_display = serializers.CharField(source='get_trip_type_display')
    status_display = serializers.CharField(source='get_status_display')
    
    class Meta:
        model = BusinessTrip
        fields = [
            'id', 'destination', 'trip_type', 'trip_type_display',
            'start_date', 'end_date', 'days', 'reason', 
            'status', 'status_display', 'created_at',
            'employee_id', 'employee_name', 'department_name'
        ]


class TravelExpenseListSerializer(serializers.ModelSerializer):
    """报销列表序列化器"""
    employee_id = serializers.CharField(source='employee.employee_id')
    employee_name = serializers.CharField(source='employee.name')
    expense_type_display = serializers.CharField(source='get_expense_type_display')
    status_display = serializers.CharField(source='get_status_display')
    trip_destination = serializers.CharField(source='business_trip.destination', default='')
    
    class Meta:
        model = TravelExpense
        fields = [
            'id', 'expense_type', 'expense_type_display', 'amount',
            'description', 'status', 'status_display', 'created_at',
            'employee_id', 'employee_name', 'trip_destination'
        ]


# ============ 批量操作序列化器 ============

class BulkIdSerializer(serializers.Serializer):
    """批量操作ID序列化器"""
    ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
        help_text='要操作的ID列表'
    )


class BulkApproveSerializer(serializers.Serializer):
    """批量审批序列化器"""
    ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )
    action = serializers.ChoiceField(choices=['approve', 'reject'])
    comments = serializers.CharField(required=False, allow_blank=True, default='')
