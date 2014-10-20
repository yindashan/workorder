# -*- coding:utf-8 -*-
# Django settings for project.
import os

DEBUG = True
#DEBUG = False
TEMPLATE_DEBUG = DEBUG
#TEMPLATE_DEBUG = False

HERE = os.path.dirname(os.path.dirname(__file__))

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'workorder', # Or path to database file if using sqlite3.
        'USER': 'root', # Not used with sqlite3.
        'PASSWORD': 'root', # Not used with sqlite3.
        'HOST': 'localhost', # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '3306', # Set to empty string for default. Not used with sqlite3.
    },
    'radius': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'radius', # Or path to database file if using sqlite3.
        'USER': 'root', # Not used with sqlite3.
        'PASSWORD': 'da4321', # Not used with sqlite3.
        'HOST': 'localhost', # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '3306', # Set to empty string for default. Not used with sqlite3.
    }
}
# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Asia/Shanghai'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'zh-cn'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(HERE, 'media').replace('\\', '/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(HERE, 'static').replace('\\', '/')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(HERE, 'static/develop/').replace('\\', '/'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'aup47ns$^=ec2uvcp6@i#a!w=6%h@%c690)=$980wpvy!q=ar6'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'workorder.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'workorder.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(HERE, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    # 'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'django.contrib.admin',
    'dynamicconfig',
    'log',
    'authority',
    'account',
    'role',
    'order',
    'problem',
    'staff',
    'executive',
    'area',
     # Celery 相关库
    'djcelery',
    'kombu.transport.django',
    'macaddr',
    'feedback',
    'wirelessacct',
    'software',
    'installrecord',
    'ittask',
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(threadName)s:%(thread)d] [%(name)s:%(lineno)d] [%(levelname)s]- %(message)s'
        },
    },
    'filters': {
    },
    'handlers': {
        'default': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/workorder/all.log', #或者直接写路径：'c://logs/all.log',
            'maxBytes': 1024 * 1024 * 5, # 5 MB
            'backupCount': 5,
            'formatter':'standard',
        },
        'notify': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/workorder/notify.log', #或者直接写路径：'c://logs/all.log',
            'maxBytes': 1024 * 1024 * 5, # 5 MB
            'backupCount': 5,
            'formatter':'standard',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': False
        },
        'django.notify': {
            'handlers': ['notify'],
            'level': 'INFO',
            'propagate': True
        },
    }
}          

# The URL where requests are redirected for login, especially when using the login_required() decorator.
# 登录页URL 
LOGIN_URL = "/loginpage"

# 设置 用户关闭浏览器，则session失效
SESSION_EXPIRE_AT_BROWSER_CLOSE = "true"

# 会话ID在cookie中的名称
SESSION_COOKIE_NAME = "workorder_sessionid"

# CSRF token在cookie 中的名称
CSRF_COOKIE_NAME = "workorder_csrftoken"


# 工单系统访问地址(邮件中会用到)
#SERVICE_ADDRESS = "http://10.2.50.50:84"
SERVICE_ADDRESS = "http://10.2.161.15:81"

# -------------　邮件发送 --------------------
# smtp 服务器用户名
MAIL_USER = "test"

# smtp 服务器密码
MAIL_PASSWORD = "test"

# 邮件服务器
MAIL_SERVER = "smtp.company.com"

IT_HEAD_EMAIL = "test@company.com"


# -------------- 短信发送 ------------------
# *** 注意短信内容必须是GBK编码 ***
# 短信通道用户名
SMS_USER = "test"

# 短信通道密码
SMS_PASSWORD = "test"

# 短信服务器
SMS_SERVER = "255.255.255.255"

# 端口
SMS_PORT = 443

# servlet_url 
SERVLET_URL = "/smmp"


# -------------- Mac 地址文件  ------------------
# 文件路径
# MAC_DIR = '/var/mac_addr'
MAC_DIR = 'd:\\test'


# ------------  异步框架Celery相关参数 --------------------
# celery命令行工具本身是不支持以daemon方式运行
# 可以使用nohup 或　Supervisord 进行管理
# ***定时任务***
# nohup python manage.py celery beat -s /var/log/workorder/celerybeat-schedule  --logfile=/var/log/workorder/celerybeat.log  -l info & 

# ***worker***
# nohup python manage.py celery worker --concurrency=1 --logfile=/var/log/workorder/celery.log -l info &
# ------------------------------------------------------
import djcelery
from datetime import timedelta
djcelery.setup_loader()

CELERY_IMPORTS = ("notify.models", "wirelessacct.models", "ittask.models")
BROKER_URL = 'django://'

CELERY_TIMEZONE = 'Asia/Shanghai'

# 定时器
CELERYBEAT_SCHEDULE = {
    'sync_radius': {
        'task': 'wirelessacct.models.sync_radius',
        'schedule': timedelta(seconds=10),
        #'args': (redis_db),
        #'options' : {'queue':'db_write_back_queue'}
    },
    'update_status_notify': {
        'task': 'ittask.models.update_notify',
        'schedule': timedelta(seconds=10),
        #'args': (redis_db),
        #'options' : {'queue':'db_write_back_queue'}
    },
}













