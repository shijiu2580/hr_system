"""创建财务角色"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_system.settings')
import django
django.setup()

from hr_management.models import Role, RBACPermission

# 创建财务角色
finance_role, created = Role.objects.get_or_create(
    code='finance',
    defaults={'name': '财务', 'description': '负责薪资发放和财务管理'}
)
if created:
    print(f'创建角色: {finance_role.name}')
else:
    print(f'角色已存在: {finance_role.name}')

# 分配权限
perms_to_add = ['salary.view', 'salary.view_all', 'salary.disburse', 'expense.view', 'expense.view_all', 'expense.approve', 'expense.pay']
for key in perms_to_add:
    try:
        perm = RBACPermission.objects.get(key=key)
        finance_role.permissions.add(perm)
        print(f'  + {key}')
    except RBACPermission.DoesNotExist:
        print(f'  - {key} (不存在)')

print()
perms = list(finance_role.permissions.values_list('key', flat=True))
print(f'财务角色权限: {perms}')
