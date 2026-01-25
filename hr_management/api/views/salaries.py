"""薪资管理 API 视图"""
from rest_framework import generics, permissions
from rest_framework.response import Response
from django.db.models import Q

from .base import LoggingMixin
from ...models import SalaryRecord
from ...permissions import IsStaffOrOwnRelated, get_managed_department_ids, HasRBACPermission
from ...rbac import Permissions
from ...utils import api_success, api_error
from ..serializers import SalaryRecordSerializer, SalaryRecordWriteSerializer


class SalaryListCreateAPIView(LoggingMixin, generics.ListCreateAPIView):
    """薪资列表与创建"""
    serializer_class = SalaryRecordSerializer
    permission_classes = [permissions.IsAuthenticated, HasRBACPermission]
    log_model_name = '薪资记录'
    
    # RBAC 权限
    def get_rbac_permissions(self):
        if self.request.method == 'POST':
            return [Permissions.SALARY_CREATE]
        return [Permissions.SALARY_VIEW]
    
    def get_queryset(self):
        qs = SalaryRecord.objects.select_related('employee', 'employee__department').all().order_by('-year', '-month')
        user = self.request.user
        if not user.is_staff:
            # 部门经理可看本部门所有员工薪资，普通员工只能看自己
            managed_dept_ids = get_managed_department_ids(user)
            if managed_dept_ids:
                qs = qs.filter(Q(employee__user=user) | Q(employee__department_id__in=managed_dept_ids))
            else:
                qs = qs.filter(employee__user=user)
        
        # 按员工ID筛选
        employee_id = self.request.query_params.get('employee')
        if employee_id:
            qs = qs.filter(employee_id=employee_id)
        
        year = self.request.query_params.get('year')
        if year:
            qs = qs.filter(year=year)
        
        return qs

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SalaryRecordWriteSerializer
        return SalaryRecordSerializer
    
    def get_log_detail(self, obj):
        return f'{obj.employee.employee_id} {obj.year}-{obj.month}'

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        if not ser.is_valid():
            return Response(api_error('验证失败', errors=ser.errors), status=400)
        salary = ser.save()
        self.log_create(request, salary)
        return Response(api_success(SalaryRecordSerializer(salary).data), status=201)


class SalaryDetailAPIView(LoggingMixin, generics.RetrieveUpdateDestroyAPIView):
    """薪资详情、更新、删除"""
    queryset = SalaryRecord.objects.select_related('employee').all()
    serializer_class = SalaryRecordSerializer
    permission_classes = [permissions.IsAuthenticated, HasRBACPermission]
    log_model_name = '薪资记录'
    
    # RBAC 权限
    def get_rbac_permissions(self):
        if self.request.method in ['PUT', 'PATCH']:
            return [Permissions.SALARY_EDIT]
        if self.request.method == 'DELETE':
            return [Permissions.SALARY_EDIT]
        return [Permissions.SALARY_VIEW]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return SalaryRecordWriteSerializer
        return SalaryRecordSerializer
    
    def get_log_detail(self, obj):
        return f'{obj.employee.employee_id} {obj.year}-{obj.month}'

    def update(self, request, *args, **kwargs):
        partial = request.method == 'PATCH'
        instance = self.get_object()
        ser = self.get_serializer(instance, data=request.data, partial=partial)
        if not ser.is_valid():
            return Response(api_error('验证失败', errors=ser.errors), status=400)
        record = ser.save()
        self.log_update(request, record)
        return Response(api_success(SalaryRecordSerializer(record).data))

    def destroy(self, request, *args, **kwargs):
        record = self.get_object()
        self.log_delete(request, record)
        detail = self.get_log_detail(record)
        record.delete()
        return Response(api_success(detail=f'已删除 {detail}'))
