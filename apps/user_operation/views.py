import time

from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.authentication import SessionAuthentication
from django.utils.encoding import force_text

from .models import UserFav, UserLeavingMessage, UserAddress
from .serializers import UserFavSerializer, UserFavDetailSerializer, LeavingMessageSerializer, AddressSerializer
from utils.permissions import IsOwnerOrReadOnly
# Create your views here.

from django.utils.translation import ugettext as _
from django.utils.translation import ungettext, pgettext_lazy
from django.http import HttpResponse


# 国际化和本地化测试
def my_view(request):
    output = _("Welcome to my site123")
    return HttpResponse(output)


def test1_view(request):
    """
    指定标准的翻译
    :param request:
    :return:
    """
    # 获得系统本地时间，返回的格式是 UTC 中的 struct_time 数据
    t = time.localtime()
    # 第 6 个元素是 tm_wday , 范围为 [0,6], 星期一 is 0
    n = t[6]
    # 星期一到星期日字符串

    weekdays = [_('Monday'), _('Tuesday'), _('Wednesday'), _('Thursday'), _('Friday'), _('Saturday'), _('Sunday')]
    # 返回一个 HttpResponse、，这段代码将用来返回服务器系统上是星期几。
    return HttpResponse(weekdays[n])

    # weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday','Friday', 'Saturday', 'Sunday']
    # return HttpResponse(_(weekdays[n]))


def my_view_test(request):
    m = 'asdgg'
    # d = '13'
    k = 12
    # output = _('Today is %(month)s %(day)s.') % {'month': m, 'day': d}
    # output = _('Today is %(month)d') % {'month': k}
    # input = _('Change history today: %s') % force_text(m)
    input = _('Sunday')
    # input = _('Monday')
    # input1 = _('0 of %(cnt)s select select') % {'cnt': k}
    # output = _('Today is {month} {day}').format(month=m, day=d)
    return HttpResponse(input)


def hello_world(request, count):
    """
    复数
    :param request:
    :param count:
    :return:
    """
    count = int(count)
    # page = ungettext('there is %(total_count)s object', 'there are %(total_count)s objects', count) % {'total_count': count}
    # page = ungettext('there is %(total_count)s object', 'there are %(total_count)s objects', count) % {'total_count': count}
    # value = ungettext('%(total_count)s selected', 'All %(total_count)s selected', count) % {'total_count': count}

    # value = ungettext('%(total_count)s selected', '%(total_count)s selected', count) % {'total_count': count}
    text = ungettext(
        'There is %(count)d  object available.',
        'There are %(count)d  objects available.',
        count) % {'count': count}
    return HttpResponse(text)


class UserFavViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                     mixins.DestroyModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    list:
        获取用户收藏列表
    retrieve:
        判断某个商品是否已经收藏
    create:
        收藏商品
    """
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)  # 验证用户是否登录， 是否是当前用户IsOwnerOrReadOnly
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)  # 验证Token，并且将User放到request.user中
    # queryset = UserFav.objects.all()    # queryset 和get_queryset功能一样二者取其一
    # lookup_field设置获取查询字段, 默认pk, DestroyModelMixin, RetrieveModelMixin 这两个中的get_object(),定义在GenericViewSet的父类中
    # 正常我们获取通过pk获取,但是如果将lookup_field = 'goods_id'，就可以通过商品id来获取收藏
    lookup_field = 'goods_id'

    def get_queryset(self):
        # a = {}
        # print(a['b'])  # 测式sentry日志收集
        return UserFav.objects.filter(user=self.request.user)
        # return UserFav.objects.all()

    # 这是方法一，方法二使用信号量 (实现商品收藏数统计)
    # def perform_create(self, serializer):  # 此方法只有在CreateModelMixin
    #     instance = serializer.save()    # serializer.save 返回model实例
    #     goods = instance.goods
    #     goods.fav_num += 1
    #     goods.save()

    # 动态设置 serializer_class
    # serializer_class = UserFavSerializer
    def get_serializer_class(self):
        """
        Return the class to use for the serializer.
        Defaults to using `self.serializer_class`.

        You may want to override this if you need to provide different
        serializations depending on the incoming request.

        (Eg. admins get full serialization, others get basic serialization)
        """
        assert self.serializer_class is None, (
                "'%s' should either include a `serializer_class` attribute, "
                "or override the `get_serializer_class()` method."
                % self.__class__.__name__
        )
        if self.action == 'list':  # 只有继承GenericViewSet 才可以使用self.action
            return UserFavDetailSerializer   # 查看用户收藏时需要显示收藏的商品
        elif self.action == 'create':
            return UserFavSerializer         # 收藏时需要填写收藏商品的id
        return UserFavSerializer


class LeavingMessageViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                            mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """
    list:
        获取用户留言
    delete:
        删除留言
    create:
        添加留言
    """
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)  # 验证用户是否登录， 是否是当前用户
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = LeavingMessageSerializer

    def get_queryset(self):
        return UserLeavingMessage.objects.filter(user=self.request.user)


class AddressViewSet(viewsets.ModelViewSet):
    """
    list:
        获取收货地址
    delete:
        删除收货地址
    create:
        添加收货地址
    update:
        更新收货地址
    """
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)  # 验证用户是否登录， 是否是当前用户
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = AddressSerializer

    def get_queryset(self):
        return UserAddress.objects.filter(user=self.request.user)


from rest_framework.response import Response
from rest_framework import status
from goods.models import Goods
from goods.serializers import GoodsSerializer


# 测试文档功能
class GoodsListView(APIView):
    """
    List all snippets, or create a new snippet.
    """
    def get(self, request, format=None):
        goods = Goods.objects.all()[:10]
        goods_serializer = GoodsSerializer(goods, many=True)
        return Response(goods_serializer.data)

    def post(self, request):
        serializer = GoodsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)

