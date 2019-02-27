#!/usr/bin/env python3
# -*- coding:utf-8 -*-
__author__ = 'hewei'
__date__ = '19-2-16'
from raven import Client
DSN = 'http://1cde83fb411f46aab457d589767494a6:29d4aefe7bb745da837bc88bcee14de2@dayushu.top:9000/2'


client = Client(DSN)

try:
    1 / 0
except ZeroDivisionError:
    client.captureException()


try:
    a = (1,2)
    b = a[4]
except IndexError:
    client.captureException()
