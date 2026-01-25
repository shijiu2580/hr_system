"""RBAC 权限与角色管理 API 视图"""
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .base import LoggingMixin
from ...models import Role, RBACPermission
from ...utils import api_error, api_success, log_event
from ...rbac import PERMISSION_GROUPS, Permissions
from ...permissions import HasRBACPermission
from ..serializers import (
    RoleSerializer, RoleWriteSerializer,
    RBACPermissionSerializer, RBACPermissionWriteSerializer
)


class RoleListAPIView(generics.ListAPIView):
    """角色列表（只读）"""
    queryset = Role.objects.prefetch_related('permissions').all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated]


class PermissionListAPIView(generics.ListAPIView):
    """权限列表（只读）"""
    queryset = RBACPermission.objects.all().order_by('id')
    serializer_class = RBACPermissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None  # 不分页，返回全部


class PermissionGroupsAPIView(APIView):
    """获取权限分组信息"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        # 获取数据库中的所有权限
        db_perms = {p.key: p for p in RBACPermission.objects.all()}
        
        groups = []
        for group_name, perms in PERMISSION_GROUPS.items():
            group_perms = []
            for key, name, desc in perms:
                perm = db_perms.get(key)
                if perm:
                    group_perms.append({
                        'id': perm.id,
                        'key': key,
                        'name': name,
                        'description': desc,
                    })
            groups.append({
                'name': group_name,
                'permissions': group_perms
            })
        
        return Response(api_success(groups))


class PermissionListCreateAPIView(LoggingMixin, generics.ListCreateAPIView):
    """权限列表与创建（管理用）"""
    queryset = RBACPermission.objects.all().order_by('id')
    serializer_class = RBACPermissionSerializer
    permission_classes = [permissions.IsAuthenticated, HasRBACPermission]
    rbac_perms = [Permissions.RBAC_PERMISSION_MANAGE]
    pagination_class = None  # 不分页，返回全部
    log_model_name = '权限'
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return RBACPermissionWriteSerializer
        return RBACPermissionSerializer
    
    def get_log_detail(self, obj):
        return obj.key
    
    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        if not ser.is_valid():
            return Response(api_error('验证失败', errors=ser.errors), status=400)
        perm = ser.save()
        self.log_create(request, perm)
        return Response(api_success(RBACPermissionSerializer(perm).data), status=201)


class PermissionDetailAPIView(LoggingMixin, generics.RetrieveUpdateDestroyAPIView):
    """权限详情、更新、删除"""
    queryset = RBACPermission.objects.all()
    serializer_class = RBACPermissionSerializer
    permission_classes = [permissions.IsAuthenticated, HasRBACPermission]
    rbac_perms = [Permissions.RBAC_PERMISSION_MANAGE]
    log_model_name = '权限'
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return RBACPermissionWriteSerializer
        return RBACPermissionSerializer
    
    def get_log_detail(self, obj):
        return obj.key
    
    def update(self, request, *args, **kwargs):
        partial = request.method == 'PATCH'
        instance = self.get_object()
        ser = self.get_serializer(instance, data=request.data, partial=partial)
        if not ser.is_valid():
            return Response(api_error('验证失败', errors=ser.errors), status=400)
        perm = ser.save()
        self.log_update(request, perm)
        return Response(api_success(RBACPermissionSerializer(perm).data))
    
    def destroy(self, request, *args, **kwargs):
        perm = self.get_object()
        self.log_delete(request, perm)
        key = perm.key
        perm.delete()
        return Response(api_success(detail=f'已删除 {key}'))


class RoleListCreateAPIView(LoggingMixin, generics.ListCreateAPIView):
    """角色列表与创建"""
    queryset = Role.objects.prefetch_related('permissions').all().order_by('code')
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated, HasRBACPermission]
    rbac_perms = [Permissions.RBAC_ROLE_MANAGE]
    log_model_name = '角色'
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return RoleWriteSerializer
        return RoleSerializer
    
    def get_log_detail(self, obj):
        return obj.code
    
    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        if not ser.is_valid():
            return Response(api_error('验证失败', errors=ser.errors), status=400)
        role = ser.save()
        self.log_create(request, role)
        return Response(api_success(RoleSerializer(role).data), status=201)


class RoleDetailAPIView(LoggingMixin, generics.RetrieveUpdateDestroyAPIView):
    """角色详情、更新、删除"""
    queryset = Role.objects.prefetch_related('permissions', 'users').all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated, HasRBACPermission]
    rbac_perms = [Permissions.RBAC_ROLE_MANAGE]
    log_model_name = '角色'
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return RoleWriteSerializer
        return RoleSerializer
    
    def get_log_detail(self, obj):
        return obj.code
    
    def update(self, request, *args, **kwargs):
        role = self.get_object()
        partial = request.method == 'PATCH'
        
        # 系统角色：只允许修改用户关联，不允许修改其他字段
        if role.is_system:
            # 只处理用户关联更新
            user_ids = request.data.get('user_ids')
            if user_ids is not None:
                from django.contrib.auth.models import User
                users = User.objects.filter(id__in=user_ids)
                # 更新角色的用户关联
                role.users.set(users)
                self.log_update(request, role)
                return Response(api_success(RoleSerializer(role).data))
            else:
                return Response(api_error('系统角色权限不可修改', code='system_role_locked'), status=400)
        
        ser = self.get_serializer(role, data=request.data, partial=partial)
        if not ser.is_valid():
            return Response(api_error('验证失败', errors=ser.errors), status=400)
        role = ser.save()
        self.log_update(request, role)
        return Response(api_success(RoleSerializer(role).data))
    
    def destroy(self, request, *args, **kwargs):
        role = self.get_object()
        if role.is_system:
            return Response(api_error('系统角色不可删除', code='system_role_locked'), status=400)
        self.log_delete(request, role)
        code = role.code
        role.delete()
        return Response(api_success(detail=f'已删除 {code}'))
