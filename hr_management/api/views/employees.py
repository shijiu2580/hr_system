"""员工管理 API 视图"""
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from django.db.models import Q

from .base import LoggingMixin
from ...models import Employee
from ...permissions import IsStaffOrReadOwnEmployee, get_managed_department_ids, HasRBACPermission
from ...rbac import Permissions
from ...utils import log_event, api_success, api_error, get_client_ip
from ..serializers import EmployeeSerializer, EmployeeWriteSerializer, EmployeeSelfUpdateSerializer


class EmployeeListCreateAPIView(LoggingMixin, generics.ListCreateAPIView):
    """员工列表与创建"""
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated, HasRBACPermission]
    log_model_name = '员工'

    # RBAC 权限：读取需要 EMPLOYEE_VIEW，创建需要 EMPLOYEE_CREATE
    def get_rbac_permissions(self):
        if self.request.method == 'POST':
            return [Permissions.EMPLOYEE_CREATE]
        return [Permissions.EMPLOYEE_VIEW]

    def get_queryset(self):
        qs = Employee.objects.select_related('department', 'position', 'user').all()
        user = self.request.user

        # 检查是否有全量访问权限（管理员/人事经理等）
        from ...permissions import user_has_rbac_permission
        has_full_access = (
            user.is_staff or
            user.is_superuser or
            user_has_rbac_permission(user, 'employee.view_all') or
            user_has_rbac_permission(user, 'employee.manage')
        )

        if not has_full_access:
            # 部门经理可看本部门所有员工，普通员工只能看自己
            managed_dept_ids = get_managed_department_ids(user)
            if managed_dept_ids:
                qs = qs.filter(Q(user=user) | Q(department_id__in=managed_dept_ids))
            else:
                qs = qs.filter(user=user)

        # 搜索过滤
        q = self.request.query_params.get('q')
        if q:
            qs = qs.filter(
                Q(employee_id__icontains=q) | Q(name__icontains=q) | Q(user__username__icontains=q)
            )

        dept = self.request.query_params.get('department')
        if dept:
            qs = qs.filter(department__id=dept)

        pos = self.request.query_params.get('position')
        if pos:
            qs = qs.filter(position__id=pos)

        active = self.request.query_params.get('active')
        if active in ['1', '0', 'true', 'false', 'True', 'False']:
            val = active in ['1', 'true', 'True']
            qs = qs.filter(is_active=val)

        # 排序
        ordering = self.request.query_params.get('ordering')
        allowed = {'id': 'id', 'employee_id': 'employee_id', 'name': 'name', 'hire_date': 'hire_date', 'salary': 'salary'}
        if ordering:
            raw = ordering.lstrip('-')
            if raw in allowed:
                field = allowed[raw]
                if ordering.startswith('-'):
                    field = f'-{field}'
                qs = qs.order_by(field)

        return qs

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return EmployeeWriteSerializer
        return EmployeeSerializer

    def get_log_detail(self, obj):
        return f'{obj.employee_id}-{obj.name}'

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        if not ser.is_valid():
            return Response(api_error('验证失败', errors=ser.errors), status=400)
        emp = ser.save()
        self.log_create(request, emp)
        return Response(api_success(EmployeeSerializer(emp).data), status=201)


class EmployeeDetailAPIView(LoggingMixin, generics.RetrieveUpdateDestroyAPIView):
    """员工详情、更新、删除"""
    queryset = Employee.objects.select_related('department', 'position', 'user').all()
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated, HasRBACPermission]
    log_model_name = '员工'

    # RBAC 权限
    def get_rbac_permissions(self):
        if self.request.method in ['PUT', 'PATCH']:
            return [Permissions.EMPLOYEE_EDIT]
        if self.request.method == 'DELETE':
            return [Permissions.EMPLOYEE_DELETE]
        return [Permissions.EMPLOYEE_VIEW]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return EmployeeWriteSerializer
        return EmployeeSerializer

    def get_log_detail(self, obj):
        return f'{obj.employee_id}-{obj.name}'

    def update(self, request, *args, **kwargs):
        partial = request.method == 'PATCH'
        instance = self.get_object()
        ser = self.get_serializer(instance, data=request.data, partial=partial)
        if not ser.is_valid():
            return Response(api_error('验证失败', errors=ser.errors), status=400)
        emp = ser.save()
        self.log_update(request, emp)
        return Response(api_success(EmployeeSerializer(emp).data))

    def destroy(self, request, *args, **kwargs):
        emp = self.get_object()
        self.log_delete(request, emp)
        detail = self.get_log_detail(emp)

        # 同时删除关联的 User 账号，这样邮箱可以重新注册
        user = emp.user
        emp.delete()
        if user:
            user.delete()

        return Response(api_success(detail=f'已删除 {detail}'))


class CurrentEmployeeAPIView(LoggingMixin, generics.RetrieveUpdateAPIView):
    """获取和更新当前登录用户的员工信息"""
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated]
    log_model_name = '个人信息'

    def get_object(self):
        try:
            return Employee.objects.select_related('department', 'position', 'user').get(user=self.request.user)
        except Employee.DoesNotExist:
            raise NotFound('当前用户没有关联的员工档案')

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return EmployeeSelfUpdateSerializer
        return EmployeeSerializer

    def get_log_detail(self, obj):
        return f'{obj.employee_id}-{obj.name}'

    def update(self, request, *args, **kwargs):
        partial = request.method == 'PATCH'
        instance = self.get_object()
        ser = self.get_serializer(instance, data=request.data, partial=partial)
        if not ser.is_valid():
            return Response(api_error('验证失败', errors=ser.errors), status=400)
        emp = ser.save()
        # 完善信息后清除 must_change_password 标记
        if emp.must_change_password and emp.name and emp.phone and emp.email:
            emp.must_change_password = False
            emp.save(update_fields=['must_change_password'])
        log_event(user=request.user, action='完善个人信息', detail=self.get_log_detail(emp), ip=get_client_ip(request))
        return Response(api_success(EmployeeSerializer(emp).data))
