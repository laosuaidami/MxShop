__author__ = 'hewei'
__date__ = '18-12-19'
from datetime import timedelta
from celery.schedules import crontab

BROKER_URL = 'redis://localhost:6379/1'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/2'
CELERY_TIMEZONE = 'Asia/Shanghai'

# 导入任务模块
CELERY_IMPORTS = (
    'celery_app.task1',
    'celery_app.task2',
)

# 配置定时任务
CELERYBEAT_SCHEDULE = {
    'task1': {
        'task': 'celery_app.task1.add',     # 任务
        'schedule': timedelta(seconds=10),  # 每10s执行一次这个任务
        'args': (2, 8),                     # 参数
    },
    'task2': {
        'task': 'celery_app.task2.multiply',
        'schedule': crontab(hour=12, minute=6),   # 每天12点6分执行这个任务
        'args': (5, 8),
    }
}

# 分别运行
#  celery worker -A celery_app -l INFO
#  celery beat -A celery_app -l INFO

# 一条命令运行
# celery -B -A celery_app worker -l INFO
