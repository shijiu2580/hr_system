"""
初始化RBAC权限数据

用法：python manage.py init_rbac
"""
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from hr_management.models import RBACPermission, Role
from hr_management.rbac import PERMISSION_GROUPS, DEFAULT_ROLES


class Command(BaseCommand):
    help = '初始化RBAC权限和角色数据'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='强制更新已存在的权限和角色',
        )
    
    def handle(self, *args, **options):
        force = options.get('force', False)
        
        self.stdout.write('开始初始化RBAC权限数据...\n')
        
        # 1. 创建权限
        perm_created = 0
        perm_updated = 0
        all_permissions = {}
        
        for group_name, permissions in PERMISSION_GROUPS.items():
            self.stdout.write(f'  处理权限组: {group_name}')
            for key, name, description in permissions:
                perm, created = RBACPermission.objects.get_or_create(
                    key=key,
                    defaults={'name': name, 'description': description}
                )
                all_permissions[key] = perm
                
                if created:
                    perm_created += 1
                    self.stdout.write(self.style.SUCCESS(f'    + 创建权限: {key}'))
                elif force:
                    perm.name = name
                    perm.description = description
                    perm.save()
                    perm_updated += 1
                    self.stdout.write(f'    ~ 更新权限: {key}')
        
        self.stdout.write(f'\n权限: 新建 {perm_created} 个, 更新 {perm_updated} 个\n')
        
        # 2. 创建角色
        role_created = 0
        role_updated = 0
        
        for code, config in DEFAULT_ROLES.items():
            try:
                # 先尝试按 code 查找
                role = Role.objects.filter(code=code).first()
                
                if role:
                    # 角色存在，按需更新
                    if force:
                        role.name = config['name']
                        role.description = config['description']
                        role.is_system = config.get('is_system', False)
                        role.save()
                        role_updated += 1
                        self.stdout.write(f'  ~ 更新角色: {config["name"]} ({code})')
                    else:
                        self.stdout.write(f'  - 角色已存在: {role.name} ({code})')
                    created = False
                else:
                    # 角色不存在，创建新角色
                    role = Role.objects.create(
                        code=code,
                        name=config['name'],
                        description=config['description'],
                        is_system=config.get('is_system', False),
                    )
                    role_created += 1
                    created = True
                    self.stdout.write(self.style.SUCCESS(f'  + 创建角色: {config["name"]} ({code})'))
                
                # 设置权限
                perm_list = config.get('permissions', [])
                if perm_list == '*':
                    # 所有权限
                    role.permissions.set(all_permissions.values())
                    self.stdout.write(f'    -> 分配所有权限 ({len(all_permissions)} 个)')
                elif perm_list:
                    perms_to_add = [all_permissions[k] for k in perm_list if k in all_permissions]
                    role.permissions.set(perms_to_add)
                    self.stdout.write(f'    -> 分配 {len(perms_to_add)} 个权限')
                    
            except IntegrityError as e:
                self.stdout.write(self.style.WARNING(f'  ! 跳过角色 {code}: {e}'))
        
        self.stdout.write(f'\n角色: 新建 {role_created} 个, 更新 {role_updated} 个\n')
        
        # 统计
        self.stdout.write(self.style.SUCCESS(
            f'\n初始化完成！\n'
            f'  - 权限总数: {RBACPermission.objects.count()}\n'
            f'  - 角色总数: {Role.objects.count()}'
        ))
