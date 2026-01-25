"""Django HR Management System - Settings"""
from pathlib import Path
from datetime import timedelta
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

# Security
SECRET_KEY = config('SECRET_KEY', default='django-insecure-your-secret-key-here')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',') + ['.ngrok-free.dev', '.ngrok.io', '.canway.site', 'canway.site']

# Apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'drf_spectacular',
    'hr_management',
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # 静态文件服务
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 自定义中间件
    'hr_management.middleware.SecurityHeadersMiddleware',
    'hr_management.middleware.GZipAPIMiddleware',
    'hr_management.middleware.APIPerformanceMiddleware',
]

ROOT_URLCONF = 'hr_system.urls'
WSGI_APPLICATION = 'hr_system.wsgi.application'

# Templates (minimal, only for Django Admin)
TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ],
    },
}]

# Database
# SQLite 配置（开发环境）
# 生产环境建议使用 PostgreSQL
DATABASE_URL = config('DATABASE_URL', default=None)
DATABASE_PATH = config('DATABASE_PATH', default=None)

if DATABASE_URL:
    # 生产环境使用环境变量配置
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.config(default=DATABASE_URL, conn_max_age=600)
    }
else:
    # 开发环境使用 SQLite
    # 支持通过环境变量自定义数据库路径（用于 Docker 持久化）
    db_path = DATABASE_PATH if DATABASE_PATH else BASE_DIR / 'db.sqlite3'
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': db_path,
            'OPTIONS': {
                'timeout': 20,  # 防止锁超时
            },
        }
    }

# 数据库连接池配置（PostgreSQL）
# 如果使用 PostgreSQL，建议配置连接池
if not DEBUG and DATABASE_URL:
    DATABASES['default']['CONN_MAX_AGE'] = 60  # 连接保持60秒
    DATABASES['default']['CONN_HEALTH_CHECKS'] = True

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Localization
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

# Static & Media
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated'],
    'DEFAULT_PAGINATION_CLASS': 'hr_management.pagination.StandardPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_RENDERER_CLASSES': ['rest_framework.renderers.JSONRenderer'],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    # 自定义异常处理
    'EXCEPTION_HANDLER': 'hr_management.middleware.custom_exception_handler',
}

# API Documentation
SPECTACULAR_SETTINGS = {
    'TITLE': 'HR管理系统 API',
    'DESCRIPTION': '''
## 人力资源管理系统 RESTful API

### 功能模块
- **员工管理**: 员工信息的增删改查
- **考勤管理**: 打卡、补卡、统计
- **请假管理**: 请假申请与审批
- **薪资管理**: 工资计算与发放
- **组织架构**: 部门与职位管理
- **权限管理**: RBAC 角色权限控制

### 认证方式
使用 JWT (JSON Web Token) 认证：
1. 调用 `/api/auth/token/` 获取 access_token
2. 在请求头中添加 `Authorization: Bearer <access_token>`
3. Token 过期后使用 refresh_token 刷新

### 通用响应格式
```json
{
    "count": 100,      // 列表接口：总数
    "next": "url",     // 列表接口：下一页
    "previous": "url", // 列表接口：上一页
    "results": []      // 列表接口：数据
}
```

### 错误响应
```json
{
    "detail": "错误信息",
    "code": "error_code"
}
```
    ''',
    'VERSION': '1.2.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'CONTACT': {
        'name': 'HR System Support',
        'email': 'support@hrsystem.local',
    },
    'LICENSE': {
        'name': 'MIT License',
    },
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayRequestDuration': True,
        'filter': True,
        'showExtensions': True,
    },
    'SWAGGER_UI_DIST': 'SIDECAR',
    'SWAGGER_UI_FAVICON_HREF': 'SIDECAR',
    'REDOC_DIST': 'SIDECAR',
    # 分组配置
    'TAGS': [
        {'name': '认证', 'description': '用户认证与授权'},
        {'name': '员工', 'description': '员工信息管理'},
        {'name': '考勤', 'description': '考勤打卡与统计'},
        {'name': '请假', 'description': '请假申请与审批'},
        {'name': '薪资', 'description': '薪资计算与发放'},
        {'name': '组织', 'description': '部门与职位管理'},
        {'name': '系统', 'description': '系统管理与监控'},
        {'name': '报表', 'description': '数据统计与报表'},
    ],
    'COMPONENT_SPLIT_REQUEST': True,
    'SORT_OPERATIONS': False,
}

# JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=2),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
}

# CORS
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = config('CORS_ALLOW_ALL', default=False, cast=bool)
_cors_env = config('CORS_ORIGINS', default='http://localhost:5173,http://127.0.0.1:5173')
CORS_ALLOWED_ORIGINS = [o.strip() for o in _cors_env.split(',') if o.strip()]
# 添加 ngrok 和 canway.site 域名支持
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://.*\.ngrok-free\.dev$",
    r"^https://.*\.ngrok\.io$",
    r"^https://.*\.canway\.site$",
    r"^https://canway\.site$",
    r"^http://.*\.canway\.site$",
    r"^http://canway\.site$",
]
CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS + [
    'https://*.ngrok-free.dev', 'https://*.ngrok.io',
    'https://canway.site', 'https://*.canway.site',
    'http://canway.site', 'http://*.canway.site',
    'http://159.75.138.185:3000', 'http://159.75.138.185:3001', 'http://159.75.138.185:8000',
]

# API Throttling - 详细限流配置
if config('ENABLE_THROTTLE', default=True, cast=bool):
    REST_FRAMEWORK['DEFAULT_THROTTLE_CLASSES'] = [
        'hr_management.throttling.BurstRateThrottle',
        'hr_management.throttling.SustainedRateThrottle',
    ]
    REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
        # 基础限流
        'anon': config('THROTTLE_ANON_RATE', default='30/min'),
        'user': config('THROTTLE_USER_RATE', default='120/min'),
        # 自定义限流
        'burst': config('THROTTLE_BURST_RATE', default='60/min'),
        'sustained': config('THROTTLE_SUSTAINED_RATE', default='10000/day'),
        'login': config('THROTTLE_LOGIN_RATE', default='5/min'),
        'password_reset': config('THROTTLE_PASSWORD_RESET_RATE', default='3/hour'),
        'export': config('THROTTLE_EXPORT_RATE', default='10/hour'),
        'upload': config('THROTTLE_UPLOAD_RATE', default='30/hour'),
        'report': config('THROTTLE_REPORT_RATE', default='20/hour'),
    }

# Production Security
if not DEBUG:
    if SECRET_KEY == 'django-insecure-your-secret-key-here':
        raise RuntimeError('Production requires secure SECRET_KEY in environment')
    
    # 只有在启用 SSL 重定向时才要求安全 Cookie
    _ssl_redirect = config('SECURE_SSL_REDIRECT', default=False, cast=bool)
    SESSION_COOKIE_SECURE = _ssl_redirect
    CSRF_COOKIE_SECURE = _ssl_redirect
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    if _ssl_redirect:
        SECURE_HSTS_SECONDS = 2592000  # 30 days
        SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_SSL_REDIRECT = _ssl_redirect
    SESSION_COOKIE_HTTPONLY = True
    CSRF_COOKIE_HTTPONLY = True
    X_FRAME_OPTIONS = 'DENY'

# Logging Configuration - 增强日志配置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {name} {module}:{lineno} - {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'simple': {
            'format': '[{levelname}] {message}',
            'style': '{',
        },
        'json': {
            'format': '{{"level": "{levelname}", "time": "{asctime}", "module": "{module}", "message": "{message}"}}',
            'style': '{',
            'datefmt': '%Y-%m-%dT%H:%M:%S',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            'filters': ['require_debug_true'],
        },
        'console_production': {
            'class': 'logging.StreamHandler',
            'formatter': 'json',
            'filters': ['require_debug_false'],
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'app.log',
            'maxBytes': 10 * 1024 * 1024,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
            'encoding': 'utf-8',
        },
        'error_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'error.log',
            'maxBytes': 10 * 1024 * 1024,  # 10MB
            'backupCount': 10,
            'formatter': 'verbose',
            'level': 'ERROR',
            'encoding': 'utf-8',
        },
        'security_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'security.log',
            'maxBytes': 10 * 1024 * 1024,  # 10MB
            'backupCount': 10,
            'formatter': 'verbose',
            'encoding': 'utf-8',
        },
    },
    'root': {
        'handlers': ['console', 'console_production'],
        'level': 'INFO' if not DEBUG else 'DEBUG',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'console_production'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console', 'console_production', 'error_file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['console', 'console_production', 'security_file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'hr_management': {
            'handlers': ['console', 'console_production', 'file'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        'hr_management.security': {
            'handlers': ['console', 'console_production', 'security_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# 确保日志目录存在
(BASE_DIR / 'logs').mkdir(exist_ok=True)

# QQ邮箱SMTP配置
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.qq.com')
EMAIL_PORT = config('EMAIL_PORT', default=465, cast=int)
EMAIL_USE_SSL = config('EMAIL_USE_SSL', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')  # QQ邮箱授权码
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default=EMAIL_HOST_USER)

# 节假日API配置（用于判断工作日/调休）
HOLIDAY_API_ENABLED = config('HOLIDAY_API_ENABLED', default=True, cast=bool)
