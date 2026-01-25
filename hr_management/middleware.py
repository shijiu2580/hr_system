"""
API 响应中间件 - 统一处理响应格式、异常和性能监控
"""
import time
import logging
from django.http import JsonResponse
from django.conf import settings
from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException, ValidationError, AuthenticationFailed, PermissionDenied
from rest_framework import status

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    自定义异常处理器 - 统一 API 错误响应格式
    
    所有 API 错误都会被包装成标准格式:
    {
        "success": false,
        "error": {
            "code": "error_code",
            "message": "错误描述",
            "details": {...}  // 可选
        }
    }
    """
    # 先调用 DRF 默认的异常处理
    response = exception_handler(exc, context)
    
    if response is not None:
        # 构建标准错误格式
        error_data = {
            'success': False,
            'error': {
                'code': 'error',
                'message': '请求处理失败'
            }
        }
        
        # 根据异常类型设置具体信息
        if isinstance(exc, ValidationError):
            error_data['error']['code'] = 'validation_error'
            error_data['error']['message'] = '数据验证失败'
            # 处理验证错误详情
            if isinstance(exc.detail, dict):
                error_data['error']['details'] = exc.detail
            elif isinstance(exc.detail, list):
                error_data['error']['message'] = exc.detail[0] if exc.detail else '数据验证失败'
            else:
                error_data['error']['message'] = str(exc.detail)
                
        elif isinstance(exc, AuthenticationFailed):
            error_data['error']['code'] = 'auth_failed'
            error_data['error']['message'] = str(exc.detail) if exc.detail else '认证失败'
            
        elif isinstance(exc, PermissionDenied):
            error_data['error']['code'] = 'permission_denied'
            error_data['error']['message'] = str(exc.detail) if exc.detail else '权限不足'
            
        elif isinstance(exc, APIException):
            error_data['error']['code'] = exc.default_code if hasattr(exc, 'default_code') else 'api_error'
            error_data['error']['message'] = str(exc.detail) if exc.detail else str(exc)
        
        response.data = error_data
    
    return response


class APIPerformanceMiddleware:
    """
    API 性能监控中间件
    
    功能:
    1. 记录 API 请求耗时
    2. 慢请求告警
    3. 请求统计
    """
    
    # 慢请求阈值（毫秒）
    SLOW_REQUEST_THRESHOLD = 1000
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # 只监控 API 请求
        if not request.path.startswith('/api/'):
            return self.get_response(request)
        
        start_time = time.time()
        
        response = self.get_response(request)
        
        # 计算耗时
        duration_ms = (time.time() - start_time) * 1000
        
        # 添加响应头
        response['X-Request-Duration'] = f'{duration_ms:.2f}ms'
        
        # 慢请求告警
        if duration_ms > self.SLOW_REQUEST_THRESHOLD:
            logger.warning(
                f'慢请求告警: {request.method} {request.path} 耗时 {duration_ms:.2f}ms',
                extra={
                    'path': request.path,
                    'method': request.method,
                    'duration_ms': duration_ms,
                    'user': request.user.username if request.user.is_authenticated else 'anonymous'
                }
            )
        
        # DEBUG 模式下打印请求信息
        if settings.DEBUG:
            logger.debug(f'{request.method} {request.path} - {response.status_code} - {duration_ms:.2f}ms')
        
        return response


class CORSDebugMiddleware:
    """
    CORS 调试中间件 - 开发环境用于排查跨域问题
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # 只在 DEBUG 模式下添加 CORS 调试头
        if settings.DEBUG:
            origin = request.META.get('HTTP_ORIGIN', '')
            if origin:
                response['X-CORS-Origin'] = origin
        
        return response


class GZipAPIMiddleware:
    """
    API 响应压缩中间件
    
    对于大于阈值的 JSON 响应自动启用 gzip 压缩
    （Django 自带的 GZipMiddleware 对所有响应生效，这个只针对 API）
    """
    
    # 压缩阈值（字节）
    MIN_COMPRESS_LENGTH = 1024  # 1KB
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # 只处理 API 请求
        if not request.path.startswith('/api/'):
            return response
        
        # 检查客户端是否支持 gzip
        accept_encoding = request.META.get('HTTP_ACCEPT_ENCODING', '')
        if 'gzip' not in accept_encoding:
            return response
        
        # 检查响应类型和大小
        content_type = response.get('Content-Type', '')
        if 'application/json' not in content_type:
            return response
        
        # 已经是流响应或已压缩
        if response.streaming or response.get('Content-Encoding'):
            return response
        
        # 检查响应大小
        content = response.content
        if len(content) < self.MIN_COMPRESS_LENGTH:
            return response
        
        # 压缩响应
        import gzip
        compressed = gzip.compress(content)
        
        # 只有压缩后更小才使用
        if len(compressed) < len(content):
            response.content = compressed
            response['Content-Encoding'] = 'gzip'
            response['Content-Length'] = len(compressed)
            response['Vary'] = 'Accept-Encoding'
        
        return response


class SecurityHeadersMiddleware:
    """
    安全响应头中间件
    
    添加各种安全相关的 HTTP 响应头
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # API 请求添加安全头
        if request.path.startswith('/api/'):
            # 防止 MIME 类型嗅探
            response['X-Content-Type-Options'] = 'nosniff'
            
            # 防止页面被嵌入 iframe
            response['X-Frame-Options'] = 'DENY'
            
            # XSS 保护
            response['X-XSS-Protection'] = '1; mode=block'
            
            # 禁止缓存敏感数据
            if request.path.startswith('/api/auth/'):
                response['Cache-Control'] = 'no-store, no-cache, must-revalidate, private'
                response['Pragma'] = 'no-cache'
        
        return response


class RequestLoggingMiddleware:
    """
    请求日志中间件 - 记录所有 API 请求
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # 只记录 API 请求
        if not request.path.startswith('/api/'):
            return self.get_response(request)
        
        response = self.get_response(request)
        
        # 记录非成功请求
        if response.status_code >= 400:
            user = request.user.username if request.user.is_authenticated else 'anonymous'
            logger.warning(
                f'API 错误: {request.method} {request.path} - {response.status_code}',
                extra={
                    'path': request.path,
                    'method': request.method,
                    'status_code': response.status_code,
                    'user': user,
                    'ip': self._get_client_ip(request)
                }
            )
        
        return response
    
    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '')

