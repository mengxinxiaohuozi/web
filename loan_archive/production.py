from .settings import *

# 生产环境安全设置
DEBUG = False
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'your-secret-key-here')

# 允许的主机
ALLOWED_HOSTS = ['*']  # 在实际部署时建议设置为具体的域名

# 数据库设置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join('/app/data', 'db.sqlite3'),
    }
}

# 静态文件设置
STATIC_ROOT = '/app/staticfiles'
STATIC_URL = '/static/'

# 媒体文件设置
MEDIA_ROOT = '/app/media'
MEDIA_URL = '/media/'

# 安全设置
SECURE_SSL_REDIRECT = False  # 如果使用HTTPS，设置为True
SESSION_COOKIE_SECURE = False  # 如果使用HTTPS，设置为True
CSRF_COOKIE_SECURE = False  # 如果使用HTTPS，设置为True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# 会话设置
SESSION_COOKIE_AGE = 86400  # 24小时
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# 中文设置
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_TZ = True

# 日志设置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/app/logs/django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
} 