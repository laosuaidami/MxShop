__author__ = 'hewei'
__date__ = '18-12-19'

# import time
#
# from celery_task import add
#
#
# if __name__ == '__main__':
#     print('start running.......')
#     result = add.delay(2, 1)
#     print('the task is over')
#     print(result)
#     while True:
#         time.sleep(0.3)
#         print(result.ready())
#         if result.ready():
#             print('take value: {}'.format(result.get()))   # 获取执行结果
#             break
#

# -------------------------分割线-------------------------------------
import time

from celery_app import task1
from celery_app import task2


if __name__ == '__main__':
    print('start running.......')
    t1 = task1.add.delay(2, 4)
    t2 = task2.multiply.delay(4, 5)
    print('the task is over')
    while True:               # 获取执行结果
        time.sleep(0.3)
        print(t1.ready())
        if t1.ready():
            print('take value: {}'.format(t1.get()))
            break

        print(t2.ready())
        if t2.ready():
            print('take value: {}'.format(t2.get()))
            break




# 分别运行
#  celery worker -A celery_app -l INFO
#  celery beat -A celery_app -l INFO

# 一条命令运行
# celery -B -A celery_app worker -l INFO