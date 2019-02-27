__author__ = 'hewei'
__date__ = '18-12-19'
import time
from celery_app import app


@app.task
def multiply(x, y):
    print('enter call multiply func ......')
    time.sleep(4)
    return x * y


