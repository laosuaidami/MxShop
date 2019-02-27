#!/usr/bin/env python3
# -*- coding:utf-8 -*-
__author__ = 'hewei'
__date__ = '19-1-15'

"""MxShop URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from rest_framework.routers import DefaultRouter
from django.conf.urls import url, include
from .views import test1_view, hello_world, my_view_test, my_view, UserFavViewSet, LeavingMessageViewSet, AddressViewSet, GoodsListView

router = DefaultRouter()
router.register(r'userfavs', UserFavViewSet, base_name='userfavs')
router.register(r'messages', LeavingMessageViewSet, base_name='messages')
router.register(r'address', AddressViewSet, base_name='address')

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^test_view/$', GoodsListView.as_view(), name='test_view'),
    url(r'^my_view/$', my_view),
    url(r'^hello_world/(\d+)/$', hello_world),
    url(r'^my_view_test/$', my_view_test),
]















