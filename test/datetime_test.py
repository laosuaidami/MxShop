#!/usr/bin/env python3
# -*- coding:utf-8 -*-
__author__ = 'hewei'
__date__ = '18-12-20'

from datetime import datetime, timedelta

now = datetime.now()

yestoday = now - timedelta(days=1)
print('yestoday', yestoday)
tommorow = now + timedelta(days=1)
print('tommorow', tommorow)

next_year = now + timedelta(days=365)
print('next_year', next_year)
