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
from django.conf.urls import url, include
import xadmin
from django.views.static import serve
from rest_framework.documentation import include_docs_urls
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views
from rest_framework_jwt.views import obtain_jwt_token
from django.views.generic import TemplateView

from MxShop.settings import MEDIA_ROOT
from goods.views_base import DoTaskView
from goods.views import GoodsListView, GoodsListViewSet, CategoryViewSet, PriceRangeViewSet, HotSearchViewSet, BannerViewSet, IndexCategoryViewSet
from users.views import SmsCodeViewset, UserRegViewSet, UserViewSet
from user_operation.views import UserFavViewSet, LeavingMessageViewSet, AddressViewSet
from trade.views import ShopCatViewSet, OrderViewSet, AlipayView

# 方法一手工绑定
goods_list = GoodsListViewSet.as_view({
    'get': 'list'
})

# 方法二使用router
router = DefaultRouter()
router.register(r'goods', GoodsListViewSet,  base_name="goods")
router.register(r'categorys', CategoryViewSet, base_name='categorys')
router.register(r'price_range', PriceRangeViewSet, base_name='price_range')
router.register(r'codes', SmsCodeViewset, base_name='codes')
router.register(r'register', UserRegViewSet, base_name='register')
router.register(r'userfavs', UserFavViewSet, base_name='userfavs')
router.register(r'users', UserViewSet, base_name='users')
router.register(r'messages', LeavingMessageViewSet, base_name='messages')
router.register(r'address', AddressViewSet, base_name='address')
router.register(r'shopcarts', ShopCatViewSet, base_name='shopcarts')
router.register(r'orders', OrderViewSet, base_name='orders')
router.register(r'banners', BannerViewSet, base_name='banners')
router.register(r'hotsearchs', HotSearchViewSet, base_name='hotsearchs')
router.register(r'indexgoods', IndexCategoryViewSet, base_name='indexgoods')

urlpatterns = [
    url(r'^xadmin/', xadmin.site.urls),
    url(r'^media/(?P<path>.*)$', serve, {'document_root': MEDIA_ROOT}),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api-token-auth/', views.obtain_auth_token),  # drf 自带的token认证模式
    # url(r'^api-token-auth/', obtain_jwt_token),   # jwt的认证接口
    url(r'^login/', obtain_jwt_token),  # jwt的认证接口

    # 商品列表页
    # url(r'^goods/$', GoodsListView.as_view(), name='goods_list'),
    # url(r'^goods/$', goods_list, name='goods_list'),     # 方法一手工绑定
    url(r'^', include(router.urls)),                        # 方法二使用router
    url(r'docs/', include_docs_urls(title='慕学生鲜')),  # 不可以加$ 符号

    url(r'^alipay/return/', AlipayView.as_view(), name='alipay'),  # 阿里支付返回接口
    url(r'^do_tasks/$', DoTaskView.as_view(), name='do_task'),  # celery test demo
    url(r'^index/', TemplateView.as_view(template_name='index.html'), name='index'),  # 前端vue项目编译结果url
    url(r'^operation/', include('user_operation.urls', namespace='operation'))
]










