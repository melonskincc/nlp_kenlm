from __future__ import absolute_import

import django, os
from celery import Celery, platforms
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NLP.settings')
django.setup()
app = Celery('NLP')  # 创建celery应用
app.config_from_object('django.conf:settings', namespace='CELERY')  # 从配置文件中加载CELERY外的其他配置
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)  # 自动检索每个app下的tasks.py
platforms.C_FORCE_ROOT = True  # 允许root用户运行celery
