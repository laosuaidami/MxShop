__author__ = 'hewei'
__date__ = '18-12-12'
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

User = get_user_model()


# https://www.django-rest-framework.org/api-guide/authentication/   中搜索post_save signals
# 注意注意一定要！！！：在apps中重载 ready 方法
@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        password = instance.password
        instance.set_password(password)
        instance.save()





