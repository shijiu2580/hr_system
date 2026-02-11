"""通用工具函数集合（日志、响应包装、参数验证等）。"""
from typing import Optional, Any, Dict, List
from functools import wraps
from django.contrib.auth.models import User
from .models import SystemLog


def log_event(action: str, level: str = 'INFO', user: Optional[User] = None, detail: Optional[str] = None, ip: Optional[str] = None):
    """写系统日志的轻量辅助函数。

    使用 try/except 防御，避免日志写入阻断主业务流程。
    参数:
        action: 操作名称（必填）
        level: 日志级别，INFO/WARNING/ERROR/DEBUG
        user: 关联用户，可为空
        detail: 详情文本
        ip: 来源 IP
    """
    if not action:
        return
    try:
        SystemLog.objects.create(action=action, level=level or 'INFO', user=user, detail=detail or '', ip_address=ip)
    except Exception:
        # 静默失败，不影响主流程
        pass


def api_success(data: Any = None, **extra) -> Dict[str, Any]:
    """标准成功响应结构封装。"""
    resp = {'success': True, 'data': data}
    if extra:
        resp.update(extra)
    return resp


def api_error(message: str, code: str = 'error', *, status: int | None = None, **extra) -> Dict[str, Any]:
    """标准错误响应结构封装（供视图组装 Response 时使用）。"""
    err = {'success': False, 'error': {'code': code, 'message': message}}
    if extra:
        err['error'].update(extra)
    if status is not None:
        err['status'] = status  # 仅作为信息，真正 HTTP 状态码由视图层传递
    return err


def get_client_ip(request) -> str:
    """从请求中获取客户端 IP 地址"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


def send_verification_email(email: str, code: str, code_type: str = 'reset_password') -> bool:
    """发送邮箱验证码

    参数:
        email: 邮箱地址
        code: 验证码
        code_type: 验证码类型
    返回:
        bool: 是否发送成功
    """
    from django.conf import settings
    from django.core.mail import EmailMessage

    # 仅在调试模式下打印验证码，避免生产环境泄露
    if settings.DEBUG:
        print(f"\n{'='*50}")
        print(f"[Email] Verification Code")
        print(f"{'='*50}")
        print(f"To: {email}")
        print(f"Code: {code}")
        print(f"Type: {code_type}")
        print(f"{'='*50}\n")

    # 发送邮件
    try:
        subject = '【HR管理系统】验证码'
        purpose = '重置密码' if code_type == 'reset_password' else '身份验证'
        message = f'''您好！

您的验证码是：{code}

此验证码用于{purpose}，5分钟内有效。

如果这不是您的操作，请忽略此邮件。

---
HR管理系统
'''
        from_email = settings.DEFAULT_FROM_EMAIL

        email_msg = EmailMessage(
            subject=subject,
            body=message,
            from_email=from_email,
            to=[email],
        )
        email_msg.encoding = 'utf-8'
        email_msg.send(fail_silently=False)
        print(f"[Email] Sent successfully to: {email}")
        return True

    except Exception as e:
        print(f"[Email] Failed to send to: {email}, error: {str(e)}")
        return False



def generate_verification_code() -> str:
    """生成6位数字验证码（使用密码学安全的随机数）"""
    import secrets
    return ''.join([str(secrets.randbelow(10)) for _ in range(6)])


# ============ 节假日API工具 ============

def is_workday(date) -> bool:
    """
    判断指定日期是否为工作日（需要签到）

    使用 timor.tech 节假日API，支持：
    - 国家法定节假日（不需签到）
    - 调休补班日（需要签到）
    - 普通周末（不需签到）
    - 普通工作日（需要签到）

    参数:
        date: datetime.date 对象
    返回:
        bool: True=工作日需签到, False=休息日不需签到
    """
    import requests
    import logging
    from django.core.cache import cache
    from django.conf import settings

    logger = logging.getLogger('hr_management.utils')

    # 检查是否启用节假日API
    if not getattr(settings, 'HOLIDAY_API_ENABLED', True):
        # 未启用API，回退到简单周末判断
        return date.weekday() < 5

    # 缓存key，避免重复调用API
    cache_key = f'holiday_type_{date.isoformat()}'
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        return cached_result

    try:
        url = f'http://timor.tech/api/holiday/info/{date.isoformat()}'
        headers = {'User-Agent': 'Mozilla/5.0 HR-System/1.0'}
        resp = requests.get(url, timeout=5, headers=headers)
        resp.raise_for_status()
        data = resp.json()

        if data.get('code') == 0:
            holiday_type = data.get('type', {}).get('type', 0)
            # type: 0=工作日, 1=周末, 2=节假日, 3=调休补班
            is_work = holiday_type in (0, 3)  # 工作日或调休补班需要签到

            # 缓存结果24小时
            cache.set(cache_key, is_work, 86400)

            type_names = {0: '工作日', 1: '周末', 2: '节假日', 3: '调休补班'}
            logger.info(f"Holiday API: {date} -> {type_names.get(holiday_type, '未知')} (is_workday={is_work})")
            return is_work
        else:
            logger.warning(f"Holiday API returned error: {data}")

    except requests.RequestException as e:
        logger.warning(f"Holiday API request failed: {e}")
    except Exception as e:
        logger.error(f"Holiday API unexpected error: {e}")

    # API失败时回退到周末判断
    fallback = date.weekday() < 5
    cache.set(cache_key, fallback, 3600)  # 失败时缓存1小时后重试
    return fallback


def get_holiday_info(date) -> Dict[str, Any]:
    """
    获取指定日期的节假日详细信息

    返回:
        {
            'is_workday': bool,      # 是否工作日
            'type': int,             # 0=工作日, 1=周末, 2=节假日, 3=调休
            'type_name': str,        # 类型中文名
            'holiday_name': str,     # 节假日名称（如"春节"）
            'from_api': bool         # 是否来自API
        }
    """
    import requests
    import logging
    from django.core.cache import cache
    from django.conf import settings

    logger = logging.getLogger('hr_management.utils')

    result = {
        'is_workday': date.weekday() < 5,
        'type': 0 if date.weekday() < 5 else 1,
        'type_name': '工作日' if date.weekday() < 5 else '周末',
        'holiday_name': None,
        'from_api': False
    }

    if not getattr(settings, 'HOLIDAY_API_ENABLED', True):
        return result

    cache_key = f'holiday_info_{date.isoformat()}'
    cached = cache.get(cache_key)
    if cached:
        return cached

    try:
        url = f'http://timor.tech/api/holiday/info/{date.isoformat()}'
        headers = {'User-Agent': 'Mozilla/5.0 HR-System/1.0'}
        resp = requests.get(url, timeout=5, headers=headers)
        resp.raise_for_status()
        data = resp.json()

        if data.get('code') == 0:
            type_data = data.get('type', {})
            holiday_type = type_data.get('type', 0)

            type_names = {0: '工作日', 1: '周末', 2: '节假日', 3: '调休补班'}
            result = {
                'is_workday': holiday_type in (0, 3),
                'type': holiday_type,
                'type_name': type_names.get(holiday_type, '未知'),
                'holiday_name': type_data.get('name'),
                'from_api': True
            }
            cache.set(cache_key, result, 86400)

    except Exception as e:
        logger.warning(f"get_holiday_info failed: {e}")

    return result

