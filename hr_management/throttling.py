"""
自定义 API 限流策略
"""
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle, SimpleRateThrottle


class BurstRateThrottle(UserRateThrottle):
    """
    突发流量限制 - 短期内的请求限制
    适用于防止短时间内大量请求
    """
    scope = 'burst'
    

class SustainedRateThrottle(UserRateThrottle):
    """
    持续流量限制 - 长期的请求限制
    适用于限制用户每天的总请求数
    """
    scope = 'sustained'


class LoginRateThrottle(AnonRateThrottle):
    """
    登录接口限流 - 防止暴力破解
    """
    scope = 'login'
    
    def get_cache_key(self, request, view):
        # 基于 IP 地址限流
        ident = self.get_ident(request)
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }


class PasswordResetThrottle(AnonRateThrottle):
    """
    密码重置接口限流 - 防止滥用
    """
    scope = 'password_reset'


class ExportThrottle(UserRateThrottle):
    """
    导出接口限流 - 导出操作消耗资源较多
    """
    scope = 'export'


class UploadThrottle(UserRateThrottle):
    """
    上传接口限流 - 限制上传频率
    """
    scope = 'upload'


class ReportThrottle(UserRateThrottle):
    """
    报表生成限流 - 报表生成消耗资源较多
    """
    scope = 'report'


class ScopedRateThrottleMixin:
    """
    基于权限范围的限流 Mixin
    高级用户可以有更高的限流配额
    """
    
    def get_rate(self):
        # 检查用户是否是管理员
        if hasattr(self, 'request') and self.request.user.is_authenticated:
            if self.request.user.is_superuser or self.request.user.is_staff:
                # 管理员使用更宽松的限制
                return self.get_admin_rate()
        return super().get_rate()
    
    def get_admin_rate(self):
        """管理员的限流速率，子类可以覆盖"""
        # 默认是普通用户的 3 倍
        rate = super().get_rate()
        if rate:
            num_requests, duration = self.parse_rate(rate)
            return f'{num_requests * 3}/{duration}'
        return rate


class AdminBurstThrottle(ScopedRateThrottleMixin, BurstRateThrottle):
    """管理员突发流量限制"""
    pass


class AdminSustainedThrottle(ScopedRateThrottleMixin, SustainedRateThrottle):
    """管理员持续流量限制"""
    pass


# 默认限流配置
DEFAULT_THROTTLE_RATES = {
    # 基础限流
    'anon': '30/min',           # 匿名用户：每分钟 30 次
    'user': '120/min',          # 登录用户：每分钟 120 次
    
    # 自定义限流
    'burst': '60/min',          # 突发限流：每分钟 60 次
    'sustained': '10000/day',   # 持续限流：每天 10000 次
    'login': '5/min',           # 登录限流：每分钟 5 次
    'password_reset': '3/hour', # 密码重置：每小时 3 次
    'export': '10/hour',        # 导出限流：每小时 10 次
    'upload': '30/hour',        # 上传限流：每小时 30 次
    'report': '20/hour',        # 报表限流：每小时 20 次
}


def get_throttle_classes_for_view(view_type='default'):
    """
    根据视图类型获取合适的限流类
    
    Args:
        view_type: 视图类型，可选值：
            - 'default': 默认限流
            - 'login': 登录接口
            - 'export': 导出接口
            - 'upload': 上传接口
            - 'report': 报表接口
            - 'sensitive': 敏感操作
    
    Returns:
        限流类列表
    """
    throttle_map = {
        'default': [BurstRateThrottle, SustainedRateThrottle],
        'login': [LoginRateThrottle],
        'password_reset': [PasswordResetThrottle],
        'export': [ExportThrottle],
        'upload': [UploadThrottle],
        'report': [ReportThrottle],
        'sensitive': [BurstRateThrottle],  # 敏感操作使用更严格的突发限流
    }
    return throttle_map.get(view_type, throttle_map['default'])
