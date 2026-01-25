"""
安全增强模块 - 输入验证、安全检查、防护措施
"""
import re
import html
import hashlib
import secrets
from typing import Any, Dict, List, Optional
from functools import wraps
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags
from rest_framework import serializers


class InputValidator:
    """输入验证器 - 防止 XSS、SQL 注入等攻击"""
    
    # 危险字符模式
    SQL_INJECTION_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER|CREATE|TRUNCATE)\b)",
        r"(--|#|/\*|\*/)",
        r"(\bOR\b\s+\d+\s*=\s*\d+)",
        r"(\bAND\b\s+\d+\s*=\s*\d+)",
        r"(;\s*\b(SELECT|INSERT|UPDATE|DELETE|DROP)\b)",
    ]
    
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe[^>]*>",
        r"<object[^>]*>",
        r"<embed[^>]*>",
    ]
    
    # 文件扩展名白名单
    ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp'}
    ALLOWED_DOCUMENT_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt'}
    ALLOWED_ARCHIVE_EXTENSIONS = {'zip', 'rar', '7z'}
    
    @classmethod
    def sanitize_string(cls, value: str, max_length: int = None) -> str:
        """
        清理字符串输入
        - 移除 HTML 标签
        - 转义特殊字符
        - 限制长度
        """
        if not isinstance(value, str):
            return value
        
        # 移除 HTML 标签
        value = strip_tags(value)
        # 转义 HTML 特殊字符
        value = html.escape(value)
        # 移除多余空白
        value = ' '.join(value.split())
        # 限制长度
        if max_length and len(value) > max_length:
            value = value[:max_length]
        
        return value
    
    @classmethod
    def check_sql_injection(cls, value: str) -> bool:
        """检查是否包含 SQL 注入风险"""
        if not isinstance(value, str):
            return False
        
        value_upper = value.upper()
        for pattern in cls.SQL_INJECTION_PATTERNS:
            if re.search(pattern, value_upper, re.IGNORECASE):
                return True
        return False
    
    @classmethod
    def check_xss(cls, value: str) -> bool:
        """检查是否包含 XSS 风险"""
        if not isinstance(value, str):
            return False
        
        for pattern in cls.XSS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                return True
        return False
    
    @classmethod
    def validate_file_extension(cls, filename: str, allowed_types: str = 'image') -> bool:
        """验证文件扩展名"""
        if not filename:
            return False
        
        ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
        
        allowed_map = {
            'image': cls.ALLOWED_IMAGE_EXTENSIONS,
            'document': cls.ALLOWED_DOCUMENT_EXTENSIONS,
            'archive': cls.ALLOWED_ARCHIVE_EXTENSIONS,
            'all': cls.ALLOWED_IMAGE_EXTENSIONS | cls.ALLOWED_DOCUMENT_EXTENSIONS | cls.ALLOWED_ARCHIVE_EXTENSIONS,
        }
        
        allowed = allowed_map.get(allowed_types, cls.ALLOWED_IMAGE_EXTENSIONS)
        return ext in allowed
    
    @classmethod
    def validate_phone(cls, phone: str) -> bool:
        """验证手机号格式"""
        if not phone:
            return True  # 允许空值
        pattern = r'^1[3-9]\d{9}$'
        return bool(re.match(pattern, phone))
    
    @classmethod
    def validate_email(cls, email: str) -> bool:
        """验证邮箱格式"""
        if not email:
            return True  # 允许空值
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @classmethod
    def validate_id_card(cls, id_card: str) -> bool:
        """验证身份证号格式（中国大陆）"""
        if not id_card:
            return True  # 允许空值
        
        # 18位身份证验证
        pattern = r'^[1-9]\d{5}(19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]$'
        if not re.match(pattern, id_card):
            return False
        
        # 校验码验证
        weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
        check_codes = '10X98765432'
        
        try:
            total = sum(int(id_card[i]) * weights[i] for i in range(17))
            return check_codes[total % 11] == id_card[-1].upper()
        except (ValueError, IndexError):
            return False


class SecureSerializerMixin:
    """安全序列化器 Mixin - 自动验证和清理输入"""
    
    def validate(self, attrs):
        """通用验证 - 检查所有字符串字段"""
        attrs = super().validate(attrs)
        
        for field_name, value in attrs.items():
            if isinstance(value, str):
                # 检查 SQL 注入
                if InputValidator.check_sql_injection(value):
                    raise serializers.ValidationError({
                        field_name: '输入包含不安全字符'
                    })
                # 检查 XSS
                if InputValidator.check_xss(value):
                    raise serializers.ValidationError({
                        field_name: '输入包含不安全的 HTML 内容'
                    })
        
        return attrs


class SanitizedCharField(serializers.CharField):
    """自动清理的字符字段"""
    
    def __init__(self, *args, sanitize=True, **kwargs):
        self.sanitize = sanitize
        super().__init__(*args, **kwargs)
    
    def to_internal_value(self, data):
        value = super().to_internal_value(data)
        if self.sanitize and isinstance(value, str):
            value = InputValidator.sanitize_string(value, self.max_length)
        return value


class PhoneField(serializers.CharField):
    """手机号字段"""
    
    def to_internal_value(self, data):
        value = super().to_internal_value(data)
        if value and not InputValidator.validate_phone(value):
            raise serializers.ValidationError('请输入有效的手机号')
        return value


class IDCardField(serializers.CharField):
    """身份证号字段"""
    
    def to_internal_value(self, data):
        value = super().to_internal_value(data)
        if value and not InputValidator.validate_id_card(value):
            raise serializers.ValidationError('请输入有效的身份证号')
        return value


class SecurityUtils:
    """安全工具类"""
    
    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """生成安全随机令牌"""
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def hash_sensitive_data(data: str, salt: str = None) -> str:
        """哈希敏感数据"""
        if salt is None:
            salt = secrets.token_hex(16)
        hashed = hashlib.sha256((data + salt).encode()).hexdigest()
        return f"{salt}${hashed}"
    
    @staticmethod
    def verify_hashed_data(data: str, hashed: str) -> bool:
        """验证哈希数据"""
        try:
            salt, expected = hashed.split('$')
            actual = hashlib.sha256((data + salt).encode()).hexdigest()
            return secrets.compare_digest(actual, expected)
        except ValueError:
            return False
    
    @staticmethod
    def mask_sensitive_info(value: str, mask_char: str = '*', visible_start: int = 3, visible_end: int = 4) -> str:
        """遮蔽敏感信息"""
        if not value or len(value) <= visible_start + visible_end:
            return value
        
        masked_length = len(value) - visible_start - visible_end
        return value[:visible_start] + mask_char * masked_length + value[-visible_end:]
    
    @staticmethod
    def mask_phone(phone: str) -> str:
        """遮蔽手机号"""
        if not phone or len(phone) != 11:
            return phone
        return phone[:3] + '****' + phone[-4:]
    
    @staticmethod
    def mask_id_card(id_card: str) -> str:
        """遮蔽身份证号"""
        if not id_card or len(id_card) < 10:
            return id_card
        return id_card[:6] + '********' + id_card[-4:]
    
    @staticmethod
    def mask_email(email: str) -> str:
        """遮蔽邮箱"""
        if not email or '@' not in email:
            return email
        local, domain = email.rsplit('@', 1)
        if len(local) <= 2:
            masked_local = local[0] + '*'
        else:
            masked_local = local[:2] + '*' * (len(local) - 2)
        return f"{masked_local}@{domain}"


def rate_limit_key(request, view):
    """生成限流键 - 结合用户ID和IP"""
    if request.user.is_authenticated:
        return f"user_{request.user.id}"
    return f"ip_{get_client_ip(request)}"


def get_client_ip(request) -> str:
    """获取客户端真实 IP"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '')
    return ip


class AuditMixin:
    """审计 Mixin - 记录敏感操作"""
    
    audit_actions = ['create', 'update', 'destroy']
    
    def perform_create(self, serializer):
        instance = serializer.save()
        self._log_audit('create', instance)
        return instance
    
    def perform_update(self, serializer):
        instance = serializer.save()
        self._log_audit('update', instance)
        return instance
    
    def perform_destroy(self, instance):
        self._log_audit('destroy', instance)
        instance.delete()
    
    def _log_audit(self, action, instance):
        """记录审计日志"""
        from hr_management.models import SystemLog
        
        request = self.request
        model_name = instance.__class__.__name__
        
        SystemLog.objects.create(
            user=request.user if request.user.is_authenticated else None,
            action=f'{action}_{model_name.lower()}',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
            details={
                'model': model_name,
                'instance_id': getattr(instance, 'id', None),
                'action': action,
            }
        )
