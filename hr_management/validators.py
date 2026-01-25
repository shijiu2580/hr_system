"""
增强的数据验证器

提供常用的验证规则和自定义验证器
"""
from rest_framework import serializers
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
import re
from datetime import date, datetime


# ============ 正则验证器 ============

phone_validator = RegexValidator(
    regex=r'^1[3-9]\d{9}$',
    message='请输入有效的手机号码'
)

id_card_validator = RegexValidator(
    regex=r'^\d{17}[\dXx]$',
    message='请输入有效的身份证号码'
)

employee_id_validator = RegexValidator(
    regex=r'^[A-Za-z0-9_-]{1,20}$',
    message='工号只能包含字母、数字、下划线和连字符，长度1-20'
)

username_validator = RegexValidator(
    regex=r'^[a-zA-Z][a-zA-Z0-9_]{2,19}$',
    message='用户名必须以字母开头，只能包含字母、数字和下划线，长度3-20'
)


# ============ 自定义验证函数 ============

def validate_id_card_checksum(id_card):
    """验证身份证校验码"""
    if not id_card or len(id_card) != 18:
        return False
    
    weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
    check_codes = '10X98765432'
    
    try:
        total = sum(int(id_card[i]) * weights[i] for i in range(17))
        return check_codes[total % 11] == id_card[-1].upper()
    except (ValueError, IndexError):
        return False


def validate_date_not_future(value):
    """验证日期不能是未来"""
    if isinstance(value, datetime):
        value = value.date()
    if value > date.today():
        raise serializers.ValidationError('日期不能是未来')


def validate_date_not_past(value):
    """验证日期不能是过去"""
    if isinstance(value, datetime):
        value = value.date()
    if value < date.today():
        raise serializers.ValidationError('日期不能是过去')


def validate_positive_decimal(value):
    """验证正数"""
    if value is not None and value < 0:
        raise serializers.ValidationError('数值必须为正数')


def validate_percentage(value):
    """验证百分比 (0-100)"""
    if value is not None and (value < 0 or value > 100):
        raise serializers.ValidationError('百分比必须在 0-100 之间')


def validate_file_size(max_size_mb):
    """文件大小验证器工厂"""
    def validator(file):
        if file.size > max_size_mb * 1024 * 1024:
            raise serializers.ValidationError(f'文件大小不能超过 {max_size_mb}MB')
    return validator


def validate_file_extension(allowed_extensions):
    """文件扩展名验证器工厂"""
    def validator(file):
        ext = file.name.split('.')[-1].lower() if '.' in file.name else ''
        if ext not in allowed_extensions:
            raise serializers.ValidationError(
                f'不支持的文件类型，允许: {", ".join(allowed_extensions)}'
            )
    return validator


# ============ 自定义字段 ============

class PhoneField(serializers.CharField):
    """手机号字段"""
    
    def __init__(self, **kwargs):
        kwargs.setdefault('max_length', 11)
        kwargs.setdefault('min_length', 11)
        super().__init__(**kwargs)
        self.validators.append(phone_validator)


class IDCardField(serializers.CharField):
    """身份证号字段"""
    
    def __init__(self, **kwargs):
        kwargs.setdefault('max_length', 18)
        kwargs.setdefault('min_length', 18)
        super().__init__(**kwargs)
        self.validators.append(id_card_validator)
    
    def to_internal_value(self, data):
        value = super().to_internal_value(data)
        if value and not validate_id_card_checksum(value):
            raise serializers.ValidationError('身份证号码校验失败')
        return value.upper() if value else value


class EmployeeIDField(serializers.CharField):
    """工号字段"""
    
    def __init__(self, **kwargs):
        kwargs.setdefault('max_length', 20)
        super().__init__(**kwargs)
        self.validators.append(employee_id_validator)


class MoneyField(serializers.DecimalField):
    """金额字段"""
    
    def __init__(self, **kwargs):
        kwargs.setdefault('max_digits', 12)
        kwargs.setdefault('decimal_places', 2)
        kwargs.setdefault('min_value', 0)
        super().__init__(**kwargs)


class PercentageField(serializers.DecimalField):
    """百分比字段"""
    
    def __init__(self, **kwargs):
        kwargs.setdefault('max_digits', 5)
        kwargs.setdefault('decimal_places', 2)
        kwargs.setdefault('min_value', 0)
        kwargs.setdefault('max_value', 100)
        super().__init__(**kwargs)


class SafeCharField(serializers.CharField):
    """
    安全字符字段 - 自动清理危险字符
    """
    
    def __init__(self, strip_html=True, **kwargs):
        self.strip_html = strip_html
        super().__init__(**kwargs)
    
    def to_internal_value(self, data):
        value = super().to_internal_value(data)
        if value and self.strip_html:
            # 移除 HTML 标签
            value = re.sub(r'<[^>]+>', '', value)
            # 移除潜在的 XSS 字符
            value = re.sub(r'javascript:', '', value, flags=re.IGNORECASE)
            value = re.sub(r'on\w+\s*=', '', value, flags=re.IGNORECASE)
        return value


class DateRangeField(serializers.Serializer):
    """日期范围字段"""
    
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)
    
    def validate(self, attrs):
        if attrs['start_date'] > attrs['end_date']:
            raise serializers.ValidationError('开始日期不能晚于结束日期')
        return attrs


# ============ 验证 Mixin ============

class DateRangeValidationMixin:
    """日期范围验证 Mixin"""
    
    def validate(self, attrs):
        attrs = super().validate(attrs)
        
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError({
                'end_date': '结束日期不能早于开始日期'
            })
        
        return attrs


class UniqueTogetherValidationMixin:
    """
    联合唯一验证 Mixin
    
    在 Meta 中定义 unique_together_fields
    """
    
    def validate(self, attrs):
        attrs = super().validate(attrs)
        
        unique_fields = getattr(self.Meta, 'unique_together_fields', None)
        if not unique_fields:
            return attrs
        
        model = self.Meta.model
        filter_kwargs = {field: attrs.get(field) for field in unique_fields if attrs.get(field)}
        
        if len(filter_kwargs) == len(unique_fields):
            queryset = model.objects.filter(**filter_kwargs)
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise serializers.ValidationError(
                    f"具有相同 {', '.join(unique_fields)} 的记录已存在"
                )
        
        return attrs


class TrimWhitespaceMixin:
    """
    自动去除字符串首尾空白 Mixin
    """
    
    def to_internal_value(self, data):
        if isinstance(data, dict):
            data = {
                key: value.strip() if isinstance(value, str) else value
                for key, value in data.items()
            }
        return super().to_internal_value(data)


# ============ 通用验证规则 ============

COMMON_VALIDATORS = {
    'phone': [phone_validator],
    'id_card': [id_card_validator],
    'employee_id': [employee_id_validator],
    'username': [username_validator],
    'positive': [validate_positive_decimal],
    'percentage': [validate_percentage],
    'not_future': [validate_date_not_future],
    'not_past': [validate_date_not_past],
}


def get_validators(types):
    """
    获取验证器列表
    
    Example:
        validators = get_validators(['phone', 'positive'])
    """
    validators = []
    for t in types:
        validators.extend(COMMON_VALIDATORS.get(t, []))
    return validators
