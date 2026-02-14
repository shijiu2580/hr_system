from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Employee, Department, Position, Attendance, LeaveRequest, SalaryRecord, SystemLog, Role, RBACPermission, CompanyDocument, BusinessTrip, TravelExpense, CheckInLocation
from django.utils import timezone


class DepartmentSerializer(serializers.ModelSerializer):
    manager = serializers.SerializerMethodField()
    supervisors = serializers.SerializerMethodField()
    parent = serializers.SerializerMethodField()
    children_count = serializers.SerializerMethodField()
    full_path = serializers.SerializerMethodField()
    supervisor_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    parent_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Department
        fields = ['id', 'name', 'description', 'manager', 'supervisors', 'supervisor_ids',
                  'parent', 'parent_id', 'children_count', 'full_path']

    def get_manager(self, obj):
        manager = getattr(obj, 'manager', None)
        if manager:
            return {
                'id': manager.id,
                'name': manager.name,
                'user_id': manager.user_id,
                'employee_id': manager.employee_id,
            }
        return None

    def get_supervisors(self, obj):
        supervisors = obj.supervisors.all()
        return [{
            'id': s.id,
            'name': s.name,
            'user_id': s.user_id,
            'employee_id': s.employee_id,
        } for s in supervisors]

    def get_parent(self, obj):
        if obj.parent:
            return {
                'id': obj.parent.id,
                'name': obj.parent.name,
            }
        return None

    def get_children_count(self, obj):
        return obj.children.count()

    def get_full_path(self, obj):
        return obj.get_full_path()

    def create(self, validated_data):
        supervisor_ids = validated_data.pop('supervisor_ids', [])
        parent_id = validated_data.pop('parent_id', None)

        # 设置父部门
        if parent_id:
            try:
                parent = Department.objects.get(id=parent_id)
                validated_data['parent'] = parent
            except Department.DoesNotExist:
                pass

        department = Department.objects.create(**validated_data)
        if supervisor_ids:
            department.supervisors.set(supervisor_ids)
        return department

    def update(self, instance, validated_data):
        supervisor_ids = validated_data.pop('supervisor_ids', None)
        parent_id = validated_data.pop('parent_id', None)

        # 检查是否将部门设置为自己的子部门（避免循环引用）
        if parent_id is not None:
            if parent_id == instance.id:
                raise serializers.ValidationError({'parent_id': '部门不能设置自己为上级部门'})
            # 检查是否设置为自己的子部门
            if parent_id:
                parent = Department.objects.filter(id=parent_id).first()
                if parent:
                    all_children = instance.get_all_children()
                    if parent in all_children:
                        raise serializers.ValidationError({'parent_id': '不能将子部门设置为上级部门'})
            instance.parent_id = parent_id

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if supervisor_ids is not None:
            instance.supervisors.set(supervisor_ids)
        return instance

class PositionSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    default_roles = serializers.SerializerMethodField()
    default_role_ids = serializers.PrimaryKeyRelatedField(
        source='default_roles', many=True, read_only=True
    )

    class Meta:
        model = Position
        fields = ['id', 'name', 'department', 'description', 'default_roles', 'default_role_ids']

    def get_default_roles(self, obj):
        return [{'id': r.id, 'name': r.name, 'code': r.code} for r in obj.default_roles.all()]

class UserSerializer(serializers.ModelSerializer):
    must_change_password = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()
    has_employee = serializers.SerializerMethodField()
    employee_id = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    employee_name = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'username', 'is_staff', 'is_superuser', 'is_active', 'email', 'first_name', 'last_name', 'must_change_password', 'roles', 'has_employee', 'employee_id', 'avatar', 'employee_name', 'date_joined', 'last_login']

    def get_must_change_password(self, obj: User):
        try:
            return bool(getattr(obj, 'employee', None) and obj.employee.must_change_password)
        except Exception:
            return False

    def get_roles(self, obj: User):
        try:
            return [{'id': r.id, 'name': r.name, 'code': r.code} for r in obj.roles.all()]
        except Exception:
            return []

    def get_has_employee(self, obj: User):
        try:
            return hasattr(obj, 'employee') and obj.employee is not None
        except Exception:
            return False

    def get_employee_id(self, obj: User):
        try:
            if hasattr(obj, 'employee') and obj.employee:
                return obj.employee.employee_id
            return None
        except Exception:
            return None

    def get_avatar(self, obj: User):
        try:
            if hasattr(obj, 'employee') and obj.employee and obj.employee.avatar:
                # 直接返回相对路径，让前端使用当前域名访问
                return obj.employee.avatar.url
            return None
        except Exception:
            return None

    def get_employee_name(self, obj: User):
        try:
            if hasattr(obj, 'employee') and obj.employee:
                return obj.employee.name
            return None
        except Exception:
            return None

class EmployeeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)
    position = PositionSerializer(read_only=True)
    checkin_location_ids = serializers.PrimaryKeyRelatedField(
        source='checkin_locations', many=True, read_only=True
    )
    checkin_locations = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    id_card_front = serializers.SerializerMethodField()
    id_card_back = serializers.SerializerMethodField()

    def get_checkin_locations(self, obj):
        return [{'id': loc.id, 'name': loc.name} for loc in obj.checkin_locations.all()]

    def _build_file_url(self, obj, field_name: str):
        f = getattr(obj, field_name, None)
        if not f:
            return None
        try:
            # 直接返回相对路径，让前端使用当前域名访问
            return f.url
        except Exception:
            return None

    def get_avatar(self, obj):
        return self._build_file_url(obj, 'avatar')

    def get_id_card_front(self, obj):
        return self._build_file_url(obj, 'id_card_front')

    def get_id_card_back(self, obj):
        return self._build_file_url(obj, 'id_card_back')

    class Meta:
        model = Employee
        fields = [
            'id', 'employee_id', 'name', 'english_name', 'gender', 'birth_date',
            'phone', 'email', 'address', 'id_card',
            # 户籍信息
            'nationality', 'hukou_location', 'hukou_type', 'native_place', 'hukou_address',
            'ethnicity', 'blood_type', 'political_status', 'party_date',
            # 紧急联系人
            'emergency_contact', 'emergency_relation', 'emergency_phone',
            # 教育信息
            'school_type', 'school_name', 'major', 'graduation_date', 'education',
            # 银行信息
            'bank_card_no', 'expense_card_no',
            # 设备信息
            'computer_info', 'computer_brand',
            # 任职/状态
            'department', 'position', 'hire_date', 'salary', 'is_active',
            'onboard_status', 'onboard_reject_reason',
            # 证件/图片
            'avatar', 'id_card_front', 'id_card_back',
            # 关联
            'user', 'checkin_location_ids', 'checkin_locations',
        ]

class AttendanceSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    is_workday = serializers.SerializerMethodField()

    class Meta:
        model = Attendance
        fields = ['id','employee','date','check_in_time','check_out_time','attendance_type','notes','is_workday']

    def get_is_workday(self, obj):
        from .utils import is_workday
        try:
            return is_workday(obj.date)
        except Exception:
            return obj.date.weekday() < 5 if obj and obj.date else True

class LeaveRequestSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    approved_by = UserSerializer(read_only=True)
    attachment_url = serializers.SerializerMethodField()
    resignation_manager_by = UserSerializer(read_only=True)
    resignation_hr_by = UserSerializer(read_only=True)
    class Meta:
        model = LeaveRequest
        fields = [
            'id','employee','leave_type','start_date','end_date','days','status','reason','comments','created_at',
            'approved_by','approved_at','attachment_url','resignation_manager_status','resignation_hr_status',
            'resignation_manager_comment','resignation_hr_comment','resignation_manager_by','resignation_hr_by',
            'resignation_manager_at','resignation_hr_at'
        ]

    def get_attachment_url(self, obj):
        if not obj.attachment:
            return None
        request = self.context.get('request')
        try:
            url = obj.attachment.url
            return request.build_absolute_uri(url) if request else url
        except Exception:
            return None

class SalaryRecordSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    class Meta:
        model = SalaryRecord
        fields = ['id','employee','year','month','basic_salary','bonus','overtime_pay','allowance','net_salary','paid','paid_at']

class SystemLogSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = SystemLog
        fields = ['id','timestamp','level','action','ip_address','detail','user']

class RBACPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RBACPermission
        fields = ['id','key','name','description']

class RoleSerializer(serializers.ModelSerializer):
    permissions = RBACPermissionSerializer(many=True, read_only=True)
    class Meta:
        model = Role
        fields = ['id','name','code','description','is_system','permissions']


# --- Write / Create & Update Serializers (for API CRUD) ---

class DepartmentWriteSerializer(serializers.ModelSerializer):
    parent_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(),
        source='parent',
        allow_null=True,
        required=False
    )
    supervisor_ids = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(),
        many=True,
        required=False,
        write_only=True
    )

    class Meta:
        model = Department
        fields = ['name', 'description', 'parent_id', 'supervisor_ids']

    def validate_parent_id(self, value):
        """验证防止循环引用"""
        if self.instance and value:
            if value.id == self.instance.id:
                raise serializers.ValidationError('部门不能设置自己为上级部门')
            # 检查是否设置为自己的子部门
            all_children = self.instance.get_all_children()
            if value in all_children:
                raise serializers.ValidationError('不能将子部门设置为上级部门')
        return value

    def create(self, validated_data):
        supervisor_ids = validated_data.pop('supervisor_ids', [])
        department = super().create(validated_data)
        if supervisor_ids:
            department.supervisors.set(supervisor_ids)
        return department

    def update(self, instance, validated_data):
        supervisor_ids = validated_data.pop('supervisor_ids', None)
        department = super().update(instance, validated_data)
        if supervisor_ids is not None:
            department.supervisors.set(supervisor_ids)
        return department


class PositionWriteSerializer(serializers.ModelSerializer):
    department_id = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all(), source='department')
    default_role_ids = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(), source='default_roles', many=True, required=False
    )

    class Meta:
        model = Position
        fields = ['name', 'description', 'department_id', 'default_role_ids']

    def create(self, validated_data):
        default_roles = validated_data.pop('default_roles', [])
        position = super().create(validated_data)
        if default_roles:
            position.default_roles.set(default_roles)
        return position

    def update(self, instance, validated_data):
        default_roles = validated_data.pop('default_roles', None)
        position = super().update(instance, validated_data)
        if default_roles is not None:
            position.default_roles.set(default_roles)
        return position


class EmployeeWriteSerializer(serializers.ModelSerializer):
    department_id = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all(), source='department', allow_null=True, required=False)
    position_id = serializers.PrimaryKeyRelatedField(queryset=Position.objects.all(), source='position', allow_null=True, required=False)
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='user', required=True, help_text='已有用户ID')
    checkin_location_ids = serializers.PrimaryKeyRelatedField(
        queryset=CheckInLocation.objects.all(),
        many=True,
        required=False,
        write_only=True
    )

    # 覆盖字段以允许空值且不触发模型验证器
    employee_id = serializers.CharField(required=False, allow_blank=True, max_length=20)
    phone = serializers.CharField(required=False, allow_blank=True, max_length=20)
    email = serializers.EmailField(required=False, allow_blank=True)
    id_card = serializers.CharField(required=False, allow_blank=True, max_length=18)

    class Meta:
        model = Employee
        fields = [
            'user_id', 'employee_id', 'name', 'english_name', 'gender', 'birth_date',
            'phone', 'email', 'address', 'id_card', 'marital_status',
            # 户籍信息
            'nationality', 'hukou_location', 'hukou_type', 'native_place', 'hukou_address',
            'ethnicity', 'blood_type', 'political_status', 'party_date',
            # 紧急联系人
            'emergency_contact', 'emergency_relation', 'emergency_phone',
            # 教育信息
            'school_type', 'school_name', 'major', 'graduation_date', 'education',
            # 银行信息
            'bank_card_no', 'expense_card_no',
            # 设备信息
            'computer_info', 'computer_brand',
            # 任职信息
            'department_id', 'position_id', 'hire_date', 'salary', 'is_active',
            # 证件上传（可选，multipart/form-data）
            'avatar', 'id_card_front', 'id_card_back',
            # 考勤地点
            'checkin_location_ids',
        ]

    def validate_phone(self, value):
        """只在有值时验证格式"""
        import re
        if value and not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('请输入有效的11位手机号')
        return value

    def validate_id_card(self, value):
        """只在有值时验证格式"""
        import re
        if value and not re.match(r'^\d{17}[\dXx]$', value):
            raise serializers.ValidationError('请输入有效的18位身份证号')
        return value

    def validate_emergency_phone(self, value):
        """只在有值时验证格式"""
        import re
        if value and not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('请输入有效的11位手机号')
        return value

    def create(self, validated_data):
        checkin_location_ids = validated_data.pop('checkin_location_ids', [])
        # 新建员工强制首次修改密码标记
        validated_data.setdefault('must_change_password', True)
        employee = super().create(validated_data)
        if checkin_location_ids:
            employee.checkin_locations.set(checkin_location_ids)
        # 自动分配职位默认角色
        if employee.position:
            for role in employee.position.default_roles.all():
                role.users.add(employee.user)
        return employee

    def update(self, instance, validated_data):
        checkin_location_ids = validated_data.pop('checkin_location_ids', None)
        old_position = instance.position
        new_position = validated_data.get('position', old_position)

        employee = super().update(instance, validated_data)
        if checkin_location_ids is not None:
            employee.checkin_locations.set(checkin_location_ids)

        # 处理职位变更时的角色同步
        if new_position != old_position:
            # 移除旧职位的默认角色（仅移除通过职位分配的）
            if old_position:
                for role in old_position.default_roles.all():
                    role.users.remove(employee.user)
            # 添加新职位的默认角色
            if new_position:
                for role in new_position.default_roles.all():
                    role.users.add(employee.user)

        return employee


class EmployeeSelfUpdateSerializer(serializers.ModelSerializer):
    """当前登录用户更新自己的员工档案（不允许改 user / employee_id）"""

    # 覆盖字段以允许空值且不触发模型验证器
    phone = serializers.CharField(required=False, allow_blank=True, max_length=20)
    email = serializers.EmailField(required=False, allow_blank=True)
    id_card = serializers.CharField(required=False, allow_blank=True, max_length=18)
    emergency_phone = serializers.CharField(required=False, allow_blank=True, max_length=20)

    class Meta:
        model = Employee
        fields = [
            'name', 'english_name', 'gender', 'birth_date',
            'phone', 'email', 'address', 'id_card', 'marital_status',
            # 户籍信息
            'nationality', 'hukou_location', 'hukou_type', 'native_place', 'hukou_address',
            'ethnicity', 'blood_type', 'political_status', 'party_date',
            # 紧急联系人
            'emergency_contact', 'emergency_relation', 'emergency_phone',
            # 教育信息
            'school_type', 'school_name', 'major', 'graduation_date', 'education',
            # 银行信息
            'bank_card_no', 'expense_card_no',
            # 设备信息
            'computer_info', 'computer_brand',
            # 证件上传（可选，multipart/form-data）
            'avatar', 'id_card_front', 'id_card_back',
        ]

    def validate_phone(self, value):
        import re
        if value and not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('请输入有效的11位手机号')
        return value

    def validate_id_card(self, value):
        import re
        if value and not re.match(r'^\d{17}[\dXx]$', value):
            raise serializers.ValidationError('请输入有效的18位身份证号')
        return value

    def validate_emergency_phone(self, value):
        import re
        if value and not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('请输入有效的11位手机号')
        return value


class AttendanceWriteSerializer(serializers.ModelSerializer):
    employee_id = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all(), source='employee')
    class Meta:
        model = Attendance
        fields = ['employee_id','date','check_in_time','check_out_time','attendance_type','notes']

    def validate(self, attrs):
        employee = attrs['employee']
        date = attrs['date']
        if Attendance.objects.filter(employee=employee, date=date).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise serializers.ValidationError('该员工该日期考勤已存在')
        return attrs


class LeaveRequestWriteSerializer(serializers.ModelSerializer):
    employee_id = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all(), source='employee', required=False, allow_null=True)
    class Meta:
        model = LeaveRequest
        fields = ['employee_id','leave_type','start_date','end_date','reason','attachment']

    def validate(self, attrs):
        start = attrs['start_date']
        end = attrs['end_date']
        if end < start:
            raise serializers.ValidationError('结束日期不能早于开始日期')
        attrs['days'] = (end - start).days + 1
        return attrs

    def create(self, validated_data):
        # days 已在 validate 中计算
        return LeaveRequest.objects.create(**validated_data, status='pending')


class LeaveApproveSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['approve','reject'])
    comments = serializers.CharField(required=False, allow_blank=True)
    stage = serializers.ChoiceField(choices=['manager','hr'], required=False, allow_null=True)


class SalaryRecordWriteSerializer(serializers.ModelSerializer):
    employee_id = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all(), source='employee', required=False)
    paid = serializers.BooleanField(required=False, default=False)
    paid_at = serializers.DateTimeField(required=False, allow_null=True)
    year = serializers.IntegerField(required=False)
    month = serializers.IntegerField(required=False)
    basic_salary = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    bonus = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    overtime_pay = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    allowance = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)

    class Meta:
        model = SalaryRecord
        fields = ['employee_id','year','month','basic_salary','bonus','overtime_pay','allowance','paid','paid_at']
        # 禁用默认的唯一约束验证器，使用自定义验证
        validators = []

    def validate(self, attrs):
        # 检查唯一约束：同员工同年月只能有一条记录
        instance = self.instance
        employee = attrs.get('employee', instance.employee if instance else None)
        year = attrs.get('year', instance.year if instance else None)
        month = attrs.get('month', instance.month if instance else None)

        if employee and year and month:
            qs = SalaryRecord.objects.filter(employee=employee, year=year, month=month)
            if instance:
                qs = qs.exclude(pk=instance.pk)
            if qs.exists():
                raise serializers.ValidationError({'month': f'该员工{year}年{month}月的薪资记录已存在'})

        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        new = attrs['new_password']
        confirm = attrs['confirm_password']
        if new != confirm:
            raise serializers.ValidationError('两次输入的新密码不一致')
        if len(new) < 8:
            raise serializers.ValidationError('新密码长度至少 8 位')
        # 简单复杂度要求：包含大小写或数字
        if not any(c.isdigit() for c in new) or not any(c.isalpha() for c in new):
            raise serializers.ValidationError('新密码需包含字母与数字')
        return attrs

# 顶级：管理员重置密码序列化器（避免嵌套导致无法导入）
class AdminResetPasswordSerializer(serializers.Serializer):
    username = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    generate_random = serializers.BooleanField(write_only=True, required=False, default=False)
    force_change_password = serializers.BooleanField(write_only=True, required=False, default=False, help_text='重置后强制用户下次登录修改密码')
    # 输出字段
    user_id = serializers.IntegerField(read_only=True)
    final_password = serializers.CharField(read_only=True)

    def validate(self, attrs):
        username = attrs['username']
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError({'username': '用户不存在'})
        attrs['user'] = user
        new = attrs.get('new_password') or ''
        gen = attrs.get('generate_random')
        if not gen:
            if not new:
                raise serializers.ValidationError({'new_password': '必须提供新密码或选择自动生成'})
            if len(new) < 8:
                raise serializers.ValidationError({'new_password': '密码长度至少 8'})
            if not any(c.isdigit() for c in new) or not any(c.isalpha() for c in new):
                raise serializers.ValidationError({'new_password': '需包含字母与数字'})
        return attrs

    def save(self):
        import secrets
        user: User = self.validated_data['user']
        gen = self.validated_data.get('generate_random')
        new = self.validated_data.get('new_password')
        if gen:
            rand_core = secrets.token_urlsafe(12)
            new = rand_core + '!A'
        user.set_password(new)
        user.save(update_fields=['password'])
        # 设置 must_change_password 标志
        if self.validated_data.get('force_change_password'):
            try:
                if hasattr(user, 'employee') and user.employee:
                    user.employee.must_change_password = True
                    user.employee.save(update_fields=['must_change_password'])
            except Exception:
                pass
        return {
            'user_id': user.id,
            'final_password': new
        }

# 用户个人资料更新序列化器（仅自身或管理员使用）
class UserProfileUpdateSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=False, allow_blank=True, max_length=30)
    last_name = serializers.CharField(required=False, allow_blank=True, max_length=150)
    email = serializers.EmailField(required=False, allow_blank=True)

    def update(self, instance: User, validated_data):
        for k,v in validated_data.items():
            setattr(instance, k, v)
        instance.save(update_fields=list(validated_data.keys()))
        return instance

    def create(self, validated_data):
        raise NotImplementedError('仅用于 update')


# --- CompanyDocument 序列化器 ---
class CompanyDocumentSerializer(serializers.ModelSerializer):
    uploaded_by = UserSerializer(read_only=True)
    file_url = serializers.SerializerMethodField()
    class Meta:
        model = CompanyDocument
        fields = ['id','title','document_type','description','version','is_active','uploaded_by','file_url','created_at','updated_at']

    def get_file_url(self, obj: CompanyDocument):
        request = self.context.get('request')
        if not obj.file:
            return None
        try:
            url = obj.file.url
            if request:
                return request.build_absolute_uri(url)
            return url
        except Exception:
            return None

class CompanyDocumentWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyDocument
        fields = ['title','document_type','description','file','version','is_active']

    def validate_version(self, v):
        if v and len(v) > 20:
            raise serializers.ValidationError('版本号长度不要超过 20')
        return v

# --- RBAC 写序列化器 ---
class RBACPermissionWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = RBACPermission
        fields = ['key','name','description']

class RoleWriteSerializer(serializers.ModelSerializer):
    permission_ids = serializers.PrimaryKeyRelatedField(queryset=RBACPermission.objects.all(), many=True, required=False, write_only=True)
    user_ids = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True, required=False, write_only=True)
    class Meta:
        model = Role
        fields = ['name','code','description','permission_ids','user_ids']

    def create(self, validated_data):
        perms = validated_data.pop('permission_ids', [])
        users = validated_data.pop('user_ids', [])
        role = Role.objects.create(**validated_data)
        if perms:
            role.permissions.set(perms)
        if users:
            role.users.set(users)
        return role

    def update(self, instance, validated_data):
        perms = validated_data.pop('permission_ids', None)
        users = validated_data.pop('user_ids', None)
        for k,v in validated_data.items():
            setattr(instance, k, v)
        instance.save()
        if perms is not None:
            instance.permissions.set(perms)
        if users is not None:
            instance.users.set(users)
        return instance


class UserWriteSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=True, help_text='创建时必填，更新时选填（留空则不修改）')
    role_ids = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), many=True, required=False, write_only=True, help_text='分配的角色ID列表')

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser', 'role_ids']

    def validate_password(self, value):
        # 创建时密码必填
        if not self.instance and not value:
            raise serializers.ValidationError('创建用户时密码不能为空')
        return value

    def create(self, validated_data):
        role_ids = validated_data.pop('role_ids', [])
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data, password=password)
        if role_ids:
            user.roles.set(role_ids)
        return user

    def update(self, instance, validated_data):
        role_ids = validated_data.pop('role_ids', None)
        password = validated_data.pop('password', None)
        for k, v in validated_data.items():
            setattr(instance, k, v)
        if password:
            instance.set_password(password)
        instance.save()
        if role_ids is not None:
            instance.roles.set(role_ids)
        return instance


class BusinessTripSerializer(serializers.ModelSerializer):
    """出差申请读取序列化器"""
    employee = EmployeeSerializer(read_only=True)
    approved_by = UserSerializer(read_only=True)

    class Meta:
        model = BusinessTrip
        fields = [
            'id', 'employee', 'destination', 'trip_type', 'start_date', 'end_date',
            'days', 'reason', 'remarks', 'status', 'comments', 'approved_by', 'approved_at', 'created_at'
        ]


class BusinessTripWriteSerializer(serializers.ModelSerializer):
    """出差申请写入序列化器"""
    employee = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all(), required=False)

    class Meta:
        model = BusinessTrip
        fields = ['employee', 'destination', 'trip_type', 'start_date', 'end_date', 'days', 'reason', 'remarks']

    def validate(self, data):
        if data.get('start_date') and data.get('end_date'):
            if data['start_date'] > data['end_date']:
                raise serializers.ValidationError({'end_date': '结束日期不能早于开始日期'})
        return data


class TravelExpenseSerializer(serializers.ModelSerializer):
    """差旅报销读取序列化器"""
    employee = EmployeeSerializer(read_only=True)
    business_trip = BusinessTripSerializer(read_only=True)
    approved_by = UserSerializer(read_only=True)

    class Meta:
        model = TravelExpense
        fields = [
            'id', 'employee', 'expense_type', 'amount', 'business_trip', 'description',
            'invoice', 'remarks', 'status', 'comments', 'approved_by', 'approved_at', 'paid_at', 'created_at'
        ]


class TravelExpenseWriteSerializer(serializers.ModelSerializer):
    """差旅报销写入序列化器"""
    employee = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all(), required=False)
    business_trip_id = serializers.PrimaryKeyRelatedField(
        queryset=BusinessTrip.objects.all(),
        source='business_trip',
        required=False,
        allow_null=True
    )
    invoice = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = TravelExpense
        fields = ['employee', 'expense_type', 'amount', 'business_trip_id', 'description', 'invoice', 'remarks']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError('报销金额必须大于0')
        return value

    def validate_invoice(self, value):
        if value:
            # 限制文件类型和大小
            allowed_types = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg']
            if hasattr(value, 'content_type') and value.content_type not in allowed_types:
                raise serializers.ValidationError('只支持PDF和图片格式(JPG/PNG)')
            if value.size > 10 * 1024 * 1024:  # 10MB
                raise serializers.ValidationError('文件大小不能超过10MB')
        return value


class CheckInLocationSerializer(serializers.ModelSerializer):
    """签到地点读取序列化器"""
    class Meta:
        model = CheckInLocation
        fields = ['id', 'name', 'address', 'latitude', 'longitude', 'radius', 'is_active', 'is_default', 'created_at', 'updated_at']


class CheckInLocationWriteSerializer(serializers.ModelSerializer):
    """签到地点写入序列化器"""
    class Meta:
        model = CheckInLocation
        fields = ['name', 'address', 'latitude', 'longitude', 'radius', 'is_active', 'is_default']

    def validate_latitude(self, value):
        # 中国范围纬度：3.86° ~ 53.55°
        if value < 3.86 or value > 53.55:
            raise serializers.ValidationError('纬度超出中国范围(3.86° ~ 53.55°)')
        return value

    def validate_longitude(self, value):
        # 中国范围经度：73.66° ~ 135.05°
        if value < 73.66 or value > 135.05:
            raise serializers.ValidationError('经度超出中国范围(73.66° ~ 135.05°)')
        return value

    def validate_radius(self, value):
        if value < 50:
            raise serializers.ValidationError('允许范围不能小于50米')
        if value > 10000:
            raise serializers.ValidationError('允许范围不能大于10000米')
        return value
