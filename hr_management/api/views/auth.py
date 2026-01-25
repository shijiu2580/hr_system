"""认证相关 API 视图"""
from rest_framework import permissions, views
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import authenticate, logout
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

from ...models import Employee, RBACPermission
from ...utils import log_event, api_success, api_error, get_client_ip
from ..serializers import (
    UserSerializer, ChangePasswordSerializer, 
    AdminResetPasswordSerializer, UserProfileUpdateSerializer
)


class CurrentUserAPIView(views.APIView):
    """获取当前登录用户信息"""
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({'authenticated': False}, status=200)
        roles = list(request.user.roles.values('id','name','code')) if hasattr(request.user,'roles') else []
        permission_keys = []
        try:
            permission_keys = sorted(set(RBACPermission.objects.filter(roles__users=request.user).values_list('key', flat=True)))
        except Exception:
            pass
        must_change = False
        try:
            if hasattr(request.user, 'employee') and request.user.employee:
                must_change = request.user.employee.must_change_password
        except Exception:
            pass
        return Response({
            'authenticated': True, 
            'user': UserSerializer(request.user).data, 
            'roles': roles, 
            'permissions': permission_keys, 
            'must_change_password': must_change
        })


class CustomTokenObtainView(views.APIView):
    """自定义 Token 获取视图，支持用户名/邮箱/手机号登录"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '')
        
        if not username or not password:
            return Response({'detail': '请输入用户名和密码'}, status=400)
        
        user = None
        
        # 尝试通过用户名直接认证
        user = authenticate(request, username=username, password=password)
        
        # 如果用户名认证失败，尝试通过邮箱查找用户
        if user is None:
            try:
                user_obj = User.objects.get(email=username)
                if user_obj.check_password(password):
                    user = user_obj
            except User.DoesNotExist:
                pass
        
        # 如果邮箱认证失败，尝试通过工号查找员工
        if user is None:
            try:
                employee = Employee.objects.select_related('user').get(employee_id=username)
                if employee.user and employee.user.check_password(password):
                    user = employee.user
            except Employee.DoesNotExist:
                pass
        
        # 如果工号认证失败，尝试通过手机号查找员工
        if user is None:
            try:
                employee = Employee.objects.select_related('user').get(phone=username)
                if employee.user and employee.user.check_password(password):
                    user = employee.user
            except Employee.DoesNotExist:
                pass
        
        if user is None or not user.is_active:
            return Response({'detail': '账号或密码错误'}, status=401)
        
        refresh = RefreshToken.for_user(user)
        log_event(user=user, action='用户登录', level='INFO', detail=f'用户名: {user.username}', ip=get_client_ip(request))
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })


class LogoutAPIView(views.APIView):
    """用户登出"""
    def post(self, request):
        if request.user.is_authenticated:
            log_event(user=request.user, action='用户退出', level='INFO', ip=get_client_ip(request))
        logout(request)
        return Response({'detail': '已退出'})


class ChangePasswordAPIView(views.APIView):
    """修改密码"""
    def post(self, request):
        if not request.user.is_authenticated:
            return Response(api_error('未登录', code='not_authenticated'), status=401)
        ser = ChangePasswordSerializer(data=request.data)
        if not ser.is_valid():
            return Response(api_error('参数错误', code='validation_error', errors=ser.errors), status=400)
        old = ser.validated_data['old_password']
        new = ser.validated_data['new_password']
        if not request.user.check_password(old):
            return Response(api_error('旧密码不正确', code='old_password_mismatch'), status=400)
        if old == new:
            return Response(api_error('新密码不能与旧密码相同', code='password_not_changed'), status=400)
        request.user.set_password(new)
        request.user.save(update_fields=['password'])
        try:
            if hasattr(request.user, 'employee') and request.user.employee.must_change_password:
                request.user.employee.must_change_password = False
                request.user.employee.save(update_fields=['must_change_password'])
        except Exception:
            pass
        log_event(user=request.user, action='修改密码', level='WARNING', detail='用户主动修改密码', ip=get_client_ip(request))
        return Response(api_success(detail='密码已更新'))


class AdminResetPasswordAPIView(views.APIView):
    """管理员重置用户密码"""
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request):
        ser = AdminResetPasswordSerializer(data=request.data)
        if not ser.is_valid():
            return Response(api_error('参数错误', errors=ser.errors), status=400)
        data = ser.save()
        user_obj = User.objects.get(id=data['user_id'])
        log_event(user=request.user, action='管理员重置密码', level='WARNING', detail=f"target={user_obj.username}", ip=get_client_ip(request))
        must_change = False
        try:
            if hasattr(user_obj, 'employee') and user_obj.employee.must_change_password:
                must_change = True
        except Exception:
            pass
        return Response(api_success({
            'user_id': data['user_id'], 
            'username': user_obj.username, 
            'new_password': data['final_password'], 
            'must_change_password': must_change
        }, detail='密码已重置'))


class UserProfileUpdateAPIView(views.APIView):
    """更新用户个人资料"""
    def post(self, request):
        if not request.user.is_authenticated:
            return Response(api_error('未登录', code='not_authenticated'), status=401)
        ser = UserProfileUpdateSerializer(data=request.data)
        if not ser.is_valid():
            return Response(api_error('参数错误', errors=ser.errors), status=400)
        user = ser.update(request.user, ser.validated_data)
        log_event(user=user, action='更新资料', level='INFO', detail='用户更新个人资料', ip=get_client_ip(request))
        return Response(api_success(UserSerializer(user).data, detail='资料已更新'))


class HealthAPIView(views.APIView):
    """健康检查与系统信息接口"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        import sys
        import os
        import django
        from pathlib import Path
        from django.db import connection
        from django.conf import settings
        from ...models import Employee, Department, Attendance, LeaveRequest, SalaryRecord, SystemLog
        
        # 数据库连接检查
        db_ok = True
        try:
            connection.ensure_connection()
        except Exception:
            db_ok = False
        
        # 基础健康信息
        data = {
            'status': 'ok' if db_ok else 'error',
            'timestamp': timezone.now().isoformat(),
            'db': db_ok,
        }
        
        # 如果用户已认证，返回更多系统信息
        if request.user.is_authenticated and request.user.is_staff:
            # 数据库文件大小
            db_path = Path(settings.DATABASES['default']['NAME'])
            db_size = db_path.stat().st_size if db_path.exists() else 0
            
            # 媒体目录大小
            media_size = 0
            media_path = Path(settings.MEDIA_ROOT)
            if media_path.exists():
                for f in media_path.rglob('*'):
                    if f.is_file():
                        media_size += f.stat().st_size
            
            data.update({
                'system_info': {
                    'python_version': sys.version.split()[0],
                    'django_version': django.__version__,
                    'debug_mode': settings.DEBUG,
                    'timezone': str(settings.TIME_ZONE),
                },
                'storage': {
                    'database_size': db_size,
                    'media_size': media_size,
                },
                'statistics': {
                    'total_employees': Employee.objects.count(),
                    'active_employees': Employee.objects.filter(is_active=True).count(),
                    'total_departments': Department.objects.count(),
                    'total_attendance': Attendance.objects.count(),
                    'total_leaves': LeaveRequest.objects.count(),
                    'total_salaries': SalaryRecord.objects.count(),
                    'total_logs': SystemLog.objects.count(),
                },
            })
        
        return Response(data)


# ==================== 找回密码 ====================

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def send_verification_code(request):
    """发送邮箱验证码"""
    from datetime import timedelta
    from ...models import VerificationCode
    from ...utils import generate_verification_code, send_verification_email
    import re
    
    email = request.data.get('email', '').strip()
    code_type = request.data.get('code_type', 'reset_password')
    
    if not email:
        return Response(api_error('请输入邮箱地址'), status=400)
    
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return Response(api_error('邮箱格式不正确'), status=400)
    
    if code_type == 'reset_password':
        if not Employee.objects.filter(email=email).exists():
            return Response(api_error('该邮箱未注册'), status=404)
    
    one_minute_ago = timezone.now() - timedelta(minutes=1)
    recent_code = VerificationCode.objects.filter(
        phone=email, code_type=code_type, created_at__gte=one_minute_ago
    ).first()
    
    if recent_code:
        return Response(api_error('发送过于频繁，请1分钟后再试'), status=429)
    
    code = generate_verification_code()
    expires_at = timezone.now() + timedelta(minutes=5)
    
    VerificationCode.objects.create(
        phone=email, code=code, code_type=code_type, expires_at=expires_at
    )
    
    if send_verification_email(email, code, code_type):
        log_event(action='发送验证码', detail=f'{email} ({code_type})', ip=get_client_ip(request))
        return Response(api_success(detail='验证码已发送到您的邮箱，请注意查收'))
    else:
        return Response(api_error('验证码发送失败，请稍后再试'), status=500)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def verify_code_and_reset_password(request):
    """验证验证码并重置密码"""
    from ...models import VerificationCode
    
    email = request.data.get('email', '').strip()
    code = request.data.get('code', '').strip()
    new_password = request.data.get('new_password', '')
    
    if not all([email, code, new_password]):
        return Response(api_error('请填写完整信息'), status=400)
    
    if len(new_password) < 8:
        return Response(api_error('新密码长度至少8位'), status=400)
    if not any(c.isdigit() for c in new_password) or not any(c.isalpha() for c in new_password):
        return Response(api_error('新密码需包含字母和数字'), status=400)
    
    verification = VerificationCode.objects.filter(
        phone=email, code=code, code_type='reset_password', is_used=False
    ).order_by('-created_at').first()
    
    if not verification:
        return Response(api_error('验证码不正确'), status=400)
    
    if not verification.is_valid():
        return Response(api_error('验证码已过期或已使用'), status=400)
    
    try:
        employee = Employee.objects.select_related('user').filter(email=email).order_by('-created_at').first()
        if not employee:
            return Response(api_error('该邮箱未关联用户'), status=404)
        user = employee.user
    except Exception as e:
        return Response(api_error(f'查找用户失败: {str(e)}'), status=500)
    
    user.set_password(new_password)
    user.save(update_fields=['password'])
    
    verification.is_used = True
    verification.save(update_fields=['is_used'])
    
    log_event(user=user, action='通过验证码重置密码', detail=email, ip=get_client_ip(request))
    
    return Response(api_success(detail='密码重置成功，请使用新密码登录'))
