#!/usr/bin/env python3
# -*- coding:utf-8 -*-
__author__ = 'hewei'
__date__ = '18-12-20'

from datetime import timedelta

import djcelery

djcelery.setup_loader()

# CELERY_TIMEZONE = 'Asia/Shanghai'

# 设置celery队列， 定时任务放到一个queue， 普通任务放到另一queue
CELERY_QUEUES = {
    'beat_tasks': {
        'exchange': 'beat_tasks',
        'exchange_type': 'direct',
        'binding_key': 'beat_tasks'
    },
    'work_queue': {
        'exchange': 'work_queue',
        'exchange_type': 'direct',
        'binding_key': 'work_queue'
    },
}

# 设置默认队列
CELERY_DEFAULT_QUEUE = 'work_queue'

CELERY_IMPORTS = (
    'goods.tasks',
    'users.tasks'
)

# 有些情况下可以放置死锁
CELERYD_FORCE_EXECV = True

# 设置并发的worker数量，一般情况下根据cup数量设置
CELERYD_CONCURRENCY = 4

# 允许重试
CELERY_ACKS_LATE = True

# 每个worker最多执行100个任务被销毁， 可以防止内存泄露
CELERYD_MAX_TASKS_PER_CHILD = 100

# 单个任务的最大运行时间
CELERYD_TASK_TIME_LIMIT = 12 * 30

# 配置定时任务
CELERYBEAT_SCHEDULE = {
    'task1': {
        'task': 'course_task',   # task的name
        'schedule': timedelta(minutes=10),
        'options': {
            'queue': 'beat_tasks'      # 指定队列
        },
        'args': (2, 8),
    },

}


# python manage.py celery worker -l INFO
# python manage.py celery beat -l INFO
# python manage.py celery flower --basic_auth=imooc:imooc
# celery flower --address=0.0.0.0 --port=5555 --broker=xxxx --basic_auth=imooc:imooc

# flower 安装 pip install flower

# 进程管理工具: supervisor
# install pip install supervisor
# start: supervisord -c /etc/supervisord.conf
# Tool: supervisorctl




