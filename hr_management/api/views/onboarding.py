"""员工自助入职 API 视图 (H5 端使用)"""
from rest_framework import permissions, views
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction
from rest_framework_simplejwt.tokens import RefreshToken

from ...models import Employee, VerificationCode
from ...utils import log_event, api_success, api_error, get_client_ip, generate_verification_code, send_verification_email


class SelfRegisterAPIView(views.APIView):
    """
    员工自助注册接口
    
    流程：
    1. 用户输入手机号/邮箱，获取验证码
    2. 验证通过后创建账号，状态为"待入职"
    3. HR 在后台审核后激活
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """自助注册"""
        name = request.data.get('name', '').strip()
        phone = request.data.get('phone', '').strip()
        email = request.data.get('email', '').strip()
        password = request.data.get('password', '')
        code = request.data.get('code', '').strip()  # 验证码
        
        # 基本验证
        if not name:
            return Response(api_error('请输入姓名', code='name_required'), status=400)
        if not phone:
            return Response(api_error('请输入手机号', code='phone_required'), status=400)
        if not email:
            return Response(api_error('请输入邮箱', code='email_required'), status=400)
        if not password:
            return Response(api_error('请设置密码', code='password_required'), status=400)
        if len(password) < 8:
            return Response(api_error('密码长度至少8位', code='password_too_short'), status=400)
        if not code:
            return Response(api_error('请输入验证码', code='code_required'), status=400)
        
        # 验证验证码
        verification = VerificationCode.objects.filter(
            phone=email, code=code, code_type='register', is_used=False
        ).order_by('-created_at').first()
        
        if not verification or not verification.is_valid():
            return Response(api_error('验证码不正确或已过期', code='invalid_code'), status=400)
        
        # 检查是否已注册
        if User.objects.filter(email=email).exists():
            return Response(api_error('该邮箱已注册', code='email_exists'), status=400)
        if Employee.objects.filter(phone=phone).exists():
            return Response(api_error('该手机号已注册', code='phone_exists'), status=400)
        
        try:
            with transaction.atomic():
                # 创建 User，用户名使用姓名（如果重复则添加随机后缀）
                import random
                base_username = name
                username = base_username
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}_{random.randint(100, 999)}"
                
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    is_active=True,  # 允许登录查看状态
                    is_staff=False,
                )
                
                # 自动生成4位数员工编号
                import random
                while True:
                    employee_id = str(random.randint(1000, 9999))
                    if not Employee.objects.filter(employee_id=employee_id).exists():
                        break
                
                # 创建 Employee（待入职状态，员工编号自动生成）
                employee = Employee.objects.create(
                    user=user,
                    employee_id=employee_id,
                    name=name,
                    phone=phone,
                    email=email,
                    onboard_status='pending',  # 待入职
                    is_active=False,  # 未激活（不参与签到等）
                )
                
                # 标记验证码已使用
                verification.is_used = True
                verification.save(update_fields=['is_used'])
                
                log_event(user=user, action='自助注册', level='INFO', 
                         detail=f'{name} ({phone}) 工号:{employee_id}', ip=get_client_ip(request))
                
                # 返回 token
                refresh = RefreshToken.for_user(user)
                
                return Response(api_success({
                    'employee_id': employee.employee_id,
                    'name': name,
                    'onboard_status': 'pending',
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                }, detail='注册成功，请完善个人信息等待审核'), status=201)
                
        except Exception as e:
            return Response(api_error(f'注册失败: {str(e)}', code='register_error'), status=500)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def send_register_code(request):
    """发送注册验证码"""
    from datetime import timedelta
    import re
    
    email = request.data.get('email', '').strip()
    
    if not email:
        return Response(api_error('请输入邮箱地址'), status=400)
    
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return Response(api_error('邮箱格式不正确'), status=400)
    
    # 检查是否已注册
    if User.objects.filter(email=email).exists():
        return Response(api_error('该邮箱已注册'), status=400)
    
    # 检查发送频率
    one_minute_ago = timezone.now() - timedelta(minutes=1)
    recent_code = VerificationCode.objects.filter(
        phone=email, code_type='register', created_at__gte=one_minute_ago
    ).first()
    
    if recent_code:
        return Response(api_error('发送过于频繁，请1分钟后再试'), status=429)
    
    code = generate_verification_code()
    expires_at = timezone.now() + timedelta(minutes=10)  # 注册码10分钟有效
    
    VerificationCode.objects.create(
        phone=email, code=code, code_type='register', expires_at=expires_at
    )
    
    if send_verification_email(email, code, 'register'):
        log_event(action='发送注册验证码', detail=email, ip=get_client_ip(request))
        return Response(api_success(detail='验证码已发送到您的邮箱'))
    else:
        return Response(api_error('验证码发送失败，请稍后再试'), status=500)


class OnboardProfileAPIView(views.APIView):
    """
    待入职员工提交/更新个人资料
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """获取当前资料"""
        try:
            emp = Employee.objects.get(user=request.user)
        except Employee.DoesNotExist:
            return Response(api_error('未找到员工信息', code='not_found'), status=404)
        
        return Response(api_success({
            'employee_id': emp.employee_id,
            'name': emp.name,
            'english_name': emp.english_name,
            'phone': emp.phone,
            'email': emp.email,
            'gender': emp.gender,
            'birth_date': str(emp.birth_date) if emp.birth_date else None,
            'id_card': emp.id_card,
            'passport_no': emp.passport_no,
            'address': emp.address,
            'marital_status': emp.marital_status,
            'emergency_contact': emp.emergency_contact,
            'emergency_phone': emp.emergency_phone,
            'emergency_relation': emp.emergency_relation,
            # 户籍信息
            'nationality': emp.nationality,
            'native_place': emp.native_place,
            'hukou_location': emp.hukou_location,
            'hukou_type': emp.hukou_type,
            'hukou_address': emp.hukou_address,
            'ethnicity': emp.ethnicity,
            'political_status': emp.political_status,
            'party_date': str(emp.party_date) if emp.party_date else None,
            'blood_type': emp.blood_type,
            # 教育信息
            'education': emp.education,
            'school_type': emp.school_type,
            'school_name': emp.school_name,
            'major': emp.major,
            'graduation_date': str(emp.graduation_date) if emp.graduation_date else None,
            # 银行信息
            'bank_card_no': emp.bank_card_no,
            'expense_card_no': emp.expense_card_no,
            # 设备信息
            'computer_info': emp.computer_info,
            'computer_brand': emp.computer_brand,
            # 文件
            'avatar': emp.avatar.url if emp.avatar else None,
            'id_card_front': emp.id_card_front.url if emp.id_card_front else None,
            'id_card_back': emp.id_card_back.url if emp.id_card_back else None,
            'id_card_copy': emp.id_card_copy.url if emp.id_card_copy else None,
            'resume': emp.resume.url if emp.resume else None,
            # 状态
            'onboard_status': emp.onboard_status,
            'onboard_reject_reason': emp.onboard_reject_reason,
        }))
    
    def post(self, request):
        """提交/更新资料"""
        try:
            emp = Employee.objects.get(user=request.user)
        except Employee.DoesNotExist:
            return Response(api_error('未找到员工信息', code='not_found'), status=404)
        
        # pending、rejected 和 onboarded 状态都可以修改个人资料
        if emp.onboard_status not in ('pending', 'rejected', 'onboarded'):
            return Response(api_error('当前状态不允许修改资料', code='status_not_allowed'), status=400)
        
        # 记录是否是被拒绝后重新提交
        was_rejected = emp.onboard_status == 'rejected'
        
        # 可更新的字段
        updatable_fields = [
            'name', 'english_name', 'gender', 'birth_date', 'id_card', 'passport_no',
            'phone', 'email', 'address', 'marital_status', 
            'emergency_contact', 'emergency_phone', 'emergency_relation',
            # 户籍信息
            'nationality', 'native_place', 'hukou_location', 'hukou_type', 
            'hukou_address', 'ethnicity', 'political_status', 'party_date', 'blood_type',
            # 教育信息
            'education', 'school_type', 'school_name', 'major', 'graduation_date',
            # 银行信息
            'bank_card_no', 'expense_card_no',
            # 设备信息
            'computer_info', 'computer_brand',
        ]
        
        date_fields = ['birth_date', 'party_date', 'graduation_date']
        
        updated = []
        for field in updatable_fields:
            if field in request.data:
                value = request.data[field]
                # 日期字段空字符串转为 None
                if field in date_fields:
                    if value == '' or value is None:
                        value = None
                    else:
                        from datetime import datetime
                        try:
                            value = datetime.strptime(value, '%Y-%m-%d').date()
                        except ValueError:
                            return Response(api_error(f'{field} 格式错误'), status=400)
                setattr(emp, field, value)
                updated.append(field)
        
        # 处理文件上传
        if 'avatar' in request.FILES:
            emp.avatar = request.FILES['avatar']
            updated.append('avatar')
        if 'id_card_front' in request.FILES:
            emp.id_card_front = request.FILES['id_card_front']
            updated.append('id_card_front')
        if 'id_card_back' in request.FILES:
            emp.id_card_back = request.FILES['id_card_back']
            updated.append('id_card_back')
        if 'id_card_copy' in request.FILES:
            emp.id_card_copy = request.FILES['id_card_copy']
            updated.append('id_card_copy')
        if 'resume' in request.FILES:
            emp.resume = request.FILES['resume']
            updated.append('resume')
        
        if updated:
            # 如果是被拒绝后重新提交，状态改回 pending
            if was_rejected:
                emp.onboard_status = 'pending'
                emp.onboard_reject_reason = ''  # 清空拒绝原因
            emp.save()
            action_text = '重新提交入职资料' if was_rejected else '更新入职资料'
            log_event(user=request.user, action=action_text, level='INFO',
                     detail=f'更新字段: {", ".join(updated)}', ip=get_client_ip(request))
        
        return Response(api_success(detail='资料已更新' if not was_rejected else '资料已重新提交，请等待审核'))


class OnboardStatusAPIView(views.APIView):
    """查询入职审核状态"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            emp = Employee.objects.select_related('onboard_reviewed_by').get(user=request.user)
        except Employee.DoesNotExist:
            return Response(api_error('未找到员工信息', code='not_found'), status=404)
        
        status_text = {
            'pending': '待审核',
            'rejected': '已拒绝',
            'onboarded': '已入职',
            'resigned': '已离职',
        }
        
        return Response(api_success({
            'status': emp.onboard_status,
            'status_text': status_text.get(emp.onboard_status, '未知'),
            'reject_reason': emp.onboard_reject_reason,
            'reviewed_at': emp.onboard_reviewed_at.isoformat() if emp.onboard_reviewed_at else None,
            'reviewed_by': emp.onboard_reviewed_by.username if emp.onboard_reviewed_by else None,
            'hire_date': str(emp.hire_date) if emp.hire_date else None,
            'department': emp.department.name if emp.department else None,
            'position': emp.position.name if emp.position else None,
        }))


# ============== HR 审核接口 ==============

class OnboardPendingListAPIView(views.APIView):
    """获取待审核的入职申请列表 (HR 使用)"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        if not request.user.is_staff:
            return Response(api_error('无权限', code='forbidden'), status=403)
        
        status_filter = request.query_params.get('status', 'pending')
        
        if status_filter == 'all':
            qs = Employee.objects.filter(onboard_status__in=['pending', 'onboarded', 'rejected', 'resigned'])
        else:
            qs = Employee.objects.filter(onboard_status=status_filter)
        
        qs = qs.select_related('user', 'onboard_reviewed_by', 'department', 'position').order_by('-created_at')
        
        data = []
        for emp in qs:
            data.append({
                'id': emp.id,
                'employee_id': emp.employee_id,
                'name': emp.name,
                'english_name': emp.english_name,
                'phone': emp.phone,
                'email': emp.email,
                'gender': emp.gender,
                'birth_date': str(emp.birth_date) if emp.birth_date else None,
                'id_card': emp.id_card,
                'passport_no': emp.passport_no,
                'marital_status': emp.marital_status,
                'nationality': emp.nationality,
                'native_place': emp.native_place,
                'ethnicity': emp.ethnicity,
                'political_status': emp.political_status,
                'blood_type': emp.blood_type,
                'hukou_location': emp.hukou_location,
                'hukou_type': emp.hukou_type,
                'education': emp.education,
                'school_name': emp.school_name,
                'major': emp.major,
                'graduation_date': str(emp.graduation_date) if emp.graduation_date else None,
                'address': emp.address,
                'emergency_contact': emp.emergency_contact,
                'emergency_phone': emp.emergency_phone,
                'avatar': emp.avatar.url if emp.avatar else None,
                'id_card_copy': emp.id_card_copy.url if emp.id_card_copy else None,
                'resume': emp.resume.url if emp.resume else None,
                'onboard_status': emp.onboard_status,
                'onboard_reject_reason': emp.onboard_reject_reason,
                'created_at': emp.created_at.isoformat() if emp.created_at else None,
                'reviewed_at': emp.onboard_reviewed_at.isoformat() if emp.onboard_reviewed_at else None,
                'reviewed_by': emp.onboard_reviewed_by.username if emp.onboard_reviewed_by else None,
                'department': emp.department.name if emp.department else None,
                'position': emp.position.name if emp.position else None,
            })
        
        return Response(api_success(data))


class OnboardApproveAPIView(views.APIView):
    """审核入职申请 (HR 使用)"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        if not request.user.is_staff:
            return Response(api_error('无权限', code='forbidden'), status=403)
        
        try:
            emp = Employee.objects.select_related('user').get(pk=pk)
        except Employee.DoesNotExist:
            return Response(api_error('员工不存在', code='not_found'), status=404)
        
        if emp.onboard_status != 'pending':
            return Response(api_error('该申请已处理', code='already_processed'), status=400)
        
        action = request.data.get('action')  # approve / reject
        
        if action == 'approve':
            # 分配正式员工编号
            new_employee_id = request.data.get('employee_id')
            department_id = request.data.get('department_id')
            position_id = request.data.get('position_id')
            hire_date = request.data.get('hire_date')
            salary = request.data.get('salary')
            
            if not new_employee_id:
                # 自动生成员工编号（4位随机数字）
                import random
                while True:
                    new_employee_id = str(random.randint(1000, 9999))
                    if not Employee.objects.filter(employee_id=new_employee_id).exists():
                        break
            
            # 检查员工编号是否重复
            if Employee.objects.filter(employee_id=new_employee_id).exclude(pk=pk).exists():
                return Response(api_error('员工编号已存在', code='employee_id_exists'), status=400)
            
            with transaction.atomic():
                emp.employee_id = new_employee_id
                emp.onboard_status = 'onboarded'
                emp.is_active = True
                emp.onboard_reviewed_by = request.user
                emp.onboard_reviewed_at = timezone.now()
                
                if department_id:
                    emp.department_id = department_id
                if position_id:
                    emp.position_id = position_id
                if hire_date:
                    from datetime import datetime
                    emp.hire_date = datetime.strptime(hire_date, '%Y-%m-%d').date()
                else:
                    emp.hire_date = timezone.localdate()
                if salary:
                    emp.salary = salary
                
                # 更新用户名为正式员工编号
                emp.user.username = new_employee_id.lower()
                emp.user.save(update_fields=['username'])
                
                emp.save()
                
                log_event(user=request.user, action='审核通过入职', level='INFO',
                         detail=f'{emp.name} -> {new_employee_id}', ip=get_client_ip(request))
            
            return Response(api_success({
                'employee_id': new_employee_id,
                'status': 'onboarded'
            }, detail=f'已通过 {emp.name} 的入职申请'))
        
        elif action == 'reject':
            reason = request.data.get('reason', '').strip()
            if not reason:
                return Response(api_error('请填写拒绝原因', code='reason_required'), status=400)
            
            emp.onboard_status = 'rejected'  # 设为已拒绝
            emp.onboard_reject_reason = reason
            emp.onboard_reviewed_by = request.user
            emp.onboard_reviewed_at = timezone.now()
            emp.save()
            
            log_event(user=request.user, action='拒绝入职申请', level='INFO',
                     detail=f'{emp.name}: {reason}', ip=get_client_ip(request))
            
            return Response(api_success(detail=f'已拒绝 {emp.name} 的入职申请'))
        
        else:
            return Response(api_error('action 必须为 approve 或 reject', code='invalid_action'), status=400)
