import os, sys

sys.path.append('/var/www/html/workorder')
os.environ['DJANGO_SETTINGS_MODULE'] = 'workorder.settings'
os.environ['PYTHON_EGG_CACHE'] = '/tmp/.python-eggs'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()


