import time
from datetime import datetime

from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.authentication import SessionAuthentication
from rest_framework import viewsets, mixins
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import redirect

from utils.permissions import IsOwnerOrReadOnly
from .serializers import ShopCartSerializer, ShopCartDetailSerializer, OrderSerializer, OrderDetailSerializer
from .models import ShoppingCart, OrderGoods, OrderInfo
from utils.alipay import alipay_verify_return_data
# Create your views here.


class ShopCatViewSet(viewsets.ModelViewSet):
    """
    购物车功能
    list:
        获取购物车详情
    delete:
        删除购物车记录
    create:
        添加购物车商品
    update:
        更新购物车记录
    """
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)  # 验证用户是否登录， 是否是当前用户
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    lookup_field = 'goods_id'

    def perform_create(self, serializer):
        shop_cart = serializer.save()
        goods = shop_cart.goods
        goods.goods_num -= shop_cart.nums
        goods.save()

    def perform_destroy(self, instance):
        goods = instance.goods
        goods.goods_num += instance.nums
        goods.save()
        instance.delete()

    def perform_update(self, serializer):
        existed_record = ShoppingCart.objects.get(id=serializer.instance.id)  # serializer.instance 获取当前的实例
        saved_record = serializer.save()
        nums = saved_record.nums - existed_record.nums
        goods = saved_record.goods
        goods.goods_num -= nums
        goods.save()

    def get_serializer_class(self):
        if self.action == 'list':
            return ShopCartDetailSerializer
        else:
            return ShopCartSerializer

    def get_queryset(self):
        return ShoppingCart.objects.filter(user=self.request.user)


class OrderViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
        订单功能
        list:
            获取个人订单详情
        delete:
            删除订单记录
        create:
            添加订单
        retrieve:
            获取订单详情
        """
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)  # 验证用户是否登录， 是否是当前用户
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = OrderSerializer

    def get_queryset(self):
        return OrderInfo.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        order = serializer.save()
        shop_carts = ShoppingCart.objects.filter(user=self.request.user)
        for shop_cart in shop_carts:
            order_goods = OrderGoods()
            order_goods.goods = shop_cart.goods
            order_goods.goods_num = shop_cart.nums
            order_goods.order = order
            order_goods.save()

            shop_cart.delete()
        return order

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return OrderDetailSerializer
        else:
            return OrderSerializer


class AlipayView(APIView):
    def get(self, request):
        """
        处理支付宝的return_url返回
        :param request:
        :return:
        """
        processed_dict = {}
        for key, value in request.GET.items():
            processed_dict[key] = value
        verify_ret = alipay_verify_return_data(processed_dict)

        if verify_ret is True:
            response = redirect('index')
            response.set_cookie('nextPath', 'pay', max_age=2)
            return response

        else:
            response = redirect('index')
            return response

    def post(self, request):
        """
        处理支付宝的notify_url
        :param request:
        :return:
        """
        processed_dict = {}
        for key, value in request.POST.items():
            processed_dict[key] = value
        verify_ret = alipay_verify_return_data(processed_dict)

        if verify_ret is True:
            out_trade_no = processed_dict.get('out_trade_no', None)
            trade_no = processed_dict.get('trade_no', None)
            trade_status = processed_dict.get('trade_status', None)

            existed_order = OrderInfo.objects.filter(order_sn=out_trade_no)
            if len(existed_order) == 1:
                # 统计销售量
                order_goods = existed_order[0].goods.all()  # 通过OrderGoods中外键的related_name="goods" 获取订单中的商品
                for order_good in order_goods:
                    goods = order_good.goods
                    goods.sold_num += order_good.goods_num
                    goods.save()
                # 修改订单支付状态
                existed_order[0].pay_status = trade_status
                existed_order[0].trade_no = trade_no
                existed_order[0].pay_time = datetime.now()
                existed_order[0].save()
                return Response('success')   # 需要给支付宝返回 success，不然支付宝，会不停发送消息













