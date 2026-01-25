"""
RBAC 权限系统核心模块

定义系统所有权限常量，以及权限检查工具函数
"""
from functools import wraps
from rest_framework.response import Response


# ================== 权限常量定义 ==================
# 格式：模块.操作

class Permissions:
    """系统权限常量"""
    
    # -------- 员工管理 --------
    EMPLOYEE_VIEW = 'employee.view'           # 查看员工
    EMPLOYEE_CREATE = 'employee.create'       # 创建员工
    EMPLOYEE_EDIT = 'employee.edit'           # 编辑员工
    EMPLOYEE_DELETE = 'employee.delete'       # 删除员工
    EMPLOYEE_IMPORT = 'employee.import'       # 导入员工
    EMPLOYEE_EXPORT = 'employee.export'       # 导出员工
    
    # -------- 部门管理 --------
    DEPARTMENT_VIEW = 'department.view'       # 查看部门
    DEPARTMENT_CREATE = 'department.create'   # 创建部门
    DEPARTMENT_EDIT = 'department.edit'       # 编辑部门
    DEPARTMENT_DELETE = 'department.delete'   # 删除部门
    
    # -------- 职位管理 --------
    POSITION_VIEW = 'position.view'           # 查看职位
    POSITION_CREATE = 'position.create'       # 创建职位
    POSITION_EDIT = 'position.edit'           # 编辑职位
    POSITION_DELETE = 'position.delete'       # 删除职位
    
    # -------- 考勤管理 --------
    ATTENDANCE_VIEW = 'attendance.view'             # 查看考勤
    ATTENDANCE_VIEW_ALL = 'attendance.view_all'     # 查看所有人考勤
    ATTENDANCE_EDIT = 'attendance.edit'             # 编辑考勤
    ATTENDANCE_APPROVE = 'attendance.approve'       # 审批补签
    ATTENDANCE_LOCATION = 'attendance.location'     # 管理考勤地点
    
    # -------- 请假管理 --------
    LEAVE_VIEW = 'leave.view'                 # 查看请假
    LEAVE_VIEW_ALL = 'leave.view_all'         # 查看所有请假
    LEAVE_CREATE = 'leave.create'             # 创建请假
    LEAVE_APPROVE = 'leave.approve'           # 审批请假
    
    # -------- 出差管理 --------
    TRIP_VIEW = 'trip.view'                   # 查看出差
    TRIP_VIEW_ALL = 'trip.view_all'           # 查看所有出差
    TRIP_CREATE = 'trip.create'               # 创建出差
    TRIP_APPROVE = 'trip.approve'             # 审批出差
    
    # -------- 薪资管理 --------
    SALARY_VIEW = 'salary.view'               # 查看薪资
    SALARY_VIEW_ALL = 'salary.view_all'       # 查看所有薪资
    SALARY_CREATE = 'salary.create'           # 创建薪资
    SALARY_EDIT = 'salary.edit'               # 编辑薪资
    SALARY_DELETE = 'salary.delete'           # 删除薪资
    SALARY_DISBURSE = 'salary.disburse'       # 发放薪资
    
    # -------- 报销管理 --------
    EXPENSE_VIEW = 'expense.view'             # 查看报销
    EXPENSE_VIEW_ALL = 'expense.view_all'     # 查看所有报销
    EXPENSE_CREATE = 'expense.create'         # 创建报销
    EXPENSE_APPROVE = 'expense.approve'       # 审批报销
    
    # -------- 文档管理 --------
    DOCUMENT_VIEW = 'document.view'           # 查看文档
    DOCUMENT_UPLOAD = 'document.upload'       # 上传文档
    DOCUMENT_DELETE = 'document.delete'       # 删除文档
    DOCUMENT_MANAGE = 'document.manage'       # 管理公司文档
    
    # -------- 报表统计 --------
    REPORT_VIEW = 'report.view'               # 查看报表
    REPORT_EXPORT = 'report.export'           # 导出报表
    REPORT_EMPLOYEE = 'report.employee'       # 员工报表
    REPORT_ATTENDANCE = 'report.attendance'   # 考勤报表
    REPORT_SALARY = 'report.salary'           # 薪资报表
    REPORT_LEAVE = 'report.leave'             # 请假报表
    
    # -------- 系统管理 --------
    SYSTEM_VIEW = 'system.view'               # 查看系统设置
    SYSTEM_LOG = 'system.log'                 # 查看系统日志
    SYSTEM_LOG_VIEW = 'system.log_view'       # 查看系统日志
    SYSTEM_LOG_CLEAR = 'system.log_clear'     # 清除系统日志
    SYSTEM_BACKUP = 'system.backup'           # 系统备份
    SYSTEM_BACKUP_VIEW = 'system.backup_view' # 查看备份
    SYSTEM_BACKUP_CREATE = 'system.backup_create'  # 创建备份
    SYSTEM_BACKUP_RESTORE = 'system.backup_restore'  # 恢复备份
    SYSTEM_RESTORE = 'system.restore'         # 系统恢复
    
    # -------- 文档管理补充 --------
    DOCUMENT_CREATE = 'document.create'       # 创建文档
    DOCUMENT_EDIT = 'document.edit'           # 编辑文档
    
    # -------- 考勤管理补充 --------
    ATTENDANCE_CREATE = 'attendance.create'   # 创建考勤记录
    
    # -------- 用户管理 --------
    USER_VIEW = 'user.view'                   # 查看用户
    USER_CREATE = 'user.create'               # 创建用户
    USER_EDIT = 'user.edit'                   # 编辑用户
    USER_DELETE = 'user.delete'               # 删除用户
    USER_RESET_PASSWORD = 'user.reset_password'  # 重置密码
    
    # -------- 权限管理 --------
    RBAC_VIEW = 'rbac.view'                     # 查看角色权限
    RBAC_MANAGE = 'rbac.manage'                 # 管理角色权限
    RBAC_ROLE_MANAGE = 'rbac.role_manage'       # 管理角色
    RBAC_PERMISSION_MANAGE = 'rbac.permission_manage'  # 管理权限
    
    # -------- 离职管理 --------
    RESIGNATION_VIEW = 'resignation.view'           # 查看离职
    RESIGNATION_VIEW_ALL = 'resignation.view_all'   # 查看所有离职
    RESIGNATION_CREATE = 'resignation.create'       # 发起离职
    RESIGNATION_APPROVE = 'resignation.approve'     # 审批离职


# 权限分组定义（用于初始化和展示）
PERMISSION_GROUPS = {
    '员工管理': [
        (Permissions.EMPLOYEE_VIEW, '查看员工', '查看员工基本信息'),
        (Permissions.EMPLOYEE_CREATE, '创建员工', '创建新员工档案'),
        (Permissions.EMPLOYEE_EDIT, '编辑员工', '编辑员工信息'),
        (Permissions.EMPLOYEE_DELETE, '删除员工', '删除员工档案'),
        (Permissions.EMPLOYEE_IMPORT, '导入员工', '批量导入员工数据'),
        (Permissions.EMPLOYEE_EXPORT, '导出员工', '导出员工数据'),
    ],
    '部门管理': [
        (Permissions.DEPARTMENT_VIEW, '查看部门', '查看部门信息'),
        (Permissions.DEPARTMENT_CREATE, '创建部门', '创建新部门'),
        (Permissions.DEPARTMENT_EDIT, '编辑部门', '编辑部门信息'),
        (Permissions.DEPARTMENT_DELETE, '删除部门', '删除部门'),
    ],
    '职位管理': [
        (Permissions.POSITION_VIEW, '查看职位', '查看职位信息'),
        (Permissions.POSITION_CREATE, '创建职位', '创建新职位'),
        (Permissions.POSITION_EDIT, '编辑职位', '编辑职位信息'),
        (Permissions.POSITION_DELETE, '删除职位', '删除职位'),
    ],
    '考勤管理': [
        (Permissions.ATTENDANCE_VIEW, '查看考勤', '查看自己的考勤记录'),
        (Permissions.ATTENDANCE_VIEW_ALL, '查看所有考勤', '查看所有员工的考勤记录'),
        (Permissions.ATTENDANCE_CREATE, '创建考勤', '创建考勤记录'),
        (Permissions.ATTENDANCE_EDIT, '编辑考勤', '编辑考勤记录'),
        (Permissions.ATTENDANCE_APPROVE, '审批补签', '审批员工补签申请'),
        (Permissions.ATTENDANCE_LOCATION, '管理考勤地点', '管理考勤打卡地点'),
    ],
    '请假管理': [
        (Permissions.LEAVE_VIEW, '查看请假', '查看自己的请假记录'),
        (Permissions.LEAVE_VIEW_ALL, '查看所有请假', '查看所有员工的请假记录'),
        (Permissions.LEAVE_CREATE, '创建请假', '发起请假申请'),
        (Permissions.LEAVE_APPROVE, '审批请假', '审批员工请假申请'),
    ],
    '出差管理': [
        (Permissions.TRIP_VIEW, '查看出差', '查看自己的出差记录'),
        (Permissions.TRIP_VIEW_ALL, '查看所有出差', '查看所有员工的出差记录'),
        (Permissions.TRIP_CREATE, '创建出差', '发起出差申请'),
        (Permissions.TRIP_APPROVE, '审批出差', '审批员工出差申请'),
    ],
    '薪资管理': [
        (Permissions.SALARY_VIEW, '查看薪资', '查看自己的薪资记录'),
        (Permissions.SALARY_VIEW_ALL, '查看所有薪资', '查看所有员工的薪资记录'),
        (Permissions.SALARY_CREATE, '创建薪资', '创建薪资记录'),
        (Permissions.SALARY_EDIT, '编辑薪资', '编辑薪资记录'),
        (Permissions.SALARY_DELETE, '删除薪资', '删除薪资记录'),
        (Permissions.SALARY_DISBURSE, '发放薪资', '批量发放薪资'),
    ],
    '报销管理': [
        (Permissions.EXPENSE_VIEW, '查看报销', '查看自己的报销记录'),
        (Permissions.EXPENSE_VIEW_ALL, '查看所有报销', '查看所有员工的报销记录'),
        (Permissions.EXPENSE_CREATE, '创建报销', '发起报销申请'),
        (Permissions.EXPENSE_APPROVE, '审批报销', '审批报销申请'),
    ],
    '文档管理': [
        (Permissions.DOCUMENT_VIEW, '查看文档', '查看文档'),
        (Permissions.DOCUMENT_CREATE, '创建文档', '创建新文档'),
        (Permissions.DOCUMENT_EDIT, '编辑文档', '编辑文档'),
        (Permissions.DOCUMENT_UPLOAD, '上传文档', '上传文档'),
        (Permissions.DOCUMENT_DELETE, '删除文档', '删除文档'),
        (Permissions.DOCUMENT_MANAGE, '管理公司文档', '管理公司公开文档'),
    ],
    '报表统计': [
        (Permissions.REPORT_VIEW, '查看报表', '查看统计报表'),
        (Permissions.REPORT_EXPORT, '导出报表', '导出统计报表'),
        (Permissions.REPORT_EMPLOYEE, '员工报表', '查看员工统计报表'),
        (Permissions.REPORT_ATTENDANCE, '考勤报表', '查看考勤统计报表'),
        (Permissions.REPORT_SALARY, '薪资报表', '查看薪资统计报表'),
        (Permissions.REPORT_LEAVE, '请假报表', '查看请假统计报表'),
    ],
    '系统管理': [
        (Permissions.SYSTEM_VIEW, '查看系统设置', '查看系统配置'),
        (Permissions.SYSTEM_LOG, '查看系统日志', '查看系统日志'),
        (Permissions.SYSTEM_LOG_VIEW, '查看日志详情', '查看系统日志详情'),
        (Permissions.SYSTEM_LOG_CLEAR, '清除系统日志', '清除系统日志'),
        (Permissions.SYSTEM_BACKUP, '系统备份', '执行系统备份'),
        (Permissions.SYSTEM_BACKUP_VIEW, '查看备份', '查看备份列表'),
        (Permissions.SYSTEM_BACKUP_CREATE, '创建备份', '创建系统备份'),
        (Permissions.SYSTEM_BACKUP_RESTORE, '恢复备份', '从备份恢复系统'),
        (Permissions.SYSTEM_RESTORE, '系统恢复', '执行系统恢复'),
    ],
    '用户管理': [
        (Permissions.USER_VIEW, '查看用户', '查看用户列表'),
        (Permissions.USER_CREATE, '创建用户', '创建新用户'),
        (Permissions.USER_EDIT, '编辑用户', '编辑用户信息'),
        (Permissions.USER_DELETE, '删除用户', '删除用户'),
        (Permissions.USER_RESET_PASSWORD, '重置密码', '重置用户密码'),
    ],
    '权限管理': [
        (Permissions.RBAC_VIEW, '查看角色权限', '查看角色和权限'),
        (Permissions.RBAC_MANAGE, '管理角色权限', '创建、编辑、删除角色和权限'),
        (Permissions.RBAC_ROLE_MANAGE, '管理角色', '创建、编辑、删除角色'),
        (Permissions.RBAC_PERMISSION_MANAGE, '管理权限', '创建、编辑、删除权限'),
    ],
    '离职管理': [
        (Permissions.RESIGNATION_VIEW, '查看离职', '查看自己的离职申请'),
        (Permissions.RESIGNATION_VIEW_ALL, '查看所有离职', '查看所有员工的离职申请'),
        (Permissions.RESIGNATION_CREATE, '发起离职', '发起离职申请'),
        (Permissions.RESIGNATION_APPROVE, '审批离职', '审批离职申请'),
    ],
}


# 默认角色定义
DEFAULT_ROLES = {
    'admin': {
        'name': '系统管理员',
        'description': '拥有系统所有权限',
        'is_system': True,
        'permissions': '*',  # 所有权限
    },
    'hr_manager': {
        'name': '人事经理',
        'description': '管理员工、考勤、请假、薪资等人事相关事务',
        'is_system': True,
        'permissions': [
            Permissions.EMPLOYEE_VIEW, Permissions.EMPLOYEE_CREATE, 
            Permissions.EMPLOYEE_EDIT, Permissions.EMPLOYEE_IMPORT, 
            Permissions.EMPLOYEE_EXPORT,
            Permissions.DEPARTMENT_VIEW, Permissions.DEPARTMENT_CREATE,
            Permissions.DEPARTMENT_EDIT,
            Permissions.POSITION_VIEW, Permissions.POSITION_CREATE,
            Permissions.POSITION_EDIT,
            Permissions.ATTENDANCE_VIEW_ALL, Permissions.ATTENDANCE_EDIT,
            Permissions.ATTENDANCE_APPROVE, Permissions.ATTENDANCE_LOCATION,
            Permissions.LEAVE_VIEW_ALL, Permissions.LEAVE_APPROVE,
            Permissions.TRIP_VIEW_ALL, Permissions.TRIP_APPROVE,
            Permissions.SALARY_VIEW_ALL, Permissions.SALARY_CREATE,
            Permissions.SALARY_EDIT, Permissions.SALARY_DISBURSE,
            Permissions.EXPENSE_VIEW_ALL, Permissions.EXPENSE_APPROVE,
            Permissions.DOCUMENT_VIEW, Permissions.DOCUMENT_UPLOAD,
            Permissions.DOCUMENT_MANAGE,
            Permissions.REPORT_VIEW, Permissions.REPORT_EXPORT,
            Permissions.USER_VIEW,
            Permissions.RESIGNATION_VIEW_ALL, Permissions.RESIGNATION_APPROVE,
        ],
    },
    'department_manager': {
        'name': '部门经理',
        'description': '管理本部门员工的考勤、请假等事务',
        'is_system': True,
        'permissions': [
            Permissions.EMPLOYEE_VIEW,
            Permissions.DEPARTMENT_VIEW,
            Permissions.POSITION_VIEW,
            Permissions.ATTENDANCE_VIEW_ALL, Permissions.ATTENDANCE_APPROVE,
            Permissions.LEAVE_VIEW_ALL, Permissions.LEAVE_APPROVE,
            Permissions.TRIP_VIEW_ALL, Permissions.TRIP_APPROVE,
            Permissions.EXPENSE_VIEW_ALL, Permissions.EXPENSE_APPROVE,
            Permissions.DOCUMENT_VIEW, Permissions.DOCUMENT_UPLOAD,
            Permissions.REPORT_VIEW,
            Permissions.RESIGNATION_VIEW_ALL, Permissions.RESIGNATION_APPROVE,
        ],
    },
    'employee': {
        'name': '普通员工',
        'description': '普通员工基本权限',
        'is_system': True,
        'permissions': [
            Permissions.EMPLOYEE_VIEW,
            Permissions.DEPARTMENT_VIEW,
            Permissions.POSITION_VIEW,
            Permissions.ATTENDANCE_VIEW,
            Permissions.LEAVE_VIEW, Permissions.LEAVE_CREATE,
            Permissions.TRIP_VIEW, Permissions.TRIP_CREATE,
            Permissions.SALARY_VIEW,
            Permissions.EXPENSE_VIEW, Permissions.EXPENSE_CREATE,
            Permissions.DOCUMENT_VIEW, Permissions.DOCUMENT_UPLOAD,
            Permissions.RESIGNATION_VIEW, Permissions.RESIGNATION_CREATE,
        ],
    },
}


def user_has_permission(user, permission_key):
    """检查用户是否拥有指定权限
    
    Args:
        user: Django User 对象
        permission_key: 权限键字符串
        
    Returns:
        bool: 是否拥有权限
    """
    if not user or not user.is_authenticated:
        return False
    
    # 超级管理员拥有所有权限
    if user.is_superuser:
        return True
    
    # 管理员角色拥有所有权限
    if hasattr(user, 'roles'):
        if user.roles.filter(code='admin').exists():
            return True
    
    # 检查用户角色中是否包含该权限
    from .models import Role
    return Role.objects.filter(
        users=user, 
        permissions__key=permission_key
    ).exists()


def require_permission(*permission_keys, any_of=False):
    """权限检查装饰器，用于视图函数
    
    Args:
        permission_keys: 需要的权限键
        any_of: True表示只需满足任一权限，False表示需要满足所有权限
        
    Usage:
        @require_permission('employee.view')
        def get(self, request):
            ...
            
        @require_permission('employee.edit', 'employee.delete', any_of=True)
        def post(self, request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(self, request, *args, **kwargs):
            user = request.user
            
            if not user or not user.is_authenticated:
                return Response({'success': False, 'message': '请先登录'}, status=401)
            
            # 超级管理员直接放行
            if user.is_superuser:
                return view_func(self, request, *args, **kwargs)
            
            # 检查权限
            if any_of:
                has_perm = any(user_has_permission(user, key) for key in permission_keys)
            else:
                has_perm = all(user_has_permission(user, key) for key in permission_keys)
            
            if not has_perm:
                return Response({
                    'success': False, 
                    'message': '权限不足',
                    'code': 'permission_denied',
                    'required_permissions': list(permission_keys)
                }, status=403)
            
            return view_func(self, request, *args, **kwargs)
        return wrapped_view
    return decorator


class RBACPermissionMixin:
    """RBAC权限检查Mixin，用于类视图
    
    Usage:
        class MyView(RBACPermissionMixin, APIView):
            required_permissions = ['employee.view']
            # 或
            required_any_permission = ['employee.edit', 'employee.delete']
    """
    required_permissions = []  # 需要所有权限
    required_any_permission = []  # 只需任一权限
    
    def check_rbac_permission(self, request):
        """检查RBAC权限"""
        user = request.user
        
        if not user or not user.is_authenticated:
            return False, '请先登录'
        
        # 超级管理员直接放行
        if user.is_superuser:
            return True, None
        
        # 检查所有必需权限
        if self.required_permissions:
            for key in self.required_permissions:
                if not user_has_permission(user, key):
                    return False, f'缺少权限: {key}'
        
        # 检查任一权限
        if self.required_any_permission:
            if not any(user_has_permission(user, key) for key in self.required_any_permission):
                return False, '权限不足'
        
        return True, None
    
    def dispatch(self, request, *args, **kwargs):
        has_perm, message = self.check_rbac_permission(request)
        if not has_perm:
            return Response({
                'success': False,
                'message': message,
                'code': 'permission_denied'
            }, status=403)
        return super().dispatch(request, *args, **kwargs)
