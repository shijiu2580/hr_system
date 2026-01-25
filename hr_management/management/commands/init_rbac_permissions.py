from django.core.management.base import BaseCommand
from django.db import transaction
from hr_management.models import RBACPermission, Role

DEFAULT_PERMISSIONS = [
    # 系统管理
    ("manage_backups", "管理备份", "创建/恢复/清理数据库备份"),
    ("manage_system_logs", "管理系统日志", "查看与清理系统日志"),
    ("manage_system_settings", "系统设置", "修改系统配置参数"),
    
    # 员工管理
    ("view_employees", "查看员工", "查看员工基本信息"),
    ("manage_employees", "管理员工", "新增/编辑/停用员工信息"),
    ("view_employee_sensitive", "查看敏感信息", "查看员工身份证、薪资等敏感字段"),
    ("export_employees", "导出员工数据", "导出员工信息为Excel/CSV"),
    
    # 组织架构
    ("view_departments", "查看部门", "查看部门列表和信息"),
    ("manage_departments", "管理部门", "新增/编辑/删除部门"),
    ("view_positions", "查看职位", "查看职位列表和信息"),
    ("manage_positions", "管理职位", "新增/编辑/删除职位"),
    
    # 考勤管理
    ("view_attendance", "查看考勤", "查看考勤记录"),
    ("manage_attendance", "管理考勤", "新增/编辑/删除考勤记录"),
    ("export_attendance", "导出考勤", "导出考勤数据"),
    
    # 请假管理
    ("view_leaves", "查看请假", "查看请假申请记录"),
    ("apply_leave", "申请请假", "提交请假申请"),
    ("approve_leave", "审批请假", "审批请假申请"),
    
    # 薪资管理
    ("view_salaries", "查看薪资", "查看薪资记录"),
    ("manage_salaries", "管理薪资", "新增/编辑薪资记录"),
    ("disburse_salaries", "发放薪资", "执行薪资发放操作"),
    ("export_salaries", "导出薪资", "导出薪资报表"),
    
    # 报表统计
    ("view_reports", "查看报表", "查看统计报表"),
    ("view_sensitive_reports", "查看敏感报表", "访问包含敏感数据的报表"),
    ("export_reports", "导出报表", "导出统计报表"),
    
    # 权限管理
    ("view_roles", "查看角色", "查看角色列表"),
    ("manage_roles", "管理角色", "新增/编辑/删除角色"),
    ("manage_permissions", "管理权限", "新增/编辑/删除权限"),
    ("assign_roles", "分配角色", "给用户分配角色"),
    
    # 用户管理
    ("view_users", "查看用户", "查看用户账号列表"),
    ("manage_users", "管理用户", "新增/编辑/禁用用户账号"),
    ("reset_user_password", "重置密码", "重置用户登录密码"),
]

DEFAULT_ROLES = [
    {
        "name": "系统管理员",
        "code": "admin",
        "description": "全量系统权限，可管理所有模块",
        "is_system": True,
        "permissions": [p[0] for p in DEFAULT_PERMISSIONS],
    },
    {
        "name": "人事主管",
        "code": "hr_manager",
        "description": "人事核心业务权限，包括员工、考勤、请假、薪资管理",
        "is_system": False,
        "permissions": [
            "view_employees", "manage_employees", "view_employee_sensitive", "export_employees",
            "view_departments", "manage_departments", "view_positions", "manage_positions",
            "view_attendance", "manage_attendance", "export_attendance",
            "view_leaves", "approve_leave",
            "view_salaries", "manage_salaries", "disburse_salaries", "export_salaries",
            "view_reports", "view_sensitive_reports", "export_reports",
        ],
    },
    {
        "name": "人事专员",
        "code": "hr_staff",
        "description": "人事基础操作权限，不含薪资发放和敏感数据",
        "is_system": False,
        "permissions": [
            "view_employees", "manage_employees", "export_employees",
            "view_departments", "view_positions",
            "view_attendance", "manage_attendance",
            "view_leaves", "approve_leave",
            "view_salaries",
            "view_reports",
        ],
    },
    {
        "name": "部门主管",
        "code": "dept_manager",
        "description": "部门管理权限，可审批本部门请假",
        "is_system": False,
        "permissions": [
            "view_employees",
            "view_departments",
            "view_attendance",
            "view_leaves", "approve_leave",
            "view_reports",
        ],
    },
    {
        "name": "普通员工",
        "code": "employees",
        "description": "员工自助权限，可查看个人信息和申请请假",
        "is_system": False,
        "permissions": [
            "view_employees",
            "view_attendance",
            "view_leaves", "apply_leave",
        ],
    },
    {
        "name": "运维审计",
        "code": "auditor",
        "description": "只读审计权限，可查看日志和敏感报表",
        "is_system": False,
        "permissions": ["view_sensitive_reports", "manage_system_logs", "view_reports"],
    },
]

class Command(BaseCommand):
    help = "初始化默认 RBAC 权限及可选角色。默认只创建权限；加 --with-roles 创建示例角色。"

    def add_arguments(self, parser):
        parser.add_argument(
            "--with-roles", action="store_true", dest="with_roles", help="同时创建示例角色"
        )
        parser.add_argument(
            "--force", action="store_true", dest="force", help="强制重新指派角色的权限(仅对示例角色)"
        )

    @transaction.atomic
    def handle(self, *args, **options):
        with_roles = options.get("with_roles")
        force = options.get("force")

        self.stdout.write(self.style.MIGRATE_HEADING("[RBAC] 开始初始化权限"))
        created = 0
        for key, name, desc in DEFAULT_PERMISSIONS:
            obj, was_created = RBACPermission.objects.get_or_create(
                key=key,
                defaults={"name": name, "description": desc},
            )
            if not was_created:
                update_needed = False
                if obj.name != name:
                    obj.name = name; update_needed = True
                if desc and obj.description != desc:
                    obj.description = desc; update_needed = True
                if update_needed:
                    obj.save()
            else:
                created += 1
                self.stdout.write(self.style.SUCCESS(f"  + 权限创建: {key}"))
        self.stdout.write(self.style.NOTICE(f"权限初始化完成，新建 {created} 个，当前总数 {RBACPermission.objects.count()}"))

        if not with_roles:
            self.stdout.write(self.style.HTTP_INFO("跳过角色创建 (--with-roles 可启用)"))
            return

        self.stdout.write(self.style.MIGRATE_HEADING("[RBAC] 创建/更新示例角色"))
        for role_def in DEFAULT_ROLES:
            perms = list(RBACPermission.objects.filter(key__in=role_def["permissions"]))
            role, r_created = Role.objects.get_or_create(
                code=role_def["code"],
                defaults={
                    "name": role_def["name"],
                    "description": role_def["description"],
                    "is_system": role_def["is_system"],
                },
            )
            if r_created:
                role.permissions.set(perms)
                self.stdout.write(self.style.SUCCESS(f"  + 角色创建: {role.name} ({role.code})"))
            else:
                # 更新基础信息
                changed = False
                if role.name != role_def["name"]:
                    role.name = role_def["name"]; changed = True
                if role.description != role_def["description"]:
                    role.description = role_def["description"]; changed = True
                if role.is_system != role_def["is_system"]:
                    role.is_system = role_def["is_system"]; changed = True
                if changed:
                    role.save()
                if force:
                    role.permissions.set(perms)
                    self.stdout.write(self.style.WARNING(f"  * 覆盖权限集合: {role.code}"))
                else:
                    # 补齐缺失权限，不移除已存在的
                    missing = [p for p in perms if p not in role.permissions.all()]
                    if missing:
                        role.permissions.add(*missing)
                        self.stdout.write(self.style.SUCCESS(f"  + 追加缺失权限: {role.code} -> {', '.join(p.key for p in missing)}"))
            role.save()
        self.stdout.write(self.style.SUCCESS("示例角色处理完成"))
        self.stdout.write(self.style.SUCCESS("RBAC 初始化完毕"))
