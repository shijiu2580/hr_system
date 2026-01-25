"""
API 版本控制模块
支持 URL 路径版本控制和向后兼容
"""
from django.urls import path, include
from functools import wraps
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


# API 版本配置
API_VERSIONS = {
    'v1': {
        'status': 'stable',
        'released': '2024-01-01',
        'deprecated': False,
        'sunset_date': None,
    },
    'v2': {
        'status': 'beta',
        'released': '2025-01-01',
        'deprecated': False,
        'sunset_date': None,
    }
}

CURRENT_VERSION = 'v1'
LATEST_VERSION = 'v2'


class APIVersionManager:
    """API 版本管理器"""
    
    @staticmethod
    def get_version_info(version: str) -> dict:
        """获取版本信息"""
        return API_VERSIONS.get(version, {})
    
    @staticmethod
    def is_deprecated(version: str) -> bool:
        """检查版本是否已弃用"""
        info = API_VERSIONS.get(version, {})
        return info.get('deprecated', False)
    
    @staticmethod
    def get_sunset_date(version: str) -> str:
        """获取版本日落日期"""
        info = API_VERSIONS.get(version, {})
        return info.get('sunset_date')
    
    @staticmethod
    def get_all_versions() -> list:
        """获取所有版本"""
        return list(API_VERSIONS.keys())


def version_header_middleware(get_response):
    """
    添加 API 版本响应头的中间件
    """
    def middleware(request):
        response = get_response(request)
        
        # 从 URL 提取版本
        path = request.path
        version = None
        for v in API_VERSIONS.keys():
            if f'/api/{v}/' in path:
                version = v
                break
        
        if version:
            response['X-API-Version'] = version
            response['X-API-Latest-Version'] = LATEST_VERSION
            
            # 如果是弃用版本，添加警告头
            if APIVersionManager.is_deprecated(version):
                sunset = APIVersionManager.get_sunset_date(version)
                response['X-API-Deprecated'] = 'true'
                if sunset:
                    response['X-API-Sunset-Date'] = sunset
                    response['Warning'] = f'299 - "This API version is deprecated and will be removed on {sunset}"'
        
        return response
    
    return middleware


def deprecated_endpoint(message: str = None, alternative: str = None):
    """
    标记端点为已弃用的装饰器
    
    Usage:
        @deprecated_endpoint(
            message="This endpoint will be removed in v2",
            alternative="/api/v2/new-endpoint/"
        )
        def old_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            response = view_func(request, *args, **kwargs)
            
            # 添加弃用警告头
            response['X-Deprecated'] = 'true'
            
            warning_parts = ['299 - "This endpoint is deprecated']
            if message:
                warning_parts.append(f': {message}')
            if alternative:
                warning_parts.append(f'. Use {alternative} instead')
            warning_parts.append('"')
            
            response['Warning'] = ''.join(warning_parts)
            
            return response
        return wrapper
    return decorator


def api_version_view(view_class, version_handlers: dict):
    """
    创建支持多版本的视图
    
    Usage:
        urlpatterns = [
            path('endpoint/', api_version_view(
                DefaultView,
                {'v2': V2View}
            )),
        ]
    """
    class VersionedView:
        def __new__(cls, *args, **kwargs):
            request = args[0] if args else kwargs.get('request')
            
            # 从请求头或 URL 获取版本
            version = None
            if request:
                version = request.headers.get('X-API-Version')
                if not version:
                    # 从 URL 路径提取
                    for v in API_VERSIONS.keys():
                        if f'/api/{v}/' in request.path:
                            version = v
                            break
            
            # 选择对应版本的视图
            handler_class = version_handlers.get(version, view_class)
            return handler_class.as_view()(*args, **kwargs)
    
    return VersionedView


@api_view(['GET'])
def api_versions(request):
    """返回所有 API 版本信息"""
    versions = {}
    for version, info in API_VERSIONS.items():
        versions[version] = {
            **info,
            'url': f'/api/{version}/',
            'docs': f'/api/{version}/docs/',
        }
    
    return Response({
        'current_version': CURRENT_VERSION,
        'latest_version': LATEST_VERSION,
        'versions': versions,
    })


@api_view(['GET'])
def api_changelog(request):
    """返回 API 变更日志"""
    changelog = [
        {
            'version': 'v1.0.0',
            'date': '2024-01-01',
            'changes': [
                {'type': 'added', 'description': '初始 API 发布'},
                {'type': 'added', 'description': '员工管理模块'},
                {'type': 'added', 'description': '考勤管理模块'},
                {'type': 'added', 'description': '请假管理模块'},
                {'type': 'added', 'description': '薪资管理模块'},
            ]
        },
        {
            'version': 'v1.1.0',
            'date': '2024-06-01',
            'changes': [
                {'type': 'added', 'description': 'RBAC 权限系统'},
                {'type': 'added', 'description': '出差申请模块'},
                {'type': 'added', 'description': '差旅报销模块'},
                {'type': 'improved', 'description': '考勤补卡功能'},
            ]
        },
        {
            'version': 'v1.2.0',
            'date': '2024-12-01',
            'changes': [
                {'type': 'added', 'description': '多地点签到支持'},
                {'type': 'added', 'description': '离职流程管理'},
                {'type': 'improved', 'description': 'API 性能优化'},
                {'type': 'improved', 'description': '缓存策略增强'},
            ]
        },
    ]
    
    return Response({
        'changelog': changelog,
        'total_versions': len(changelog),
    })


def create_versioned_urlpatterns(urlpatterns, version='v1'):
    """
    为 URL 模式添加版本前缀
    
    Usage:
        versioned_urls = create_versioned_urlpatterns(api_urlpatterns, 'v1')
    """
    return [
        path(f'{version}/', include((urlpatterns, 'api'), namespace=version))
    ]
