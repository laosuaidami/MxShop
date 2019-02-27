__author__ = 'hewei'
__date__ = '18-12-12'
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from user_operation.models import UserFav
# 注意必须要在apps.py中重载 ready 方法
@receiver(post_save, sender=UserFav)
def create_fav_num(sender, instance=None, created=False, **kwargs):
    if created:   # 只有新增 create 才为True
        goods = instance.goods
        goods.fav_num += 1
        goods.save()


@receiver(post_delete, sender=UserFav)
def delete_fav_num(sender, instance=None, created=False, **kwargs):
    goods = instance.goods
    goods.fav_num -= 1
    goods.save()



