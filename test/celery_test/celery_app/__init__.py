__author__ = 'hewei'
__date__ = '18-12-19'

from celery import Celery


app = Celery('demo')
app.config_from_object('celery_app.celeryconfig')  # 通过 Celery 实例加载配置模块


#celery worker -A celery_app -l INFO