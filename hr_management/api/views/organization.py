"""组织架构（部门与职位）API 视图"""
from rest_framework import generics, permissions
from rest_framework.response import Response

from .base import LoggingMixin
from ...models import Department, Position
from ...permissions import IsStaffOrReadOnly, HasRBACPermission
from ...rbac import Permissions
from ...utils import api_error, api_success
from ..serializers import (
    DepartmentSerializer, DepartmentWriteSerializer,
    PositionSerializer, PositionWriteSerializer
)


class DepartmentListCreateAPIView(LoggingMixin, generics.ListCreateAPIView):
    """部门列表与创建"""
    queryset = Department.objects.all().order_by('name')
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated, HasRBACPermission]
    log_model_name = '部门'
    
    # RBAC 权限
    def get_rbac_permissions(self):
        if self.request.method == 'POST':
            return [Permissions.DEPARTMENT_CREATE]
        return [Permissions.DEPARTMENT_VIEW]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return DepartmentWriteSerializer
        return DepartmentSerializer
    
    def get_log_detail(self, obj):
        return obj.name

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        if not ser.is_valid():
            return Response(api_error('验证失败', errors=ser.errors), status=400)
        dept = ser.save()
        self.log_create(request, dept)
        return Response(api_success(DepartmentSerializer(dept).data), status=201)


class DepartmentDetailAPIView(LoggingMixin, generics.RetrieveUpdateDestroyAPIView):
    """部门详情、更新、删除"""
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated, HasRBACPermission]
    log_model_name = '部门'
    
    # RBAC 权限
    def get_rbac_permissions(self):
        if self.request.method in ['PUT', 'PATCH']:
            return [Permissions.DEPARTMENT_EDIT]
        if self.request.method == 'DELETE':
            return [Permissions.DEPARTMENT_DELETE]
        return [Permissions.DEPARTMENT_VIEW]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return DepartmentWriteSerializer
        return DepartmentSerializer
    
    def get_log_detail(self, obj):
        return obj.name

    def update(self, request, *args, **kwargs):
        partial = request.method == 'PATCH'
        instance = self.get_object()
        ser = self.get_serializer(instance, data=request.data, partial=partial)
        if not ser.is_valid():
            return Response(api_error('验证失败', errors=ser.errors), status=400)
        dept = ser.save()
        self.log_update(request, dept)
        return Response(api_success(DepartmentSerializer(dept).data))

    def destroy(self, request, *args, **kwargs):
        dept = self.get_object()
        self.log_delete(request, dept)
        name = dept.name
        dept.delete()
        return Response(api_success(detail=f'已删除 {name}'))


class PositionListCreateAPIView(LoggingMixin, generics.ListCreateAPIView):
    """职位列表与创建"""
    queryset = Position.objects.select_related('department').all().order_by('department__name', 'name')
    serializer_class = PositionSerializer
    permission_classes = [permissions.IsAuthenticated, HasRBACPermission]
    log_model_name = '职位'
    
    # RBAC 权限
    def get_rbac_permissions(self):
        if self.request.method == 'POST':
            return [Permissions.POSITION_CREATE]
        return [Permissions.POSITION_VIEW]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PositionWriteSerializer
        return PositionSerializer
    
    def get_log_detail(self, obj):
        return f'{obj.department.name}-{obj.name}'

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        if not ser.is_valid():
            return Response(api_error('验证失败', errors=ser.errors), status=400)
        pos = ser.save()
        self.log_create(request, pos)
        return Response(api_success(PositionSerializer(pos).data), status=201)


class PositionDetailAPIView(LoggingMixin, generics.RetrieveUpdateDestroyAPIView):
    """职位详情、更新、删除"""
    queryset = Position.objects.select_related('department').all()
    serializer_class = PositionSerializer
    permission_classes = [permissions.IsAuthenticated, HasRBACPermission]
    log_model_name = '职位'
    
    # RBAC 权限
    def get_rbac_permissions(self):
        if self.request.method in ['PUT', 'PATCH']:
            return [Permissions.POSITION_EDIT]
        if self.request.method == 'DELETE':
            return [Permissions.POSITION_DELETE]
        return [Permissions.POSITION_VIEW]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return PositionWriteSerializer
        return PositionSerializer
    
    def get_log_detail(self, obj):
        return f'{obj.department.name}-{obj.name}'

    def update(self, request, *args, **kwargs):
        partial = request.method == 'PATCH'
        instance = self.get_object()
        ser = self.get_serializer(instance, data=request.data, partial=partial)
        if not ser.is_valid():
            return Response(api_error('验证失败', errors=ser.errors), status=400)
        pos = ser.save()
        self.log_update(request, pos)
        return Response(api_success(PositionSerializer(pos).data))

    def destroy(self, request, *args, **kwargs):
        pos = self.get_object()
        self.log_delete(request, pos)
        detail = self.get_log_detail(pos)
        pos.delete()
        return Response(api_success(detail=f'已删除 {detail}'))
