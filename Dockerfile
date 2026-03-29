# Django 后端 Dockerfile - 服务器部署版
FROM python:3.11-slim

WORKDIR /app

# 复制并安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip install --no-cache-dir -r requirements.txt gunicorn -i https://pypi.tuna.tsinghua.edu.cn/simple

# 设置 Python 环境变量（优化内存）
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONMALLOC=malloc \
    MALLOC_TRIM_THRESHOLD_=100000

# 复制项目文件
COPY . .

# 创建必要目录并设置权限
RUN mkdir -p /app/media /app/logs && \
    chmod 777 /app && \
    touch /app/db.sqlite3 && \
    chmod 666 /app/db.sqlite3

# 收集静态文件
RUN python manage.py collectstatic --no-input || true

# 暴露端口
EXPOSE 8000

# 启动命令（只执行 migrate，不自动 loaddata 避免覆盖数据）
CMD ["sh", "-c", "python manage.py migrate && gunicorn hr_system.wsgi:application --bind 0.0.0.0:8000 --workers 1 --threads 2 --timeout 120 --max-requests 300 --max-requests-jitter 30 --worker-class sync --preload"]

