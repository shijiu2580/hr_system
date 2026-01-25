"""通用 Mixin 和基础类"""
from rest_framework.response import Response
from rest_framework import status, generics
from django.db.models import Q
from ...utils import log_event, get_client_ip, api_success, api_error
from ...permissions import get_managed_department_ids


class LoggingMixin:
    """为视图添加操作日志记录功能的 Mixin"""
    log_action_create = '创建'
    log_action_update = '更新'
    log_action_delete = '删除'
    log_model_name = ''  # 子类需设置，如 '员工', '部门'
    
    def get_log_detail(self, obj):
        """获取日志详情，子类可覆盖"""
        return str(obj)
    
    def log_create(self, request, obj):
        log_event(
            user=request.user, 
            action=f'{self.log_action_create}{self.log_model_name}',
            detail=self.get_log_detail(obj),
            ip=get_client_ip(request)
        )
    
    def log_update(self, request, obj):
        log_event(
            user=request.user,
            action=f'{self.log_action_update}{self.log_model_name}',
            detail=self.get_log_detail(obj),
            ip=get_client_ip(request)
        )
    
    def log_delete(self, request, obj, level='WARNING'):
        log_event(
            user=request.user,
            action=f'{self.log_action_delete}{self.log_model_name}',
            level=level,
            detail=self.get_log_detail(obj),
            ip=get_client_ip(request)
        )


class OptimizedQueryMixin:
    """优化查询的 Mixin - 自动添加 select_related 和 prefetch_related"""
    
    # 子类可设置这些属性
    select_related_fields = []
    prefetch_related_fields = []
    
    def get_queryset(self):
        qs = super().get_queryset()
        if self.select_related_fields:
            qs = qs.select_related(*self.select_related_fields)
        if self.prefetch_related_fields:
            qs = qs.prefetch_related(*self.prefetch_related_fields)
        return qs


class DepartmentScopeMixin:
    """部门权限范围限制 Mixin - 非管理员只能访问本部门数据"""
    
    # 员工关联字段名，默认为 'employee'
    employee_field = 'employee'
    
    def get_department_filtered_queryset(self, qs):
        """根据用户权限过滤查询集"""
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return qs
        
        # 获取用户管理的部门
        managed_dept_ids = get_managed_department_ids(user)
        
        # 构建过滤条件
        employee_field = self.employee_field
        if managed_dept_ids:
            # 部门经理可以看本部门和自己的
            q = Q(**{f'{employee_field}__user': user}) | Q(**{f'{employee_field}__department_id__in': managed_dept_ids})
        else:
            # 普通员工只能看自己的
            q = Q(**{f'{employee_field}__user': user})
        
        return qs.filter(q)


class StandardResponseMixin:
    """统一响应格式的 Mixin"""
    
    def success_response(self, data=None, message=None, **extra):
        """返回成功响应"""
        return Response(api_success(data, message=message, **extra))
    
    def error_response(self, message, code='error', http_status=status.HTTP_400_BAD_REQUEST, **extra):
        """返回错误响应"""
        return Response(api_error(message, code=code, **extra), status=http_status)
    
    def not_found_response(self, message='资源不存在'):
        """返回 404 响应"""
        return Response(api_error(message, code='not_found'), status=status.HTTP_404_NOT_FOUND)
    
    def forbidden_response(self, message='权限不足'):
        """返回 403 响应"""
        return Response(api_error(message, code='forbidden'), status=status.HTTP_403_FORBIDDEN)


class DateRangeFilterMixin:
    """日期范围过滤 Mixin"""
    
    date_field = 'date'  # 子类可覆盖
    
    def filter_by_date_range(self, qs):
        """根据请求参数过滤日期范围"""
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            qs = qs.filter(**{f'{self.date_field}__gte': date_from})
        if date_to:
            qs = qs.filter(**{f'{self.date_field}__lte': date_to})
        
        return qs


class PaginationMixin:
    """分页相关的便捷方法"""
    
    def get_paginated_response_data(self, data):
        """获取分页响应数据（不包含 Response 对象）"""
        return {
            'count': self.paginator.page.paginator.count if hasattr(self, 'paginator') and self.paginator else len(data),
            'results': data
        }


class SearchFilterMixin:
    """搜索过滤 Mixin"""
    
    # 搜索字段列表，子类需设置
    search_fields = []
    
    def filter_by_search(self, qs):
        """根据 q 参数进行搜索"""
        search = self.request.query_params.get('q', '').strip()
        if not search or not self.search_fields:
            return qs
        
        q_objects = Q()
        for field in self.search_fields:
            q_objects |= Q(**{f'{field}__icontains': search})
        
        return qs.filter(q_objects)


class OrderingMixin:
    """排序 Mixin"""
    
    # 允许排序的字段映射 {参数名: 数据库字段}
    ordering_fields = {}
    default_ordering = '-id'
    
    def apply_ordering(self, qs):
        """应用排序"""
        ordering = self.request.query_params.get('ordering', '')
        
        if ordering:
            raw = ordering.lstrip('-')
            if raw in self.ordering_fields:
                field = self.ordering_fields[raw]
                if ordering.startswith('-'):
                    field = f'-{field}'
                return qs.order_by(field)
        
        if self.default_ordering:
            return qs.order_by(self.default_ordering)
        
        return qs


class EnhancedListCreateView(
    LoggingMixin, 
    OptimizedQueryMixin, 
    StandardResponseMixin, 
    SearchFilterMixin,
    OrderingMixin,
    generics.ListCreateAPIView
):
    """增强的列表创建视图 - 集成所有通用功能"""
    
    def get_queryset(self):
        qs = super().get_queryset()
        qs = self.filter_by_search(qs)
        qs = self.apply_ordering(qs)
        return qs
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return self.error_response('验证失败', errors=serializer.errors)
        instance = serializer.save()
        self.log_create(request, instance)
        return self.success_response(
            self.get_serializer(instance).data, 
            http_status=status.HTTP_201_CREATED
        )


class EnhancedRetrieveUpdateDestroyView(
    LoggingMixin,
    OptimizedQueryMixin,
    StandardResponseMixin,
    generics.RetrieveUpdateDestroyAPIView
):
    """增强的详情更新删除视图"""
    
    def update(self, request, *args, **kwargs):
        partial = request.method == 'PATCH'
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if not serializer.is_valid():
            return self.error_response('验证失败', errors=serializer.errors)
        instance = serializer.save()
        self.log_update(request, instance)
        return self.success_response(self.get_serializer(instance).data)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.log_delete(request, instance)
        detail = self.get_log_detail(instance)
        instance.delete()
        return self.success_response(detail=f'已删除 {detail}')
