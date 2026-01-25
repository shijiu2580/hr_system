"""用户管理 API 视图"""
from django.contrib.auth.models import User
from rest_framework import generics, permissions
from rest_framework.response import Response

from .base import LoggingMixin
from ...utils import api_error, api_success, get_client_ip, log_event
from ...permissions import HasRBACPermission
from ...rbac import Permissions
from ..serializers import UserSerializer, UserWriteSerializer


class UserListAPIView(generics.ListAPIView):
    """用户列表（只读）"""
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        qs = super().get_queryset()
        unassigned = self.request.query_params.get('unassigned')
        if unassigned == '1':
            qs = qs.filter(employee__isnull=True)
        return qs


class UserListCreateAPIView(LoggingMixin, generics.ListCreateAPIView):
    """用户列表与创建"""
    queryset = User.objects.prefetch_related('roles').all().order_by('-id')
    permission_classes = [permissions.IsAuthenticated, HasRBACPermission]
    log_model_name = '用户'
    
    # RBAC 权限
    def get_rbac_permissions(self):
        if self.request.method == 'POST':
            return [Permissions.USER_CREATE]
        return [Permissions.USER_VIEW]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserWriteSerializer
        return UserSerializer
    
    def get_log_detail(self, obj):
        return obj.username
    
    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        if not ser.is_valid():
            return Response(api_error('验证失败', errors=ser.errors), status=400)
        user = ser.save()
        self.log_create(request, user)
        return Response(api_success(UserSerializer(user).data), status=201)


class UserDetailAPIView(LoggingMixin, generics.RetrieveUpdateDestroyAPIView):
    """用户详情、更新、删除"""
    queryset = User.objects.prefetch_related('roles').all()
    permission_classes = [permissions.IsAuthenticated, HasRBACPermission]
    log_model_name = '用户'
    
    # RBAC 权限
    def get_rbac_permissions(self):
        if self.request.method in ['PUT', 'PATCH']:
            return [Permissions.USER_EDIT]
        if self.request.method == 'DELETE':
            return [Permissions.USER_DELETE]
        return [Permissions.USER_VIEW]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserWriteSerializer
        return UserSerializer
    
    def get_log_detail(self, obj):
        return obj.username
    
    def update(self, request, *args, **kwargs):
        user = self.get_object()
        partial = request.method == 'PATCH'
        ser = self.get_serializer(user, data=request.data, partial=partial)
        if not ser.is_valid():
            return Response(api_error('验证失败', errors=ser.errors), status=400)
        user = ser.save()
        log_event(
            user=request.user, 
            action='更新用户', 
            detail=user.username, 
            ip=get_client_ip(request)
        )
        return Response(api_success(UserSerializer(user).data))
    
    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        if user.is_superuser and User.objects.filter(is_superuser=True).count() == 1:
            return Response(api_error('不能删除最后一个超级管理员', code='last_superuser'), status=400)
        username = user.username
        user.delete()
        log_event(
            user=request.user, 
            action='删除用户', 
            level='WARNING', 
            detail=username, 
            ip=get_client_ip(request)
        )
        return Response(api_success(detail=f'已删除 {username}'))
