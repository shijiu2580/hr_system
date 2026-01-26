from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.utils import timezone


class Department(models.Model):
    """部门模型"""
    name = models.CharField(max_length=100, verbose_name='部门名称')
    description = models.TextField(blank=True, verbose_name='部门描述')
    icon = models.ImageField(upload_to='departments/', blank=True, null=True, verbose_name='部门图标')
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='children', verbose_name='上级部门')
    manager = models.ForeignKey('Employee', on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='managed_departments', verbose_name='部门经理')
    supervisors = models.ManyToManyField('Employee', blank=True, related_name='supervised_departments',
                                         verbose_name='部门主管')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '部门'
        verbose_name_plural = '部门'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_full_path(self):
        """获取部门完整路径，如：总公司 > 技术部 > 前端组"""
        path = [self.name]
        parent = self.parent
        while parent:
            path.insert(0, parent.name)
            parent = parent.parent
        return ' > '.join(path)

    def get_all_children(self):
        """获取所有子部门（递归）"""
        children = list(self.children.all())
        for child in self.children.all():
            children.extend(child.get_all_children())
        return children


class Position(models.Model):
    """职位模型"""
    name = models.CharField(max_length=100, verbose_name='职位名称')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name='所属部门')
    description = models.TextField(blank=True, verbose_name='职位描述')
    salary_range_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                         verbose_name='最低薪资')
    salary_range_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                         verbose_name='最高薪资')
    requirements = models.TextField(blank=True, verbose_name='任职要求')
    default_roles = models.ManyToManyField('Role', blank=True, related_name='positions',
                                          verbose_name='默认角色')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '职位'
        verbose_name_plural = '职位'
        ordering = ['department', 'name']

    def __str__(self):
        return f"{self.department.name} - {self.name}"


class Employee(models.Model):
    """员工模型"""
    GENDER_CHOICES = [
        ('M', '男'),
        ('F', '女'),
    ]

    MARITAL_STATUS_CHOICES = [
        ('single', '未婚'),
        ('married', '已婚'),
        ('divorced', '离婚'),
        ('widowed', '丧偶'),
    ]

    # 入职状态：待入职（自助注册）→ 已入职（HR审核通过）→ 离职
    ONBOARD_STATUS_CHOICES = [
        ('pending', '待入职'),      # 自助注册，等待HR审核
        ('onboarded', '已入职'),    # HR审核通过，正式员工
        ('resigned', '已离职'),     # 离职
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='用户账户')
    employee_id = models.CharField(max_length=20, unique=True, verbose_name='员工编号')
    name = models.CharField(max_length=50, blank=True, verbose_name='姓名')
    english_name = models.CharField(max_length=50, blank=True, verbose_name='英文名')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, verbose_name='性别')
    birth_date = models.DateField(null=True, blank=True, verbose_name='出生日期')
    phone = models.CharField(max_length=20, blank=True, validators=[RegexValidator(
        regex=r'^1[3-9]\d{9}$', message='请输入有效的手机号码')], verbose_name='手机号码')
    email = models.EmailField(blank=True, verbose_name='邮箱')
    address = models.TextField(blank=True, verbose_name='联系地址')
    id_card = models.CharField(max_length=18, blank=True, validators=[RegexValidator(
        regex=r'^\d{17}[\dXx]$', message='请输入有效的身份证号码')], verbose_name='身份证号')
    passport_no = models.CharField(max_length=20, blank=True, verbose_name='护照号码')
    marital_status = models.CharField(max_length=10, choices=MARITAL_STATUS_CHOICES,
                                    default='single', blank=True, verbose_name='婚姻状况')
    emergency_contact = models.CharField(max_length=50, blank=True, verbose_name='紧急联系人')
    emergency_phone = models.CharField(max_length=20, blank=True, verbose_name='紧急联系电话')
    emergency_relation = models.CharField(max_length=20, blank=True, verbose_name='与本人关系')

    # 户籍信息
    nationality = models.CharField(max_length=50, default='中国', blank=True, verbose_name='国籍')
    native_place = models.CharField(max_length=100, blank=True, verbose_name='籍贯')
    hukou_location = models.CharField(max_length=200, blank=True, verbose_name='户籍所在地')
    hukou_type = models.CharField(max_length=20, blank=True, verbose_name='户籍性质')  # 农村/城镇
    hukou_address = models.CharField(max_length=200, blank=True, verbose_name='户籍地址')
    ethnicity = models.CharField(max_length=20, default='汉族', blank=True, verbose_name='民族')
    political_status = models.CharField(max_length=20, blank=True, verbose_name='政治面貌')  # 群众/团员/党员
    party_date = models.DateField(null=True, blank=True, verbose_name='入党/团日期')
    blood_type = models.CharField(max_length=5, blank=True, verbose_name='血型')

    # 教育信息
    education = models.CharField(max_length=20, blank=True, verbose_name='学历')  # 高中/大专/本科/硕士/博士
    school_type = models.CharField(max_length=20, blank=True, verbose_name='学校分类')  # 普通本科/211/985等
    school_name = models.CharField(max_length=100, blank=True, verbose_name='毕业学校名称')
    major = models.CharField(max_length=100, blank=True, verbose_name='专业')
    graduation_date = models.DateField(null=True, blank=True, verbose_name='毕业时间')

    # 银行信息
    bank_card_no = models.CharField(max_length=30, blank=True, verbose_name='工资卡银行账号')
    expense_card_no = models.CharField(max_length=30, blank=True, verbose_name='报销卡银行账号')

    # 设备信息
    computer_info = models.CharField(max_length=20, blank=True, verbose_name='电脑信息')  # 自带/公司配
    computer_brand = models.CharField(max_length=50, blank=True, verbose_name='电脑品牌')

    # 入职状态
    onboard_status = models.CharField(max_length=20, choices=ONBOARD_STATUS_CHOICES,
                                      default='onboarded', verbose_name='入职状态')
    onboard_reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                            related_name='reviewed_employees', verbose_name='入职审核人')
    onboard_reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name='入职审核时间')
    onboard_reject_reason = models.TextField(blank=True, verbose_name='入职拒绝原因')

    # 工作相关信息
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='所属部门')
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='职位')
    hire_date = models.DateField(null=True, blank=True, verbose_name='入职日期')
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='基本工资')
    is_active = models.BooleanField(default=True, verbose_name='在职状态')

    # 照片和文档
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='头像照片')
    id_card_front = models.ImageField(upload_to='documents/id_cards/', blank=True, null=True, verbose_name='身份证人像面')
    id_card_back = models.ImageField(upload_to='documents/id_cards/', blank=True, null=True, verbose_name='身份证国徽面')
    # 首次登录强制修改密码标记
    must_change_password = models.BooleanField(default=False, verbose_name='首次登录需改密码')

    # 关联的考勤地点（多对多）
    checkin_locations = models.ManyToManyField(
        'CheckInLocation',
        blank=True,
        related_name='employees',
        verbose_name='关联考勤地点'
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '员工'
        verbose_name_plural = '员工'
        ordering = ['employee_id']

    def __str__(self):
        return f"{self.employee_id} - {self.name}"

    def save(self, *args, **kwargs):
        """保存时自动生成员工编号"""
        if not self.employee_id:
            self.employee_id = self.generate_employee_id()
        super().save(*args, **kwargs)

    @classmethod
    def generate_employee_id(cls):
        """生成随机4位数员工编号"""
        import random
        existing_ids = set(cls.objects.values_list('employee_id', flat=True))
        for _ in range(1000):  # 最多尝试1000次
            new_id = str(random.randint(1000, 9999))
            if new_id not in existing_ids:
                return new_id
        # 如果4位数用完了，使用5位数
        return str(random.randint(10000, 99999))

    @property
    def age(self):
        """计算年龄"""
        if not self.birth_date:
            return None
        today = timezone.now().date()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )

    @property
    def work_years(self):
        """计算工作年限"""
        if not self.hire_date:
            return None
        today = timezone.now().date()
        return today.year - self.hire_date.year - (
            (today.month, today.day) < (self.hire_date.month, self.hire_date.day)
        )


class Attendance(models.Model):
    """考勤记录模型"""
    ATTENDANCE_TYPE_CHOICES = [
        ('check_in', '上班打卡'),
        ('check_out', '下班打卡'),
        ('late', '迟到'),
        ('early_leave', '早退'),
        ('absent', '缺勤'),
        ('leave', '请假'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name='员工')
    date = models.DateField(verbose_name='日期')
    check_in_time = models.TimeField(null=True, blank=True, verbose_name='上班时间')
    check_out_time = models.TimeField(null=True, blank=True, verbose_name='下班时间')
    attendance_type = models.CharField(max_length=20, choices=ATTENDANCE_TYPE_CHOICES,
                                     default='check_in', verbose_name='考勤类型')
    notes = models.TextField(blank=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '考勤记录'
        verbose_name_plural = '考勤记录'
        ordering = ['-date', 'employee']
        unique_together = ['employee', 'date']
        indexes = [
            models.Index(fields=['date', 'attendance_type']),
            models.Index(fields=['employee', '-date']),
        ]

    def __str__(self):
        return f"{self.employee.name} - {self.date}"


class AttendanceSupplement(models.Model):
    """考勤补签申请模型"""
    SUPPLEMENT_TYPE_CHOICES = [
        ('check_in', '补签到'),
        ('check_out', '补签退'),
    ]

    STATUS_CHOICES = [
        ('pending', '待审批'),
        ('approved', '已批准'),
        ('rejected', '已拒绝'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name='员工')
    date = models.DateField(verbose_name='补签日期')
    time = models.TimeField(verbose_name='补签时间')
    supplement_type = models.CharField(max_length=20, choices=SUPPLEMENT_TYPE_CHOICES, verbose_name='补签类型')
    reason = models.TextField(verbose_name='补签原因')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   verbose_name='审批人')
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name='审批时间')
    comments = models.TextField(blank=True, verbose_name='审批意见')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='申请时间')

    class Meta:
        verbose_name = '补签申请'
        verbose_name_plural = '补签申请'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['employee', '-created_at']),
        ]

    def __str__(self):
        return f"{self.employee.name} - {self.date} - {self.get_supplement_type_display()}"


class LeaveRequest(models.Model):
    """请假申请模型"""
    LEAVE_TYPE_CHOICES = [
        ('sick', '病假'),
        ('personal', '事假'),
        ('annual', '年假'),
        ('maternity', '产假'),
        ('paternity', '陪产假'),
        ('other', '其他'),
        ('resignation', '离职申请'),
    ]

    STATUS_CHOICES = [
        ('pending', '待审批'),
        ('approved', '已批准'),
        ('rejected', '已拒绝'),
    ]

    RESIGN_APPROVAL_CHOICES = [
        ('pending', '待处理'),
        ('approved', '已同意'),
        ('rejected', '已拒绝'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name='员工')
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPE_CHOICES, verbose_name='请假类型')
    start_date = models.DateField(verbose_name='开始日期')
    end_date = models.DateField(verbose_name='结束日期')
    days = models.IntegerField(verbose_name='请假天数')
    reason = models.TextField(verbose_name='请假原因')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   verbose_name='审批人')
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name='审批时间')
    comments = models.TextField(blank=True, verbose_name='审批意见')
    attachment = models.FileField(upload_to='documents/leave_attachments/', blank=True, null=True, verbose_name='附件')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='申请时间')
    resignation_manager_status = models.CharField(max_length=20, choices=RESIGN_APPROVAL_CHOICES, default='pending', verbose_name='直属上级审批状态')
    resignation_hr_status = models.CharField(max_length=20, choices=RESIGN_APPROVAL_CHOICES, default='pending', verbose_name='人事审批状态')
    resignation_manager_comment = models.TextField(blank=True, verbose_name='直属上级意见')
    resignation_hr_comment = models.TextField(blank=True, verbose_name='人事意见')
    resignation_manager_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resignation_manager_reviews', verbose_name='直属上级审批人')
    resignation_hr_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resignation_hr_reviews', verbose_name='人事审批人')
    resignation_manager_at = models.DateTimeField(null=True, blank=True, verbose_name='直属上级审批时间')
    resignation_hr_at = models.DateTimeField(null=True, blank=True, verbose_name='人事审批时间')

    class Meta:
        verbose_name = '请假申请'
        verbose_name_plural = '请假申请'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['employee', 'leave_type', 'status']),
        ]

    def __str__(self):
        return f"{self.employee.name} - {self.leave_type} - {self.start_date}"


class SalaryRecord(models.Model):
    """薪资记录模型"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name='员工')
    year = models.IntegerField(verbose_name='年份')
    month = models.IntegerField(verbose_name='月份')
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='基本工资')
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='奖金')
    overtime_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='加班费')
    allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='津贴')
    net_salary = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='实发工资')
    paid = models.BooleanField(default=False, verbose_name='已发薪')
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name='发薪时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '薪资记录'
        verbose_name_plural = '薪资记录'
        ordering = ['-year', '-month', 'employee']
        unique_together = ['employee', 'year', 'month']

    def __str__(self):
        return f"{self.employee.name} - {self.year}年{self.month}月"

    def save(self, *args, **kwargs):
        # 自动计算实发工资
        self.net_salary = self.basic_salary + self.bonus + self.overtime_pay + self.allowance
        super().save(*args, **kwargs)


class CompanyDocument(models.Model):
    """公司文档模型"""
    DOCUMENT_TYPE_CHOICES = [
        ('policy', '政策文件'),
        ('procedure', '流程文件'),
        ('template', '模板文件'),
        ('announcement', '公告通知'),
        ('training', '培训资料'),
        ('other', '其他'),
    ]

    title = models.CharField(max_length=200, verbose_name='文档标题')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES, verbose_name='文档类型')
    description = models.TextField(blank=True, verbose_name='文档描述')
    file = models.FileField(upload_to='documents/company/', verbose_name='文档文件')
    version = models.CharField(max_length=20, default='1.0', verbose_name='版本号')
    is_active = models.BooleanField(default=True, verbose_name='是否有效')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='上传人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '公司文档'
        verbose_name_plural = '公司文档'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - v{self.version}"


class SystemLog(models.Model):
    """系统日志模型（避免与 django.contrib.admin LogEntry 冲突）"""
    LEVEL_CHOICES = [
        ('INFO', '信息'),
        ('WARNING', '警告'),
        ('ERROR', '错误'),
        ('DEBUG', '调试'),
    ]

    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='时间')
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default='INFO', verbose_name='级别')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='system_logs', verbose_name='用户')
    action = models.CharField(max_length=100, verbose_name='操作')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP地址')
    detail = models.TextField(blank=True, verbose_name='详情')

    class Meta:
        verbose_name = '系统日志'
        verbose_name_plural = '系统日志'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['level', '-timestamp']),
            models.Index(fields=['-timestamp']),
        ]

    def __str__(self):
        return f"[{self.level}] {self.action} - {self.timestamp:%Y-%m-%d %H:%M:%S}"


class RBACPermission(models.Model):
    """细粒度权限定义（自定义业务权限标签，而不是直接使用 Django 内置权限）"""
    key = models.CharField(max_length=50, unique=True, verbose_name='权限键')
    name = models.CharField(max_length=100, verbose_name='权限名称')
    description = models.TextField(blank=True, verbose_name='描述')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = 'RBAC权限'
        verbose_name_plural = 'RBAC权限'
        ordering = ['id']

    def __str__(self):
        return f"{self.key} ({self.name})"


class Role(models.Model):
    """角色：聚合一组 RBACPermission，并可分配给用户"""
    name = models.CharField(max_length=100, unique=True, verbose_name='角色名称')
    code = models.SlugField(max_length=50, unique=True, verbose_name='代码')
    description = models.TextField(blank=True, verbose_name='描述')
    permissions = models.ManyToManyField(RBACPermission, blank=True, related_name='roles', verbose_name='权限集合')
    users = models.ManyToManyField(User, blank=True, related_name='roles', verbose_name='关联用户')
    is_system = models.BooleanField(default=False, verbose_name='系统内置')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '角色'
        verbose_name_plural = '角色'
        ordering = ['code']

    def __str__(self):
        return self.name

    def has_permission(self, key: str) -> bool:
        return self.permissions.filter(key=key).exists()


def user_has_rbac_permission(user: User, key: str) -> bool:
    """检查用户是否具备某个自定义 RBAC 权限。

    权限来源（混合模式）：
    1. 超级管理员(superuser)直接放行
    2. 用户直接关联的角色
    3. 用户员工档案对应职位的默认角色
    """
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True

    # 检查用户直接关联的角色
    if Role.objects.filter(users=user, permissions__key=key).exists():
        return True

    # 检查职位默认角色
    try:
        employee = user.employee
        if employee and employee.position:
            if Role.objects.filter(positions=employee.position, permissions__key=key).exists():
                return True
    except Exception:
        pass

    return False


def get_user_all_roles(user: User):
    """获取用户的所有角色（个人角色 + 职位默认角色）"""
    roles = set(user.roles.all())
    try:
        employee = user.employee
        if employee and employee.position:
            roles.update(employee.position.default_roles.all())
    except Exception:
        pass
    return list(roles)


def get_user_all_permissions(user: User):
    """获取用户的所有权限键（合并个人角色和职位角色）"""
    if not user.is_authenticated:
        return []
    if user.is_superuser:
        return ['*']  # 表示全部权限

    permission_keys = set()
    for role in get_user_all_roles(user):
        permission_keys.update(role.permissions.values_list('key', flat=True))
    return list(permission_keys)


class BusinessTrip(models.Model):
    """出差申请模型"""
    TRIP_TYPE_CHOICES = [
        ('domestic', '国内出差'),
        ('overseas', '海外出差'),
    ]

    STATUS_CHOICES = [
        ('pending', '待审批'),
        ('approved', '已批准'),
        ('rejected', '已拒绝'),
        ('cancelled', '已取消'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name='员工')
    destination = models.CharField(max_length=200, verbose_name='出差地点')
    trip_type = models.CharField(max_length=20, choices=TRIP_TYPE_CHOICES, default='domestic', verbose_name='出差类型')
    start_date = models.DateField(verbose_name='开始日期')
    end_date = models.DateField(verbose_name='结束日期')
    days = models.IntegerField(verbose_name='出差天数')
    reason = models.TextField(verbose_name='出差事由')
    remarks = models.TextField(blank=True, verbose_name='备注')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   verbose_name='审批人')
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name='审批时间')
    comments = models.TextField(blank=True, verbose_name='审批意见')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='申请时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '出差申请'
        verbose_name_plural = '出差申请'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['employee', '-created_at']),
        ]

    def __str__(self):
        return f"{self.employee.name} - {self.destination} ({self.start_date} 至 {self.end_date})"


class VerificationCode(models.Model):
    """手机验证码模型（用于找回密码等场景）"""
    CODE_TYPE_CHOICES = [
        ('reset_password', '重置密码'),
        ('register', '注册验证'),
        ('login', '登录验证'),
    ]

    phone = models.CharField(max_length=11, verbose_name='手机号')
    code = models.CharField(max_length=6, verbose_name='验证码')
    code_type = models.CharField(max_length=20, choices=CODE_TYPE_CHOICES, default='reset_password', verbose_name='验证码类型')
    is_used = models.BooleanField(default=False, verbose_name='是否已使用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    expires_at = models.DateTimeField(verbose_name='过期时间')

    class Meta:
        verbose_name = '验证码'
        verbose_name_plural = '验证码'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['phone', 'code_type', '-created_at']),
        ]

    def __str__(self):
        return f"{self.phone} - {self.code} ({self.code_type})"

    def is_valid(self):
        """检查验证码是否有效"""
        return not self.is_used and timezone.now() < self.expires_at


class CheckInLocation(models.Model):
    """签到地点模型"""
    name = models.CharField(max_length=100, verbose_name='地点名称')
    address = models.CharField(max_length=255, verbose_name='详细地址')
    latitude = models.DecimalField(max_digits=10, decimal_places=7, verbose_name='纬度')
    longitude = models.DecimalField(max_digits=10, decimal_places=7, verbose_name='经度')
    radius = models.IntegerField(default=1000, verbose_name='允许范围(米)')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    is_default = models.BooleanField(default=False, verbose_name='是否为默认签到点')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '签到地点'
        verbose_name_plural = '签到地点'
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.name} ({self.address})"

    def save(self, *args, **kwargs):
        # 如果设为默认，将其他的默认取消
        if self.is_default:
            CheckInLocation.objects.filter(is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)


class TravelExpense(models.Model):
    """差旅报销模型"""
    EXPENSE_TYPE_CHOICES = [
        ('travel', '差旅费'),
        ('transport', '交通费'),
        ('accommodation', '住宿费'),
        ('meal', '餐饮费'),
        ('other', '其他'),
    ]

    STATUS_CHOICES = [
        ('pending', '待审批'),
        ('approved', '已批准'),
        ('rejected', '已拒绝'),
        ('paid', '已报销'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name='员工')
    expense_type = models.CharField(max_length=20, choices=EXPENSE_TYPE_CHOICES, default='travel', verbose_name='报销类型')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='报销金额')
    business_trip = models.ForeignKey(BusinessTrip, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='expenses', verbose_name='关联出差')
    description = models.TextField(verbose_name='报销事由')
    invoice = models.FileField(upload_to='invoices/', blank=True, null=True, verbose_name='发票文件')
    remarks = models.TextField(blank=True, verbose_name='备注')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   verbose_name='审批人')
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name='审批时间')
    comments = models.TextField(blank=True, verbose_name='审批意见')
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name='报销时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='申请时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '差旅报销'
        verbose_name_plural = '差旅报销'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['employee', '-created_at']),
        ]

    def __str__(self):
        return f"{self.employee.name} - {self.get_expense_type_display()} - ¥{self.amount}"
