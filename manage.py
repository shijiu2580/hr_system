"""
Django人事管理系统
HR Management System

管理命令和初始化脚本
"""

import os
import django
from django.core.management import execute_from_command_line

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_system.settings')
    django.setup()
    execute_from_command_line()




