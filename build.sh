#!/usr/bin/env bash
# Render 构建脚本

set -o errexit  # 出错立即退出

# 安装依赖
pip install -r requirements.txt

# 安装 gunicorn（生产服务器）
pip install gunicorn whitenoise

# 收集静态文件
python manage.py collectstatic --no-input

# 运行数据库迁移
python manage.py migrate

# 导入数据（如果存在）
if [ -f "data_clean.json" ]; then
    python manage.py loaddata data_clean.json || true
    echo "Data loaded"
fi

# 确保 admin 用户密码可用
python -c "
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_system.settings')
django.setup()
from django.contrib.auth.models import User
try:
    user = User.objects.get(username='admin')
    user.set_password('admin123')
    user.save()
    print('Admin password reset to admin123')
except User.DoesNotExist:
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Admin user created with password admin123')
"
