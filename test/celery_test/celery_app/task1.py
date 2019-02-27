__author__ = 'hewei'
__date__ = '18-12-19'
import time
from celery_app import app


@app.task
def add(x, y):
    print('enter call  add func ......')
    time.sleep(4)
    return x + y


