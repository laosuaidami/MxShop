#!/usr/bin/env python3
# -*- coding:utf-8 -*-
__author__ = 'hewei'
__date__ = '18-12-20'
import time

from celery.task import Task


class CourseTask(Task):
    name = 'course_task'  # 定义任务的名字

    def run(self, *args, **kwargs):
        print('start course task')
        time.sleep(4)
        print('args={}, kwargs={}'.format(args, kwargs))
        print('end course task')








