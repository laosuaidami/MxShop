#!/usr/bin/env python3
# -*- coding:utf-8 -*-
__author__ = 'hewei'
__date__ = '19-2-26'
from utils.yunpian import YunPian
from MxShop.settings import APIKEY

from celery.task import Task


class SendSmsTask(Task):
    name = 'send_sms_task'  # 定义任务的名字

    def run(self, *args, **kwargs):
        yun_pian = YunPian(APIKEY)
        sms_status = yun_pian.send_sms(code=kwargs['code'], mobile=kwargs['mobile'])
        print('args={}, kwargs={}, sms_status={}'.format(args, kwargs, sms_status))
        print(kwargs['code'], kwargs['mobile'])
        # return sms_status